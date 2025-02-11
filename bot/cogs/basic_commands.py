from discord.ext import commands
from lol.lol_requests import LolRequests
import json

class BasicCommands(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        super().__init__()

    @commands.command(name="test")
    async def test(self, ctx, *, arg):
        await ctx.send(arg)

    @commands.command(name="ping")
    async def ping(self, ctx):
        await ctx.send('pong')


    @commands.command(name="lol")
    async def lol(self, ctx, *, arg):
        puuid: str = LolRequests().get_puuid(arg)
        match_history: list = LolRequests().get_match_history(puuid)
        for match_id in match_history:
            match_details: dict = LolRequests().get_match_details(match_id)
            await ctx.send(match_details)

    @commands.command(name="summoner")
    async def summoner(self, ctx, *, arg):
        guild_id = str(ctx.guild.id)
        member_id = str(ctx.author.id)

        try:
            with open('data/summoner_names.json', 'r') as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

        # Create nested structure if it doesn't exist
        if guild_id not in data:
            data[guild_id] = {}
        if member_id not in data[guild_id]:
            data[guild_id][member_id] = {}
        
        # Update summoner name
        data[guild_id][member_id]['summoner_name'] = arg

        with open('data/summoner_names.json', 'w') as file:
            json.dump(data, file)
        await ctx.send(f'Summoner name {arg} added to the database')

async def setup(bot):
    await bot.add_cog(BasicCommands(bot))