import matplotlib.pyplot as plt
import numpy as np

from itertools import combinations
from sentence_transformers import SentenceTransformer, util
from tqdm.autonotebook import trange, tqdm



def jacc_sim(answers: list, models: list):
    # Ensure the input is valid
    if len(answers) != len(models):
        print("Error: The number of models and answers must be the same.")
        return

    # Calculate Jaccard Similarity for all model pairs
    for (i, j) in combinations(range(len(models)), 2):
        set1 = set(answers[i])
        set2 = set(answers[j])
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        similarity = intersection / union if union != 0 else 0
        print(f"Jaccard Similarity between {models[i]} and {models[j]}: {similarity:.2f}")


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

