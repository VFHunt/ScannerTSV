import os
from backend_filepro import FileHandler
from pinecone import Pinecone, ServerlessSpec
from io import BytesIO

# Initialize Pinecone
pc = Pinecone(api_key='pcsk_42coaV_3AHp5VkNqafH8yGeWY9AHXCwZij9FwfyPnjFLCrcZs7Z6Y5LErpcPb2vPWvs7R4')
index_name = "smart-scanner-index"

folder_path = r"C:\Users\Virginia\PycharmProjects\ScannerTSV\files"


# Create index if it doesn't exist
if index_name not in [i["name"] for i in pc.list_indexes()]:
    pc.create_index(
        index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

index = pc.Index(index_name)

files = []
for filename in os.listdir(folder_path):
    if filename.endswith(('.pdf', '.txt', '.docx')):
        with open(os.path.join(folder_path, filename), "rb") as f:
            file_obj = BytesIO(f.read())
            file_obj.name = filename
            files.append(file_obj)
scanner = FileHandler(files)
processed_data = scanner.process_all_files()

# Convert to Pinecone format
vectors = []
for filename, data in processed_data.items():
    for i, entry in enumerate(data):
        vector_id = f"{filename}_{i}"
        embedding = entry["embedding"].tolist()
        metadata = entry["metadata"]

        vectors.append((vector_id, embedding, metadata))

# Upload to Pinecone
index.upsert(vectors)
print("whole code is run")


"""
def upload_embeddings(chunks, embeddings):
    vectors=[]
    for i, emb in enumerate(embeddings):
        vector_id = f"doc_{i}"
        metadata = chunks[i]["metadata"]
        vectors.append((vector_id, emb.tolist, {"filename": metadata.get("filename", "unknown")}))
    print(f"uploading {len(vectors)} embeddings...")
    for v in vectors[:3]:
        print(f"Vectors ID: {c[0]}, Metadata: {v[2]}")
    print("pinecone status before upsert", index.describe_index_stats())
    index.upsert(vectors)
    print(f"pinecone stats after upsert", index.describe_index_stats())

upload_embeddings(atakan.chunks, embeddings)
query_vector = file_handler.embedder.encode("foundation")
query_vector = query_vector.tolist()
result = index.query(vector=query_vector, top_k=5, include_metadata=True)
print(result)
"""
