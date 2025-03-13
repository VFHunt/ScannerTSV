import pdfplumber
import pytesseract # text from images
import logging
from docx import Document
from PIL import Image # handle image files
from typing import List, Dict
from streamlit.runtime.uploaded_file_manager import UploadedFile

# Configure Logging
logging.basicConfig(level=logging.INFO) #experiment on off
logger = logging.getLogger(__name__)

class FileProcessor:
    def __init__(self, file: UploadedFile):
        """Initialize with a single uploaded file."""
        self.file = file
        self.file_type = file.name.split(".")[-1].lower()

    def extract_text_chunks(self, chunk_size: int = 300) -> List[Dict[str, str]]:
        """Extract text from different file types and return chunks."""
        if self.file_type == "pdf":
            return self._extract_pdf_text(chunk_size)
        elif self.file_type == "docx":
            return self._extract_docx_text(chunk_size)
        elif self.file_type == "txt":
            return self._extract_txt_text(chunk_size)
        else:
            logger.error(f"Unsupported file type: {self.file_type}")
            return []

    def _extract_pdf_text(self, chunk_size: int) -> List[Dict[str, str]]:
        """Extract text from PDF and split into chunks."""
        chunks = []
        with pdfplumber.open(self.file) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or self._extract_pdf_images(page)
                words = text.split()
                for i in range(0, len(words), chunk_size):
                    chunk = " ".join(words[i:i + chunk_size])
                    chunks.append({"content": chunk, "metadata": {"page": page_num}})
        logger.info(f"Extracted {len(chunks)} chunks from PDF")
        return chunks

    def _extract_pdf_images(self, page) -> str:
        """Extract text from images inside a PDF page using OCR."""
        images = page.images
        text = ""
        for img in images:
            image_obj = Image.open(img.stream)
            text += pytesseract.image_to_string(image_obj) + "\n"
        return text

    def _extract_docx_text(self, chunk_size: int) -> List[Dict[str, str]]:
        """Extract text from DOCX and split into chunks."""
        doc = Document(self.file)
        text = "\n".join([para.text for para in doc.paragraphs])
        words = text.split()
        chunks = [{"content": " ".join(words[i:i + chunk_size]), "metadata": {"page": 1}}
                  for i in range(0, len(words), chunk_size)]
        logger.info(f"Extracted {len(chunks)} chunks from DOCX")
        return chunks

    def _extract_txt_text(self, chunk_size: int) -> List[Dict[str, str]]:
        """Extract text from TXT and split into chunks."""
        text = self.file.read().decode("utf-8")
        words = text.split()
        chunks = [{"content": " ".join(words[i:i + chunk_size]), "metadata": {"page": 1}}
                  for i in range(0, len(words), chunk_size)]
        logger.info(f"Extracted {len(chunks)} chunks from TXT")
        return chunks
