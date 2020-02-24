import unittest
import os
import datetime
import json
import main
from ESPN_FFB.url_info import URLInfo
from ESPN_FFB.league_info import LeagueInfo

def get_sample_json():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    open_file = open(os.path.join(current_directory, "sampleJSON.txt"))
    sample_json = json.load(open_file)
    open_file.close()
    return sample_json

class ApplicationWindowTests(unittest.TestCase):

    def setUp(self):
        self.league_info = LeagueInfo()
        self.league_info.cached_json = get_sample_json()

    def test_sample_JSON_exists(self):
        self.assertGreater(len(self.league_info.cached_json), 0)

    def test_clear_cache(self):
        main.FFB.on_click_clear_cache_button(self.league_info)
        self.assertFalse(self.league_info.cached_json) #Empty list = false

        #Rebuild
        self.league_info.cached_json = get_sample_json()

    def test_url_info(self):
        #TODO: Add check for current year
        view = "mTeam"
        league_id = 368182
        first_season = 2014
        # current_year = datetime.datetime.now().year
        current_directory = os.path.dirname(os.path.abspath(__file__))
        parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
        print(parent_directory)
        cookie_file = os.path.join(parent_directory, 'ESPN_FFB\\cookies.txt')
        url_info = URLInfo(view, self.league_info)

        first_season_url_expected = "https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory" \
                                    f"/{league_id}?seasonId={first_season}"

        url_count = len(url_info.urls)
        self.assertEqual(first_season_url_expected, url_info.urls[url_count - 1])

if __name__ == "__main__":
    unittest.main()
