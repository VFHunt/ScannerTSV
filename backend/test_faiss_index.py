import numpy as np
from faiss_index import FaissIndex
from db import ChunkDatabase
from constants import get_model

# Initialize the SentenceTransformer model
model = get_model()

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

