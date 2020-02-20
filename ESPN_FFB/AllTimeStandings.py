import requests
import json
import matplotlib.pyplot as plt
import datetime
import treelib as tl
import numpy as np
import multiprocessing
import os

ESPN_ID_TO_TEAM = { #ESPN's team id : team
    1: "DJ",
    2: "Nick",
    3: "Tim",
    4: "Joe",
    5: "Davey",
    6: "Jason",
    7: "Ben",
    8: "Drew",
    9: "Luke",
    10: "Jack",
    11: "Tony",
    12: "Dano"
}

FIGURE_OPTIONS = {
    "All Time Record": 0,
    "All Time Record - Adjusted (%)": 1,
    "All Time Points": 2,
    "All Time Points - Adjusted (Per Game)": 3,
    0: "All Time Record",
    1: "All Time Record - Adjusted (%)",
    2: "All Time Points",
    3: "All Time Points - Adjusted (Per Game)"
}

STATS_TAGS = {
    0: "Wins",
    1: "Losses",
    2: "Ties",
    3: "Points For",
    4: "Points Against"
}

STATS_IDS = {
    0: "wins",
    1: "losses",
    2: "ties",
    3: "pointsFor",
    4: "pointsAgainst"
}

AXIS_LABELS = {
    0: "Games",
    1: "Points",
    2: "% of Games"
}

class URLArgs:
    def __init__(self, url, view, cookieFile):
        self.url = url
        self.view = view

        cookies = open(cookieFile, "r").readlines()
        self.SWID = cookies[0].strip()
        self.espn_s2 = cookies[1].strip()

def main(parsed_json: list, figure_option, league_id: int=368182, first_season_id: int=2014) -> bool:
    """ Main function for AllTimeStandings. Given a passed in figure_option, generates that figure.

        If parsed_json is populated, this is assumed to be cached off data from a previous request
        and we will not request new data from ESPN. If parsed_json is not populated, new requests
        will be sent to ESPN and parsed results will be stored.
    """
    view = "mTeam"
    current_directory = os.path.dirname(os.path.abspath(__file__))
    cookie_file = os.path.join(current_directory, 'cookies.txt')
    urls = identify_urls(league_id, first_season_id)
    if len(parsed_json) == 0:
        if pull_data_from_ESPN(urls, view, parsed_json, cookie_file) is False:
            return False

    team_stat_tree = tl.Tree()
    initialize_tree(team_stat_tree)
    translate_parsed_json_to_tree(parsed_json, team_stat_tree)

    if is_all_time_record_figure(figure_option) is True:
        x_labels = [STATS_TAGS.get(0), STATS_TAGS.get(1), STATS_TAGS.get(2)]
        if figure_option == FIGURE_OPTIONS.get("All Time Record - Adjusted (%)"):
            y_label = AXIS_LABELS.get(2)
            tree_adjusted_for_seasons(team_stat_tree)
        else:
            y_label = AXIS_LABELS.get(0)
    elif is_all_time_point_figure(figure_option) is True:
        y_label = AXIS_LABELS.get(1)
        x_labels = [STATS_TAGS.get(3), STATS_TAGS.get(4)]
        if figure_option == FIGURE_OPTIONS.get("All Time Points - Adjusted (Per Game)"):
            tree_adjusted_for_seasons(team_stat_tree)

    prepare_figure(figure_option, team_stat_tree, x_labels, y_label)
    plt.show()
    return True

def identify_urls(league_id: int, first_season_id: int, year: int=datetime.datetime.now().year) -> list:
    """ Returns list of URLs for ESPNs fantasy football APIs.
        Will create one URL per year, starting from the passed in year
        until the first season of the league.

        If no year is supplied, will start at the current year.
    """
    urls = list()
    if year < first_season_id:
        return urls

    if is_year_active(year) is False:
        year -= 1
    while (year >= first_season_id):
        if len(urls) < 2: #Adding this check because 2 years currently use active url
            urls.append(construct_url_current(league_id, year))
        else:
            urls.append(construct_url_historical(league_id, year))
        year -= 1
    return urls

def is_year_active(year: int) -> bool:
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

def construct_url_current(league_id: int, seasonId: int) -> str:
    """
        Constructs "active" URLs for ESPN fantasy football.
        Active URLs appear to be used for the last 2 seasons.
    """
    return "http://fantasy.espn.com/apis/v3/games/ffl/seasons" \
    f"/{seasonId}/segments/0/leagues/{league_id}"

def construct_url_historical(league_id: int, seasonId: int) -> str:
    """
        Constructs "historical" URLs for ESPN fantasy football.
        Historical URLs appear to be used for seasons more than 2 years back.
    """
    return "https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory" \
        f"/{league_id}?seasonId={seasonId}"

def pull_data_from_ESPN(urls: list, view: str, parsed_json: list, cookie_file: str):
    """ Given a list of URLs and the desired view, this will request info from each URL with the given view.
        Requests are initially returned in JSON.

        Returned information will be stored in parsed_json.
    """
    responses = list()
    urlArgs = list()
    for url in urls:
        urlArgs.append(URLArgs(url, view, cookie_file))
    process_pool = multiprocessing.Pool()
    try:
        responses = process_pool.map(get_ESPN_data, urlArgs)
    except requests.exceptions.ConnectionError:
        process_pool.close()
        return False
    process_pool.close()
    process_pool.join()

    for request in responses:
        if 'leagueHistory' in request.url:
            request = request.json()[0]
        else:
            request = request.json()
        parsed_json.append(request)

def initialize_tree(team_stat_tree: tl.Tree):
    """ Create team and stat nodes for a new tree. """
    team_stat_tree.create_node("Teams", "teams")
    for team in ESPN_ID_TO_TEAM:
        team_stat_tree.create_node(ESPN_ID_TO_TEAM.get(team),team, parent='teams')
        initialize_tree_children(team_stat_tree, team)

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

def is_all_time_record_figure(figure_option) -> bool:
    """ Returns True if a given figure option is related to All Time Records.
        Expects either string or int from dictionary FIGURE_OPTIONS.
    """
    if figure_option in [FIGURE_OPTIONS.get("All Time Record"), FIGURE_OPTIONS.get("All Time Record - Adjusted (%)")]:
        return True
    elif figure_option in [FIGURE_OPTIONS.get(0), FIGURE_OPTIONS.get(1)]:
        return True
    else:
        return False

def tree_adjusted_for_seasons(tree:tl.Tree):
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

def is_all_time_point_figure(figure_option) -> bool:
    """ Returns True if a given figure option is related to All Time Points.
        Expects either string or int from dictionary FIGURE_OPTIONS.
    """
    if figure_option in [FIGURE_OPTIONS.get("All Time Points"), FIGURE_OPTIONS.get("All Time Points - Adjusted (Per Game)")]:
        return True
    elif figure_option in [FIGURE_OPTIONS.get(2), FIGURE_OPTIONS.get(3)]:
        return True
    else:
        return False

def prepare_figure(figure_option, team_stat_tree: tl.Tree, labels: list, y_label: str="yLabel"):
    """ Stating point for preparing bar graph.
    """
    if figure_option == FIGURE_OPTIONS.get("All Time Points - Adjusted (Per Game)") or figure_option == FIGURE_OPTIONS.get("All Time Points"):
        tree_type = 1
    else:
        tree_type = 0
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(16,6))
    prepare_figure_bars(
        tree_to_list_key_team(team_stat_tree, tree_type),
        labels, team_stat_tree, x, fig, ax, y_label,
        FIGURE_OPTIONS.get(figure_option))

def prepare_figure_bars(list, labels: list, tree: tl.Tree, x, fig, ax, y_label :str="yLabel", title :str="Title", width :float=0.075):
    """ Generates the actual bars to display in a bar graph.
        Currently hardcoded to appropriately display and space 12 bars.
    """
    #Create bars per team
    rects = []
    i = width*-6
    for team in ESPN_ID_TO_TEAM:
        rects.append(
            ax.bar(
                x + i,
                list[team-1],
                width,
                label=ESPN_ID_TO_TEAM.get(team),
                linewidth=1,
                edgecolor='black')
            )
        i += width

    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend(fontsize='medium', shadow=True, title='Teams', title_fontsize='large')

    add_bar_labels(ax, rects)
    fig.tight_layout()

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
                        xytext=(0, vertical_offset),  # 3 points vertical offset
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

def get_ESPN_data(urlArgs) -> list:
    return requests.get(
        urlArgs.url,
        params={"view": urlArgs.view},
        cookies={"SWID": urlArgs.SWID,
                 "espn_s2": urlArgs.espn_s2})

def tree_to_list_key_stat(tree: tl.Tree) -> list:
    """ Given a tree and it's type, returns an equivalent list.
        This list will be formatted as a list of lists. The index matches the stats
        index in STATS_IDS and the values are stored as [team1, team2, team3, etc.].

        Type options:   0 - Record
                        1 - Points

        Example:
        [[stat1-team1, stat1-team2, stat1-team3], [stat2-team1, stat2-team2, stat2-team3]]
    """
    return_list = []
    for stat in STATS_IDS:
        return_list.insert(stat, [get_team_stat_combo_id(team, stat) for team in ESPN_ID_TO_TEAM])
    return return_list

def get_team_stat_combo_tag(team: int, stat: int) -> str:
    """ Returns string to uniquely identify team/stat combination.
        Uses statTag from STATS_TAGS (user-friendly stat names).

        Format: 'team;Stat Name'
    """
    return f"{team};{STATS_TAGS.get(stat)}"

if __name__ == "__main__": #For Testing Purposes
    parsed_json = list()
    main(parsed_json, 3)
    main(parsed_json, 1)
