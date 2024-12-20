import discord
import os
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DC_TOKEN')

class MyClient(discord.Client):

    def __init__(self, *, intents, **options):
        super().__init__(intents=intents, **options)
        self.GUILD_ID = None
        self.on_ready()


    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        print(f'Bot is ready!')

        for guild in bot.guilds:
            print(f'{bot.user} is connected to the following guild:\n'
                  f'{guild.name}(id: {guild.id})')
            self.GUILD_ID = guild.id

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')
        
        if message.content == 'ping':
            await message.channel.send('pong')

      

intents = discord.Intents.default()
intents.message_content = True
bot = MyClient(intents=intents)

bot = MyClient(intents=intents)
bot.run(TOKEN)
