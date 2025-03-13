from sentence_transformers import SentenceTransformer
import os

MODEL_NAME = "all-MiniLM-L6-v2"
CACHE_DIR = "model_cache"

os.makedirs(CACHE_DIR, exist_ok=True)

model = SentenceTransformer(MODEL_NAME)
model.save(os.path.join(CACHE_DIR, MODEL_NAME))

print(f"Model saved to {CACHE_DIR}/{MODEL_NAME}")