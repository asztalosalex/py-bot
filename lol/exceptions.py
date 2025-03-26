class SummonerNotFoundError(Exception):
    """Raised when a summoner cannot be found."""
    pass

class RateLimitError(Exception):
    """Raised when the Riot API rate limit is exceeded."""
    pass

class RiotApiError(Exception):
    """Raised when a general Riot API error occurs."""
    def __init__(self, message, status_code=None):
        self.status_code = status_code
        super().__init__(message)