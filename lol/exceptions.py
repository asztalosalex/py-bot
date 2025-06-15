class SummonerNotFoundError(Exception):

    pass

class RateLimitError(Exception):

    pass

class RiotApiError(Exception):

    def __init__(self, message, status_code=None):
        self.status_code = status_code
        super().__init__(message)