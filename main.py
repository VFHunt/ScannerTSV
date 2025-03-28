import logging
import os
import pickle
from backend_filepro import FileHandler
from Test.test_search import search_terms_in_pinecone
from gen_syn import GenModel, generate_judge_eng, augment_prompt
from syn_database import DataHandler

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

    # Creating all the llms we need
    judge, eng = generate_judge_eng(syn_number=2) # change the number to the user's preference
    syn = GenModel('gpt-4o',
                   "You are a Dutch linguist and construction specialist with expertise in industry terminology. Output only five words separated by commas")
    db_handler = DataHandler(os.path.join(os.getcwd(), "data", "syn_db.json"))
    number = 2 # todo: change this 
    # Main search loop
    while True:
        # Ask for keyword
        keyword = input("\nEnter a Dutch keyword to search (or 'quit' to exit): ").strip()

        if db_handler.is_saved(keyword):
            synonyms = db_handler.get_synonyms(keyword)
        else: 
            augmented_prompt = augment_prompt(keyword, f'find {number} synonyms of {keyword}', syn, judge, eng)
            synonyms = syn.generate_synonyms(augmented_prompt)
            db_handler.add_synonyms(keyword, synonyms)

        synonyms.append(keyword)
        # Send terms to search in pinecone
        search_terms_in_pinecone(synonyms)

        if keyword.lower() == 'quit':
            print("Goodbye!")
            break
            
        if not keyword:
            print("Please enter a valid keyword.")
            continue
            


if __name__ == "__main__":
    main()
