import logging
import os
import pickle
from search import generate_related_terms
from vector_db import index
from backend_filepro import FileHandler

# Configure logging
logging.basicConfig(level=logging.INFO)

def search_keyword(keyword):
    """
    Searches for a keyword and its related terms in the vector database.
    """
    logging.info(f"Searching for related terms of '{keyword}'...")

    # Generate expanded search terms
    related_terms = generate_related_terms(keyword)
    logging.info(f"Related terms: {related_terms}")

    # Perform search in Pinecone
    query_results = []
    for term in [keyword] + related_terms:
        result = index.query(vector=[0]*384, top_k=5, include_metadata=True)  # Dummy vector (replace with actual embedding)
        query_results.append((term, result))

    # Display results
    for term, result in query_results:
        print(f"Results for '{term}': {result}")

def process_files():
    """
    Processes files and saves them if not already processed.
    """
    FILES_DIRECTORY = "files/"
    file_handler = FileHandler([os.path.join(FILES_DIRECTORY, f) for f in os.listdir(FILES_DIRECTORY)])
    processed_data = file_handler.process_all_files()

    # Save processed data
    with open("processed_data.pkl", "wb") as f:
        pickle.dump(processed_data, f)

    print("Files processed and data saved!")

if __name__ == "__main__":
    # Check if previous data exists
    if not os.path.exists("processed_data.pkl"):
        print("No processed data found. Automatically processing files...")
        process_files()
    else:
        reprocess = input("Do you want to reprocess all files? (yes/no): ").strip().lower()
        if reprocess == "yes":
            print("Reprocessing all files... This may take a while.")
            process_files()

        else:
            print("Loading existing processed data...")
            with open("processed_data.pkl", "rb") as f:
                processed_data = pickle.load(f)
            print("Loaded saved processed data.")

    # Ask for keyword after processing
    keyword = input("Enter a Dutch keyword to search: ").strip()
    search_keyword(keyword)
