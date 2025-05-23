
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
from backend_filepro import FileHandler
from werkzeug.utils import secure_filename, send_file
from gen_syn import GenModel, generate_judge_eng
from syn_database import DataHandler
import time
from document_pro import ProjectHandler
from db import ChunkDatabase
from faiss_index import FaissIndex

app = Flask(__name__)
CORS(app)  # Allows React frontend to talk to Flask backend

logging.basicConfig(level=logging.INFO)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get backend folder path

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")  # Dynamically set uploads path
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure folder exists

# Generate judge and engineer information
judge, eng = generate_judge_eng(syn_number=5)  # Change the number to the user's preference
    
# Initialize the synonym generator 
syn = GenModel('gpt-4o', "You are a Dutch linguist and construction specialist with expertise in industry terminology. Output only five words separated by commas")
db_handler = DataHandler(os.path.join(os.getcwd(), "data", "syn_db.json"))

global p_handler # to delete
p_handler = ProjectHandler(10)  # Initialize the project handler

global handler
handler = FileHandler([])  # Initialize the file handler

global db 
db = ChunkDatabase()  # Initialize the database handler

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/upload", methods=["POST"])
def upload_file():
    """Upload files to the server."""
    if "files" not in request.files:
        return jsonify({"error": "No files uploaded"}), 400

    files = request.files.getlist("files")  # Get multiple files
    uploaded_files = []

    for file in files:
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)  # Save file locally
        uploaded_files.append(file_path)

    if not uploaded_files:
        return jsonify({"error": "No valid files uploaded"}), 400
    
    print(f"Uploaded files: {uploaded_files}")  # Log the uploaded files
    handler.initialize(uploaded_files)  # Reset the project with the new files

    return jsonify({
        "message": "Files uploaded successfully!",
        "files": uploaded_files
    }), 200

@app.route("/process-files", methods=["POST"])
def process_files():
    """Process uploaded files."""
    handler.process_all_files() # processes them
    db.insert_chunks(handler.get_project_name(), handler.get_results())  # Save chunks to the database
    return jsonify({"message": "Files processed successfully"}), 200


@app.route("/search", methods=["POST"])
def search():
    data = request.json
    keywords = data.get("keyword", [])

    if not isinstance(keywords, list):
        return jsonify({"error": "No keyword provided"}), 400
    
    emb = db.get_embeddings_by_project(handler.get_project_name())  # Get chunks from the database

    f = FaissIndex(emb, temperature=0.1)  # Initialize the FAISS index
    f.f_search(keywords, db)  # Search for keywords in the FAISS index and save them in the database

    #print("[DEBUG] Manually calling add_keyword_and_distance()...")
    #db.add_keyword_and_distance("2b5813b4-0079-40b3-aea3-3c886eb2469e", "machine", 0.123)

    return jsonify({"message": "Search completed!"})

@app.route("/download_zip", methods=["GET"])
def download_zip():
    zip_file_path = "backend/zipped_results"

    if os.path.exists(zip_file_path):
        return send_file(zip_file_path, as_attachment=True)
    else:
        return jsonify({"error": "ZIP file not found."}), 404


    
@app.route("/get_synonyms", methods=["POST"])
def getting_syn(): 
    try:
        # Get the keywords from the request data
        data = request.get_json()
        keywords = data.get("keywords", [])
        all_words = []

        if not keywords:
            return jsonify({"error": "No keywords provided"}), 400
            
        for keyword in keywords: 
            if db_handler.is_saved(keyword):
                synonyms = db_handler.get_synonyms(keyword)
            else: 
                prompt = f'Find 5 dutch synonyms of {keyword}'
                synonyms = syn.generate_synonyms(prompt)
                db_handler.add_synonyms(keyword, synonyms)

            all_words.extend(synonyms)
            print(f'MAIN;"{keyword}" synonyms: {synonyms}')

        all_words = list(set(word.lower() for word in all_words))
        
        return jsonify({"synonyms": all_words}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/uploaded_files", methods=["GET"])
def list_uploaded_files():
    files = []
    for filename in os.listdir(app.config["UPLOAD_FOLDER"]):
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        filename_ = "uploads/" + filename
        if os.path.isfile(file_path):
            files.append({
                "filename": filename,
                "uploaded_at": time.ctime(os.path.getmtime(file_path)),
                "scanned": True,
                "keywords": "N/A"
            })
    return jsonify({"files": files})

@app.route("/delete_file", methods=["POST"])
def delete_file():
    data = request.get_json()
    filename = data.get("filename")

    if not filename:
        return jsonify({"error": "Filename not provided"}), 400

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({"message": f"{filename} deleted successfully"}), 200
    else:
        return jsonify({"error": "File not found"}), 404

    
@app.route("/fetch_results", methods=["GET"])
def fetch_results():
    try:
        project_name = handler.get_project_name()  # Get the current project name
        results = db.get_filename(project_name)  # Fetch filenames and keywords from the database
        print(f"Fetched results: {results}")  # Log the fetched results
        
        return jsonify({"results": results}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/fetch_docresults/<filename>", methods=["GET"])
def fetch_doc_results(filename):
    try:

        print(f"Fetching results for filename: {filename}")
        project_name = handler.get_project_name()
        if not project_name:
            return jsonify({"error": "Missing project name"}), 400

        results = db.get_chunks_by_project_and_file(project_name, filename)
        return jsonify({"results": results}), 200

    except Exception as e:
        print(f"Error in /fetch_docresults: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/set_project_name", methods=["POST"])
def set_project_name():
    try:
        data = request.get_json()  # Get the JSON data from the request
        project_name = data.get("projectName")  # Extract the project name

        if not project_name:
            return jsonify({"error": "Project name is required"}), 400
        handler.reset_project()  # Reset the project name and results
        handler.set_project_name(project_name)  # Set the project name in the handler

        return jsonify({"success": True, "message": f"Project '{project_name}' created successfully."}), 200
    except Exception as e:
        print(f"Error in /set_project_name: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/projects", methods=["GET"])
def get_projects():
    try:
        # Retrieve the list of projects from the ProjectHandler
        projects = db.get_projects()  # Returns list of project names as strings
        project_data = [{"projectName": name} for name in projects]
        return jsonify({"projects": project_data}), 200
    except Exception as e:
        print(f"Error in /projects: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.debug = True  # Enable debug mode for development
    app.run()