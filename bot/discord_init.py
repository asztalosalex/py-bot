import discord
import os
from dotenv import load_dotenv
from discord.ext import commands

class DiscordBot(commands.Bot):

    def __init__(self):
        load_dotenv()
        self.token = os.getenv('DC_TOKEN')
        if not self.token:
            raise ValueError("No DC_TOKEN found in")
        
        print("Initializing bot...")
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents, description='test')


    async def on_ready(self):
        print(f'Successfully logged in as {self.user}')
        print(f'Bot ID: {self.user.id}')
        print('Connected to guilds:')
        for guild in self.guilds:
            print(f'- {guild.name} (ID: {guild.id})')
        print('Bot is ready for commands!')

    
def run_bot():
    bot = DiscordBot()
    bot.run(bot.token)

run_bot()