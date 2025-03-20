import os
from backend_filepro import FileHandler, translate
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

for filename, chunks in processed_data.items():
    for chunk in chunks:
        translated_text=translate(chunk["content"])
        chunk["translated_content"] = translated_text


# Convert to Pinecone format
vectors = []
for filename, data in processed_data.items():
    for i, entry in enumerate(data):
        vector_id = f"{filename}_{i}"
        embedding = entry["embedding"].tolist()
        metadata = {
            "filename": filename,
            "original_text": entry["content"],
            "translated_text": entry["translated_content"],
            "page": entry["metadata"]["page"]
        }

        vectors.append((vector_id, embedding, metadata))

# Upload to Pinecone
index.upsert(vectors)

"""
keyword = "bouwplaats"
# Translate keyword before expanding
translated_keyword = translator(keyword, max_length=512)[0]["translation_text"]
expanded_query_terms = [translated_keyword] + generate_related_terms(translated_keyword)
print(f"Expanded query terms: {expanded_query_terms} (Translated from '{keyword}')")
"""


