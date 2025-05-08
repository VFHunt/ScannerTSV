from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
import pickle
from backend_filepro import FileHandler
from werkzeug.utils import secure_filename, send_file
from test_search import search_terms_in_pinecone, create_zip
from gen_syn import GenModel, generate_judge_eng, augment_prompt
from syn_database import DataHandler
from vector_db import upload_to_pinecone
import time
from pinecone import Pinecone
import json
from document_pro import DocHandler, Doc

pc = Pinecone(api_key='pcsk_42coaV_3AHp5VkNqafH8yGeWY9AHXCwZij9FwfyPnjFLCrcZs7Z6Y5LErpcPb2vPWvs7R4') #INSERT API KEY
index_name = "smart-scanner-index"

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

    return jsonify({
        "message": "Files uploaded successfully!",
        "files": uploaded_files
    }), 200

@app.route("/process-files", methods=["POST"])
def process_files():
    """Process uploaded files."""

    upload_folder = "uploads"
    global handler
    handler = DocHandler(upload_folder) # handles all the files uploaded
    handler.process_files() # processes them
    return jsonify({"message": "Files processed successfully"}), 200


@app.route("/search", methods=["POST"])
def search():
    data = request.json
    keywords = data.get("keyword", [])

    if not isinstance(keywords, list):
        return jsonify({"error": "No keyword provided"}), 400

    handler.keywords_in_documents(keywords) # processes them

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
                # augmented_prompt = augment_prompt(keyword, f'find 5 synonyms of {keyword}', syn, judge, eng)
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

@app.route("/empty_pinecone", methods=["POST"])
def empty_pinecone():
    try:
        if index_name in pc.list_indexes():
            index = pc.Index(index_name)
            index.delete(filter={})  # Delete everything
        return jsonify({"success": True, "message": "Pinecone index cleared successfully."}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    
@app.route("/fetch_results", methods=["GET"])
def fetch_results():
    try:
        print("these are the keywords per doc: ", handler.get_keywords_per_doc(), type(handler.get_keywords_per_doc()))
        results_df = handler.get_keywords_per_doc()  # This returns a pandas DataFrame
        results = results_df.to_dict(orient="records")
        return jsonify({"results": results}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/fetch_docresults/<filename>", methods=["GET"])
def fetch_doc_results(filename):
    try:
        # Hardcoded results for testing
        print(f"Fetching results for filename: {filename}")  
        results = [
            {
                "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit...",
                "keywords": ["Aluminium", "Gevel"],
                "page": 3,
            },
            {
                "text": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris...",
                "keywords": ["Aluminium"],
                "page": 5,
            },
            {
                "text": "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore...",
                "keywords": ["Gevel"],
                "page": 9,
            },
        ]
        return jsonify({"results": results}), 200
    except Exception as e:
        print(f"Error in /fetch_docresults: {e}")  # Log the error
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.debug = True  # Enable debug mode for development
    app.run()