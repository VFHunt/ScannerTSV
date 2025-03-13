import sys
import pdfplumber
from test_file_processor import FileProcessor  # Ensure this matches your class file name


def search_keyword_in_pdf(pdf_path, keyword):
    """Extracts text from a PDF file and searches for a keyword."""

    # Open the PDF file
    with open(pdf_path, "rb") as pdf_file:
        processor = FileProcessor(pdf_file)  # Pass file to FileProcessor
        chunks = processor.extract_text_chunks()  # Extract text in chunks

    # Search for keyword and retrieve surrounding chunks
    matches = []
    for i, chunk in enumerate(chunks):
        if keyword.lower() in chunk["content"].lower():
            # Retrieve the previous, current, and next chunk
            previous_chunk = chunks[i - 1]["content"] if i > 0 else ""
            current_chunk = chunk["content"]
            next_chunk = chunks[i + 1]["content"] if i < len(chunks) - 1 else ""
            matches.append({
                "page": chunk["metadata"]["page"],
                "previous": previous_chunk,
                "current": current_chunk,
                "next": next_chunk
            })

    # Print results
    if matches:
        print(f"Found '{keyword}' in the following chunks:")
        for match in matches:
            print(f"- Page {match['page']}:")
            print(f"  Previous: {match['previous'][:15]}...")  # Print first 50 characters
            print(f"  Current: {match['current'][:15]}...")  # Print first 50 characters
            print(f"  Next: {match['next'][:15]}...")  # Print first 50 characters
    else:
        print(f"No matches found for '{keyword}'.")


# Run the script with arguments: python test_file.py test.pdf keyword
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python test_file_processor.py test.pdf is")
    else:
        search_keyword_in_pdf(sys.argv[1], sys.argv[2])
