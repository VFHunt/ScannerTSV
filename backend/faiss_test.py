import numpy as np
import pandas as pd
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
from faiss_index import FaissIndex  # Replace with your FAISS class path
import matplotlib.pyplot as plt
import seaborn as sns
from constants import get_model

# === Load model ===
encoder = get_model()

# === Extract text from PDF ===
def extract_text_from_pdf(path):
    reader = PdfReader(path)
    return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())

# === Split text into chunks by character length ===
def split_into_chunks(text, max_chars=200):
    words = text.split()
    chunks = []
    current = ""

    for word in words:
        if len(current) + len(word) + 1 <= max_chars:
            current += word + " "
        else:
            chunks.append(current.strip())
            current = word + " "
    if current:
        chunks.append(current.strip())
    return chunks

# === Prepare embeddings for FAISS ===
def prepare_embeddings(chunks, encoder):
    vectors = encoder.encode(chunks, convert_to_numpy=True, normalize_embeddings=True)
    return [(str(i), vec) for i, vec in enumerate(vectors)]

# === Summarize similarities ===
def summarize_similarities(queries, query_vectors, index):
    summary = []
    for i, query_vec in enumerate(query_vectors):
        sims, _ = index.index.search(query_vec.reshape(1, -1), len(index.ids))
        scores = sims[0]
        summary.append(scores.min(), scores.max(), scores.mean())
    return summary

# === Dummy DB ===
class DummyChunkDatabase:
    def add_keyword_and_distance(self, chunk_id, queries, distances):
        pass  # Optional logging

# === Main Analysis ===
pdf_path = "files/test.pdf"
text = extract_text_from_pdf(pdf_path)
queries = ["aansprakelijkheid", "betalingstermijn", "opzegging", "herroepingsrecht", "diensten"]
query_vectors = encoder.encode(queries, convert_to_numpy=True, normalize_embeddings=True)

results = []

for chunk_size in [50, 100, 200, 300, 400]:
    print(f"🔍 Processing chunk size: {chunk_size}")
    chunks = split_into_chunks(text, max_chars=chunk_size)
    embeddings = prepare_embeddings(chunks, encoder)
    index = FaissIndex(embeddings, temperature = 100)
    db = DummyChunkDatabase()
    distances, _ = index.f_search(queries, db)

    for i, query in enumerate(queries):
        scores = distances[i]
        results.append({
            "Chunk Size": chunk_size,
            "Query": query,
            "Min Similarity": round(float(np.min(scores)), 3),
            "Max Similarity": round(float(np.max(scores)), 3),
            "Avg Similarity": round(float(np.mean(scores)), 3)
        })

# Convert to DataFrame and display
df = pd.DataFrame(results)
print("\n📊 Similarity Stats Across Chunk Sizes:")
print(df)



# Set up the plot style
sns.set(style="whitegrid")

# Convert 'Chunk Size' to categorical (just in case)
df["Chunk Size"] = df["Chunk Size"].astype(int)

# Create a separate plot for each query
for query in df["Query"].unique():
    sub_df = df[df["Query"] == query]
    
    plt.figure(figsize=(10, 5))
    plt.plot(sub_df["Chunk Size"], sub_df["Min Similarity"], marker='o', label="Min Similarity", linestyle='--')
    plt.plot(sub_df["Chunk Size"], sub_df["Max Similarity"], marker='o', label="Max Similarity", linestyle='-.')
    plt.plot(sub_df["Chunk Size"], sub_df["Avg Similarity"], marker='o', label="Avg Similarity", linestyle='-')
    
    plt.title(f"Similarity Scores vs Chunk Size — Query: '{query}'")
    plt.xlabel("Chunk Size (characters)")
    plt.ylabel("Similarity Score")
    plt.ylim(0, 1.05)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
