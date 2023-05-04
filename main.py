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
from discord.ext import tasks
import os
from plugins import error_debugger
from plugins import gpt_llama_cpp
from plugins import deez_nuts
from plugins import chatbot
from plugins import reddit_bot
from plugins import google
from plugins import web
from plugins import pygmalion
from plugins import social_agi


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
    async def use_plugin(
        user,
        channel,
        input,
        prompt,
        request_message=None,  # User's original message
        response_type: Optional[str] = 'completion',  # 'completion' or 'chat'
        show_prompt: Optional[bool] = False,
        require_request_message: Optional[bool] = True,
        response_prefix: Optional[str] = '',
        **kwargs
    ):
        async with channel.typing():
            if user == client.user:
                return

            await client.request_queued()
            if require_request_message and request_message is None:
                preprompt = f"🤖\n> _**Prompt:** {prompt}_\n > \n" if show_prompt else '🤖\n'
                request_message = await sender.send_message(f'{preprompt}> <@{user.id}>: _{input}_', channel, **kwargs)

            if response_type == 'chat':
                receive = await chatgpt.get_response_with_system(user, prompt, input,  **kwargs)
            else:
                receive = await chatgpt.get_text_completion(prompt, **kwargs)

        if require_request_message:
            await sender.reply_message(request_message, response_prefix + receive)
        else:
            await sender.send_message(response_prefix + receive, channel)
        await client.request_done()

    # Commands available via "/""
    @ client.tree.command(name="chat", description=f'Chat with {bot_name}')
    async def chat(interaction: discord.Interaction, *, message: str, temperature: Optional[str] = None):
        await interaction.response.defer()
        await interaction.delete_original_response()

        prompt = chatbot.get_prompt(bot_name)
        await use_plugin(interaction.user, interaction.channel, message, prompt, response_type='chat', temperature=temperature)

    @ client.tree.command(name="chat_pro", description="Have a custom chat with a system message")
    async def chat_pro_cmd(interaction: discord.Interaction, *, system_message: str, message: str, think: Optional[str] = None, temperature: Optional[str] = None):
        await interaction.response.defer()
        await interaction.delete_original_response()

        chatgpt.update_api_key(
            '../llama.cpp/models/vicuna/7B/ggml-vicuna-7b-4bit-rev1.bin')
        await use_plugin(interaction.user, interaction.channel, message, system_message, response_type='chat', think=think, show_prompt=True, temperature=temperature)
        chatgpt.reset_api_key()

    @ client.tree.command(name="autocomplete", description="Autocomplete your sentence")
    async def autocomplete_cmd(interaction: discord.Interaction, *, prompt: str, stop_on: Optional[str] = None, same_line: bool = False):
        await interaction.response.defer()
        await interaction.delete_original_response()
        await use_plugin(interaction.user, interaction.channel, prompt, prompt, stop=stop_on, same_line=same_line)

    @ client.tree.command(name="ask", description=f"Ask {bot_name} about gpt-llama.cpp ")
    async def ask_cmd(interaction: discord.Interaction, *, question: str):
        await interaction.response.defer()
        await interaction.delete_original_response()

        prompt = gpt_llama_cpp.get_prompt(question, bot_name)
        await use_plugin(interaction.user, interaction.channel, question, prompt, response_type="completion", stop='\n\n', same_line=True)

    @ client.tree.command(name="reddit", description=f"talk about top news of a subreddit")
    async def reddit_cmd(interaction: discord.Interaction, *, subreddit: str):
        await interaction.response.defer()
        await interaction.delete_original_response()

        prompt = reddit_bot.get_prompt(subreddit, interaction.user.name)
        await use_plugin(interaction.user, interaction.channel, subreddit, prompt, response_type="completion", stop='\n\n\n', same_line=True)

    @ client.tree.command(name="google", description=f"google something")
    async def google_cmd(interaction: discord.Interaction, *, question: str):
        await interaction.response.defer()
        await interaction.delete_original_response()
        
        prompt = google.get_prompt(question)
        await use_plugin(interaction.user, interaction.channel, question, prompt, response_type="completion", stop='\n\n', same_line=True)
    
    @ client.tree.command(name="ask_website", description=f"get answers based on a source website")
    async def web_ask_cmd(interaction: discord.Interaction, *, url: str, question: str):
        await interaction.response.defer()
        await interaction.delete_original_response()
        
        prompt = web.get_prompt(url, question)
        await use_plugin(interaction.user, interaction.channel, question, prompt, response_type="completion", stop='\n\n', same_line=True)

    @ client.tree.command(name="debug", description="Debug your error log")
    async def debug_cmd(interaction: discord.Interaction, *, error_message: str):
        await interaction.response.defer()
        await interaction.delete_original_response()
        prompt = error_debugger.get_prompt(error_message)
        await use_plugin(interaction.user, interaction.channel, error_message, prompt, stop='\n\n')

    @ client.tree.command(name="roleplay", description="Roleplay conversation")
    async def rp_cmd(interaction: discord.Interaction, *, character_name: str, persona: str, scenario: str, message: str):
        await interaction.response.defer()
        await interaction.delete_original_response()

        chatgpt.update_api_key(
            '../llama.cpp/models/pygmalion/7B/ggml-model-q5_1.bin')
        prompt = pygmalion.get_prompt(character_name, persona, scenario, message)
        await use_plugin(interaction.user, interaction.channel, message, prompt, temperature=0.95, stop=['You:'])
        chatgpt.reset_api_key()


    # CREATE A DISCORD BOT THAT JOINS CONVERSATIONS RANDOMLY
    @ client.event
    async def on_message(message):
        channel = message.channel

        blacklist = set(['announcements', 'rules', 'changelog', 'help-forum', 'sentient-bots'])
        graylist = set(['bot-spam'])

        # 0.1 = 10% chance of responding if not directly mentioning the bot
        response_probability = 0.05

        # don't react to system message or unreadable messages
        if message.content == '':
            return

        # don't react to your own messages
        if message.author == client.user:
            return

        # don't message in blacklisted channels
        if channel.name in blacklist:
            return

        # respond if addressed
        # if not addressed only respond to 10% of the messages
        r = random.random()
        message.type == "Message"

        bot_mentioned = bot_name.lower() in message.content.lower(
        ) or f'<@{client.user.id}>' in message.content
        is_reply_to_bot = message.reference is not None and message.reference.resolved.author == client.user
        is_graylist = channel.name in graylist

        # if not addressed (always reply when addressed)
        if not (bot_mentioned or is_reply_to_bot):
            # if channel is in graylist, never respond if not mentioned
            if is_graylist:
                return

            # respond randomly to only 'response_probability' of messages
            if r > response_probability:
                return

        print(f'{bot_name} auto-generating a message...')

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
            f"{'DISCORD BOT' if m.content.startswith('🤖') else f'You ({bot_name})' if m.author.name == bot_name else m.author.name} [{m.created_at.strftime('%H:%M:%S %m-%d-%Y')}]:\n{utils.replace_string(m.content, authors_id_to_name)}" for m in message_history)

        prompt = f"""You, {author_names} are users on a public #{message.channel.name} channel of a discord server. You are {bot_name}, an active and fun discord member of the server who's good at coding and is very interested in the recent ai text generation improvements. Each message is formatted in a "<NAME> [DATE]: <MESSAGE>" format, and you guys refer to each other with "@NAME". {bot_name} seems to be very capable at coding and answering questions despite being just human. You guys are having a fun, non-repetitive conversation:

{message_history_str}

You ({bot_name}) [{datetime.now().strftime('%H:%M:%S %m-%d-%Y')}]:"""
        res_message = None
        async with channel.typing():
            await client.request_queued()

            response = await chatgpt.get_text_completion_stream(prompt, '\n\n')
            receive = ''
            queued_chunks = 0
            max_queue_chunks = 7

            async for chunk in response:
                if chunk['choices'][0]['finish_reason']:
                    # response with :no_mouth: if the response failed
                    receive = ':no_mouth:' if len(receive) == 0 else receive
                    break

                curr_chunk = chunk['choices'][0]['delta']['content']
                receive = receive + curr_chunk
                queued_chunks += 1

                if queued_chunks > max_queue_chunks:
                    queued_chunks = 0
                    if len(receive) > 0:
                        res_message = await sender.send_human_message_stream(receive, res_message, channel)

        # send the final message
        await client.request_done()
        await sender.send_human_message_stream(utils.replace_string(receive, authors_name_to_id).lower(), res_message, channel)
        

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
            await use_plugin(message.author, channel, content, prompt, request_message=message, response_type="completion", stop='\n\n', same_line=True)
        elif reaction.emoji == '➕':
            await use_plugin(message.author, channel, message, content, request_message=message)
        elif reaction.emoji == '🐞':
            prompt = error_debugger.get_prompt(content)
            await use_plugin(message.author, channel, content, prompt, request_message=message)
        elif reaction.emoji == '🥜':
            prompt = deez_nuts.get_prompt(content)
            await use_plugin(message.author, channel, content, prompt, request_message=message, temperature=1)



    # TASK LOOPS
    @tasks.loop(seconds=60)
    # sentient bots channel id 1103394781041786980
    
    async def reddit_updates():
        return
        response_probability = 1
        r = random.random()
        if r > response_probability:
            print('Skipping sending sentient message')
            return

        print('Sending sentient message')
        chatgpt.update_api_key('../llama.cpp/models/pygmalion/7B/ggml-model-q5_1.bin')
        channel = await client.fetch_channel(1103394781041786980)
        user = await client.fetch_user(184534707000573952)
        messages = [message async for message in channel.history(limit=2)]
        response_author = messages[1].content.split(': ')[0]
        prompt = await social_agi.get_prompt('ELIZA', 'ALICE', response_author, channel)


        await use_plugin(user, channel, None, prompt, require_request_message=False, temperature=0.9, top_p=1.3, same_line=True, stop='\n', response_prefix=f"{response_author}: ")
        chatgpt.reset_api_key()
        return
        # print('## SEARCHING AND POSTING REDDIT UPDATES')
        # subreddit_list = ['localllama', 'machinelearning', 'chatgpt', 'pygmalionai', 'openai']
        # subreddit = random.choice(subreddit_list)
        # prompt = reddit_bot.get_prompt(subreddit, bot_name)
        # channel = await client.fetch_channel(1099452096383832155)
        # user = await client.fetch_user(184534707000573952)
        # request_message = await sender.send_message(f'**Time to check out `r/{subreddit}` for news!**', channel)
        # await use_plugin(user, channel, subreddit, prompt, response_type="completion", request_message=request_message, stop='\n\n\n', same_line=True)

    # On bot ready
    @client.event
    async def on_ready():
        reddit_updates.start()
        await client.sync()
        print("Bot ready.")
    

    client.run(os.getenv('DISCORD_TOKEN'))


if __name__ == '__main__':
    keep_alive()
    run()
