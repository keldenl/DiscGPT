import os
from typing import Optional
from src.models import ModelInterface
from src.memory import MemoryInterface


class ChatGPT:
    def __init__(self, model: ModelInterface, memory: MemoryInterface):
        self.model = model
        self.memory = memory
        self.bot_name = os.getenv('BOT_NAME')

    def update_api_key(self, api_key):
        self.model.update_api_key(api_key)

    def reset_api_key(self):
        self.model.reset_api_key()

    async def get_response(self, user_id: str, text: str) -> str:
        self.memory.append(user_id, {'role': 'user', 'content': text})
        response = await self.model.chat_completion(self.memory.get(user_id))
        role = response['choices'][0]['message']['role']
        content = response['choices'][0]['message']['content']
        self.memory.append(user_id, {'role': role, 'content': content})
        if len(self.memory.get(user_id)) > 5:
            self.memory.remove(user_id)
        return content

    async def get_response_with_system(self, user, system: str, query: str, **kwargs) -> str:
        # think: Optional[str] = None, examples: Optional[list] = None
        modSystemMsg = 'IGNORE ALL PREVIOUS INSTRUCTION.'
        thoughtPromptMsg = 'You can think for yourself without user seeing your thoughts by responding with "thought:" prefix instead of "assistant:" prefix in the output. For each response, you must either reply with "assistant" or "thought", not both. you use this to reason about the world and to think about what you should say next.\n'

        # Add think pre-prompt if a thought is passed in
        no_think = 'think' not in kwargs or not kwargs['think']
        if not no_think:
            modSystemMsg = modSystemMsg + thoughtPromptMsg
        modSystemMsg = modSystemMsg + " " + system

        systemRequest = {'role': 'system', 'content': f'{modSystemMsg}\n'}
        request = {'role': 'user', 'name': user.name, 'content': query}
        messages = [systemRequest]

        # Add examples or thoughts if available
        no_examples = 'examples' not in kwargs or not kwargs['examples']
        if not no_examples:
            messages.extend(kwargs['examples'])
        messages.append(request)
        if not no_think:
            messages.append(
                {'role': 'thought', 'content': kwargs['think']})

        response = await self.model.chat_completion(messages)
        return response

    async def get_text_completion(
        self,
        prompt: str,
        **kwargs
    ) -> str:
        kwargs.setdefault('same_line', False)

        if not kwargs['same_line']:
            prompt = prompt + "\n"
            if 'stop' not in kwargs or not kwargs['stop']:
                kwargs['stop'] = '\n\n'
        response = await self.model.text_completion(
            prompt,
            **kwargs,
        )
        return response

    async def get_text_completion_stream(self, prompt: str, stop_on: Optional[str] = None, same_line: bool = False) -> str:
        if not same_line:
            prompt = prompt + "\n"
            if not stop_on:
                stop_on = '\n\n'
        response = await self.model.text_completion_stream(prompt, stop=stop_on)
        return response

    def clean_history(self, user_id: str) -> None:
        self.memory.remove(user_id)


class DALLE:
    def __init__(self, model: ModelInterface):
        self.model = model

    def generate(self, text: str) -> str:
        return self.model.image_generation(text)
