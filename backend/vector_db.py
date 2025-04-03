from backend_filepro import FileHandler, _model_instance
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Pinecone
pc = Pinecone(api_key='') #INSERT API KEY
index_name = "smart-scanner-index"

# Create index if it doesn't exist
if index_name not in [i["name"] for i in pc.list_indexes()]:
    pc.create_index(
        index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

index = pc.Index(index_name)

# Initialize FileHandler with the folder path
scanner = FileHandler()
processed_data = scanner.process_all_files()

def upload_to_pinecone(processed_data):
    """Upload processed data to Pinecone."""
    vectors = []
    for filename, data in processed_data.items():
        for i, entry in enumerate(data):
            vector_id = f"{filename}_{i}"
            embedding = entry["embedding"].tolist()
            metadata = {
                "filename": filename,
                "text": entry["content"],
                "page": entry["metadata"]["page"]
            }
            vectors.append((vector_id, embedding, metadata))
    print(f"Uploading {len(vectors)} vectors to Pinecone...")
    print("Sample vector:", vectors[:2])
    
    # Upload to Pinecone
    index.upsert(vectors)
    return len(vectors)

def search_pinecone(search_term):
    """Search for a term in Pinecone."""
    search_vector = _model_instance.encode(search_term).tolist()
    results = index.query(
        vector=search_vector,
        top_k=100,
        include_metadata=True
    )
    
    return [
        {
            'score': match.score,
            'text': match.metadata['text'],
            'filename': match.metadata['filename'],
            'page': match.metadata['page']
        }
        for match in results.matches
    ]



