
import os

from dotenv import load_dotenv
import discord

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

    @client.tree.command(name="chat", description="Have a chat with EVA")
    async def chat(interaction: discord.Interaction, *, message: str):
        user_id = interaction.user.id # username: interaction.user.name
        if interaction.user == client.user:
            return
        await interaction.response.defer()
        receive = await chatgpt.get_response(
            user_id, message)
        await sender.send_message(interaction, message, receive)

    @client.tree.command(name="chat_advanced", description="Have a custom chat with a system message")
    async def chat(interaction: discord.Interaction, *, system_message: str, message: str):
        user_id = interaction.user.id # username: interaction.user.name
        if interaction.user == client.user:
            return
        chatgpt.clean_history(user_id)
        await interaction.response.defer()
        receive = await chatgpt.get_response_with_system(
            user_id, system_message, message)
        await sender.send_message(interaction, message, receive, system_message)

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
            content = message.content
            pending_message = await message.reply('_EVA is typing..._')
            receive = await chatgpt.get_response(
                user.id, 'My name is "' + user.name + '". ' + content)
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
