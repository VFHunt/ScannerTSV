import numpy as np
from faiss_index import FaissIndex
from sentence_transformers import SentenceTransformer
from db import ChunkDatabase

# Initialize the SentenceTransformer model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

db = ChunkDatabase()

emb = db.get_embeddings_by_project("cecilia")  # Get chunks from the database


# Instantiate FaissIndex with a temperature threshold
temperature_threshold = 1.5
faiss_index = FaissIndex(embeddings=emb, temperature=temperature_threshold)

# Define proper test queries
test_queries = [
    "What is artificial intelligence?",
    "Explain machine learning.",
    "How does deep learning work?",
    "What is natural language processing?",
    "What is computer vision?"
]

# Perform search and print results
results = faiss_index.f_search(test_queries, db)

