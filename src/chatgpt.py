from src.models import ModelInterface
from src.memory import MemoryInterface


class ChatGPT:
    def __init__(self, model: ModelInterface, memory: MemoryInterface):
        self.model = model
        self.memory = memory

    def get_response(self, user_id: str, text: str) -> str:
        self.memory.append(user_id, {'role': 'user', 'content': text})
        response = self.model.chat_completion(self.memory.get(user_id))
        role = response['choices'][0]['message']['role']
        content = response['choices'][0]['message']['content']
        self.memory.append(user_id, {'role': role, 'content': content})
        if len(self.memory.get(user_id)) > 5:
            self.memory.remove(user_id)
        return content

    def get_response_with_system(self, user_id: str, system: str, query: str) -> str:
        systemRequest = {'role': 'system', 'content': system}
        request = {'role': 'user', 'content': query}
        response = self.model.chat_completion([systemRequest, request])
        print(response)
        content = response['choices'][0]['message']['content']
        return content


    def clean_history(self, user_id: str) -> None:
        self.memory.remove(user_id)


class DALLE:
    def __init__(self, model: ModelInterface):
        self.model = model

    def generate(self, text: str) -> str:
        return self.model.image_generation(text)
