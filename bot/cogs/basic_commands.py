from discord.ext import commands
from lol import lol_requests
from lol.lol_requests import LolRequests
import json

class BasicCommands(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        super().__init__()

    @commands.command(name="lol")
    async def lol(self, ctx, *, arg):
        puuid: str = LolRequests().get_puuid(arg)
        match_history: list = LolRequests().get_match_history(puuid)
        for match_id in match_history:
            match_details: dict = LolRequests().get_match_details(match_id)
            await ctx.send(match_details)

    @commands.command(name="sumpuuid")
    async def get_sum_puuid_by_name(self, ctx, arg):
        get_puuid = lol_requests.LolRequests()
        await ctx.send(get_puuid.get_puuid(arg))

    @commands.command(name="summoner")
    async def summoner(self, ctx, *, arg):
        guild_id = str(ctx.guild.id)
        puuid: str = LolRequests().get_puuid(arg)

        try:
            with open('data/summoner_names.json', 'r') as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

        # Create nested structure if it doesn't exist
        if guild_id not in data:
            data[guild_id] = {}
        
        
        # Update summoner name
        data[guild_id][arg] = puuid
        with open('data/summoner_names.json', 'w') as file:
            json.dump(data, file)
        await ctx.send(f'Summoner name {arg} added to the database')

    @commands.command(name="summoners")
    async def get_registered_summoners_list(self, ctx):
        with open('data/summoner_names.json') as file:
            print(file.read())

async def setup(bot):
    await bot.add_cog(BasicCommands(bot))