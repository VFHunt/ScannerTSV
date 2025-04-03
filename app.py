from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
import pickle
from backend.backend_filepro import FileHandler
from backend.Test.test_search import search_terms_in_pinecone
from backend.gen_syn import GenModel, generate_judge_eng, augment_prompt
from backend.syn_database import DataHandler

app = Flask(__name__)
CORS(app)  # Allows React frontend to talk to Flask backend

logging.basicConfig(level=logging.INFO)

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    file_path = os.path.join("uploads", file.filename)
    
    # Save file locally before processing
    file.save(file_path)
    
    # Process the file using your existing method
    handler = FileHandler()  # Instantiate your FileHandler class
    processed_data = handler.process_all_files()  # Assuming process_file handles single file
    
    # Save processed data
    with open("processed_data.pkl", "wb") as f:
        pickle.dump(processed_data, f)
    
    return jsonify({"message": "File uploaded and processed successfully!"})

@app.route("/search", methods=["POST"])
def search():
    data = request.json
    keyword = data.get("keyword", "")

    if not keyword:
        return jsonify({"error": "No keyword provided"}), 400

    # Generate judge and engineer information
    judge, eng = generate_judge_eng(syn_number=2)  # Change the number to the user's preference
    
    # Initialize the synonym generator and database handler
    syn = GenModel('gpt-4o', "You are a Dutch linguist and construction specialist with expertise in industry terminology. Output only five words separated by commas")
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
    search_terms_in_pinecone(synonyms)

    return jsonify({"message": "Search completed!"})
    

if __name__ == "__main__":
    app.run()

