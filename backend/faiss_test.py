import numpy as np
from faiss_index import FaissIndex
from typing import List, Dict
import matplotlib.pyplot as plt
from constants import get_model
from typing import Any
from db import ChunkDatabase

encoder = get_model()
db = ChunkDatabase()

keywords = [
    "artificial intelligence",
    "machine learning",
    "deep learning",
    "natural language processing",
    "computer vision",
    "reinforcement learning",
    "AI ethics",
    "robotics",
    "big data",
    "edge computing"
]

chunks = [
    {"id": "chunk_1", "text": "Artificial intelligence is transforming industries."},
    {"id": "chunk_2", "text": "Machine learning is a subset of AI focused on data-driven predictions."},
    {"id": "chunk_3", "text": "Deep learning uses neural networks to analyze complex patterns."},
    {"id": "chunk_4", "text": "Natural language processing enables machines to understand human language."},
    {"id": "chunk_5", "text": "Computer vision allows machines to interpret visual data."},
    {"id": "chunk_6", "text": "Reinforcement learning trains models through rewards and penalties."},
    {"id": "chunk_7", "text": "AI ethics is a critical area of research to ensure responsible use of technology."},
    {"id": "chunk_8", "text": "Robotics integrates AI to create intelligent machines."},
    {"id": "chunk_9", "text": "Big data analytics is essential for training AI models."},
    {"id": "chunk_10", "text": "Edge computing brings AI capabilities closer to devices."}
]

def l2_normalize(vecs: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    return vecs / norms

def vectorize(text: List[str]) -> np.ndarray:
    return encoder.encode(text, convert_to_numpy=True)

def add_embeddings_to_chunks(chunks: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    texts = [chunk["text"] for chunk in chunks]
    embeddings = vectorize(texts)
    embeddings = l2_normalize(embeddings)  # Normalize here ✅

    for chunk, embedding in zip(chunks, embeddings):
        chunk["embedding"] = embedding
    return chunks

def visualize_distances(distances: np.ndarray, indices: np.ndarray):
    for i, (dist_list, idx_list) in enumerate(zip(distances, indices)):
        # Calculate the average distance for the current query
        avg_distance = np.mean(dist_list)
        print(f"Query {i} - Average Distance: {avg_distance:.4f}")

        # Plot the distances
        plt.figure(figsize=(10, 5))
        plt.bar(range(len(dist_list)), dist_list, tick_label=idx_list)
        plt.title(f"Query {i} - Distances per Index (Avg: {avg_distance:.4f})")
        plt.xlabel("Index")
        plt.ylabel("Distance")
        plt.show()

# Debugging function to print distances and indices
def debug_distances(distances: np.ndarray, indices: np.ndarray):
    for i, (dist_list, idx_list) in enumerate(zip(distances, indices)):
        print(f"Query {i}:")
        for dist, idx in zip(dist_list, idx_list):
            print(f"  Index: {idx}, Distance: {dist:.4f}")

def analyze_similarities(queries, chunk_texts, encoder, top_k=10):
    # Vectorize & normalize all texts
    chunk_embeddings = encoder.encode(chunk_texts, convert_to_numpy=True, normalize_embeddings=True)
    query_embeddings = encoder.encode(queries, convert_to_numpy=True, normalize_embeddings=True)

    # Compute cosine similarities (dot product since all are normalized)
    similarity_matrix = np.dot(query_embeddings, chunk_embeddings.T)

    # Stats and histogram per query
    for i, query in enumerate(queries):
        sims = similarity_matrix[i]
        sorted_sims = np.sort(sims)[::-1]  # descending

        print(f"\n=== Query: '{query}' ===")
        print(f"Top-{top_k} similarities: {sorted_sims[:top_k]}")
        print(f"Mean similarity: {np.mean(sims):.4f}")
        print(f"Median similarity: {np.median(sims):.4f}")
        print(f"Max similarity: {np.max(sims):.4f}")
        print(f"Min similarity: {np.min(sims):.4f}")

        plt.figure(figsize=(8, 4))
        plt.hist(sims, bins=20, color='skyblue', edgecolor='black')
        plt.title(f"Similarity Distribution for Query: '{query}'")
        plt.xlabel("Cosine Similarity")
        plt.ylabel("Frequency")
        plt.grid(True)
        plt.show()

# Main test function
def test_faiss_search():

    # chunks_with_embeddings = add_embeddings_to_chunks(chunks)
    # embeddings = [(chunk["id"], chunk["embedding"]) for chunk in chunks_with_embeddings]

    # print("Sample normalized vector:", chunks_with_embeddings[0]['embedding'][:5])
    # print("L2 norm:", np.linalg.norm(chunks_with_embeddings[0]['embedding']))

    # f = FaissIndex(embeddings, temperature=500)  # Initialize the FAISS index

    # distances, indices = f.f_search(keywords, db)  # Perform the search

    # # visualize_distances(distances, indices)  # Visualize distances
    encoder = get_model()  # SentenceTransformer
    queries = [
        "artificial intelligence",
        "robotics",
        "natural language processing"
    ]
    chunk_texts = [chunk["text"] for chunk in chunks]

    analyze_similarities(queries, chunk_texts, encoder)

    
    

# Run the test
if __name__ == "__main__":
    test_faiss_search()