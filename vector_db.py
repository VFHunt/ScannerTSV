from atakan import FileHandler
import pinecone
from main import file_handler

pinecone.init(api_key = 'pcsk_42coaV_3AHp5VkNqafH8yGeWY9AHXCwZij9FwfyPnjFLCrcZs7Z6Y5LErpcPb2vPWvs7R4', environment= "us-east1-gcp")
index_name = "smart-scanner-index"
if index_name not in pinecone.list_indexes():
    pinecone.create_index(
        index_name,
        dimension = 384,
    ) # dimensions match embedding size
index = pinecone.Index(index_name)

def upload_embeddings(chunks, embeddings):
    vectors=[]
    for i, emb in enumerate(embeddings):
        vector_id = f"doc_{i}"
        metadata = chunks[i]["metadata"]
        vectors.append((vector_id, emb.tolist(), {"filename": chunks[i]["metadata"].get("filename", "unknown")}))
    index.upsert(vectors)

query_vector = file_handler.embedder.encode("example query")
result = index.query(vector=query_vector, top_k=5, include_metadata=True)
print(result)

