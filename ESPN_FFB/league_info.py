class LeagueInfo:

    def __init__(self, league_id: int = 368182, first_year: int = 2014):
        self.cached_json = list()
        self.league_id = league_id
        self.first_year = first_year

    def set_league(self, league_id: int, first_year: int):
        self.cached_json = list()
        self.league_id = league_id
        self.first_year = first_year

    def clear_cache(self):
        self.cached_json.clear()

    def is_cache_empty(self):
        return len(self.cached_json) == 0