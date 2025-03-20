import os
import logging
from typing import List, Dict, Any
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from sentence_transformers import SentenceTransformer
import PyPDF2
from docx import Document
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, force=True)

TRANSLATION_MODEL_NAME = "Helsinki-NLP/opus-mt-nl-en"
translator_pipeline = pipeline("translation", model=TRANSLATION_MODEL_NAME)

def translate(text: str) -> str:
    """Translate Dutch text to English using the preloaded model."""
    try:
        result = translator_pipeline(text, max_length=512)[0]["translation_text"]
        return result
    except Exception as e:
        logger.error(f"Translation failed for text: {text} | Error: {e}")
        return text  # Return original text if translation fails


MODEL_PATH = "model_cache/all-MiniLM-L6-v2"

if os.path.exists(MODEL_PATH):
    logger.info(f"Loading embedding model from {MODEL_PATH}")
    EMBEDDING_MODEL = SentenceTransformer(MODEL_PATH)
else:
    raise FileNotFoundError(f"Model not found at {MODEL_PATH}, run download_model.py")

FILES_DIRECTORY = "files/"  # Directory where documents are stored

class FileHandler:
    def __init__(self, files):
        """
        Initialize FileHandler to process local files.
        """
        self.files = files
        self.tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
        self.embedder = EMBEDDING_MODEL
        self.files = [os.path.join(FILES_DIRECTORY, f) for f in os.listdir(FILES_DIRECTORY)]
        logger.info(f"Found {len(self.files)} files in '{FILES_DIRECTORY}'")

    def process_all_files(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Process all files and return tokenized, translated, and embedded chunks.
        """
        results = {}

        for file_path in self.files:
            logger.info(f"Processing file: {file_path}")
            chunks = self.extract_text_chunks(file_path)  # Extract text chunks

            # Embed translated text
            embeddings = self.get_embeddings([chunk["translated_content"] for chunk in chunks])

            results[os.path.basename(file_path)] = [
                {
                    "content": chunks[i]["content"],
                    "translated_content": chunks[i]["translated_content"],
                    "embedding": embeddings[i],
                    "metadata": chunks[i]["metadata"]
                }
                for i in range(len(chunks))
            ]

        return results

    def extract_text_chunks(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract text from a file and split into chunks.
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        chunks = []

        try:
            if file_ext == '.pdf':
                text_pages = self._extract_pdf_text_with_pages(file_path)
            elif file_ext == '.docx':
                text_pages = self._extract_docx_text_with_pages(file_path)
            elif file_ext == '.txt':
                text_pages = [(1, self._extract_txt_text(file_path))]
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")

            for page_num, text in text_pages:
                if not text.strip():
                    continue  # Skip empty pages

                paragraphs = text.split("\n\n")
                for paragraph in paragraphs:
                    if len(paragraph) > 500:
                        sub_chunks = self._split_into_chunks(paragraph)
                        for sub_chunk in sub_chunks:
                            print(f"Translating chunk: {sub_chunk[:50]}...")  # Show part of the text being processed
                            translated_text = translate(sub_chunk)
                            chunks.append({
                                "content": sub_chunk,
                                "translated_content": translated_text,
                                "metadata": {"page": page_num}})
                    else:
                        translated_text = translate(paragraph)
                        chunks.append({
                            "content": paragraph,
                            "translated_content": translated_text,
                            "metadata": {"page": page_num}})

        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            raise

        return chunks

    def _extract_pdf_text_with_pages(self, file_path: str) -> List[tuple[int, str]]:
        """
        Extract text from PDF with OCR if needed.
        """
        text_pages = []
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()

                if not text.strip():
                    logger.info(f"Page {page_num + 1} is an image, running OCR...")
                    images = convert_from_path(file_path, first_page=page_num + 1, last_page=page_num + 1)
                    ocr_text = pytesseract.image_to_string(images[0]) if images else "[OCR Failed]"
                    text_pages.append((page_num + 1, ocr_text.strip()))
                else:
                    text_pages.append((page_num + 1, text))

        return text_pages

    def _extract_docx_text_with_pages(self, file_path: str) -> List[tuple[int, str]]:
        """
        Extract text from DOCX.
        """
        doc = Document(file_path)
        text_pages = []
        current_text = []
        chars_per_page = 3000
        page_num = 1

        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                current_text.append(text)
                if sum(len(t) for t in current_text) >= chars_per_page:
                    text_pages.append((page_num, "\n".join(current_text)))
                    page_num += 1
                    current_text = []

        if current_text:
            text_pages.append((page_num, "\n".join(current_text)))
        return text_pages

    def _extract_txt_text(self, file_path: str) -> str:
        """
        Extract text from a TXT file.
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()

    def _split_into_chunks(self, text: str, chunk_size: int = 200) -> List[str]:
        """
        Split text into smaller chunks while preserving word boundaries.
        """
        words = text.split()
        chunks, current_chunk = [], []
        current_length = 0

        for word in words:
            if current_length + len(word) + 1 <= chunk_size:
                current_chunk.append(word)
                current_length += len(word) + 1
            else:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = len(word)

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def get_embeddings(self, text_chunks: List[str]):
        return self.embedder.encode(text_chunks, convert_to_numpy=True)
