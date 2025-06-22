import faiss
import numpy as np
from typing import List, Tuple, Dict, Any
from db import ChunkDatabase
from constants import get_model


class FaissIndex:
    def __init__(self, embeddings: List[Tuple[str, np.ndarray]], temperature: float):
        """Initialize the FaissIndex with embeddings mapped to integers.

        Args:
            embeddings: A list of tuples where each tuple contains an integer and a numpy array (embedding).
            temperature: A threshold for filtering results based on distance.

        """
        if not embeddings:
            raise ValueError("Embeddings list is empty. Cannot build FAISS index.")

        self.temperature = temperature
        self.embeddings = embeddings
        self.encoder = get_model()  # Initialize the encoder model

        self.vectors = np.array([embedding for _, embedding in embeddings])
        self.vectors = self._normalize(self.vectors)

        self.ids = [id_ for id_, _ in embeddings]  # Extract IDs from the embeddings
        self.dimension = self.vectors.shape[1]
        self.index = faiss.IndexFlatIP(self.dimension)  # Using L2 distance for simplicity
        self._add()

    def _normalize(self, vectors: np.ndarray) -> np.ndarray:
        """
        Normalize the vectors to have unit length.
        """
        # Ensure vectors are 2D
        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)  # Reshape to (1, n_features)
        return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)

    def _add(self):
        """Add vectors to the index."""
        self.index.add(self.vectors)
        assert self.index.ntotal == len(self.ids), f"Index size mismatch: {self.index.ntotal} vs {len(self.ids)}"

    def _vectorize_queries(self, queries: List[str]) -> np.ndarray:
        vecs = self.encoder.encode(queries, convert_to_numpy=True)
        return self._normalize(vecs)
        
    def _index_to_ids(self, indices):
        """Convert FAISS indices to actual IDs.

        Args:
            indices: A list of indices from the FAISS index.

        Returns:
            list: A list of corresponding IDs.
        """
        return [self.ids[i] for i in indices]
         

    def f_search(self, queries: List[str], db: ChunkDatabase) -> List[Dict[str, Any]]:
        """Search for the k nearest neighbors of a query vector.

        Args:
            query: A list of query strings (keywords).

        Returns:
            tuple: Distances and indices of the nearest neighbors.
        """

        if not queries:
             raise ValueError("Queries must be a non-empty list of strings.")

        k = len(self.vectors)  # Number of vectors in the index
        query_vector = self._vectorize_queries(queries)

        # print("[DEBUG] Norms of query vectors:", np.linalg.norm(query_vector, axis=1))
        # print("[DEBUG] Norms of indexed vectors:", np.linalg.norm(self.vectors, axis=1)[:5])  # Show first 5


        # Validate dimensionality
        if query_vector.shape[1] != self.dimension:
            raise ValueError(f"Query vector dimensionality ({query_vector.shape[1]}) does not match FAISS index dimensionality ({self.dimension}).")

        distances, indices = self.index.search(query_vector, k)

        # Dictionary to store chunk IDs and their corresponding queries
        chunk_query_dict = {}

        # Iterate over each query and its corresponding distances and indices
        for query_str, dist_list, idx_list in zip(queries, distances, indices):
            for dist, idx in zip(dist_list, idx_list):
                # print(f"[DEBUG] raw dist = {dist}, idx = {idx}, threshold = {self.temperature}, total_ids = {len(self.ids)}")
                if dist >= self.temperature and idx != -1 and idx < len(self.ids):
                    # Ensure that self._index_to_ids([idx]) returns an iterable
                    chunk_id_result = self._index_to_ids([idx])
                    #print(f"[DEBUG] FAISS index {idx} → chunk_id {chunk_id_result[0]}, distance = {dist}")

                    if chunk_id_result is None:
                        continue  # Skip this iteration if chunk_id_result is None
                    #print(f"[DEBUG] chunk_id_result = {chunk_id_result}")

                    chunk_id = chunk_id_result[0]  # Assuming this maps an index to an ID

                    # If the chunk_id is not in the dictionary, add it with empty lists for queries and distances
                    if chunk_id not in chunk_query_dict:
                        chunk_query_dict[chunk_id] = {"queries": [], "distances": []}

                    # Append the query and distance to the lists for this chunk_id
                    chunk_query_dict[chunk_id]["queries"].append(query_str)
                    chunk_query_dict[chunk_id]["distances"].append(float(round(dist, 2)))

        # Print the resulting dictionary
        for chunk_id, data in chunk_query_dict.items():
            # print(f"Chunk ID: {chunk_id}")
            # print("Queries:", data["queries"])
            # print("Distances:", data["distances"])
            # print(f"[DEBUG] About to call add_keyword_and_distance for chunk {chunk_id}")
            db.add_keyword_and_distance(str(chunk_id), str(data["queries"]), str(data["distances"]))

        return distances, indices