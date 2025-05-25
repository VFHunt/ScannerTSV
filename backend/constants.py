from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from openai import OpenAI 
import os
import logging

# ____________________________ Constants ___________________________

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ____________________________ Model for encoding into embeddings ___________________________
_TRANS_MODEL = None

def get_model():
    global _TRANS_MODEL
    if _TRANS_MODEL is None:
        _TRANS_MODEL = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2') # paraphrase-multilingual-MiniLM-L12-v2
    return _TRANS_MODEL

# ____________________________ OpenAI Client ___________________________

# Load environment variables from .env file
load_dotenv()

_OPENAI_CLIENT = None  # internal private instance

def get_openai_client():
    global _OPENAI_CLIENT
    if _OPENAI_CLIENT is None:
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.error("OPENAI_API_KEY environment variable not set.")
            raise ValueError("API key must be set in the environment variable 'OPENAI_API_KEY'.")
        _OPENAI_CLIENT = OpenAI(api_key=api_key)
    return _OPENAI_CLIENT
