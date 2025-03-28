from backend_filepro import EMBEDDING_MODEL
from vector_db import index

def search_terms_in_pinecone(terms):
    """
    Search for multiple terms using semantic search in Pinecone.
    """
    # Search for each term
    all_results = []
    for term in terms:
        # Encode the search term
        search_vector = EMBEDDING_MODEL.encode(term).tolist() # tolist Converts the vector from a NumPy array (or tensor) to a Python list Pinecone only accepts lists as input.
        
        # Query Pinecone
        results = index.query(
            vector=search_vector,
            top_k=100,
            include_metadata=True
        )
        
        # Add results with the search term used
        for match in results.matches:
            all_results.append({
                'term': term,
                'score': match.score,
                'text': match.metadata['text'],
                'filename': match.metadata['filename'],
                'page': match.metadata['page']
            })
    
    # Sort all results by score
    all_results.sort(key=lambda x: x['score'], reverse=True)
    
    # Display results
    print(f"\nFound {len(all_results)} relevant matches:")
    for i, result in enumerate(all_results, 1):
        print(f"\n{i}. Match")
        print(f"   Retrieved using: '{result['term']}'")
        print(f"   File: {result['filename']}")
        print(f"   Page: {result['page']}")
        print(f"   Text: {result['text']}")
        print(f"   Similarity Score: {result['score']:.4f}")

