import numpy as np
from ESPN_FFB.constants import ESPN_ID_TO_TEAM, STATS_IDS
from ESPN_FFB.figure_options import (is_all_time_point_figure, is_all_time_record_figure,
                                     is_adjusted_figure_option)

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

    def get_figure_heights(self, figure_option) -> list:
        team_stats = self._format_response_as_dict()
        figure_heights = list()
        if is_all_time_record_figure(figure_option):
            for team in ESPN_ID_TO_TEAM:
                figure_heights.insert(team, team_stats.get(team)[:3])
        elif is_all_time_point_figure(figure_option):
            for team in ESPN_ID_TO_TEAM:
                figure_heights.insert(team, team_stats.get(team)[3:5])

        figure_heights = self._adjust_for_seasons_if_necessary(
            figure_heights, team_stats, figure_option)
        return figure_heights

    def _format_response_as_dict(self) -> dict:
        formatted_response = dict()
        for request in self.cached_json:
            for team in request['teams']:
                running_record = formatted_response.get(team['id'], [0] * len(STATS_IDS))
                new_record_addition = [0] * len(STATS_IDS)
                for stat in STATS_IDS:
                    season_stat = team['record']['overall'][str(STATS_IDS.get(stat))]
                    new_record_addition[stat] = season_stat
                running_record = np.add(running_record, new_record_addition)
                formatted_response.update({team['id']: running_record.tolist()})
        for team in formatted_response:
            formatted_response.update({team: [round(x) for x in formatted_response.get(team)]})
        return formatted_response

    def _adjust_for_seasons_if_necessary(self, figure_heights: list, all_team_stats: dict, figure_option: int):
        """ Expects a tree following structure of those created by initialize_tree.
            Returns the tree with all stat nodes divided by the number of games
            that team has played.
        """
        if is_adjusted_figure_option(figure_option) is False:
            return figure_heights
        for team in ESPN_ID_TO_TEAM:
            team_stats = figure_heights[team - 1]
            games_played = self._total_games(team, all_team_stats)
            for stat in range(len(team_stats)):
                temp_value = team_stats[stat] / games_played
                if len(team_stats) == 3: #For record, these need to be converted to %
                    temp_value *= 100
                team_stats[stat] = round(temp_value, 1)
            figure_heights[team - 1] = team_stats
        return figure_heights

    def _total_games(self, team: int, all_team_stats: dict):
        """ Returns the all time number of games a given team has played. """
        return sum(all_team_stats.get(team)[:3])
