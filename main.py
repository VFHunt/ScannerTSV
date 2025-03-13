import os
import io
from atakan import FileHandler  # Import your FileHandler class

# Path to your test folder
TEST_FOLDER = "files"  # Replace with your actual folder path

# Get all file paths in the test folder
file_paths = [os.path.join(TEST_FOLDER, f) for f in os.listdir(TEST_FOLDER)]

# Convert files into file-like objects (mimicking uploaded files)
uploaded_files = []
for file_path in file_paths:
    with open(file_path, "rb") as f:
        file_bytes = io.BytesIO(f.read())  # Convert file content to BytesIO
        file_bytes.name = os.path.basename(file_path)  # Add file name attribute
        uploaded_files.append(file_bytes)

# Initialize FileHandler with multiple files
file_handler = FileHandler(files=uploaded_files)

# Process files
for file in uploaded_files:
    print(f"\nProcessing file: {file.name}")
    chunks = file_handler.process_file(file)

    # Tokenize and embed text chunks
    for idx, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
        tokenized = file_handler.tokenize_text(chunk["content"])
        embeddings = file_handler.get_embeddings(tokenized)
        print(f"Chunk {idx + 1}: {chunk['content'][:200]}")  # Show first 200 characters
        print(f"Tokenized: {tokenized}")
        print(f"Embedding shape: {embeddings.shape}\n")
