from dotenv import load_dotenv
load_dotenv()
import utils
from src.server import keep_alive
from src.memory import Memory
from src.models import OpenAIModel
from src.chatgpt import ChatGPT, DALLE
from src.logger import logger
from src.discordBot import DiscordClient, Sender
from typing import Optional
from datetime import datetime
import asyncio
import random
import discord
import os
from plugins import error_debugger
from plugins import gpt_llama_cpp
from plugins import deez_nuts
from plugins import chatbot


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
    async def use_plugin(user, channel, message, input, prompt, response_type='completion', stop_on=None, same_line=None):
        async with channel.typing():
            if user == client.user:
                return

            if message is None:
                message = await sender.send_human_message(f'> _**Prompt:** {prompt}_\n\n> <@{user.id}>: _{input}_', channel)

            if response_type == 'chat':
                receive = await chatgpt.get_response_with_system(user, prompt, input)
            else:
                receive = await chatgpt.get_text_completion(prompt, stop_on, same_line)

            return await sender.reply_message(message, receive)

    # Commands available via "/""
    @ client.tree.command(name="chat", description=f'Chat with {bot_name}')
    async def chat(interaction: discord.Interaction, *, message: str):
        prompt = chatbot.get_prompt(bot_name)
        await interaction.response.defer()
        await use_plugin(interaction.user, interaction.channel, None, message, prompt, 'chat')

    @ client.tree.command(name="ask", description=f"Ask {bot_name} about gpt-llama.cpp ")
    async def system_cmd(interaction: discord.Interaction, *, question: str):
        prompt = gpt_llama_cpp.get_prompt(question, bot_name)
        await interaction.response.defer()
        await use_plugin(interaction.user, interaction.channel, None, question, prompt, "completion", '\n\n', True)

    @ client.tree.command(name="debug", description="Debug your error log")
    async def debug_cmd(interaction: discord.Interaction, *, error_message: str):
        prompt = error_debugger.get_prompt(error_message)
        await interaction.response.defer()
        await use_plugin(interaction.user, interaction.channel, None, error_message, prompt, '\n\n')

    @ client.tree.command(name="autocomplete", description="Autocomplete your sentence")
    async def autocomplete_cmd(interaction: discord.Interaction, *, prompt: str, stop_on: Optional[str]=None, same_line: bool=False):
        await interaction.response.defer()
        await use_plugin(interaction.user, interaction.channel, None, prompt, prompt, 'completion', stop_on, same_line)

    @ client.tree.command(name="chat_advanced", description="Have a custom chat with a system message")
    async def system_cmd(interaction: discord.Interaction, *, system_message: str, message: str, think: Optional[str]=None):
        chatgpt.update_api_key(
            '../llama.cpp/models/vicuna/7B/ggml-vicuna-7b-4bit-rev1.bin')
        await interaction.response.defer()
        await use_plugin(interaction.user, interaction.channel, None, message, system_message, 'chat')
        chatgpt.reset_api_key()


    # CREATE A DISCORD BOT THAT JOINS CONVERSATIONS RANDOMLY
    @ client.event
    async def on_message(message):
        # 0.1 = 10% chance of responding if not directly mentioning the bot
        response_probability = 0.1

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

        bot_not_mentioned = bot_name.lower() not in message.content.lower(
        ) and f'<@{client.user.id}>' not in message.content
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
                message_history = messages[i: i+15]
        message_history.reverse()  # they come in reversed order

        # Get authors
        authors_full_list = [message.author for message in message_history]
        authors_name_to_id, authors_id_to_name = utils.create_id_name_hashmaps(
            authors_full_list)

        authors = [
            message.author.name for message in message_history if message.author.name != bot_name]
        authors = list(set(authors))  # get unique set of authors
        author_names = ", ".join(authors)

        # Replace author bot_name with 'You' for the prompt
        # Replace bot responses (starting with 🤖) with "Bot" author. This is so we don't confuse "you" with being the bot
        message_history_str = "\n\n".join(
            f"{'Bot' if m.content.startswith('🤖') else f'You ({bot_name})' if m.author.name == bot_name else m.author.name} [{m.created_at.strftime('%H:%M:%S %m-%d-%Y')}]:\n{utils.replace_string(m.content, authors_id_to_name)}" for m in message_history)

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
                    # response with :no_mouth: if the response failed
                    receive = ':no_mouth:' if len(receive) == 0 else receive
                    await sender.send_human_message_stream(utils.replace_string(receive, authors_name_to_id), res_message, channel)
                    continue

                curr_chunk = chunk['choices'][0]['delta']['content'].lower()
                receive = receive + curr_chunk
                queued_chunks += 1

                if queued_chunks > max_queue_chunks:
                    queued_chunks = 0
                    if len(receive) > 0:
                        res_message = await sender.send_human_message_stream(receive, res_message, channel)

    # @ client.tree.command(name="reset", description="Reset ChatGPT conversation history")
    # async def reset(interaction: discord.Interaction):
    #     user_id = interaction.user.id
    #     logger.info(f"resetting memory from {user_id}")
    #     try:
    #         await interaction.response.defer(ephemeral=True)
    #         chatgpt.clean_history(user_id)
    #         await interaction.followup.send(f'> Reset ChatGPT conversation history < - <@{user_id}>')
    #     except Exception as e:
    #         logger.error(f"Error resetting memory: {e}")
    #         await interaction.followup.send('> Oops! Something went wrong. <')

    # REACTION PLUGINS
    @ client.event
    async def on_reaction_add(reaction, user):
        message = reaction.message
        content = message.content  # username: user.name
        channel = message.channel

        # Max only 1 reply per reaction
        if reaction.count > 1:
            return

        if reaction.emoji == '🦙':
            prompt = gpt_llama_cpp.get_prompt(content, bot_name)
            await use_plugin(message.author, channel, message, content, prompt, "completion", '\n\n', True)
        if reaction.emoji == '➕':
            await use_plugin(message.author, channel, message, content, content)
        if reaction.emoji == '🐞':
            prompt = error_debugger.get_prompt(content)
            await use_plugin(message.author, channel, message, content, prompt)

        if reaction.emoji == '🥜':
            prompt = deez_nuts.get_prompt(content)
            await use_plugin(message.author, channel, message, content, prompt)
            
    client.run(os.getenv('DISCORD_TOKEN'))


if __name__ == '__main__':
    keep_alive()
    run()
