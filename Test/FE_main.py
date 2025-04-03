import logging
import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.backend_filepro import FileHandler
from backend.test_search import search_terms_in_pinecone
from backend.gen_syn import GenModel, generate_judge_eng, augment_prompt
from backend.syn_database import DataHandler
from typing import List
from pathlib import Path
from backend.vector_db import upload_to_pinecone

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="SmartScanner API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize necessary objects
judge, eng = generate_judge_eng(syn_number=2)
syn = GenModel('gpt-4o',
               "You are a Dutch linguist and construction specialist with expertise in industry terminology. Output only five words separated by commas")
db_handler = DataHandler(os.path.join(os.getcwd(), "data", "syn_db.json"))

# Model for search request
class SearchRequest(BaseModel):
    search_term: str

@app.get("/health")
async def health_check():
    """Health check endpoint to verify the backend is running."""
    return {"status": "healthy"}


@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """Uploads and processes PDF files."""
    try:
        # Create uploads directory if it doesn't exist
        upload_dir = Path("backend/files")
        upload_dir.mkdir(exist_ok=True)

        # Save uploaded files and process them directly
        saved_files = []
        for file in files:
            file_path = upload_dir / file.filename
            with open(file_path, "wb") as buffer:
                content = await file.read()  # Read the file content
                buffer.write(content)  # Save the uploaded file
            saved_files.append(str(file_path))  # Append file path for processing

        # Initialize FileHandler without passing saved files
        handler = FileHandler()  # Initialize FileHandler
        processed_data = {}

        # Process each uploaded file
        for saved_file in saved_files:
            processed_data[saved_file] = handler.process_all_files(saved_files)

        # Upload to Pinecone (ensure this matches your requirements)
        num_vectors = upload_to_pinecone(processed_data)

        return {
            "message": f"Successfully processed {len(files)} files",
            "vectors_uploaded": num_vectors
        }
    except Exception as e:
        logger.error(f"Error processing files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
async def search_documents(request: SearchRequest):
    """Search for a keyword and its synonyms in uploaded documents."""
    try:
        keyword = request.search_term.strip()
        if not keyword:
            raise HTTPException(status_code=400, detail="Search term cannot be empty")

        # Get synonyms using existing logic
        if db_handler.is_saved(keyword):
            synonyms = db_handler.get_synonyms(keyword)
        else:
            augmented_prompt = augment_prompt(keyword, f'find 2 synonyms of {keyword}', syn, judge, eng)
            synonyms = syn.generate_synonyms(augmented_prompt)
            db_handler.add_synonyms(keyword, synonyms)

        synonyms.append(keyword)
        
        # Search using existing function
        results = search_terms_in_pinecone(synonyms)
        return results
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


