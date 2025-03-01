from dotenv import load_dotenv
import os
import requests

load_dotenv()

FCS_URL = "https://fcsapi.com/api-v3/forex/latest"
SYMBOLS = "EUR/HUF,USD/HUF,GBP/HUF"

class FcsApi:
    def __init__(self) -> None:
        self.base_url = os.getenv('FCS_API_BASE_URL')


    def get_forex_data(self):
        params = {
            'symbol': SYMBOLS,
            'access_key': os.getenv('FCSAPI')
        }

        response = requests.get(FCS_URL, params=params)
        response.raise_for_status()
        if response.status_code != 200:
            return f'Error: {response.status_code}'
        else:
            return response.json()
        
