
import os

from dotenv import load_dotenv
load_dotenv()

import discord
from typing import Optional

from src.discordBot import DiscordClient, Sender
from src.logger import logger
from src.chatgpt import ChatGPT, DALLE
from src.models import OpenAIModel
from src.memory import Memory
from src.server import keep_alive

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
            user_id, system_message, message, think)
        await sender.send_message(interaction, message, receive, system_message, think, hide_system_thoughts)

    # Personalities
    plugins = {
        'deez_nuts': {'system_message': 'Respond to each user message with a deez nuts joke. A deez nuts joke is when you rephrase the original message by adding the words DEEZ NUTZ in it. The response is intended to confused the user and be funny. For example, user message "can you hold this for me" could have a assistant response of "can you hold on deez nuts for me", because telling the user to hold "deez nutz" instead of "this" is funny',
                      'think': 'This is a perfect opportunity to respond with a funny "deez nuts" joke... here comes the delivery..'},
        'discord_user': {'system_message': 'You are to act like a polite & respectful human discord user in a discord channel. Nobody knows you are a bot. You are currently in a discord server called gpt-llama.cpp. User messages arent directed to you specifically, but contribute to the conversation based on the messages context clues. This is not your first message nor your first day in the discord channel. Make sure your responses are short and less than 180 characters like a tweet. Make your responses look like it was 90% written by a human by using more sentence variation and burstiness. For example, "lol fixed a bug, introduced two bugs" could have a response of "i know right, its such a struggle" because you are relating to the original message',
                      'think': 'this was not addressed to me specifically, but I let me contribute to this public conversation...'}
    }

    @client.tree.command(name="chat", description=f'Have a chat with {bot_name}')
    async def chat(interaction: discord.Interaction, *, message: str):
        user_id = interaction.user.id  # username: interaction.user.name
        if interaction.user == client.user:
            return
        await interaction.response.defer()
        receive = await chatgpt.get_response(
            user_id, message)
        await sender.send_message(interaction, message, receive)

    @client.tree.command(name="chat_advanced", description="Have a custom chat with a system message")
    async def system_cmd(interaction: discord.Interaction, *, system_message: str, message: str, think: Optional[str] = None):
        await system_chat(interaction, system_message, message, think)

    @client.tree.command(name="deez_nuts", description="Hit them with a deez nuts joke")
    async def deez_chat(interaction: discord.Interaction, *, message: str):
        deez_nuts = plugins['deez_nuts']
        await system_chat(interaction, deez_nuts['system_message'], message, deez_nuts['think'], True)

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
    async def on_reaction_add(reaction, user):
        message = reaction.message
        content = message.content  # username: user.name
        if reaction.emoji == '🦙':
            pending_message = await message.reply(f'🦙 _{bot_name} is typing..._')
            receive = await chatgpt.get_response(user.id, content)
            await sender.reply_message(message, receive, pending_message)
            return
        if reaction.emoji == '🥜':
            pending_message = await message.reply(f'🥜 _{bot_name} is typing..._')
            plug = plugins['deez_nuts']
            receive = await chatgpt.get_response_with_system(user.id, plug['system_message'], content, plug['think'])
            await sender.reply_message(message, receive, pending_message)
            return
        if reaction.emoji == '🤖':
            pending_message = await message.reply(f'🤖 _{bot_name} is typing..._')
            plug = plugins['discord_user']
            receive = await chatgpt.get_response_with_system(user.id, plug['system_message'], content, plug['think'])
            await sender.reply_message(message, receive.lower(), pending_message)
            return


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
