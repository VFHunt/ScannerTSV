import logging
import os
import pickle
from search import generate_related_terms
from vector_db import index
from backend_filepro import FileHandler, EMBEDDING_MODEL

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
        term_vector = EMBEDDING_MODEL.encode(term).tolist()
        result = index.query(vector=term_vector, top_k=5, include_metadata=True)
        query_results.append((term, result))

    # Display results
    for term, result in query_results:
        print(f"Results for '{term}': {result}")

def process_files():
    """Process all files and save the results."""
    handler = FileHandler([])  # Empty list as files are loaded from directory
    processed_data = handler.process_all_files()
    
    # Save processed data
    with open("processed_data.pkl", "wb") as f:
        pickle.dump(processed_data, f)
    print("Files processed and data saved successfully!")

if __name__ == "__main__":
    # Check if processed data exists and has content
    if os.path.exists("processed_data.pkl"):
        try:
            with open("processed_data.pkl", "rb") as f:
                processed_data = pickle.load(f)
                if processed_data:  # Check if data is not empty
                    print("Found existing processed data.")
                    reprocess = input("Do you want to reprocess all files? (yes/no): ").strip().lower()
                    if reprocess == "yes":
                        print("Reprocessing all files... This may take a while.")
                        process_files()
                    else:
                        print("Using existing processed data.")
                else:
                    print("Found empty processed data file. Processing files...")
                    process_files()
        except (pickle.UnpicklingError, EOFError):
            print("Error reading processed data file. Processing files...")
            process_files()
    else:
        print("No processed data found. Processing files...")
        process_files()

    # Ask for keyword after processing
    keyword = input("Enter a Dutch keyword to search: ").strip()
    search_keyword(keyword)
