#MODIFY WITH OPENAI MODEL
import gensim.downloader as api

# Load Word2Vec Pretrained Model (Google News Vectors)
print("Loading Word2Vec model (this may take a while)...")
word2vec_model = api.load("word2vec-google-news-300")
print("Word2Vec model loaded successfully!")

def generate_related_terms(keyword, top_n=10):
    """
    Generate related words for a given keyword using Word2Vec embeddings.
    """
    # Get related words using Word2Vec
    try:
        similar_words = word2vec_model.most_similar(keyword, topn=top_n)
        related_terms = [word for word, score in similar_words]
    except KeyError:
        related_terms = ["Word not found in vocabulary"]

    print(f"Generated related words: {related_terms}")
    return related_terms

