import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List

global encoder
encoder = model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def adapt_numpy_array(arr: np.ndarray) -> bytes:
    """
    Serialize numpy array to bytes to store in SQLite BLOB.
    """
    return arr.tobytes()

def convert_blob_to_numpy(blob: bytes, dtype=np.float32, shape=(384,)) -> np.ndarray:
    """
    Convert bytes back to numpy array.
    You must know dtype and shape of the original array.
    """
    return np.frombuffer(blob, dtype=dtype).reshape(shape)

class FaissIndex:
    def __init__(self, blobs: List[bytes], temperature: float):
        """Initialize the FaissIndex with blobs from an SQL column.

        Args:
            blobs: A list of serialized numpy arrays (blobs) retrieved from an SQL column.
            temperature: A threshold for filtering results based on distance.
        """
        self.chunks = [convert_blob_to_numpy(blob).tolist() for blob in blobs]
        self.temperature = temperature
        self.vectors = np.array(self.chunks)
        self.dimension = self.vectors.shape[1]
        self.index = faiss.IndexFlatL2(self.dimension)  # Using L2 distance for simplicity

    def _add(self):
        """Add vectors to the index."""
        self.index.add(self.vectors)


    def _vectorize_queries(self, queries: List[str]):
        """Vectorize a list of query strings (keywords).

        Args:
            queries: A list of query strings to vectorize.

        Returns:
            numpy.ndarray: A 2D array of vectorized queries.
        """
        return encoder.encode(queries, convert_to_numpy=True)

    def f_search(self, query: List[str], k: int):
        """Search for the k nearest neighbors of a query vector.

        Args:
            query: A list of query strings (keywords).
            k: The number of nearest neighbors to return.

        Returns:
            tuple: Distances and indices of the nearest neighbors.
        """
        self._add()
        query_vector = self._vectorize_queries(query)
        distances, indices = self.index.search(query_vector, k)
        print(f"Distances: {distances}")
        print(f"Indices: {indices}")
        
        results = []
        for query_idx, query_indices in enumerate(indices):
            print(f"Query {query[query_idx]}: {query_indices}")
            query_results = [self.chunks[i] for i in query_indices if distances[query_idx][i] < self.temperature]
            results.append(query_results)
        return results

if __name__ == "__main__":
    """Test the FaissIndex class with sample data."""
    chunks = [
        "The Eiffel Tower is located in Paris.",
        "Python is a popular programming language.",
        "FAISS is a library for efficient similarity search.",
        "FastAPI is a modern web framework for Python.",
        "The capital of Japan is Tokyo.",
        "Cats are known for their agility.",
        "The mitochondrion is the powerhouse of the cell.",
        "Blockchain enables decentralized applications.",
        "Mount Everest is the highest mountain on Earth.",
        "The Great Wall of China is visible from space."
    ]

    queries = ["Tokyo"]

    searcher = FaissIndex(chunks, temperature=1.0)
    results = searcher.f_search(queries, k=5)

    print("Results:", results)
