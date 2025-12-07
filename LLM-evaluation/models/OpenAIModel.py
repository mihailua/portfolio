from pathlib import Path
import os
from dotenv import load_dotenv
from openai import OpenAI

root = Path(__file__).resolve().parents[0]

with open(root/'prompt.txt', 'r', encoding='utf-8') as f1:
    prompt = f1.read()

load_dotenv(dotenv_path=root /'env'/'.env')

api_key = os.getenv("OPENAI_API_KEY")
if api_key is None:
    raise ValueError('No OpenAI API key found')

class OpenAIModel:

    def __init__(self):
        self.client = OpenAI()
        self.model_name = 'gpt-4o'
        self.message = prompt

        self.client.responses.create(
            model=self.model_name,
            input = self.message
        )

    def request(self, qty, target_lang) -> list:

        self.message = str(qty) + 'in English and in' + target_lang

        response = self.client.responses.create( #type: ignore
            model=self.model_name,
            input = self.message
        )

        assistant_reply = response.output_text

        return assistant_reply.split(';')
    def request_translation(self, pair, lang = '') -> str:
        self.message = pair + 'from target language into source' + lang

        response = self.client.responses.create(  # type: ignore
            model=self.model_name,
            input=self.message
        )

        assistant_reply = response.output_text

        return assistant_reply

gpt = OpenAIModel()

