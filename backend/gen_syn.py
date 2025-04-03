# Open AI's generative model use

from openai import OpenAI 
from syn_evaluators import calculate_embedding_similarity
import tiktoken
import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client with API key
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    logger.error("OPENAI_API_KEY environment variable not set.")
    raise ValueError("API key must be set in the environment variable 'OPENAI_API_KEY'.")

client = OpenAI(api_key=api_key)  # Pass the API key to the OpenAI client

class GenModel():
    def __init__(self, model: str, role: str):
        logger.info("Initializing GenModel")
        self.model = model
        self.role = role
        self.answers = []

    def get_answer(self) -> str:
        return self.answers

    def estimate_tokens(self) -> int:
        text_ = [self.role, self.prompt, self.answers]
        type_ = ["role", "prompt", "answer"]
        text = "".join(text_)

        try:
            encoding = tiktoken.encoding_for_model(self.model)
        except KeyError:
            logger.warning("Model not found. Using default encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")

        tokens = encoding.encode(text)
        logger.debug(f"Total tokens: {len(tokens)}")
        return len(tokens)

    def generate_answer(self, prompt: str) -> list:
        self.prompt = prompt
        completion = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "developer", "content": self.role},
                {"role": "user", "content": self.prompt},
            ]
        )
        answer = completion.choices[0].message.content
        self.answers = answer
        return self.get_answer()

    def generate_synonyms(self, prompt: str) -> list: 
        self.answers = []
        self.prompt = prompt
        completion = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "developer", "content": self.role},
                {"role": "user", "content": self.prompt},
            ]
        )
        answer = completion.choices[0].message.content
        answer_words = [word.strip() for word in answer.split(',')]
        self.answers.extend(answer_words)
        logger.info(f"Generated synonyms: {self.answers}")
        return self.get_answer()

def generate_judge_eng(syn_number: int):
    """Generate judge and engineer models for synonym evaluation."""
    judge = GenModel('gpt-4o', f'You are a judge on the quality of the synonyms generated for a given word.')
    engineer = GenModel('gpt-4o', f'You are a prompt engineer, you need to improve the prompt that has been given to generate {str(syn_number)} synonyms. Keep it short, effective, and a Dutch word related to construction work that you will be given.')
    return judge, engineer

def augment_prompt(keyword: str, initial_prompt: str, synonym_model: GenModel, judge: GenModel, engineer: GenModel):
    """Augment the prompt based on feedback from judge and engineer."""
    prompt = initial_prompt
    iteration = 0
    while iteration < 2:
        logger.info(f"Iteration {iteration + 1} for word: {keyword}")

        synonyms = synonym_model.generate_synonyms(prompt)
        similarity = calculate_embedding_similarity(keyword, synonyms)

        feedback_prompt = f'The synonyms are: {synonyms} and this is the min, max, and average values of the synonyms closeness to the keyword: {similarity}. Inform the prompt engineer on the quality of the prompt: {prompt}'
        judgement = judge.generate_answer(feedback_prompt)

        # Generate a refined prompt
        prompt = engineer.generate_answer(judgement)
        logger.info(f"New Prompt: {prompt}")

        iteration += 1

    return prompt
