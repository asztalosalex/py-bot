import json

class DataManager:
    def __init__(self):
        self.file_path = 'data/summoner_names.json'

    def get_summoner_name_by_member_id(self, guild_id: str, member_id: int) -> str:
        """Get summoner name from database by guild ID and member ID."""
        with open(self.file_path, 'r') as f:
            data = json.load(f)

            try:
                member_data = data[str(guild_id)][str(member_id)]
                return list(member_data.keys())[0]
            except KeyError:
                raise Exception(f'No summoner name found for the Guild ID: {guild_id} and member ID: {member_id}')

    def load_data(self) -> dict[str, dict[str, dict[str, str]]]:
        """Load all data from the JSON file."""
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_data(self, data: dict[str, str]) -> None:
        """Save data to the JSON file."""
        with open(self.file_path, 'w+') as f:
            json.dump(data, f, indent=4)