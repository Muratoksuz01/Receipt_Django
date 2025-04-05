from abc import ABC, abstractmethod
import google.generativeai as genai
# import openai


class BaseTextProcessor(ABC):
    @abstractmethod
    def process_text(self, text):
        pass

class OpenAIProcessor(BaseTextProcessor):
    def __init__(self, api_key):
        self.api_key = api_key

    def process_text(self, text):
        openai.api_key = self.api_key
        response = openai.ChatCompletion.create(
            model="gpt-4", messages=[{"role": "user", "content": text}]
        )
        return response["choices"][0]["message"]["content"]


# Metin İşleyici Seçici
def get_text_processor(engine="gemini", api_key=None):
    if engine == "gemini":
        return GeminiProcessor(api_key)
    # elif engine == "openai":
    #     return OpenAIProcessor(api_key)
    else:
        raise ValueError("Geçersiz Metin İşleyici Seçildi")
