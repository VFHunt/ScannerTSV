# Open AI's generative model use

from openai import OpenAI 
import tiktoken

client = OpenAI(api_key="")

class GenModel():
    def __init__(self, model: str, role: str):
        print("Model generated")
        self.model = model
        self.role = role
        self.answers = []

    def generate(self, prompt: str) -> None: 
        self.prompt = prompt
        completion = client.chat.completions.create(
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

    def get_answer(self) -> str:
        print(self.answers)
        return self.answers

    def estimate_tokens(self)  -> int:
        text_ = [self.role, self.prompt, self.answers]
        type_ = ["role", "prompt", "answer"]
        text = ""
        for i in range(len(text_)):
            text += text_[i]
            print(f"For {type_[i]} the text is: {text_[i]}")
        try:
            encoding = tiktoken.encoding_for_model(self.model)
        except KeyError:
            print("Model not found. Using default encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        
        tokens = encoding.encode(text)
        print(text)
        print("The total tokens are: ", len(tokens))
        return len(tokens)
    
    def generate_synonyms(self, prompt: str) -> list:
        self.generate(prompt)
        return self.get_answer() # bad practice I believe but we will work with this