from discord.ext import commands
from idna import encode
from lol import lol_requests
from lol.exceptions import RateLimitError, RiotApiError, SummonerNotFoundError
from lol.lol_requests import LolRequests
import json
from urllib.parse import quote
from lol.data_manager import DataManager

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

   
    #TODO: MAKE JSON IF NOT EXISTS
    @commands.command(name="summoner", help="Add a summoner name to the database")
    async def summoner(self, ctx, *, summoner_name_and_tag: str):
        try:
            summoner_name, tag = summoner_name_and_tag.split('#')
            clean_name= summoner_name.strip('"')
            clean_tag = tag.strip('"')
            encoded_summoner_name = quote(clean_name)
            encoded_tag = quote(clean_tag)
            guild_id = str(ctx.guild.id)
            member_id = str(ctx.author.id)
            puuid: str = ''
            puuid = LolRequests().get_puuid(encoded_summoner_name, encoded_tag)
            
            try:
                with open('data/summoner_names.json', 'r') as file:
                    data = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                print('File not found')
                data = {}

            # Create nested structure if it doesn't exist
            if guild_id not in data:
                data[guild_id] = {}
            if member_id not in data[guild_id]:
                data[guild_id][member_id] = {}
            
            # Check if summoner name is already in the database
            if f'{clean_name}#{clean_tag}' in data[guild_id][member_id]:
                await ctx.send(f'Summoner name {summoner_name} is already in the database')
                return
            
            # Update summoner name
            data[guild_id][member_id][f'{clean_name}#{clean_tag}'] = puuid
            with open('data/summoner_names.json', 'w') as file:
                json.dump(data, file)
            await ctx.send(f'Summoner name {summoner_name} added to the database')
            
        except ValueError:
            await ctx.send('Helytelen parancs változó. Helyes formátum: !summoner "summonername#tag"')
        except SummonerNotFoundError:
                await ctx.send(f'A megadott felhasználó nem található: {summoner_name_and_tag}')
        except RateLimitError:
            await ctx.send('Túl sok kérés érkezett az API-hoz. Próbáld később')
        except RiotApiError as e:
            await ctx.send(f'Riot API hiba: {str(e)}')

        
    @commands.command(name="summoners")
    async def get_registered_summoners_list(self, ctx):
        with open('data/summoner_names.json') as file:
            print(file.read())

async def setup(bot):
    await bot.add_cog(BasicCommands(bot))