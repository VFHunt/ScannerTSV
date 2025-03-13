import sys
from atakan import FileHandler  # Ensure this matches your class file name

def search_keyword_in_file(file_path, keyword):
    """Extracts text from a file and searches for a keyword."""

    # Initialize FileHandler and extract text chunks (paragraphs)
    handler = FileHandler([file_path])
    chunks = handler.extract_text_chunks(file_path)

    matches = []
    for i, chunk in enumerate(chunks):
        if keyword.lower() in chunk["content"].lower():
            # Retrieve the previous, current, and next paragraph
            previous_paragraph = chunks[i - 1]["content"] if i > 0 else "N/A"
            current_paragraph = chunk["content"]
            next_paragraph = chunks[i + 1]["content"] if i < len(chunks) - 1 else "N/A"

            matches.append({
                "page": chunk["metadata"]["page"],
                "previous": previous_paragraph,
                "current": current_paragraph,
                "next": next_paragraph
            })

    # Print results
    if matches:
        print(f"Found '{keyword}' in the following paragraphs:")
        for match in matches:
            print(f"\n--- Page {match['page']} ---")
            print(f"Previous Paragraph: {match['previous']}")
            print(f"Current Paragraph: {match['current']}")
            print(f"Next Paragraph: {match['next']}")
    else:
        print(f"No matches found for '{keyword}'.")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python search.py test.pdf keyword")
    else:
        search_keyword_in_file(sys.argv[1], sys.argv[2])
