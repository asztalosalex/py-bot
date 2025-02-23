import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

class LolRequests:

    REGION = 'europe'

    def __init__(self):
        self.api_key = os.getenv('LOL_API_KEY')
        
    def get_puuid(self, summoner_name: str, tag: str)->str:
        url = f"https://{self.REGION}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{tag}"
        response = requests.get(url, headers={'X-Riot-Token': self.api_key})
        if response.status_code == 200:
            return response.json()['puuid']
        else:
            raise Exception(f"Failed to fetch PUUID for {summoner_name}. \n Status code is: {response.status_code}\n Request url: {url}")
        
    def get_match_history(self, puuid)->list:
        url = f"https://{self.REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
        response = requests.get(url, headers={'X-Riot-Token': self.api_key})
        return response.json()
    
    def get_match_details(self, match_id)->dict:
        url = f"https://{self.REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}"
        response = requests.get(url, headers={'X-Riot-Token': self.api_key})
        return response.json()
    
    def get_summoner_name_by_member_id(guild_id: str, member_id: int) -> str:
        with open ('data/summoner_names.json', 'r') as f:
            data = json.load(f)

            try:
                return data[str(guild_id)][str(member_id)]['summoner_name']
            except KeyError:
                raise Exception(f'No summoner name found for the Guild ID: {guild_id} and member ID: {member_id}')
    
    def get_active_game(self, puuid: int)->dict:

        url:str = f"https://{self.REGION}.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{puuid}"
        response = requests.get(url, headers={'X-Riot-Token': self.api_key})
        if response.status_code == 200:
            return response.json()
        else:
            print(f'Jelenleg nincs aktív játék')
            return None
         
