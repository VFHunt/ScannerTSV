import matplotlib.pyplot as plt
import numpy as np

from itertools import combinations
from sentence_transformers import SentenceTransformer, util
from tqdm.autonotebook import trange, tqdm


model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

def semantic_similarity(word1, word2):
    emb1 = model.encode(word1)
    emb2 = model.encode(word2)
    return util.cos_sim(emb1, emb2).item()

def calculate_embedding_similarity(keyword: str, answers: list) -> list:
    similarities = [semantic_similarity(keyword, answer) for answer in answers]

    # Calculate min, max, and average similarity
    min_sim = min(similarities)
    max_sim = max(similarities)
    avg_sim = sum(similarities) / len(similarities)

    print(f"Smallest Similarity: {min_sim:.4f}")
    print(f"Largest Similarity: {max_sim:.4f}")
    print(f"Average Similarity: {avg_sim:.4f}")

    return [min_sim, max_sim, avg_sim]

