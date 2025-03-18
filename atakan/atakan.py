import os
import tempfile
import mimetypes
from typing import List, Dict, Any, Union
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile
import PyPDF2
from docx import Document
import logging
from transformers import AutoTokenizer
from sentence_transformers import SentenceTransformer
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, force=True)
MODEL_PATH = "../model_cache/all-MiniLM-L6-v2"

if os.path.exists(MODEL_PATH):
    logger.info(f"Loading model from {MODEL_PATH}")
    MODEL = SentenceTransformer(MODEL_PATH)
else:
    raise FileNotFoundError(f"Model not found at  {MODEL_PATH}, run download_model.py")

class FileHandler:
    def __init__(self, files: Union[UploadedFile, List[UploadedFile]] = None ):
        """
        Initialize FileHandler with uploaded files.

        Args:
            files: Single uploaded file or list of uploaded files from Streamlit.
        """
        self.tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
        self.embedder = MODEL
        self.files = [files] if isinstance(files, UploadedFile) else (files or [])
        self.temp_dir = tempfile.mkdtemp()
        logger.debug(f"Initialized FileHandler with {len(self.files)} files in temp dir: {self.temp_dir}")
        # Initialize mimetypes
        mimetypes.init()

    def process_file(self, file: UploadedFile) -> List[Dict[str, Any]]:
        """
        Process a single file and return its chunks.

        Args:
            file: Uploaded file from Streamlit.

        Returns:
            List of chunks with content and metadata.
        """
        # Save file
        file_path = self.save_upload(file)

        try:
            # Extract text chunks
            chunks = self.extract_text_chunks(file_path)
            #return chunks
        finally:
            # Clean up temporary file
            #if os.path.exists(file_path):
            os.remove(file_path) # test deleting file after extraction for speed
        return chunks

    def process_all_files(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Process all uploaded files and return a dictionary containing tokenized text chunks and embeddings.

        Returns:
            Dict where keys are filenames and values are lists of processed text chunks.
        """
        results = {}

        for file in self.files:
            logger.info(f"Processing file: {file.name}")
            chunks = self.process_file(file)  # Extract text chunks

            """
            logger.info(f"Debug: {file.name} - First 3 Chunks:")
            for idx, chunk in enumerate(chunks[:3]):
                logger.info(f"Chunk {idx + 1}: {chunk}")
            
            #tokenized_chunks = [self.tokenize_text(chunk["content"]) for chunk in chunks]  # Tokenization is extra bc already done in process files
            
            logger.info(f"Debug: {file.name} - First 3 Tokenized Chunks:")
            for idx, tokenized in enumerate(tokenized_chunks[:3]):
                logger.info(f"Tokenized Chunk {idx +1}: {tokenized}")
            

            # Flatten the tokenized chunks and embed
            #flat_tokenized = [token for sublist in tokenized_chunks for token in sublist]
            #print(f"Number of tokenized chunks: {len(flat_tokenized)}")
            """

            embeddings = self.get_embeddings([chunk["content"] for chunk in chunks])

            # Store results
            results[file.name] = [
                {"content": chunk, "embedding": embedding.tolist(), "metadata": {"filename": file.name}}
                for chunk, embedding in zip(chunks, embeddings)
            ]

        return results

    def save_upload(self, file: UploadedFile) -> str:
        """
        Save an uploaded file to a temporary directory.

        Args:
            file: Uploaded file from Streamlit.

        Returns:
            Path to the saved file.
        """
        file_path = os.path.join(self.temp_dir, file.name)
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
        logger.debug(f"Saved uploaded file to: {file_path}")
        return file_path

    def _split_into_chunks(self, text: str, chunk_size: int = 200) -> List[str]:
        """
        Split text into smaller chunks while preserving word boundaries.

        Args:
            text: The text to be split.
            chunk_size: Maximum chunk size in characters.

        Returns:
            List of text chunks.
        """
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0

        for word in words:
            word_length = len(word)
            if current_length + word_length + 1 <= chunk_size:
                current_chunk.append(word)
                current_length += word_length + 1
            else:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = word_length

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks


    def tokenize_text(self, text: str, max_tokens: int = 256) -> List[str]:
        """
        Tokenize text into chunks based on token count using Hugging Face tokenizer.

        Args:
            text: The text to tokenize.
            max_tokens: Maximum number of tokens per chunk.

        Returns:
            List of tokenized text chunks.
        """
        # Convert text into token IDs
        tokens = self.tokenizer.encode(text, add_special_tokens=False)
        # Split tokens into chunks of size max_tokens
        token_chunks = [tokens[i : i + max_tokens] for i in range(0, len(tokens), max_tokens)]
        # Optionally decode each chunk back to text if needed
        text_chunks = [self.tokenizer.decode(chunk) for chunk in token_chunks]
        return text_chunks

    def get_embeddings(self, text_chunks: List[str]):
        embeddings = self.embedder.encode(text_chunks, convert_to_numpy=True)
        print(f"Embedding shape  CHECKK: {embeddings.shape}")  # Debug output
        return embeddings

    def _split_into_paragraphs(self, text: str) -> List[str]:
        """
        Split text into paragraphs.

        Args:
            text: The text to split.

        Returns:
            List of paragraphs.
        """
        # Split on double newlines to separate paragraphs
        paragraphs = [p.strip() for p in text.split("\n\n")]
        return [p for p in paragraphs if p]

    def extract_text_chunks(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract text from a file and split into chunks with metadata.

        Args:
            file_path: The path to the file.

        Returns:
            List of dictionaries containing text chunks and metadata.
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        chunks = []

        try:
            if file_ext == '.pdf':
                # Extract text with page numbers from PDF
                text_pages = self._extract_pdf_text_with_pages(file_path)

                for page_num, text in text_pages:
                    # Split page text into paragraphs
                    paragraphs = self._split_into_paragraphs(text)
                    for paragraph in paragraphs:
                        # Further split paragraphs into smaller chunks if needed
                        if len(paragraph) > 500:  # If paragraph is too long
                            sub_chunks = self._split_into_chunks(paragraph)
                            for sub_chunk in sub_chunks:
                                chunks.append({
                                    "content": sub_chunk,
                                    "metadata": {"page": page_num}
                                })
                        else:
                            chunks.append({
                                "content": paragraph,
                                "metadata": {"page": page_num}
                            })

            elif file_ext == '.docx':
                # Extract text with page numbers from DOCX
                text_pages = self._extract_docx_text_with_pages(file_path)
                for page_num, text in text_pages:
                    paragraphs = self._split_into_paragraphs(text)
                    for paragraph in paragraphs:
                        if len(paragraph) > 500:
                            sub_chunks = self._split_into_chunks(paragraph)
                            for sub_chunk in sub_chunks:
                                chunks.append({
                                    "content": sub_chunk,
                                    "metadata": {"page": page_num}
                                })
                        else:
                            chunks.append({
                                "content": paragraph,
                                "metadata": {"page": page_num}
                            })

            elif file_ext == '.txt':
                # For text files, we don't have page numbers
                text = self._extract_txt_text(file_path)
                paragraphs = self._split_into_paragraphs(text)
                for paragraph in paragraphs:
                    if len(paragraph) > 500:
                        sub_chunks = self._split_into_chunks(paragraph)
                        for sub_chunk in sub_chunks:
                            chunks.append({
                                "content": sub_chunk,
                                "metadata": {"page": 1}
                            })
                    else:
                        chunks.append({
                            "content": paragraph,
                            "metadata": {"page": 1}
                        })
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")

        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            raise

        return chunks

    def _extract_pdf_text_with_pages(self, file_path: str) -> List[tuple[int, str]]:
        """
        Extract text from a PDF, using OCR if necessary.

        Args:
            file_path: Path to the PDF file.

        Returns:
            List of tuples with page number and extracted text.
        """
        text_pages = []
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)

            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()

                if not text or text.strip() == "":  # If page has no text (probably scanned)
                    logger.info(f"Page {page_num + 1} appears to be an image. Running OCR...")
                    images = convert_from_path(file_path, first_page=page_num + 1, last_page=page_num + 1)
                    if images:
                        ocr_text = pytesseract.image_to_string(images[0])  # Run OCR on the first image
                        text_pages.append((page_num + 1, ocr_text.strip()))
                    else:
                        text_pages.append((page_num + 1, "[OCR Failed: No image Found]"))
                else:
                    text_pages.append((page_num + 1, text))

        return text_pages

    def _extract_docx_text_with_pages(self, file_path: str) -> List[tuple[int, str]]:
        """
        Extract text from DOCX with page numbers (approximate).

        Args:
            file_path: Path to the DOCX file.

        Returns:
            List of tuples with page number and extracted text.
        """
        doc = Document(file_path)
        text_pages = []
        current_page = 1
        current_text = []
        chars_per_page = 3000  # Approximate characters per page

        for element in doc.element.body:
            if element.tag.endswith('p'): # docs paragraphs end with p
                text = element.text.strip()
                if text:
                    current_text.append(text)
                    # If we've accumulated enough text for a page
                    if sum(len(t) for t in current_text) >= chars_per_page:
                        text_pages.append((current_page, "\n".join(current_text)))
                        current_page += 1
                        current_text = []

            elif element.tag.endswith('graphic'): # chunk ends with image
                logger.info(f"Image detected in {current_page}. Running OCR...")
                try:
                    image_data = element.blob
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_img:
                        temp_img.write(image_data)
                        temp_img_path = temp_img.name

                    ocr_text = pytesseract.image_to_string(Image.open(temp_img_path))
                    text_pages.append((current_page, ocr_text.strip()))
                    os.remove(temp_img_path) # clean after ocr
                except Exception as e:
                    logger.error(f"OCR failed for image DOCX {str(e)}")
                    text_pages.append((current_page, "[OCR Failed, Image unreadable]"))
        # Add any remaining text
        if current_text:
            text_pages.append((current_page, "\n".join(current_text)))
        return text_pages

    def _extract_txt_text(self, file_path: str) -> str: # different than docx and pdf bc txt does not have pages
        """
        Extract text from a plain text file.

        Args:
            file_path: Path to the text file.

        Returns:
            The extracted text as a string.
        """
        text = []
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                text.append(line.strip())
            return "\n".join(text)

    def cleanup(self):
        """
        Clean up temporary files created during processing.
        """
        try:
            if os.path.exists(self.temp_dir):
                for filename in os.listdir(self.temp_dir):
                    file_path = os.path.join(self.temp_dir, filename)
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                os.rmdir(self.temp_dir)
                logger.debug(f"Cleaned up temp directory: {self.temp_dir}")
        except Exception as e:
            logger.error(f"Error cleaning up temp directory: {str(e)}")
