import os
import logging
from typing import List, Dict, Any
from transformers import AutoTokenizer
from torch import Tensor
from sentence_transformers import SentenceTransformer
import PyPDF2
from docx import Document
import pytesseract
from pdf2image import convert_from_path
from constants import get_model
import re
import string

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, force=True)


class FileHandler:
    _instance = None  # Class-level variable to store the single instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            # Create a new instance if it doesn't exist
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, files=None):
        """
        Initialize FileHandler to process files.
        Args:
            files: List of file paths to process. If None, no files are loaded.
        """
        if not hasattr(self, "initialized"):  # Ensure __init__ runs only once
            self.tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
            self.embedder = get_model()
            self.files = files or []
            self.results = {}
            self.project_name = None
            self.initialized = True  # Mark as initialized

    def initialize(self, files):
        """
        Initialize the FileHandler with a new set of files.
        """
        self.files = files
        self.results = {}

    def reset_project(self):
        """Reset the project name and results."""
        self.files = []
        self.results = {}
        self.project_name = None
        logger.info("Project reset: project name and results cleared.")

    def set_project_name(self, project_name: str):
        """Set the project name for the file handler."""
        if not project_name:
            logger.warning("Project name is empty. Please provide a valid name.")
            return
        self.project_name = project_name
        logger.info(f"Project name set to: {self.project_name}")

    def get_project_name(self) -> str:
        """Get the project name."""
        if not self.project_name:
            logger.warning("Project name is not set.")
            return ""
        return self.project_name

    def get_results(self) -> List[Dict[str, Any]]:
        if not self.results:
            logger.warning("No results available. Please process files first.")
            return []

            # Flatten the results dictionary into a list of dictionaries
        flattened_results = []
        for file_name, chunks in self.results.items():
            for chunk in chunks:
                chunk["file_name"] = file_name
                flattened_results.append(chunk)

        return flattened_results

    def set_results(self, results):
        if not results:
            logger.warning("No results to set.")
            return
        self.results = results
        logger.info(f"Results set with {len(self.results)} entries.")

    def add_files(self, files: List[str]):
        """Add files to process."""
        self.files.extend(files)
        logger.info(f"Added {len(files)} files. Total files: {len(self.files)}")

    def set_actual_names(self, actual_names: List[str]):
        self.actual_names = actual_names
        logger.info(f"Actual names set with {len(self.actual_names)} entries.")

    def get_actual_names(self) -> List[str]:
        """Get the actual names of the files."""
        if not hasattr(self, 'actual_names'):
            logger.warning("Actual names are not set.")
            return []
        return self.actual_names

    def process_all_files(self) -> Dict[str, List[Dict[str, Any]]]:
        """Process all files and return tokenized and embedded chunks."""
        if not self.files:
            logger.warning("No files to process")
            return {}

        actual_names = self.get_actual_names()  # Get actual names if set
        for i, file_path in enumerate(self.files):
            logger.info(f"Processing file: {file_path}")
            chunks = self.extract_text_chunks(file_path)  # Extract text chunks

            # Embed text directly
            embeddings = self.get_embeddings([chunk["content"] for chunk in chunks])

            # Use actual name if available and valid, otherwise use the filename from the path
            file_key = actual_names[i] if actual_names and i < len(actual_names) else os.path.basename(file_path)
            self.results[file_key] = [
                {
                    "content": chunks[i]["content"],
                    "embedding": embeddings[i],
                    "metadata": chunks[i]["metadata"]
                }
                for i in range(len(chunks))
            ]
        # logger.debug(f"Results structure: {results}")
        self.set_results(self.results)  # Set results for each file
        return self.results

    def _split_text(self, text, sent_length):
        """
        Split text into chunks of up to `sent_length` characters, combining smaller sentences if needed.
        """
        # Clean excessive dots and other unnecessary characters
        text = self._clean_text(text)

        # Split text into sentences
        pattern = r'(?i)((?<!\bMr\.)(?<!\bMrs\.)(?<!\bDr\.)(?<=[.!?])\s+|(?<=[.!?]["”]))'
        sentences = [s.strip() for s in re.split(pattern, text.strip()) if s.strip()]

        chunks = []
        current_chunk = ""

        for sentence in sentences:
            # Check if adding the sentence exceeds the maximum chunk size
            if len(current_chunk) + len(sentence) + 1 <= sent_length:
                # Add the sentence to the current chunk
                current_chunk += (" " + sentence).strip()
            else:
                # Save the current chunk and start a new one
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence

        # Add the last chunk if it exists
        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def _get_index(self, sent, ind):
        ind -= 10
        if ind < 0:
            ind = len(sent) - 1
        else:
            while ind < len(sent) and (sent[ind] not in string.punctuation and not sent[ind].isspace()):
                ind += 1
        return ind + 1

    def _halve(self, sent):
        result = []
        index1 = int(len(sent) / 2)
        index = self._get_index(sent, index1)
        part1 = sent[:index].strip()
        part2 = sent[index:].strip()
        result.append(part1)
        result.append(part2)
        return result

    # function to split the sentences according to a maximum number of characters
    def _split_sentences(self, one_sent, maxchar):
        if not one_sent.strip():  # Skip empty sentences
            return []
        result = []
        if len(one_sent) <= maxchar:
            result.append(one_sent)
        elif len(one_sent) <= 2 * maxchar:
            result.extend(self._halve(one_sent))
        else:
            index = self._get_index(one_sent, maxchar)
            part1 = one_sent[:index].strip()
            result.append(part1)
            part2 = one_sent[index:].strip()
            if len(part2) > maxchar:
                part2 = self._split_sentences(part2, maxchar)
                result.extend(part2)
            else:
                result.append(part2)
        return result

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

                clean_text = self._clean_text(text)  # Clean the text
                # print(f"Extracted text from page {page_num}: {clean_text}")  # Debugging output
                text_chunks = self._split_text(clean_text, 500)  # Split long paragraphs

                for sub_chunk in text_chunks:
                    if sub_chunk.strip():  # Skip empty sub-chunks
                        # print(f"Processing sub-chunk: {sub_chunk, len(sub_chunk)} ")  # Debugging output
                        chunks.append({
                            "content": sub_chunk,
                            "metadata": {"page": page_num}
                        })

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

    def _split_into_chunks(self, text: str, chunk_size: int = 500) -> List[str]:
        """
        Split text into smaller chunks while preserving word boundaries.
        """
        if not text.strip():  # Skip empty text
            return []

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

    def _clean_text(self, text: str) -> str:
        """
        Clean excessive dots, new lines, bullet points, and other unnecessary characters from the text.
        """
        # Replace 3 or more dots with a single space
        text = re.sub(r"\.{3,}", " ", text)
        # Replace new lines with a single space
        text = text.replace("\n", " ")
        # Remove bullet points (e.g., •, -, *, or numbered lists like 1.)
        text = re.sub(r"^\s*[\u2022\-\*\d]+\.\s*", " ", text, flags=re.MULTILINE)
        # Remove extra spaces
        text = re.sub(r"\s+", " ", text)
        return text.strip()  # Ensure no leading/trailing whitespace
    

class FileNaming:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Initialize the instance attributes
            cls._instance._actual_names = []
            cls._instance._temp_names = []
            cls._instance._name_mapping = {}
        return cls._instance
    
    def __init__(self):
        """
        Initialize the FileNaming singleton if it hasn't been initialized.
        The actual initialization is done in __new__.
        """
        pass
    
    def update_names(self, actual_names: List[str], temp_names: List[str]) -> None:
        """
        Update the naming dictionary with new actual and temporary names.
        Skip names that are already in the mapping.
        
        Args:
            actual_names: List of actual file names
            temp_names: List of temporary file names
        """
        if len(actual_names) != len(temp_names):
            raise ValueError("The lists of actual names and temporary names must have the same length")
            
        for actual, temp in zip(actual_names, temp_names):
            if temp not in self._name_mapping:
                self._name_mapping[temp] = actual
                self._actual_names.append(actual)
                self._temp_names.append(temp)
                logger.info(f"Added mapping: {temp} -> {actual}")
            else:
                logger.debug(f"Skipping existing mapping for {temp}")
    
    def get_actual_name(self, temp_name: str) -> str:
        """
        Get the actual name for a temporary name.
        
        Args:
            temp_name: The temporary name to look up
            
        Returns:
            The actual name if found, otherwise returns the temporary name
        """
        return self._name_mapping.get(temp_name, temp_name)
    
    def get_temp_name(self, actual_name: str) -> str:
        """
        Get the temporary name for an actual name.
        
        Args:
            actual_name: The actual name to look up
            
        Returns:
            The temporary name if found, otherwise returns None
        """
        for temp, actual in self._name_mapping.items():
            if actual == actual_name:
                return temp
        return None
    
    def get_temp_names_for_actuals(self, actual_names: List[str]) -> List[str]:
        """
        Get the temporary names for a list of actual names.
        If an actual name doesn't have a mapping, it will be excluded from the result.
        
        Args:
            actual_names: List of actual file names to look up
            
        Returns:
            List of corresponding temporary names (in the same order)
        """
        temp_names = []
        for actual_name in actual_names:
            temp_name = self.get_temp_name(actual_name)
            if temp_name is not None:
                temp_names.append(temp_name)
            else:
                logger.debug(f"No temporary name found for {actual_name}")
        return temp_names
    
    def get_all_mappings(self) -> Dict[str, str]:
        """
        Get all name mappings.
        
        Returns:
            Dictionary with temporary names as keys and actual names as values
        """
        return self._name_mapping.copy()
    
    def clear_mappings(self) -> None:
        """
        Clear all name mappings.
        """
        self._actual_names.clear()
        self._temp_names.clear()
        self._name_mapping.clear()
        logger.info("All file name mappings cleared")

# Example usage:
# file_naming = FileNaming()  # Gets the singleton instance
# file_naming.update_names(['actual1.pdf', 'actual2.pdf'], ['temp1.pdf', 'temp2.pdf'])
