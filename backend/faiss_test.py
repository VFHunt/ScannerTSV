import numpy as np
import pandas as pd
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
from faiss_index import FaissIndex  # Replace with your FAISS class path
import matplotlib.pyplot as plt
import seaborn as sns
from constants import get_model
from gen_syn import GenModel

gpt = GenModel(model="gpt-4o", role="You are a Dutch judge on the quality of the similarity scores of a given word based on the chunks of a text. Keep your answers under 20 words")

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
queries = [
    "aansprakelijkheid",
    "betalingstermijn",
    "opzegging",
    "herroepingsrecht",
    "diensten",
    "verplichtingen",
    "contractduur",
    "schadevergoeding",
    "overmacht",
    "geheimhouding",
    "toepasselijk recht",
    "beëindiging",
    "geschillen",
    "leveringsvoorwaarden",
    "intellectuele eigendom",
    "facturatie",
    "boetebeding",
    "annulering",
    "garantie",
    "verzekeringen"
]

query_vectors = encoder.encode(queries, convert_to_numpy=True, normalize_embeddings=True)

results = []



for chunk_size in [500]:
    print(f"🔍 Processing chunk size: {chunk_size}")
    chunks = split_into_chunks(text, max_chars=chunk_size)
    embeddings = prepare_embeddings(chunks, encoder)
    index = FaissIndex(embeddings, temperature = 100)
    db = DummyChunkDatabase()
    distances, indices = index.f_search(queries, db)

    answers = []

    for i, query in enumerate(queries):
        scores = distances[i]
        max_sim = float(np.max(scores))
        max_idx = int(np.argmax(scores))
        chunk_idx = indices[i][max_idx]
        top_chunk = chunks[chunk_idx] if chunk_idx != -1 else "[No matching chunk]"

        answer = gpt.generate_answer( "What do you think should be the cosine similarity score given that we retrieve these"
            f"Query: {query}\n"
            f"Top Chunk: {top_chunk}\n"
            f"Max Similarity: {max_sim:.3f}\n"
        )

        answers.append(answer)

        results.append({
            "Chunk Size": chunk_size,
            "Query": query,
            "Min Similarity": round(float(np.min(scores)), 3),
            "Max Similarity": round(max_sim, 3),
            "Avg Similarity": round(float(np.mean(scores)), 3),
            "Top Chunk": top_chunk[:300] + ("..." if len(top_chunk) > 300 else ""),
            "GPT Answer": answer
        })

import pandas as pd

df_results = pd.DataFrame(results)
pd.set_option('display.max_colwidth', None)  # Optional: show full text

# Save table
df_results.to_csv("semantic_similarity_.csv", index=False)


crazy = gpt.generate_answer("I asked you for your answers on the quality of the top chunks retrieved and their cosine similarity, what do you think is the best value to use as a threshold to retrieve the proper chunks, here you get my answers" + str(answers))
print("GPT SAYS:", crazy)

# Convert to DataFrame and display
df = pd.DataFrame(results)
print("\n📊 Similarity Stats Across Chunk Sizes:")
print(df)



# Set up the plot style
sns.set(style="whitegrid")

# Convert 'Chunk Size' to categorical (just in case)
df["Chunk Size"] = df["Chunk Size"].astype(int)

# # Create a separate plot for each query
# for query in df["Query"].unique():
#     sub_df = df[df["Query"] == query]
    
#     plt.figure(figsize=(10, 5))
#     plt.plot(sub_df["Chunk Size"], sub_df["Min Similarity"], marker='o', label="Min Similarity", linestyle='--')
#     plt.plot(sub_df["Chunk Size"], sub_df["Max Similarity"], marker='o', label="Max Similarity", linestyle='-.')
#     plt.plot(sub_df["Chunk Size"], sub_df["Avg Similarity"], marker='o', label="Avg Similarity", linestyle='-')
    
#     plt.title(f"Similarity Scores vs Chunk Size — Query: '{query}'")
#     plt.xlabel("Chunk Size (characters)")
#     plt.ylabel("Similarity Score")
#     plt.ylim(0, 1.05)
#     plt.legend()
#     plt.grid(True)
#     plt.tight_layout()
#     plt.show()
