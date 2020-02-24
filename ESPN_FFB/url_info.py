import datetime
import os
from sys import exc_info
from ESPN_FFB.league_info import LeagueInfo

class URLInfo:

    def __init__(self, view: str, league_info: LeagueInfo):
        self.urls = self.get_urls(league_info)
        self.view = view

        cookies = self.get_cookies()
        self.SWID = cookies[0].strip()
        self.espn_s2 = cookies[1].strip()

    def get_cookies(self) -> list:
        current_directory = os.path.dirname(os.path.abspath(__file__))
        cookie_file = os.path.join(current_directory, 'cookies.txt')
        try:
            open_cookie_file = open(cookie_file, "r")
            cookies = open_cookie_file.readlines()
            open_cookie_file.close()
        except:
            print("Unable to open cookie file.")
            print(exc_info()[0])
        return cookies

    def get_urls(self, league_info: LeagueInfo, year: int = datetime.datetime.now().year) -> list:
        """ Returns list of URLs for ESPNs fantasy football APIs.
        Will create one URL per year, starting from the passed in year
        until the first season of the league.

        If no year is supplied, will start at the current year.
        """
        urls = list()
        if year < league_info.first_year:
            return urls

        if self.is_year_active(year) is False:
            year -= 1
        while year >= league_info.first_year:
            if len(urls) < 2: #Adding this check because 2 years currently use active url
                urls.append(self.construct_url_current(league_info.league_id, year))
            else:
                urls.append(self.construct_url_historical(league_info.league_id, year))
            year -= 1
        return urls

    def is_year_active(self, year: int) -> bool:
        """ NFL seasons start the weekend after the first Monday of September.
        Reference: https://en.wikipedia.org/wiki/NFL_regular_season
        """
        current_date = datetime.date.today()
        if year < current_date.year:
            return True

        if current_date.month != 9:
            if current_date.month < 9:
                return False
            else:
                return True
        #Check if we've reached the first Monday of September
        current_day = current_date.day
        if current_day < 7:
            current_weekday = current_date.weekday() #Monday == 0
            if current_day - current_weekday < 0:
                return False
        return True

    def construct_url_current(self, league_id: int, seasonId: int) -> str:
        """
            Constructs "active" URLs for ESPN fantasy football.
            Active URLs appear to be used for the last 2 seasons.
        """
        return "http://fantasy.espn.com/apis/v3/games/ffl/seasons" \
        f"/{seasonId}/segments/0/leagues/{league_id}"

    def construct_url_historical(self, league_id: int, seasonId: int) -> str:
        """
            Constructs "historical" URLs for ESPN fantasy football.
            Historical URLs appear to be used for seasons more than 2 years back.
        """
        return "https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory" \
            f"/{league_id}?seasonId={seasonId}"
