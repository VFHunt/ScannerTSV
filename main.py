import logging
import os
import pickle
from backend_filepro import FileHandler
from Test.test_search import search_terms_in_pinecone

# Configure logging
logging.basicConfig(level=logging.INFO)

def process_files():
    """Process all files and save the results."""
    handler = FileHandler()
    processed_data = handler.process_all_files()
    
    # Save processed data
    with open("processed_data.pkl", "wb") as f:
        pickle.dump(processed_data, f)
    print("Files processed and data saved successfully!")

def main():
    """Main function to handle user interaction and file processing."""
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

    # Main search loop
    while True:
        # Ask for keyword
        keyword = input("\nEnter a Dutch keyword to search (or 'quit' to exit): ").strip()
        # send keyword to gen sym
        # retreive terms list from

        # Send terms to search in pinecone
        search_terms_in_pinecone(terms)

        if keyword.lower() == 'quit':
            print("Goodbye!")
            break
            
        if not keyword:
            print("Please enter a valid keyword.")
            continue
            


if __name__ == "__main__":
    main()
