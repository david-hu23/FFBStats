import unittest
import os
import datetime
import json
import main
from ESPN_FFB.URLInfo import URLInfo

def get_sample_JSON():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    open_file = open(os.path.join(current_directory, "sampleJSON.txt"))
    JSON = json.load(open_file)
    open_file.close()
    return JSON

class ApplicationWindowTests(unittest.TestCase):

    def setUp(self):
        self.sample_json = get_sample_JSON()

    def test_sample_JSON_exists(self):
        self.assertGreater(len(self.sample_json), 0)

    def test_clear_cache(self):
        main.FFB.on_click_clear_cache_button(self.sample_json)
        self.assertFalse(self.sample_json) #Empty list = false

        #Rebuild
        self.sample_json = get_sample_JSON()

    def test_url_info(self):
        #TODO: Add check for current year
        view = "mTeam"
        league_id=368182
        first_season=2014
        # current_year = datetime.datetime.now().year
        current_directory = os.path.dirname(os.path.abspath(__file__))
        parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
        print(parent_directory)
        cookie_file = os.path.join(parent_directory, 'ESPN_FFB\\cookies.txt')
        url_info = URLInfo(view, cookie_file, league_id, first_season)

        first_season_url_expected = "https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory" \
                                    f"/{league_id}?seasonId={first_season}"

        url_count = len(url_info.urls)
        self.assertEqual(first_season_url_expected, url_info.urls[url_count - 1])

if __name__ == "__main__":
    unittest.main()
