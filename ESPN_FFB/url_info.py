import datetime
import os
from multiprocessing import Pool
from sys import exc_info
import requests
from ESPN_FFB.league_info import LeagueInfo

class URLInfo:

    def __init__(self, view: str, league_info: LeagueInfo):
        self.urls = self._get_urls(league_info)
        self.view = view

        cookies = self._get_cookies()
        self.swid = cookies[0].strip()
        self.espn_s2 = cookies[1].strip()

    def _get_cookies(self) -> list:
        current_directory = os.path.dirname(os.path.abspath(__file__))
        cookie_file = os.path.join(current_directory, 'cookies.txt')
        try:
            open_cookie_file = open(cookie_file, "r")
            cookies = open_cookie_file.readlines()
            open_cookie_file.close()
        except:
            raise Exception(f'Unable to open cookie file. Reported error: {exc_info()[0]}')
        return cookies

    def _get_urls(self, league_info: LeagueInfo, year: int = datetime.datetime.now().year) -> list:
        """ Returns list of URLs for ESPNs fantasy football APIs.
        Will create one URL per year, starting from the passed in year
        until the first season of the league.

        If no year is supplied, will start at the current year.
        """
        urls = list()
        if year < league_info.first_year:
            return urls

        if _is_year_active(year) is False:
            year -= 1
        while year >= league_info.first_year:
            if len(urls) < 2: #Adding this check because 2 years currently use active url
                urls.append(self._construct_url_current(league_info.league_id, year))
            else:
                urls.append(self._construct_url_historical(league_info.league_id, year))
            year -= 1
        return urls

    def _construct_url_current(self, league_id: int, year: int) -> str:
        """
            Constructs "active" URLs for ESPN fantasy football.
            Active URLs appear to be used for the last 2 seasons.
        """
        return "http://fantasy.espn.com/apis/v3/games/ffl/seasons" \
        f"/{year}/segments/0/leagues/{league_id}"

    def _construct_url_historical(self, league_id: int, year: int) -> str:
        """
            Constructs "historical" URLs for ESPN fantasy football.
            Historical URLs appear to be used for seasons more than 2 years back.
        """
        return "https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory" \
            f"/{league_id}?seasonId={year}"

    def get_formatted_espn_data(self):
        responses, all_requests_successful = self._request_espn_data()
        parsed_response = list()
        for response in responses:
            if 'leagueHistory' in response.url:
                response = response.json()[0]
            else:
                response = response.json()
            parsed_response.append(response)

        return parsed_response, all_requests_successful

    def _request_espn_data(self):
        success = True
        process_pool = Pool()
        try:
            responses = process_pool.map(self._get_single_espn_response, self.urls)
        except requests.exceptions.ConnectionError:
            success = False
        return responses, success

    def _get_single_espn_response(self, url: str) -> list:
        response = requests.get(
            url,
            params={"view": self.view},
            cookies={"SWID": self.swid,
                     "espn_s2": self.espn_s2})
        return response

def _is_year_active(year: int) -> bool:
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

    return _is_september_date_after_nfl_start(current_date)

def _is_september_date_after_nfl_start(date: datetime.date):
    day = date.day
    if day < 13:
        first_monday = _get_first_september_monday(date.year)
        if first_monday + 6 > day:
            return False
    return True

def _get_first_september_monday(year: int):
    for day in range(1, 8):
        date = datetime.date(year, 9, day)
        if date.weekday() == 0: #Monday == 0
            return day
