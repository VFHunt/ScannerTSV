import numpy as np
from faiss_index import FaissIndex
from sentence_transformers import SentenceTransformer
from db import ChunkDatabase

# Initialize the SentenceTransformer model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

db = ChunkDatabase()

# Define chunks of text
chunks = [
    "Artificial intelligence is transforming the world.",
    "Machine learning is a subset of artificial intelligence.",
    "Deep learning uses neural networks to analyze data.",
    "Natural language processing enables machines to understand human language.",
    "Computer vision allows machines to interpret visual data.",
    "Reinforcement learning trains models through rewards and penalties.",
    "Data science combines statistics and computer science to analyze data.",
    "Big data refers to extremely large datasets that require advanced tools to process.",
    "Cloud computing provides scalable resources over the internet.",
    "Cybersecurity protects systems and networks from digital attacks."
]

# Generate random embeddings and IDs
random_embeddings = [(np.random.randint(1000), model.encode(chunk, convert_to_numpy=True)) for chunk in chunks]

# Instantiate FaissIndex with a temperature threshold
temperature_threshold = 1.5
faiss_index = FaissIndex(embeddings=random_embeddings, temperature=temperature_threshold)

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

