import numpy as np
from ESPN_FFB.constants import ESPN_ID_TO_TEAM, STATS_IDS
from ESPN_FFB.figure_options import (is_all_time_point_figure, is_all_time_record_figure,
                                     is_adjusted_figure_option)

class LeagueInfo:

    def __init__(self, league_id: int = 368182, first_year: int = 2014):
        self.cached_responses = list()
        self.league_id = league_id
        self.first_year = first_year

    def set_league(self, league_id: int, first_year: int):
        self.cached_responses = list()
        self.league_id = league_id
        self.first_year = first_year

    def clear_cache(self):
        self.cached_responses.clear()

    def is_cache_empty(self):
        return len(self.cached_responses) == 0

    def get_figure_heights(self, figure_option) -> list:
        all_team_stats = self._format_response_as_dict()

        figure_heights = _strip_irrelevant_figure_heights(figure_option, all_team_stats)

        figure_heights = self._adjust_per_game_if_necessary(
            figure_heights, all_team_stats, figure_option)
        return figure_heights

    def _format_response_as_dict(self) -> dict:
        formatted_response = dict()

        for request in self.cached_responses:
            formatted_response = _format_all_teams_single_season(request, formatted_response)

        formatted_response = _round_formatted_response(formatted_response)
        return formatted_response

    def _adjust_per_game_if_necessary(self, figure_heights: list, all_team_stats: dict, figure_option: int):
        if is_adjusted_figure_option(figure_option) is False:
            return figure_heights

        for team in ESPN_ID_TO_TEAM:
            games_played = self._all_time_total_games_played(team, all_team_stats)
            figure_heights[team - 1] = self._adjust_per_game(team, figure_heights, games_played)
        return figure_heights

    def _all_time_total_games_played(self, team: int, all_team_stats: dict):
        return sum(all_team_stats.get(team)[:3])

    def _adjust_per_game(self, team: int, figure_heights: list, games_played: int) -> list:
        team_stats = figure_heights[team - 1]

        for stat in range(len(team_stats)):
            team_stat_value = team_stats[stat] / games_played
            team_stat_value = convert_to_percent_if_record_stats(team_stats, team_stat_value)

            team_stats[stat] = round(team_stat_value, 1)
        return team_stats

def _format_all_teams_single_season(request: dict, formatted_response: dict) -> dict:
    for team in request['teams']:
        formatted_response = _format_team_single_season(formatted_response, team)
    return formatted_response

def _format_team_single_season(formatted_response: dict, team: dict) -> dict:
    running_record = formatted_response.get(team['id'], [0] * len(STATS_IDS))
    new_record_addition = [0] * len(STATS_IDS)

    for stat in STATS_IDS:
        stat_this_season = team['record']['overall'][str(STATS_IDS.get(stat))]
        new_record_addition[stat] = stat_this_season

    running_record = np.add(running_record, new_record_addition)
    formatted_response.update({team['id']: running_record.tolist()})
    return formatted_response

def _round_formatted_response(formatted_response: dict) -> dict:
    for team in formatted_response:
        formatted_response.update({team: [round(x) for x in formatted_response.get(team)]})
    return formatted_response

def _strip_irrelevant_figure_heights(figure_option: int, all_team_stats: dict) -> list:
    figure_heights = list()

    relevant_slice = _get_relevant_slice(figure_option)
    for team in ESPN_ID_TO_TEAM:
        figure_heights.insert(team, all_team_stats.get(team)[
            relevant_slice[0]:relevant_slice[1]])
    return figure_heights

def _get_relevant_slice(figure_option: int):
    if is_all_time_record_figure(figure_option):
        relevant_slice = [0, 3]
    elif is_all_time_point_figure(figure_option):
        relevant_slice = [3, 5]
    return relevant_slice

def convert_to_percent_if_record_stats(team_stats: list, team_stat_value: float):
    if len(team_stats) == 3:
        team_stat_value *= 100
    return team_stat_value
