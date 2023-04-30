import os

from typing import List, Dict
import openai


class ModelInterface:
    async def chat_completion(self, messages: List[Dict]) -> str:
        pass

    async def text_completion(self, prompt: str) -> str:
        pass

    async def text_completion_stream (self, prompt: str) -> str:
        pass


    def update_api_key(self, api_key: str):
        pass

    def reset_api_key(self):
        pass

    def image_generation(self, prompt: str) -> str:
        pass


class OpenAIModel(ModelInterface):
    def __init__(self, api_key: str, model_engine: str, image_size: str = '512x512'):
        openai.api_key = api_key
        if os.getenv("OPENAI_API_BASE_URL", None):
            openai.api_base = os.getenv('OPENAI_API_BASE_URL')

        self.model_engine = model_engine
        self.image_size = image_size

    def update_api_key(self, api):
        openai.api_key = api

    def reset_api_key(self):
        openai.api_key = os.getenv('OPENAI_API')

    async def chat_completion(self, messages) -> str:
        response = await openai.ChatCompletion.acreate(
            model=self.model_engine,
            messages=messages,
            temperature=1,
            top_p=0.1,
            max_tokens=2000/4,  # 1 token ~= 4 characters. discord limit = 2000 characters
        )
        return response
    
    async def text_completion(self, prompt, stop) -> str:
        response = await openai.Completion.acreate(
            model=self.model_engine,
            prompt=prompt,
            temperature=2,
            top_p=0.1,
            max_tokens=1000/4,  # 1 token ~= 4 characters. discord limit = 2000 characters
            stop=stop
        )
        return response
    
    async def text_completion_stream(self, prompt, stop) -> str:
        response = await openai.Completion.acreate(
            model=self.model_engine,
            prompt=prompt,
            temperature=2,
            top_p=0.1,
            max_tokens=1000/4,  # 1 token ~= 4 characters. discord limit = 2000 characters
            stop=stop,
            stream=True
        )
        return response

    def image_generation(self, prompt: str) -> str:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size=self.image_size
        )
        image_url = response.data[0].url
        return image_url
