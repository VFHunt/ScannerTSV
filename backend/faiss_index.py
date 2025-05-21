import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Tuple, Dict, Any

global encoder
encoder = model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')


class FaissIndex:
    def __init__(self, embeddings: List[Tuple[int, np.ndarray]], temperature: float):
        """Initialize the FaissIndex with embeddings mapped to integers.

        Args:
            embeddings: A list of tuples where each tuple contains an integer and a numpy array (embedding).
            temperature: A threshold for filtering results based on distance.
        """
        self.temperature = temperature
        self.embeddings = embeddings

        self.vectors = np.array([embedding for _, embedding in embeddings])
        self.ids = [id_ for id_, _ in embeddings]  # Extract IDs from the embeddings
        self.dimension = self.vectors.shape[1]
        self.index = faiss.IndexFlatL2(self.dimension)  # Using L2 distance for simplicity
        self._add()

    def _add(self):
        """Add vectors to the index."""
        self.index.add(self.vectors)
        assert self.index.ntotal == len(self.ids), f"Index size mismatch: {self.index.ntotal} vs {len(self.ids)}"


    def _vectorize_queries(self, queries: List[str]):
        """Vectorize a list of query strings (keywords).

        Args:
            queries: A list of query strings to vectorize.

        Returns:
            numpy.ndarray: A 2D array of vectorized queries.
        """
        return encoder.encode(queries, convert_to_numpy=True)
    
    def _index_to_ids(self, indices):
        """Convert FAISS indices to actual IDs.

        Args:
            indices: A list of indices from the FAISS index.

        Returns:
            list: A list of corresponding IDs.
        """
        return [self.ids[i] for i in indices]
         

    def f_search(self, queries: List[str]) -> List[Dict[str, Any]]:
        """Search for the k nearest neighbors of a query vector.

        Args:
            query: A list of query strings (keywords).

        Returns:
            tuple: Distances and indices of the nearest neighbors.
        """

        if not queries:
                raise ValueError("Queries must be a non-empty list of strings.")

        results = []

        k = len(self.vectors)  # Number of vectors in the index
        print("k is: ", k)
        query_vector = self._vectorize_queries(queries)

        # Validate dimensionality
        if query_vector.shape[1] != self.dimension:
            raise ValueError(f"Query vector dimensionality ({query_vector.shape[1]}) does not match FAISS index dimensionality ({self.dimension}).")

        distances, indices = self.index.search(query_vector, k)
        print(f"Distances: {distances}")
        print(f"Indices: {indices}")

        results = []
        # Iterate over each query and its corresponding distances and indices
        for query_str, dist_list, idx_list in zip(queries, distances, indices):
            print(f"Query: {query_str}")
            query_results = []
            
            for dist, idx in zip(dist_list, idx_list):
                if dist < self.temperature and idx != -1 and idx < len(self.ids):
                    query_results.append({
                        "query": query_str,
                        "distance": round(dist, 2),  # Assuming this maps an index to an ID
                        "id": self._index_to_ids([idx])[0]
                    })
            
            results.append(query_results)
        return results # 
    

#  for query in queries:
#             if not isinstance(query, str):
#                 raise ValueError("Query must be a string.")

#             query_vector = self._vectorize_queries(query)

#             # Ensure query_vector is 2D
#             if query_vector.ndim == 1:
#                 query_vector = query_vector.reshape(1, -1)

#             distances, indices = self.index.search(query_vector, len(self.vectors))  # Search for all vectors

#             # Separate filtered distances and indices
#             filtered_distances = [distances[0][i] for i in range(len(distances[0])) if distances[0][i] < self.temperature]
#             filtered_indices = [self.ids[indices[0][i]] for i in range(len(indices[0])) if distances[0][i] < self.temperature]

#             # Save filtered results for the query
#             query_result = {
#                 "query": query,
#                 "distances": filtered_distances,
#                 "ids": self.index_to_ids(filtered_indices)
#             }
#             results.append(query_result)