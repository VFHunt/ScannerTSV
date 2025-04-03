from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
import pickle
from backend_filepro import FileHandler
from werkzeug.utils import secure_filename
from test_search import search_terms_in_pinecone, create_zip
from gen_syn import GenModel, generate_judge_eng, augment_prompt
from syn_database import DataHandler
from vector_db import upload_to_pinecone

app = Flask(__name__)
CORS(app)  # Allows React frontend to talk to Flask backend

logging.basicConfig(level=logging.INFO)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get backend folder path
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")  # Dynamically set uploads path
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure folder exists

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/upload", methods=["POST"])
def upload_file():

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

    handler = FileHandler(files=uploaded_files)  # Instantiate your FileHandler class
    processed_data = handler.process_all_files()  # Assuming process_file handles single file
    # sep into /pinecone
    if processed_data:
        num_vectors = upload_to_pinecone(processed_data)
        print(f"Uploaded {num_vectors} vectors to Pinecone.")
    else:
        return jsonify({"error": "No data to upload to Pinecone"}), 500

    # Save processed data
    with open("processed_data.pkl", "wb") as f:
        pickle.dump(processed_data, f)

    return jsonify({
        "message": "File uploaded and processed successfully!",
        "files": uploaded_files
    }), 200


@app.route("/search", methods=["POST"])
def search():
    data = request.json
    keyword = data.get("keyword", "")

    if not keyword:
        return jsonify({"error": "No keyword provided"}), 400

    # Generate judge and engineer information
    judge, eng = generate_judge_eng(syn_number=2)  # Change the number to the user's preference

    # Initialize the synonym generator and database handler
    syn = GenModel('gpt-4o',
                   "You are a Dutch linguist and construction specialist with expertise in industry terminology. Output only five words separated by commas")
    db_handler = DataHandler(os.path.join(os.getcwd(), "data", "syn_db.json"))
    number = 2  # TODO: Change this number based on user preference

    # Check if the keyword is already saved in the database
    if db_handler.is_saved(keyword):
        synonyms = db_handler.get_synonyms(keyword)
    else:
        augmented_prompt = augment_prompt(keyword, f'find {number} synonyms of {keyword}', syn, judge, eng)
        synonyms = syn.generate_synonyms(augmented_prompt)
        db_handler.add_synonyms(keyword, synonyms)

    synonyms.append(keyword)

    # Send terms to search in Pinecone
    results = search_terms_in_pinecone(synonyms)

    # zip file new function
    zip_file_path = create_zip(results)
    if zip_file_path:
        print(f"ZIP file created successfully: {zip_file_path}")
    else:
        print("Failed to create ZIP file.")

    return jsonify({"message": "Search completed!"})


if __name__ == "__main__":
    app.run()

