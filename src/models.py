import os

from typing import List, Dict, Optional
import openai


class ModelInterface:
    async def chat_completion(
        self,
        messages: List[Dict],
        max_tokens: float,
        temperature: float,
        top_p: float,
        stop: str
    ) -> str:
        pass

    async def text_completion(
        self,
        prompt: str,
        max_tokens: float,
        temperature: float,
        top_p: float,
        stop: str
    ) -> str:
        pass

    async def text_completion_stream(self, prompt: str) -> str:
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

    async def chat_completion(self, messages, **kwargs) -> str:
        # Default parameters for chat completion
        kwargs.setdefault('max_tokens', 2000/4)
        kwargs.setdefault('temperature', 0.72)
        kwargs.setdefault('top_p', 0.01)
        kwargs.setdefault('stop', '\n\n')

        response = await openai.ChatCompletion.acreate(
            model=self.model_engine,
            messages=messages,
            **kwargs
        )
        return response['choices'][0]['message']['content']

    async def text_completion(self, prompt, **kwargs) -> str:
        # Default parameters for text completion
        kwargs.setdefault('max_tokens', 2000/4)
        kwargs.setdefault('temperature', 0.72)
        kwargs.setdefault('top_p', 0.01)
        kwargs.setdefault('stop', '\n\n')

        response = await openai.Completion.acreate(
            model=self.model_engine,
            prompt=prompt,
            **kwargs
        )
        return response['choices'][0]['text']['content']

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
