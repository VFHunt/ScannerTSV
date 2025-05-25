import os
import time
import numpy as np
import pandas as pd
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
from faiss_index import FaissIndex
from constants import get_model
from gen_syn import GenModel

def main():
    # === GPT Judge ===
    gpt = GenModel(model="gpt-4o", role="You are a Dutch judge evaluating how good the retrieved text chunk is for the given query.")

    # === Config ===
    pdf_files = [
        "files/test.pdf",
        "files/test2.pdf",
        "files/test3.pdf"
    ]

    models_to_test = [
        "distiluse-base-multilingual-cased-v1",
        "NetherlandsForensicInstitute/robbert-2022-dutch-sentence-transformers",
        "paraphrase-multilingual-MiniLM-L12-v2"
    ]

    queries = [
        "aansprakelijkheid", "betalingstermijn", "opzegging", "herroepingsrecht", "diensten",
        "verplichtingen", "contractduur", "schadevergoeding", "overmacht", "geheimhouding",
        "toepasselijk recht", "beëindiging", "geschillen", "leveringsvoorwaarden",
        "intellectuele eigendom", "facturatie", "boetebeding", "annulering", "garantie", "verzekeringen"
    ]


    # === Utils ===
    def extract_text_from_pdf(path):
        reader = PdfReader(path)
        return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())

    def split_into_chunks(text, max_chars=500):
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

    def prepare_embeddings(chunks, encoder):
        vectors = encoder.encode(chunks, convert_to_numpy=True)
        return [(str(i), vec) for i, vec in enumerate(vectors)]

    class DummyChunkDatabase:
        def add_keyword_and_distance(self, chunk_id, queries, distances):
            pass

    # === Experiment Loop ===
    results = []

    for model_name in models_to_test:
        print(f"\n🔬 Testing model: {model_name}")
        encoder = SentenceTransformer(model_name)

        for pdf_path in pdf_files:
            print(f"📄 File: {pdf_path}")
            text = extract_text_from_pdf(pdf_path)
            chunks = split_into_chunks(text)
            embeddings = prepare_embeddings(chunks, encoder)

            index = FaissIndex(embeddings, temperature=0, encoder=encoder)
            db = DummyChunkDatabase()

            query_vectors = encoder.encode(queries, convert_to_numpy=True)

            start_time = time.time()
            distances, indices = index.f_search(queries, db)
            elapsed_time = round(time.time() - start_time, 2)

            for i, query in enumerate(queries):
                scores = distances[i]
                max_sim = float(np.max(scores))
                max_idx = int(np.argmax(scores))
                chunk_idx = indices[i][max_idx]
                top_chunk = chunks[chunk_idx] if chunk_idx != -1 else "[No matching chunk]"

                answer = gpt.generate_answer(
                    f"Query: {query}\nTop Chunk: {top_chunk}\nMax Similarity: {max_sim:.3f}\n"
                )

                results.append({
                    "Model": model_name,
                    "File": os.path.basename(pdf_path),
                    "Query": query,
                    "Max Similarity": round(max_sim, 3),
                    "Avg Similarity": round(float(np.mean(scores)), 3),
                    "Top Chunk": top_chunk[:300] + ("..." if len(top_chunk) > 300 else ""),
                    "GPT Answer": answer,
                    "Seconds": elapsed_time
                })

    # === Save & View Results ===
    df = pd.DataFrame(results)
    df.to_csv("model_comparison_results.csv", index=False)
    pd.set_option('display.max_colwidth', None)
    print("\n✅ Results saved to model_comparison_results.csv")
    print(df.head(10))  # Print preview



import pandas as pd

# Load your results CSV
df = pd.read_csv("model_comparison_results.csv")

# 1. Summarize GPT's qualitative answers by model
def summarize_gpt_answers(df):
    print("=== GPT Answers Summary by Model ===\n")
    models = df["Model"].unique()
    for model in models:
        print(f"Model: {model}")
        answers = df[df["Model"] == model]["GPT Answer"].dropna().unique()
        # You could also do some clustering or keyword extraction here for better summaries
        for ans in answers:
            print(f"- {ans.strip()}")
        print("\n" + "-"*40 + "\n")

# 2. Show retrieved chunks for each file, query, and model
def show_retrieved_chunks(df):
    print("=== Retrieved Chunks by Model, File, and Query ===\n")
    grouped = df.groupby(["File", "Model", "Query"])
    for (file, model, query), group in grouped:
        print(f"File: {file} | Model: {model} | Query: '{query}'")
        # There may be multiple rows per group if chunk sizes or other params vary
        for idx, row in group.iterrows():
            print(f"  - Top Chunk (first 300 chars): {row['Top Chunk']}")
            print(f"    Max Similarity: {row['Max Similarity']} | Avg Similarity: {row['Avg Similarity']}")
            print(f"    GPT's Comment: {row['GPT Answer']}")
            print(f"    Time taken: {row.get('Seconds', 'N/A')} seconds")
        print("\n" + "="*60 + "\n")

# Run the summaries
        
if __name__ == "__main__":
    summarize_gpt_answers(df)
    show_retrieved_chunks(df)
