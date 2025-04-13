import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from lol.lol_requests import LolRequests

class DiscordBot(commands.Bot):

    def __init__(self):
        load_dotenv()
        self.token = os.getenv('DC_TOKEN')
        if not self.token:
            raise ValueError("No DC_TOKEN found in")

        print("Initializing bot...")
        intents = discord.Intents.default()
        intents.message_content = True
        intents.presences = True
        intents.members = True
        super().__init__(command_prefix='!', intents=intents, description='pybot')
        self.bot = self.run_bot()

    async def setup_hook(self):
        """This is called when the bot starts up"""
        await self.load_extension('bot.cogs.basic_commands')
        await self.load_extension('bot.cogs.ai_handler')


    async def on_guild_channel_update(self, before, after):
        print(f'Channel {before.name} updated to {after.name}')

    async def on_presence_update(self, before, after):

        if before.activity is None and after.activity is not None:
            await self.get_channel(1201609666099150980).send(f'{after.name} started playing {after.activity.name}')

        elif before.activity is not None and after.activity is None:
            await self.get_channel(1201609666099150980).send(f'{after.name} stopped playing {before.activity.name}')

        elif (before.activity and after.activity and
              before.activity.details != after.activity.details and
              after.activity.details is not None):
            lol_requests = LolRequests()
            summoner_name: str = lol_requests.get_summoner_name_by_member_id(after.id)
            puuid: int = lol_requests.get_puuid(summoner_name=summoner_name)
            active_game = lol_requests.get_active_game(puuid=puuid)

            await self.get_channel(1201609666099150980).send(
                f'{after.id} - {after.name} is now playing {after.activity.name} - {after.activity.details}\n Game details{active_game}'
            )


    async def on_ready(self):
        print(f'Successfully logged in as {self.user}')
        print(f'Bot ID: {self.user.id}')
        print('Bot is connected servers below:')
        for guild in self.guilds:
            print(f'- {guild.name} (ID: {guild.id})')
        print('Bot is ready for commands!')
        await self.get_channel(1201609666099150980).send('Jó napot!')


    def run_bot(self):
        self.run(self.token)
