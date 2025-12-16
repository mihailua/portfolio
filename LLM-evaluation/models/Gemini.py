from google import genai
from pathlib import Path
import os
from dotenv import load_dotenv

_models_root = Path(__file__).resolve().parent

with open(_models_root / 'prompt_repetitive.txt', 'r', encoding='utf-8') as f1:
    prompt = f1.read()

load_dotenv(dotenv_path=_models_root / 'env' / '.env')

api_key = os.getenv("GEMINI_API_KEY")
if api_key is None:
    raise ValueError('No Gemini API key found')



class GeminiWrapper:
    def __init__(self, model: str = "gemini-2.5-flash"):

        self.model = model
        self.client = genai.Client(api_key=api_key)
        self.prompt_get_pairs = prompt
        self.message = ''

    def request(self, qty: int, target_lang: str) -> list[str]:
        self.message = ((self.prompt_get_pairs.replace('_number_', str(qty))
                        .replace('_target_lang_', target_lang))
                        .replace('_numb_wrong_', str(qty/2)))

        response = self.client.models.generate_content(
            model=self.model,
            contents=self.message
        )

        assistant_reply = response.text
        return assistant_reply.split(';')

    def request_translation(self, pair:str, lang='') -> str:
        self.message = f'{pair} from target language into source {lang}'

        response = self.client.models.generate_content(
            model=self.model,
            contents=self.message
        )

        assistant_reply = response.text
        return assistant_reply

gemini = GeminiWrapper()
