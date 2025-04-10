from backend_filepro import FileHandler, _model_instance
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Pinecone
pc = Pinecone(api_key='pcsk_42coaV_3AHp5VkNqafH8yGeWY9AHXCwZij9FwfyPnjFLCrcZs7Z6Y5LErpcPb2vPWvs7R4') #INSERT API KEY
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

def upload_to_pinecone(processed_data, batch_size=100):
    """Upload processed data to Pinecone in smaller batches."""
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

    print(f"Uploading {len(vectors)} vectors to Pinecone in batches of {batch_size}...")

    # Batch upsert to avoid payload size limit
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        try:
            index.upsert(batch)
            print(f"Batch {i // batch_size + 1}: Uploaded {len(batch)} vectors.")
        except Exception as e:
            logger.error(f"Error uploading batch {i // batch_size + 1}: {e}")

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



