import os
from backend_filepro import FileHandler
from pinecone import Pinecone, ServerlessSpec
from io import BytesIO
from search import generate_related_terms

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

keyword = "bouwplaats"
expanded_query_terms = [keyword] + generate_related_terms(keyword)
print("Expanded query terms:", expanded_query_terms)


