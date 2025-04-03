from backend_filepro import FileHandler
from pinecone import Pinecone, ServerlessSpec

# Initialize Pinecone
pc = Pinecone(api_key='pcsk_42coaV_3AHp5VkNqafH8yGeWY9AHXCwZij9FwfyPnjFLCrcZs7Z6Y5LErpcPb2vPWvs7R4') #INSERT API KEY
index_name = "smart-scanner-index"

folder_path = r"C:\Users\Blanca San Millan\PycharmProjects\ScannerTSV\files"

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

# Convert to Pinecone format
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

# Upload to Pinecone
index.upsert(vectors)



