import requests
import json
import matplotlib.pyplot as plt
import datetime
import treelib as tl
import numpy as np
import multiprocessing
import os

teamDict = { #ESPN's team id : team
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

figureOptions = {
    "All Time Record": 0,
    "All Time Record - Adjusted (%)": 1,
    "All Time Points": 2,
    "All Time Points - Adjusted (Per Game)": 3,
    0: "All Time Record",
    1: "All Time Record - Adjusted (%)",
    2: "All Time Points",
    3: "All Time Points - Adjusted (Per Game)"
}

statsTagDict = {
    0: "Wins",
    1: "Losses",
    2: "Ties",
    3: "Points For",
    4: "Points Against"
}

statsIdDict = {
    0: "wins",
    1: "losses",
    2: "ties",
    3: "pointsFor",
    4: "pointsAgainst"
}

axisLabels = {
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

def is_all_time_record_figure(figureOption) -> bool:
    """ Returns True if a given figure option is related to All Time Records.
        Expects either string or int from dictionary figureOptions.
    """
    if figureOption in [figureOptions.get("All Time Record"), figureOptions.get("All Time Record - Adjusted (%)")]:
        return True
    elif figureOption in [figureOptions.get(0), figureOptions.get(1)]:
        return True
    else:
         return False

def is_all_time_point_figure(figureOption) -> bool:
    """ Returns True if a given figure option is related to All Time Points.
        Expects either string or int from dictionary figureOptions.
    """
    if figureOption in [figureOptions.get("All Time Points"), figureOptions.get("All Time Points - Adjusted (Per Game)")]:
        return True
    elif figureOption in [figureOptions.get(2), figureOptions.get(3)]:
        return True
    else:
        return False

def construct_url_current(leagueId:int, seasonId:int) -> str:
    """ Constructs "active" URLs for ESPN fantasy football. Active URLs appear to be used for the last 2 seasons. """
    return f"http://fantasy.espn.com/apis/v3/games/ffl/seasons/{seasonId}/segments/0/leagues/{leagueId}"

def construct_url_historical(leagueId:int, seasonId:int) -> str:
    """ Constructs "historical" URLs for ESPN fantasy football. Historical URLs appear to be used for seasons more than 2 years back. """
    return f"https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory/{leagueId}?seasonId={seasonId}"

def get_ESPN_data(urlArgs) -> list:
    return requests.get(urlArgs.url,
        params={"view": urlArgs.view},
        cookies={"SWID": urlArgs.SWID,
                "espn_s2": urlArgs.espn_s2})

def initialize_tree(teamStatTree:tl.Tree):
    """ Create team and stat nodes for a new tree. """
    teamStatTree.create_node("Teams", "teams")
    for team in teamDict:
        teamStatTree.create_node(teamDict.get(team),team, parent='teams')
        initialize_tree_children(teamStatTree, team)

def initialize_tree_children(tree:tl.Tree, teamNode):
    """ Will create each stat node for the given team in the given tree. """
    for stat in statsIdDict:
        tree.create_node(f'{teamNode};{statsTagDict.get(stat)}', f'{teamNode};{statsIdDict.get(stat)}', parent=teamNode, data=0)

def tree_to_list_key_team(tree:tl.Tree, type:int) -> list:
    """ Given a tree and it's type, returns an equivalent list.
        This list will be formatted as a list of lists. The index matches the team ID
        from teamDict and the values are stored as [stat1, stat2, stat3].

        Type options:   0 - Record
                        1 - Points

        Example:
        [[team1-stat1, team1-stat2, team1-stat3], [team2-stat1, team2-stat2, team2-stat3]]
    """
    returnList = []
    if type == 0: #Record
        for team in teamDict:
            returnList.insert(team, 
                [tree.get_node(get_team_stat_combo_id(team, stat)).data for stat in range(3)])
    elif type == 1: #Points
        for team in teamDict:
            returnList.insert(team, 
                [int(tree.get_node(get_team_stat_combo_id(team, stat)).data) for stat in range(3,5)])
    return returnList

def tree_to_list_key_stat(tree:tl.Tree) -> list:
    """ Given a tree and it's type, returns an equivalent list.
        This list will be formatted as a list of lists. The index matches the stats
        index in statsIdDict and the values are stored as [team1, team2, team3, etc.].

        Type options:   0 - Record
                        1 - Points

        Example:
        [[stat1-team1, stat1-team2, stat1-team3], [stat2-team1, stat2-team2, stat2-team3]]
    """
    returnList = []
    for stat in statsIdDict:
        returnList.insert(stat, [get_team_stat_combo_id(team, stat) for team in teamDict])
    return returnList

def get_team_stat_combo_id(team:int, stat:int) -> str:
    """ Returns string to uniquely identify team/stat combination. 
        Uses stat string from statsIdDict (as formatted by ESPN).

        Format: 'team;statName'
    """
    return f"{team};{statsIdDict.get(stat)}"

def get_team_stat_combo_tag(team:int, stat:int) -> str:
    """ Returns string to uniquely identify team/stat combination.
        Uses statTag from statsTagDict (user-friendly stat names).

        Format: 'team;Stat Name'
    """
    return f"{team};{statsTagDict.get(stat)}"

def tree_adjusted_for_seasons(tree:tl.Tree):
    """ Expects a tree following structure of those created by initialize_tree.
        Returns the tree with all stat nodes divided by the number of games
        that team has played.
    """
    for team in teamDict:
        gamesPlayed = total_games(team, tree)
        for stat in statsIdDict:
            tempValue = tree.get_node(get_team_stat_combo_id(team, stat)).data/gamesPlayed
            if stat != 3 and stat != 4:
                tempValue *= 100
            tree.get_node(get_team_stat_combo_id(team, stat)).data = round(tempValue,1)

def add_bar_labels(ax, groupRects:list, vertOffset:int=3):
    """ Expects a list of responses from ax.bar(), each of which should itself be a list of bars.
        Prints value of the bar above the bar itself.
    """
    for rects in groupRects:
        for rect in rects:
            height = rect.get_height()
            if height == 0:
                continue
            ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, vertOffset),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')

def prepare_figure(figureOption, teamStatTree:tl.Tree, labels:list, yLabel:str="yLabel"):
    """ Stating point for preparing bar graph.
    """
    if figureOption == figureOptions.get("All Time Points - Adjusted (Per Game)") or figureOption == figureOptions.get("All Time Points"):
        treeType = 1
    else:
        treeType = 0
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(16,6))
    prepare_figure_bars(tree_to_list_key_team(teamStatTree, treeType), 
                        labels, teamStatTree, x, fig, ax, yLabel, 
                        figureOptions.get(figureOption))

def prepare_figure_bars(list, labels:list, tree:tl.Tree, x, fig, ax, yLabel:str="yLabel", title:str="Title", width:float=0.075):
    """ Generates the actual bars to display in a bar graph.
        Currently hardcoded to appropriately display and space 12 bars.
    """
    #Create bars per team
    rects = []
    i = width*-6
    for team in teamDict:
        rects.append(ax.bar(x + i, list[team-1], width, label=teamDict.get(team), linewidth=1, edgecolor='black'))
        i += width

    ax.set_ylabel(yLabel)
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend(fontsize='medium', shadow=True, title='Teams', title_fontsize='large')

    add_bar_labels(ax, rects)
    fig.tight_layout()

def identify_urls(leagueId:int, firstseasonId:int, year:int=datetime.datetime.now().year) -> list:
    """ Returns list of URLs for ESPNs fantasy football APIs.
        Will create one URL per year, starting from the passed in year
        until the first season of the league.

        If no year is supplied, will start at the current year.
    """
    urls = list()
    if year < firstseasonId:
        return urls

    if is_year_active(year) is False:
        year -= 1
    while (year >= firstseasonId):
        if len(urls) < 2: #Adding this check because 2 years currently use active url
            urls.append(construct_url_current(leagueId, year))
        else:
            urls.append(construct_url_historical(leagueId,year))
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


def pull_data_from_ESPN(urls:list, view:str, parsedJSON:list, cookieFile:str):
    """ Given a list of URLs and the desired view, this will request info from each URL with the given view.
        Requests are initially returned in JSON.

        Returned information will be stored in parsedJSON.
    """
    responses = list()
    urlArgs = list()
    for url in urls:
        urlArgs.append(URLArgs(url, view, cookieFile))
    processPool = multiprocessing.Pool()
    try:
        responses = processPool.map(get_ESPN_data, urlArgs)
    except requests.exceptions.ConnectionError:
        processPool.close()
        return False
    processPool.close()
    processPool.join()

    for request in responses:
        if 'leagueHistory' in request.url:
            request = request.json()[0]
        else:
            request = request.json()
        parsedJSON.append(request)

def translate_parseJSON_to_tree(parsedJSON:list, teamStatTree:tl.Tree):
    """ Given parsedJSON with results from requests to ESPN, this will reformat
        the results and store them in a tree.
    """
    for request in parsedJSON:
        for team in request['teams']:
            for stat in statsIdDict:
                teamStatTree.get_node(get_team_stat_combo_id(team['id'], stat)).data += team['record']['overall'][str(statsIdDict.get(stat))]

def total_games(team: int, teamStatTree:tl.Tree):
    """ Returns the all time number of games a given team has played. """
    return teamStatTree.get_node(get_team_stat_combo_id(team, 0)).data \
                + teamStatTree.get_node(get_team_stat_combo_id(team, 1)).data \
                + teamStatTree.get_node(get_team_stat_combo_id(team, 2)).data

def main(parsedJSON: list,figureOption, leagueId: int=368182, firstseasonId: int=2014, numberOfTeams: int=12) -> bool:
    """ Main function for AllTimeStandings. Given a passed in figureOption, generates that figure.

        If parsedJSON is populated, this is assumed to be cached off data from a previous request and
        we will not request new data from ESPN. If parsedJSON is not populated, new requests will be
        sent to ESPN and parsed results will be stored.
    """
    view = "mTeam"
    currentDirectory = os.path.dirname(os.path.abspath(__file__))
    cookieFile = os.path.join(currentDirectory, 'cookies.txt')
    urls = identify_urls(leagueId, firstseasonId)
    if len(parsedJSON) == 0: 
        if pull_data_from_ESPN(urls, view, parsedJSON, cookieFile) is False:
            return False

    teamStatTree = tl.Tree()
    initialize_tree(teamStatTree)
    translate_parseJSON_to_tree(parsedJSON, teamStatTree)

    if is_all_time_record_figure(figureOption) is True:
        xLabels = [statsTagDict.get(0), statsTagDict.get(1), statsTagDict.get(2)]
        if figureOption == figureOptions.get("All Time Record - Adjusted (%)"):
            yLabel = axisLabels.get(2)
            tree_adjusted_for_seasons(teamStatTree)
        else:
            yLabel = axisLabels.get(0)
    elif is_all_time_point_figure(figureOption) is True:
        yLabel = axisLabels.get(1)
        xLabels = [statsTagDict.get(3), statsTagDict.get(4)]
        if figureOption == figureOptions.get("All Time Points - Adjusted (Per Game)"):
            tree_adjusted_for_seasons(teamStatTree)

    prepare_figure(figureOption, teamStatTree, xLabels, yLabel)
    plt.show()
    return True

if __name__ == "__main__": #For Testing Purposes
    parsedJSON = list()
    main(parsedJSON, 3)
    main(parsedJSON, 1)