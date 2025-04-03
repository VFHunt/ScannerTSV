from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
import pickle
from backend_filepro import FileHandler
from Test.test_search import search_terms_in_pinecone
from gen_syn import GenModel, generate_judge_eng, augment_prompt
from syn_database import DataHandler

app = Flask(__name__)
CORS(app)  # Allows React frontend to talk to Flask backend

logging.basicConfig(level=logging.INFO)

# Generate judge and engineer information
judge, eng = generate_judge_eng(syn_number=5)  # Change the number to the user's preference
    
# Initialize the synonym generator 
syn = GenModel('gpt-4o', "You are a Dutch linguist and construction specialist with expertise in industry terminology. Output only five words separated by commas")
db_handler = DataHandler(os.path.join(os.getcwd(), "data", "syn_db.json"))


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

    # Send terms to search in Pinecone
    search_terms_in_pinecone(keyword)

    return jsonify({"message": "Search completed!"})
    
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
                augmented_prompt = augment_prompt(keyword, f'find 5 synonyms of {keyword}', syn, judge, eng)
                synonyms = syn.generate_synonyms(augmented_prompt)
                db_handler.add_synonyms(keyword, synonyms)

            all_words.extend(synonyms)
            print(f'MAIN;"{keyword}" synonyms: {synonyms}')

        all_words = list(set(word.lower() for word in all_words))
        
        return jsonify({"synonyms": all_words}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()

