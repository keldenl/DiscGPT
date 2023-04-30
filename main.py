from dotenv import load_dotenv
load_dotenv()

import os
import discord
import random
import asyncio

from datetime import datetime
from typing import Optional
from src.discordBot import DiscordClient, Sender
from src.logger import logger
from src.chatgpt import ChatGPT, DALLE
from src.models import OpenAIModel
from src.memory import Memory
from src.server import keep_alive
import utils


bot_name = os.getenv('BOT_NAME')
model_name = os.getenv('MODEL_NAME')

models = OpenAIModel(api_key=os.getenv('OPENAI_API'),
                     model_engine=os.getenv('OPENAI_MODEL_ENGINE'))

memory = Memory(system_message=os.getenv('SYSTEM_MESSAGE'))
chatgpt = ChatGPT(models, memory)
dalle = DALLE(models)


def run():
    client = DiscordClient()
    sender = Sender()


    # Utils
    async def system_chat(interaction: discord.Interaction, system_message: str, message: str, think: Optional[str] = None, hide_system_thoughts: Optional[bool] = False):
        user_id = interaction.user.id  # username: interaction.user.name
        if interaction.user == client.user:
            return
        await interaction.response.defer()
        receive = await chatgpt.get_response_with_system(
            interaction.user, system_message, message, think)
        await sender.send_message(message, receive, system_message, think, hide_system_thoughts)

                    
    async def use_plugin(user, channel, message, input, prompt, response_type='completion', stop_on=None, same_line=None):
        async with channel.typing():
            if user == client.user:
                return

            if message is None:
                message = await sender.send_human_message(f'> <@{user.id}>: _{input}_', channel)
            
            if response_type == 'chat':
                receive = await chatgpt.get_response_with_system(user, prompt, input)
            else:
                receive = await chatgpt.get_text_completion(prompt, stop_on, same_line)
                
            return await sender.reply_message(message, receive)


    # Personalities
    plugins = {
        'deez_nuts': {
            # 'system_message': 'Respond to each user message with a deez nuts joke. A deez nuts joke is when you rephrase the original message by adding the words DEEZ NUTZ in it. The response is intended to confuse the user and be funny.',
            'system_message': 'Convert messages to DEEZ NUTS jokes. DEEZ NUTS jokes rephrase messages to containt the phrase "DEEZ NUTS" and make contextual sense. Contextual sense is when either an object in the original message is replaced with "deez nuts" or a word in the original message that sounds like "deez" is replaced with "deez nuts". You may also rephrase other words to make the response mildy sexual, like suck resulting in "suck on deez nuts" or goblin resulting in "gobbling deez nuts" or pudding resulting in "pudding deez nuts in your mouth".',
            'examples': [
                {'role': 'user', 'content': 'can you hold this for me'},
                {'role': 'think', 'content': 'nuts are something you can hold. rephrasing..'},
                {'role': 'assistant', 'content': 'can you hold DEEZ NUTS for me'},
                {'role': 'user', 'content': 'something came in the mail today'},
                {'role': 'think', 'content': 'nuts can be something that comes in the mail. rephrasing..'},
                {'role': 'assistant', 'content': 'deez nuts came in the mail today'},
                {'role': 'user', 'content': 'have you seen wendy around?'},
                {'role': 'think', 'content': 'the "dy" in wendy is pronounced like "dee", which sounds like "deez nuts". rephrasing..'},
                {'role': 'assistant', 'content': 'ive seen deez nuts hit your face'},
                {'role': 'user', 'content': 'i like banking with bofa'},
                {'role': 'think', 'content': 'bofa sounds like "both of". males have 2 nuts, and this is mildly sexual we can rephrase with a play-on with "both of these nuts". rephrasing..'},
                {'role': 'assistant',
                    'content': 'more like you like bofa deez nuts all over you!'},
                {'role': 'user', 'content': 'i honestly cant wait to eat my pudding'},
                {'role': 'think', 'content': 'pudding sounds like "putting", and putting nuts in mouths is mildy sexual. rephrasing..'},
                {'role': 'assistant', 'content': 'pudding deez nuts in your mouth?'},
                {'role': 'user', 'content': 'what happened at kenya?'},
                {'role': 'think', 'content': 'kenya sounds like "can ya", and asking user if they can fit these nuts in their mouth is mildy sexual. rephrasing..'},
                {'role': 'assistant', 'content': 'kenya fit deez nuts in your mouth?!'},
                {'role': 'system', 'content': 'Continue analysing and rephrasing, but simplify your thoughts to focus on whether or not its easy to rephrase. Do not explain the analysis in your thoughts like you have been.'},
                {'role': 'assistant', 'content': 'Understood. I will continue analysing, but only state if its easy to rephrase or not in my thoughts.'},
            ],
            'think': 'Easy to rephrase. rephrasing..'
        },
        'discord_user': {
            'system_message': f'This is a partial transcript of a 1000 page, never ending conversation between discord users. Messages starting with "assistant: " represent {bot_name}, a discord user and not an actual assistant.'
            # 'think': 'using context clues from the above messages, ill send a response to blend into their conversation...'
        }
    }

    @client.tree.command(name="chat", description=f'Have a chat with {bot_name}')
    async def chat(interaction: discord.Interaction, *, message: str):
        prompt = f"You are {bot_name}, a large language model trained by Meta. You are currently chatting with a user in a public discord server called gpt-llama.cpp. Follow the user's instructions carefully."
        await use_plugin(interaction.user, interaction.channel, None, message, prompt, 'chat')

    @client.tree.command(name="ask", description=f"Ask {bot_name} about gpt-llama.cpp ")
    async def system_cmd(interaction: discord.Interaction, *, question: str):
        prompt = f"""I am a highly intelligent question answering bot for the gpt-llama.cpp project. My name is {bot_name}. If you ask me a question that is in my knowledge base, I will give you the answer. If you ask me a question that is nonsense, trickery, or has no clear answer, I will respond with a variation of "I'm not sure" or "That's not relevant". Below is information about gpt-llama.cpp:
* gpt-llama.cpp is a local API server that simulates OpenAI's API GPT endpoints using local llama-based models to process requests
* Link to repo: https://github.com/keldenl/gpt-llama.cpp
* It is compatible with Windows, Linux, and MacOS platforms
* To use gpt-llama.cpp, llama.cpp project setup is required
* Link to llama.cpp: https://github.com/ggerganov/llama.cpp
* Installation instructions can be found at https://github.com/keldenl/gpt-llama.cpp#quickstart-installation
* gpt-llama.cpp cannot work without setting up the llama.cpp project separately, and llama model downloads are not provided. 
* For support or to view validated supported applications, visit https://github.com/keldenl/gpt-llama.cpp#supported-applications
* If you encounter issues, create an issue in GitHub at https://github.com/keldenl/gpt-llama.cpp/issues or post in Discord on #help-forums or #live-troubleshooting. 
* Confirmed supported gpt-projects: chatbot-ui, auto-gpt (not perfect but functioning), ChatGPT-Siri, ChatGPT-Discord-Bot, see readme for more info. 
* Best performing models from  best to worse is wizard 7b > vicuna > gpt4-x-alpaca > gpt4all > Alpaca Native > Alpaca LoRA > Base Llama.

Q: What's the link to the repo?
A: You can find `gpt-llama.cpp` at <https://github.com/keldenl/gpt-llama.cpp>

Q: I'm getting 'Readstream is not defined'
A: Make sure your system node version is >= 18. Readstream isn't supported for any older node versions.

Q: What's 1+1?
A: That's not relevant. If you want to chat, use that /chat function or mention {bot_name} in your message.

Q: Getting 'openai wrong api key'
A: Make sure you set the value of the openai_api_key in gpt-powered app's .env to the path to your llama model. Also make sure the gpt-powered app making request to your localhost gpt-llama.cpp server

Q: Does gpt-llama.cpp support GPU?
A: Not as of now, ooba's text-generation-ui is a better project to GPU heavy hardware

Q: What to set openai_api_key to?
is `xxx-xxx` okay?
A: No. It should be set to an absolute path or relative path to specifically your gpt-llama.cpp folder. 
For example, on mac 
absolute: ~/documents/llama.cpp/models/ggml.bin
relative: ../llama.cpp/models.ggml.bin if your gpt-llama.cpp and llama.cpp folders are next to each other

Q: Who's bob?
A: I'm not sure...

Q: {question}
A: """
        await use_plugin(interaction.user, interaction.channel, None, question, prompt, '\n\n', True)

    @client.tree.command(name="chat_advanced", description="Have a custom chat with a system message")
    async def system_cmd(interaction: discord.Interaction, *, system_message: str, message: str, think: Optional[str] = None):
        chatgpt.update_api_key('../llama.cpp/models/vicuna/7B/ggml-vicuna-7b-4bit-rev1.bin')
        await system_chat(interaction, system_message, message, think)
        chatgpt.reset_api_key()

    @client.tree.command(name="debug", description="Debug an error log")
    async def debug_cmd(interaction: discord.Interaction, *, error_message: str, think: Optional[str] = None):
        prompt = f"{error_message}\n\nExplanation of what the error means and potential solution:"
        await interaction.response.defer()
        await use_plugin(interaction.user, interaction.channel, None, error_message, prompt, '\n\n')

    @client.tree.command(name="autocomplete", description="Autocomplete your sentence")
    async def autocomplete(interaction: discord.Interaction, *, prompt: str, stop_on: Optional[str]=None, same_line:bool=False):
        if interaction.user == client.user:
            return
        await interaction.response.defer()
        await interaction.followup.send("> " + prompt )
        receive = await chatgpt.get_text_completion(prompt, stop_on, same_line)
        if len(receive) > 2000:
            await interaction.followup.send(receive[:2000])
            await interaction.followup.send(receive[2000:])
        else:
            await interaction.followup.send(receive)

    @client.tree.command(name="reset", description="Reset ChatGPT conversation history")
    async def reset(interaction: discord.Interaction):
        user_id = interaction.user.id
        logger.info(f"resetting memory from {user_id}")
        try:
            await interaction.response.defer(ephemeral=True)
            chatgpt.clean_history(user_id)
            await interaction.followup.send(f'> Reset ChatGPT conversation history < - <@{user_id}>')
        except Exception as e:
            logger.error(f"Error resetting memory: {e}")
            await interaction.followup.send('> Oops! Something went wrong. <')

    @client.event
    async def on_message(message):
        response_probability = 0.2 # 0.1 = 10% chance of responding if not directly mentioning the bot

        # don't react to system message or unreadable messages
        if message.content == '':
            return

        # don't react to your own messages
        if message.author == client.user:
            return
        
        # respond if addressed
        # if not addressed only respond to 10% of the messages
        r = random.random()
        message.type == "Message"

        bot_not_mentioned = bot_name.lower() not in message.content.lower() and f'<@{client.user.id}>' not in message.content
        is_reply_to_bot = message.reference is not None and message.reference.resolved.author == client.user
        if (not is_reply_to_bot) and bot_not_mentioned and r > response_probability:
            return
        
        print(f'{bot_name} auto-generating a message...')
        channel = message.channel

        # Get last 30 messages in the channel
        messages = [message async for message in channel.history(limit=20)]
        message_history = []

        # Just get the last 20 before the current message
        for i, msg in enumerate(messages):
            if msg.id == message.id:
                message_history = messages[i:i+15]
        message_history.reverse() # they come in reversed order

        # Get authors
        authors_full_list = [message.author for message in message_history]
        authors_name_to_id, authors_id_to_name = utils.create_id_name_hashmaps(authors_full_list)

        authors = [message.author.name for message in message_history if message.author.name != bot_name]
        authors = list(set(authors)) # get unique set of authors
        author_names = ", ".join(authors)

        # Replace author bot_name with 'You' for the prompt
        # Replace bot responses (starting with 🤖) with "Bot" author. This is so we don't confuse "you" with being the bot
        message_history_str = "\n\n".join(f"{'Bot' if m.content.startswith('🤖') else f'You ({bot_name})' if m.author.name == bot_name else m.author.name} [{m.created_at.strftime('%H:%M:%S %m-%d-%Y')}]:\n{utils.replace_string(m.content, authors_id_to_name)}" for m in message_history)

        prompt = f"""You, {author_names} are users on a public #{message.channel.name} channel of a discord server. You are {bot_name}, an active and fun discord member of the server who's good at coding and is very interested in the recent ai text generation improvements. Each message is formatted in a "<NAME> [DATE]: <MESSAGE>" format, and you guys refer to each other with "@NAME". {bot_name} seems to be very capable at coding and answering questions despite being just human. You guys are having a fun, non-repetitive conversation:

{message_history_str}

You ({bot_name}) [{datetime.now().strftime('%H:%M:%S %m-%d-%Y')}]:"""
        res_message = None
        async with channel.typing():
            response = await chatgpt.get_text_completion_stream(prompt, '\n\n', True)
            receive = ''
            queued_chunks = 0
            max_queue_chunks = 7

            async for chunk in response:
                if chunk['choices'][0]['finish_reason']:
                    receive = ':no_mouth:' if len(receive) == 0 else receive # response with :no_mouth: if the response failed
                    await sender.send_human_message_stream(utils.replace_string(receive, authors_name_to_id), res_message, channel)
                    continue

                curr_chunk = chunk['choices'][0]['delta']['content'].lower()
                receive = receive + curr_chunk
                queued_chunks += 1

                if queued_chunks > max_queue_chunks:
                    queued_chunks = 0
                    if len(receive) > 0:
                        res_message = await sender.send_human_message_stream(receive, res_message, channel)


    @client.event
    async def on_reaction_add(reaction, user):
        message = reaction.message
        content = message.content  # username: user.name
        channel = message.channel

        # Max only 1 reply per reaction
        if reaction.count > 1:
            return

        if reaction.emoji == '🦙':
            async with channel.typing():
                prompt = f"""I am a highly intelligent question answering bot for the gpt-llama.cpp project. My name is {bot_name}. If you ask me a question that is in my knowledge base, I will give you the answer. If you ask me a question that is nonsense, trickery, or has no clear answer, I will respond with a variation of "I'm not sure" or "That's not relevant". Below is information about gpt-llama.cpp:
* gpt-llama.cpp is a local API server that simulates OpenAI's API GPT endpoints using local llama-based models to process requests
* Link to repo: https://github.com/keldenl/gpt-llama.cpp
* It is compatible with Windows, Linux, and MacOS platforms
* To use gpt-llama.cpp, llama.cpp project setup is required
* Link to llama.cpp: https://github.com/ggerganov/llama.cpp
* Installation instructions can be found at https://github.com/keldenl/gpt-llama.cpp#quickstart-installation
* gpt-llama.cpp cannot work without setting up the llama.cpp project separately, and llama model downloads are not provided. 
* For support or to view validated supported applications, visit https://github.com/keldenl/gpt-llama.cpp#supported-applications
* If you encounter issues, create an issue in GitHub at https://github.com/keldenl/gpt-llama.cpp/issues or post in Discord on #help-forums or #live-troubleshooting. 
* Confirmed supported gpt-projects: chatbot-ui, auto-gpt (not perfect but functioning), ChatGPT-Siri, ChatGPT-Discord-Bot, see readme for more info. 
* Best performing models from  best to worse is wizard 7b > vicuna > gpt4-x-alpaca > gpt4all > Alpaca Native > Alpaca LoRA > Base Llama.

Q: What's the link to the repo?
A: You can find `gpt-llama.cpp` at <https://github.com/keldenl/gpt-llama.cpp>

Q: I'm getting 'Readstream is not defined'
A: Make sure your system node version is >= 18. Readstream isn't supported for any older node versions.

Q: What's 1+1?
A: That's not relevant. If you want to chat, use that /chat function or mention {bot_name} in your message.

Q: Getting 'openai wrong api key'
A: Make sure you set the value of the openai_api_key in gpt-powered app's .env to the path to your llama model. Also make sure the gpt-powered app making request to your localhost gpt-llama.cpp server

Q: Does gpt-llama.cpp support GPU?
A: Not as of now, ooba's text-generation-ui is a better project to GPU heavy hardware

Q: What to set openai_api_key to?
is `xxx-xxx` okay?
A: No. It should be set to an absolute path or relative path to specifically your gpt-llama.cpp folder. 
For example, on mac 
absolute: ~/documents/llama.cpp/models/ggml.bin
relative: ../llama.cpp/models.ggml.bin if your gpt-llama.cpp and llama.cpp folders are next to each other

Q: Who's bob?
A: I'm not sure...

Q: {content}
A: """
                await use_plugin(message.author, channel, message, content, prompt, '\n\n', True)
                return
        if reaction.emoji == '➕':
            await use_plugin(message.author, channel, message, content, content)
        if reaction.emoji == '🐞':
            prompt = f"{content}\n\nExplanation of what the error means and potential solution:\n"
            await use_plugin(message.author, channel, message, content, prompt, '#')

        if reaction.emoji == '🥜':
            await use_plugin(message.author, channel, message, content, f"{plugins['deez_nuts']['system_message']}\n\nExample:\nQ: {content}\nA:")
            # plug = plugins['deez_nuts']
            # receive = await chatgpt.get_response_with_system(message.author, plug['system_message'], content, plug['think'], plug['examples'])
            # await sender.reply_message(message, receive)
            # return
#         if reaction.emoji == '🤖':
#             # Get last 30 messages in the channel
#             messages = [message async for message in channel.history(limit=30)]
#             message_history = []

#             # Just get the last 20 before the current message
#             for i, msg in enumerate(messages):
#                 if msg.id == message.id:
#                     message_history = messages[i:i+25]
#             message_history.reverse() # they come in reversed order

#             # Replace author bot_name with 'You' for the prompt
#             # Replace bot responses (starting with 🤖) with "Bot" author. This is so we don't confuse "you" with being the bot
#             message_history_str = "\n".join(f"{'Bot' if m.content.startswith('🤖') else 'You' if m.author.name == bot_name else m.author.name}: {m.content}" for m in message_history)
            
#             authors = [message.author.name for message in message_history if message.author.name != bot_name]
#             authors = list(set(authors)) # get unique set of authors
#             author_names = ", ".join(authors)

#             prompt = f"""You, {author_names} are users on a public #{message.channel.name} channel of a discord server. Your name is {bot_name}. You guys are having a fun conversations:
# {message_history_str}
# You:"""
#             async with channel.typing():
#                 receive = await chatgpt.get_text_completion(prompt, '\n', True)
#                 receive = ':no_mouth:' if len(receive) == 0 else receive # response with :no_mouth: if the response failed
#             await sender.send_human_message(receive.lower(), channel)
#             return

    # ImageGen not supported
    # @client.tree.command(name="imagine", description="Generate image from text")
    # async def imagine(interaction: discord.Interaction, *, prompt: str):
    #     if interaction.user == client.user:
    #         return
    #     await interaction.response.defer()
    #     image_url = dalle.generate(prompt)
    #     await sender.send_image(interaction, prompt, image_url)

    client.run(os.getenv('DISCORD_TOKEN'))


if __name__ == '__main__':
    keep_alive()
    run()
