from logging import Logger
import requests
import os
from dotenv import load_dotenv
import json
from .exceptions import SummonerNotFoundError, RiotApiError, RateLimitError
from logger import setup_logger

load_dotenv()

logger = setup_logger('lol.lol_requests')

class LolRequests:

    REGION = 'europe'

    def __init__(self):
        self.api_key = os.getenv('LOL_API_KEY')
        
    def get_puuid(self, summoner_name: str, tag: str)->str:
        url = f"https://{self.REGION}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{tag}"
        response = requests.get(url, headers={'X-Riot-Token': self.api_key})
        if response.status_code == 200:
            return response.json()['puuid']
        elif response.status_code == 404:
            logger.warning(f'Summoner name not found: {summoner_name}#{tag}')
            raise SummonerNotFoundError(f'Summoner name not found: {summoner_name}#{tag}')
        elif response.status_code == 429:
            raise RateLimitError('Rate limit has reached')
        else:
            raise RiotApiError(f'API hiba: {response.status_code}')
        
    def get_match_history(self, puuid)->list:
        url = f"https://{self.REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
        response = requests.get(url, headers={'X-Riot-Token': self.api_key})
        return response.json()
    
    def get_match_details(self, match_id)->dict:
        url = f"https://{self.REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}"
        response = requests.get(url, headers={'X-Riot-Token': self.api_key})
        return response.json()
    
    
    
    def get_active_game(self, puuid: int)->dict:

        url:str = f"https://{self.REGION}.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{puuid}"
        response = requests.get(url, headers={'X-Riot-Token': self.api_key})
        if response.status_code == 200:
            return response.json()
        else:
            print(f'Jelenleg nincs aktív játék')
            return None
         
