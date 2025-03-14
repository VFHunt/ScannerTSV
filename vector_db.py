from atakan import FileHandler
from pinecone import Pinecone, ServerlessSpec
from main import file_handler
import numpy as np

pc = Pinecone(api_key = 'pcsk_42coaV_3AHp5VkNqafH8yGeWY9AHXCwZij9FwfyPnjFLCrcZs7Z6Y5LErpcPb2vPWvs7R4')

print("Available indexes:" , pc.list_indexes())

index_name = "smart-scanner-index"
if index_name not in [i["name"] for i in pc.list_indexes()]:
    pc.create_index(
        index_name,
        dimension = 384,
        metric= "cosine",
        spec = ServerlessSpec(
            cloud = "aws",
            region="us-east-1"
        )
    )
else:
    print(f"Index {index_name} already exists")
index = pc.Index(index_name)


def upload_embeddings(chunks, embeddings):
    vectors=[]
    for i, emb in enumerate(embeddings):
        vector_id = f"doc_{i}"
        metadata = chunks[i]["metadata"]
        vectors.append({
            "id": vector_id,
            "values": emb.tolist(),
            "metadata": {"filename": chunks[i]["metadata"].get("filename", "unknown")}
        })
    index.upsert(vectors)
    print(f"Uploaded {len(vectors)} embeddings to Pinecone")

query_vector = file_handler.embedder.encode("foundation")
query_vector = query_vector.tolist()
result = index.query(vector=query_vector, top_k=5, include_metadata=True)
print(result)

