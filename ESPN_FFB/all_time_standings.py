import requests
import matplotlib.pyplot as plt
import treelib as tl
import numpy as np
import multiprocessing
from ESPN_FFB.url_info import URLInfo
from ESPN_FFB.constants import *
from ESPN_FFB.figure_options import *
from ESPN_FFB.league_info import LeagueInfo

class AxesLabels():

    def __init__(self):
        self.x_labels = None
        self.y_label = None

    def set_all_time_record_labels(self, figure_option: int):
        self.x_labels = [STATS_TAGS.get(0), STATS_TAGS.get(1), STATS_TAGS.get(2)]

        if is_adjusted_figure_option(figure_option):
            self.y_label = AXES_LABELS.get(2)
        else:
            self.y_label = AXES_LABELS.get(0)

    def set_all_time_point_labels(self, figure_option: int):
        self.x_labels = [STATS_TAGS.get(3), STATS_TAGS.get(4)]
        self.y_label = AXES_LABELS.get(1)

def generate_all_time_graph(league_info: LeagueInfo, figure_option: int) -> bool:
    """ Main function for AllTimeStandings. Given a passed in figure_option, generates that figure.

        If parsed_json is populated, this is assumed to be cached off data from a previous request
        and we will not request new data from ESPN. If parsed_json is not populated, new requests
        will be sent to ESPN and parsed results will be stored.
    """
    view = "mTeam"
    url_info = URLInfo(view, league_info)
    if league_info.is_cache_empty():
        if pull_data_from_ESPN(url_info, league_info.cached_json) is False:
            return False

    team_stat_tree = format_response_as_tree(league_info)

    axes_labels = get_axes_labels(figure_option)
    if is_adjusted_figure_option(figure_option):
        adjust_tree_for_seasons(team_stat_tree)

    prepare_figure(figure_option, team_stat_tree, axes_labels)
    plt.show()
    return True

def pull_data_from_ESPN(url_info: URLInfo, parsed_json: list):
    """ Given a list of URLs and the desired view, this will request info from each URL with the given view.
        Requests are initially returned in JSON.

        Returned information will be stored in parsed_json.
    """
    responses = list()

    try:
        responses = get_ESPN_data(url_info)
    except requests.exceptions.ConnectionError:
        return False

    for request in responses:
        if 'leagueHistory' in request.url:
            request = request.json()[0]
        else:
            request = request.json()
        parsed_json.append(request)

def format_response_as_tree(league_info: LeagueInfo):
    response_tree = tl.Tree()
    initialize_tree(response_tree)
    translate_parsed_json_to_tree(league_info.cached_json, response_tree)
    return response_tree

def initialize_tree(response_tree: tl.Tree):
    """ Create team and stat nodes for a new tree. """
    response_tree.create_node("Teams", "teams")
    for team in ESPN_ID_TO_TEAM:
        response_tree.create_node(ESPN_ID_TO_TEAM.get(team),team, parent='teams')
        initialize_tree_children(response_tree, team)

def initialize_tree_children(tree:tl.Tree, teamNode):
    """ Will create each stat node for the given team in the given tree. """
    for stat in STATS_IDS:
        tree.create_node(f'{teamNode};{STATS_TAGS.get(stat)}', f'{teamNode};{STATS_IDS.get(stat)}', parent=teamNode, data=0)

def translate_parsed_json_to_tree(parsed_json: list, team_stat_tree: tl.Tree):
    """ Given parsed_json with results from requests to ESPN, this will reformat
        the results and store them in a tree.
    """
    for request in parsed_json:
        for team in request['teams']:
            for stat in STATS_IDS:
                team_stat_tree.get_node(get_team_stat_combo_id(team['id'], stat)).data += team['record']['overall'][str(STATS_IDS.get(stat))]

def get_axes_labels(figure_option: int) -> AxesLabels:
    return_labels = AxesLabels()

    if is_all_time_record_figure(figure_option):
        return_labels.set_all_time_record_labels(figure_option)
    elif is_all_time_point_figure(figure_option):
        return_labels.set_all_time_point_labels(figure_option)

    return return_labels

def adjust_tree_for_seasons(tree:tl.Tree):
    """ Expects a tree following structure of those created by initialize_tree.
        Returns the tree with all stat nodes divided by the number of games
        that team has played.
    """
    for team in ESPN_ID_TO_TEAM:
        games_played = total_games(team, tree)
        for stat in STATS_IDS:
            temp_value = tree.get_node(get_team_stat_combo_id(team, stat)).data/games_played
            if stat != 3 and stat != 4:
                temp_value *= 100
            tree.get_node(get_team_stat_combo_id(team, stat)).data = round(temp_value, 1)

def total_games(team: int, team_stat_tree:tl.Tree):
    """ Returns the all time number of games a given team has played. """
    return team_stat_tree.get_node(get_team_stat_combo_id(team, 0)).data \
                + team_stat_tree.get_node(get_team_stat_combo_id(team, 1)).data \
                + team_stat_tree.get_node(get_team_stat_combo_id(team, 2)).data

def prepare_figure(figure_option, team_stat_tree: tl.Tree, axes_labels: AxesLabels):
    """ Stating point for preparing bar graph.
    """
    tree_type = get_tree_type(figure_option)
    team_stat_tree = tree_to_list_key_team(team_stat_tree, tree_type)

    x = np.arange(len(axes_labels.x_labels))
    fig, ax = plt.subplots(figsize=(16, 6))

    assign_figure_attributes(
        axes_labels, x, ax,
        FIGURE_OPTIONS.get(figure_option))

    prepare_figure_bars(team_stat_tree, x, fig, ax)

def get_tree_type(figure_option: int):
    if is_all_time_point_figure(figure_option):
        return 1
    else:
        return 0

def assign_figure_attributes(axes_labels: AxesLabels, x, ax, title: str):
    ax.set_ylabel(axes_labels.y_label)
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(axes_labels.x_labels)

def prepare_figure_bars(team_stat_tree, x, fig, ax, width: float=0.075):
    """ Generates the actual bars to display in a bar graph.
        Currently hardcoded to appropriately display and space 12 bars.
    """
    rects = generate_bars_per_team(team_stat_tree, x, ax, width)
    add_bar_labels(ax, rects)
    ax.legend(fontsize='medium', shadow=True, title='Teams', title_fontsize='large')
    fig.tight_layout()

def generate_bars_per_team(list: list, x, ax, width: float=0.075):
    bars = []
    i = width*-6
    for team in ESPN_ID_TO_TEAM:
        bars.append(
            ax.bar(
                x + i,
                list[team-1],
                width,
                label=ESPN_ID_TO_TEAM.get(team),
                linewidth=1,
                edgecolor='black')
            )
        i += width
    return bars

def add_bar_labels(ax, group_rects: list, vertical_offset: int=3):
    """ Expects a list of responses from ax.bar(), each of which should itself be a list of bars.
        Prints value of the bar above the bar itself.
    """
    for rects in group_rects:
        for rect in rects:
            height = rect.get_height()
            if height == 0:
                continue
            ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, vertical_offset),
                        textcoords="offset points",
                        ha='center', va='bottom')

def tree_to_list_key_team(tree:tl.Tree, type:int) -> list:
    """ Given a tree and it's type, returns an equivalent list.
        This list will be formatted as a list of lists. The index matches the team ID
        from ESPN_ID_TO_TEAM and the values are stored as [stat1, stat2, stat3].

        Type options:   0 - Record
                        1 - Points

        Example:
        [[team1-stat1, team1-stat2, team1-stat3], [team2-stat1, team2-stat2, team2-stat3]]
    """
    return_list = []
    if type == 0: #Record
        for team in ESPN_ID_TO_TEAM:
            return_list.insert(team, 
                [tree.get_node(get_team_stat_combo_id(team, stat)).data for stat in range(3)])
    elif type == 1: #Points
        for team in ESPN_ID_TO_TEAM:
            return_list.insert(team, 
                [int(tree.get_node(get_team_stat_combo_id(team, stat)).data) for stat in range(3,5)])
    return return_list

def get_team_stat_combo_id(team: int, stat: int) -> str:
    """ Returns string to uniquely identify team/stat combination.
        Uses stat string from STATS_IDS (as formatted by ESPN).

        Format: 'team;statName'
    """
    return f"{team};{STATS_IDS.get(stat)}"

def get_ESPN_data(url_info: URLInfo) -> list:
    return_list = list()
    for url in url_info.urls:
        return_list.append(
            requests.get(
            url,
            params={"view": url_info.view},
            cookies={"SWID": url_info.SWID,
            "espn_s2": url_info.espn_s2})
        )
    return return_list

def get_team_stat_combo_tag(team: int, stat: int) -> str:
    """ Returns string to uniquely identify team/stat combination.
        Uses statTag from STATS_TAGS (user-friendly stat names).

        Format: 'team;Stat Name'
    """
    return f"{team};{STATS_TAGS.get(stat)}"

if __name__ == "__main__": #For Testing Purposes
    test_json = list()
    generate_all_time_graph(test_json, 3)
    generate_all_time_graph(test_json, 1)
