
import os

from dotenv import load_dotenv
import discord
from typing import Optional

from src.discordBot import DiscordClient, Sender
from src.logger import logger
from src.chatgpt import ChatGPT, DALLE
from src.models import OpenAIModel
from src.memory import Memory
from src.server import keep_alive

load_dotenv()

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
    personalities = {
        'deez_nuts': {'system_message': 'Respond to each user message with a deez nuts joke. A deez nuts joke is when you reply and rephrase the original statement the user made, but add the words DEEZ NUTZ in itas a response to confuse the user and be funny',
                      'think': 'This is a perfect opportunity to respond with a "deez nuts" joke as instructed. Here comes my response..'}
    }

    @client.tree.command(name="chat", description="Have a chat with EVA")
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
        deez_nuts = personalities['deez_nuts']
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
        if reaction.emoji == '🦙':
            message = reaction.message
            content = message.content  # username: user.name
            pending_message = await message.reply('_EVA is typing..._')
            receive = await chatgpt.get_response(content)
            await sender.reply_message(message, receive, pending_message)

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
