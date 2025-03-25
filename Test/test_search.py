from backend_filepro import EMBEDDING_MODEL
from vector_db import index

def search_keyword_in_pinecone(keyword):
    """
    Searches for a keyword using semantic search in Pinecone.
    """
    print(f"\nSearching for '{keyword}' in all files...")

    # Encode the search term
    search_vector = EMBEDDING_MODEL.encode(keyword).tolist()
    
    # Search in Pinecone
    results = index.query(
        vector=search_vector,
        top_k=5,  # Get top 5 most relevant results
        include_metadata=True  # Include the original text and other metadata
    )

    # Display results like this also for semantic generated results
    if results.matches:
        print(f"\nFound {len(results.matches)} relevant matches:")
        for match in results.matches:
            print(f"\nFile: {match.metadata['filename']}")
            print(f"Page: {match.metadata['page']}")
            print(f"Text: {match.metadata['text']}")
            print(f"Score: {match.score:.2f}")  # Similarity score
        return results.matches
    else:
        print("No relevant matches found.")
        return []

