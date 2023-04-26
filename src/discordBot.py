import discord
from src.logger import logger

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

model_name = 'Vicuna 7B'


class DiscordClient(discord.Client):
    def __init__(self) -> None:
        super().__init__(intents=intents)
        self.synced = False
        self.added = False
        self.tree = discord.app_commands.CommandTree(self)
        self.activity = discord.Activity(
            type=discord.ActivityType.watching, name="/chat | 🦙 react | /chat-advanced")

    async def on_ready(self):
        await self.wait_until_ready()
        logger.info("Syncing")
        if not self.synced:
            await self.tree.sync()
            self.synced = True
        if not self.added:
            self.added = True
        logger.info(f"Synced, {self.user} is running!")


class Sender():
    async def send_message(self, interaction, send, receive, system_message=None, think=None, hide_system_thoughts=False):
        try:
            user_id = interaction.user.id
            system_msg = '' if hide_system_thoughts or system_message is None else f'> _**SYSTEM**: {system_message}_\n> \n'
            think_msg = '' if hide_system_thoughts or think is None else f'> _[@EVA thinking: {think}]_\n> \n'
            query = f'> <@{str(user_id)}>:  _{send}_\n\n'
            response = f'**@EVA:**\n{receive}\n\n~~-                              -~~\n_Start a chat yourself by reacting to a message with 🦙 or typing /chat\nDisclaimer: Responses may not be accurate (Running {model_name})_'
            await interaction.followup.send(system_msg + query + think_msg + response)
            logger.info(f"{user_id} sent: {send}, response: {receive}")
        except Exception as e:
            await interaction.followup.send('> **Error: Something went wrong, please try again later!**')
            logger.exception(
                f"Error while sending:{send} in chatgpt model, error: {e}")

    async def reply_message(self, message, receive, pending_message):
        try:
            response = f'{receive}\n~~-                              -~~\n_Start a chat yourself by reacting to a message with 🦙 or typing /chat\nDisclaimer: Responses may not be accurate (Running 1.1 Vicuna 7B)_'
            await pending_message.delete()
            await message.reply(response)
            logger.info(f"message replied sent: {receive}")
        except Exception as e:
            await message.reply('> **Error: Something went wrong, please try again later!**')
            logger.exception(
                f"Error while replying to message in chatgpt model, error: {e}")

    async def send_image(self, interaction, send, receive):
        try:
            user_id = interaction.user.id
            response = f'> **{send}** - <@{str(user_id)}> \n\n'
            await interaction.followup.send(response)
            await interaction.followup.send(receive)
            logger.info(f"{user_id} sent: {send}, response: {receive}")
        except Exception as e:
            await interaction.followup.send('> **Error: Something went wrong, please try again later!**')
            logger.exception(
                f"Error while sending:{send} in dalle model, error: {e}")
