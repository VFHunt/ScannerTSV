from backend_filepro import get_model
from vector_db import index
import os
import zipfile
from typing import List, Dict, Any

UPLOAD_FOLDER = "uploads"
ZIP_OUTPUT_FOLDER = "zipped_results/"
_model_instance = None

def search_terms_in_pinecone(terms: List[str]) -> List[Dict[str, Any]]:
    """
    Search for multiple terms using semantic search in Pinecone.
    """

    global _model_instance
    if _model_instance is None:
        _model_instance = get_model()

    all_results = []
    for term in terms:
        # Encode the search term
        search_vector = _model_instance.encode(term).tolist() # tolist Converts the vector from a NumPy array (or tensor) to a Python list Pinecone only accepts lists as input.
        
        # Query Pinecone
        results = index.query(
            vector=search_vector,
            top_k=100,
            include_metadata=True
        )
        
        # Add results with the search term used
        for match in results.matches:
            all_results.append({
                'term': term,
                'score': match.score,
                'text': match.metadata['text'],
                'filename': match.metadata['filename'],
                'page': match.metadata['page']
            })
    
    # Sort all results by score
    all_results.sort(key=lambda x: x['score'], reverse=True)
    print("Search Results:")
    for result in all_results:
        print(f"Term: {result['term']}, Score: {result['score']}, File: {result['filename']}, Page: {result['page']}, Text: {result['text']}")
    return all_results

def create_zip(results: List[Dict[str, Any]]) -> str:
    """Create a ZIP file of the matched files from the uploads folder."""
    os.makedirs(ZIP_OUTPUT_FOLDER, exist_ok=True)  # Ensure the output folder exists
    zip_filename = os.path.join(ZIP_OUTPUT_FOLDER, "search_results.zip")

    try:
        with zipfile.ZipFile(zip_filename, "w") as zipf:
            for result in results:
                # Retrieve the filename from the result metadata
                filename = result['filename']  # Get the filename from metadata
                file_path = os.path.join(UPLOAD_FOLDER, filename)  # Construct the full file path

                # Check if the file exists in uploads folder before adding to the ZIP
                if os.path.exists(file_path):
                    zipf.write(file_path, arcname=filename)  # Add the actual file to the ZIP
                else:
                    print(f"Warning: {file_path} does not exist. Skipping.")

    except Exception as e:
        print(f"Error making zip file: {e}")
        return None

    return zip_filename