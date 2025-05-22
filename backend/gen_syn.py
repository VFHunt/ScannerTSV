# Open AI's generative model use
from syn_evaluators import calculate_embedding_similarity
import logging
from constants import get_openai_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_client = get_openai_client()

class GenModel():
    def __init__(self, model: str, role: str):
        self.model = model
        self.role = role
        self.answers = []
        logger.info("Initializing GenModel with role: %s", role)


    def get_answer(self) -> str:
        # print(self.answers)
        return self.answers

    def generate_answer(self, prompt: str) -> list:
        self.prompt = prompt
        completion = _client.chat.completions.create(
        model=self.model,
        messages=[
            {
                "role": "developer",
                "content": self.role
            },
            {
                "role": "user",
                "content": self.prompt
            },
        ]
        )
        answer = completion.choices[0].message.content
        self.answers = answer
        return self.get_answer() 
    
    def generate_synonyms(self, prompt:str) -> list: 
        self.answers = []
        self.prompt = prompt
        completion = _client.chat.completions.create(
        model=self.model,
        messages=[
            {
                "role": "developer",
                "content": self.role
            },
            {
                "role": "user",
                "content": self.prompt
            },
        ]
        )
        answer = completion.choices[0].message.content
        answer_words = [word.strip() for word in answer.split(',')]
        self.answers.extend(answer_words)
        print(f"Generated answer: {self.answers}")
        return self.get_answer()


def generate_judge_eng(syn_number: int):
    judge = GenModel('gpt-4o', f'You are a judge on the quality of the synonyms generated for a given word.')
    engineer = GenModel('gpt-4o', f'You are a prompt engineer, you need to improve the prompt that has been given to generate {str(syn_number)} synonyms. Keep it short, effective, and a Dutch word related to construction work that you will be given.')
    return judge, engineer

def augment_prompt(keyword: str, initial_prompt: str, synonym_model: GenModel, judge: GenModel, engineer: GenModel):
    prompt = initial_prompt
    iteration = 0
    while iteration < 2:
        # print(f"Iteration {iteration + 1} for word: {keyword}")

        synonyms = synonym_model.generate_synonyms(prompt)

        similarity = calculate_embedding_similarity(keyword, synonyms)

        feedback_prompt = f'The synonyms are: {synonyms} and this is the min, max, and average values of the synonyms closeness to the keyword: {similarity}. Inform the prompt engineer on the quality of the prompt: {prompt}'
        judgement = judge.generate_answer(feedback_prompt)

        # Generate a refined prompt
        prompt = engineer.generate_answer(judgement)
        # print(f"New Prompt: {prompt}\n")

        iteration += 1

    return prompt
