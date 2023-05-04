import os
import discord
import random

from src.logger import logger

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

class DiscordClient(discord.Client):
    def __init__(self) -> None:
        super().__init__(intents=intents)
        self.synced = False
        self.added = False
        self.tree = discord.app_commands.CommandTree(self)
        self.requestQueue = 0
        self.activity = discord.Activity(
            type=discord.ActivityType.streaming, name=f"{self.requestQueue} requests")

    async def sync(self):
        await self.wait_until_ready()
        logger.info("Syncing")
        if not self.synced:
            await self.tree.sync()
            self.synced = True
        if not self.added:
            self.added = True
        logger.info(f"Synced, {self.user} is running!")

    async def request_queued(self):
        self.requestQueue += 1
        self.activity = discord.Activity(
            type=discord.ActivityType.streaming, name=f"{self.requestQueue} requests")
        await super().change_presence(activity=self.activity)
        
    async def request_done(self):
        self.requestQueue -= 1
        self.activity = discord.Activity(
            type=discord.ActivityType.streaming, name=f"{self.requestQueue} requests")
        await super().change_presence(activity=self.activity)


class Sender():
    bot_name = os.getenv('BOT_NAME')
    model_name = os.getenv('MODEL_NAME')
            
    async def send_message(self, receive, text_channel, **kwargs):
        try:
            no_think = 'think' not in kwargs or not kwargs['think']
            think_msg = '' if no_think else f'\n> ||_@{self.bot_name} thinking: {kwargs["think"]}_||'
            return await text_channel.send(content=receive + think_msg, tts=True)
        except Exception as e:
            await text_channel.send('> **Error: Something went wrong, please try again later!**')
            logger.exception(
                f"Error while replying to message in chatgpt model, error: {e}")
            
    async def send_human_message_stream(self, receive, message, channel):
        try:
            print('send stream: ', receive)
            if message is None:
                res_message = await self.send_message(receive, channel)
                return res_message
            else:
                await message.edit(content=receive)
                return message
        except Exception as e:
            await message.edit('> **Error: Something went wrong, please try again later!**')
            logger.exception(
                f"Error while replying to message in chatgpt model, error: {e}")
            return message

    async def reply_message(self, message, receive, pending_message=None):
        try:
            response = f'{receive}'
            tagline = f'\n\n_Start a chat yourself by reacting with 🤖/🦙 or typing `/chat`\nDisclaimer: Responses may not be accurate (Running {self.model_name})_'
            if random.random() < 0.1:
                response = response + tagline
            if not pending_message is None:
                await pending_message.delete() 
            await message.reply('🤖\n' + response)
                
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
