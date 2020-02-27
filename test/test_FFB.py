import unittest
import os
import datetime
import json
import main
from ESPN_FFB.axes_labels import AxesLabels
from ESPN_FFB.url_info import URLInfo, _is_year_active, _is_september_date_after_nfl_start
from ESPN_FFB.league_info import LeagueInfo
from ESPN_FFB.constants import STATS_TAGS, AXES_LABELS, ESPN_ID_TO_TEAM
from ESPN_FFB.figure_options import FIGURE_OPTIONS

def get_sample_json():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    open_file = open(os.path.join(current_directory, "sampleData.json"))
    sample_json = list()
    sample_json.append(json.load(open_file))
    open_file.close()
    return sample_json

class ApplicationWindowTests(unittest.TestCase):

    def setUp(self):
        self.league_info = LeagueInfo()
        self.league_info.cached_responses = get_sample_json()

    def test_sample_json_exists(self):
        self.assertGreater(len(self.league_info.cached_responses), 0)

    def test_clear_cache(self):
        main.FFB.on_click_clear_cache_button(self.league_info)
        self.assertFalse(self.league_info.cached_responses) #Empty list = false

        #Rebuild
        self.league_info.cached_responses = get_sample_json()

    def test_record_figure_heights(self):
        for figure_option in range(0, 2):
            figure_heights = self.league_info.get_figure_heights(figure_option)
            for team in ESPN_ID_TO_TEAM:
                self.assertEqual(
                    len(figure_heights[team - 1]), 3,
                    "League info is not returning the right number " \
                    "of bar heights for Record figures.")

        for figure_option in range(2, 4):
            figure_heights = self.league_info.get_figure_heights(figure_option)
            for team in ESPN_ID_TO_TEAM:
                self.assertEqual(
                    len(figure_heights[team - 1]), 2,
                    "League info is not returning the right number " \
                    "of bar heights for Points figures.")

    def test_axes_labels(self):
        raw_data_figures = [FIGURE_OPTIONS.get(0), FIGURE_OPTIONS.get(1)]
        season_adjusted_figures = [FIGURE_OPTIONS.get(2), FIGURE_OPTIONS.get(3)]

        for figure_option in raw_data_figures:
            axes_labels = AxesLabels(figure_option)
            self.assert_axes_labels_not_none(axes_labels)

            self.assertEqual(axes_labels.x_labels, [
                STATS_TAGS.get(0), STATS_TAGS.get(1), STATS_TAGS.get(2)])
            self.assertIn(axes_labels.y_label, [AXES_LABELS.get(2), AXES_LABELS.get(0)])

        for figure_option in season_adjusted_figures:
            axes_labels = AxesLabels(figure_option)
            self.assert_axes_labels_not_none(axes_labels)

            self.assertEqual(axes_labels.x_labels, [STATS_TAGS.get(3), STATS_TAGS.get(4)])
            self.assertEqual(axes_labels.y_label, AXES_LABELS.get(1))

        axes_labels = AxesLabels(-1)
        self.assertIsNone(axes_labels.x_labels)
        self.assertIsNone(axes_labels.y_label)

    def assert_axes_labels_not_none(self, axes_labels: AxesLabels):
        self.assertIsNotNone(axes_labels.x_labels)
        self.assertIsNotNone(axes_labels.y_label)

    def test_url_info(self):
        view = "mTeam"
        league_id = 368182
        first_season = 2014
        current_directory = os.path.dirname(os.path.abspath(__file__))
        parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
        print(parent_directory)
        url_info = URLInfo(view, self.league_info)

        first_season_url_expected = "https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory" \
                                    f"/{league_id}?seasonId={first_season}"

        url_count = len(url_info.urls)
        self.assertEqual(first_season_url_expected, url_info.urls[url_count - 1])

    def test_is_year_active(self):
        current_year = datetime.datetime.now().year
        for i in range(1, 6):
            self.assertTrue(
                _is_year_active(current_year - i),
                f"Previous year {current_year - i} not considered active.")

            self.assertFalse(
                _is_year_active(current_year + i),
                f"Future year {current_year + i} considered active.")

    def test_is_september_date_after_nfl_start(self):
        self.assert_september_dates_after_nfl_start()
        self.assert_september_dates_before_nfl_start()

    def assert_september_dates_after_nfl_start(self):
        years_and_days_to_check = [
            [2019, 26], [2019, 16], [2019, 18],
            [2018, 20], [2018, 27],
            [2017, 11], [2017, 13]
        ]
        for year_and_day in years_and_days_to_check:
            date = datetime.date(year_and_day[0], 9, year_and_day[1])
            self.assertTrue(
                _is_september_date_after_nfl_start(date),
                f"Date {date} is after NFL start, but your code disagrees.")

    def assert_september_dates_before_nfl_start(self):
        years_and_days_to_check = [
            [2019, 1], [2019, 5], [2019, 7],
            [2018, 3], [2018, 8],
            [2017, 1], [2017, 9]
        ]
        for year_and_day in years_and_days_to_check:
            date = datetime.date(year_and_day[0], 9, year_and_day[1])
            self.assertFalse(
                _is_september_date_after_nfl_start(date),
                f"Date {date} is before NFL start, but your code disagrees.")

if __name__ == "__main__":
    unittest.main()
