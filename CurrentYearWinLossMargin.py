import requests
import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
import os

teamDict = { #team id : team
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

def main():
    currentDirectory = os.path.dirname(os.path.abspath(__file__))
    cookieFile = os.path.join(currentDirectory, 'cookies.txt')
    leagueID = 368182
    seasonID = 2019
    view = "mMatchup"

    currentUrl = "http://fantasy.espn.com/apis/v3/games/ffl/seasons/" + str(seasonID) + "/segments/0/leagues/" + str(leagueID)

    #initial http request
    cookies = open(cookieFile, "r").readlines()
    r = requests.get(currentUrl, 
            params={"view" : view},
            cookies={"SWID": cookies[0].strip(),
                    "espn_s2": cookies[1].strip()})

    data = r.json() #Need to add '[0]' directly to end for historical url

    #Create matchup DataFrame
    matchupDF = [[
            game['matchupPeriodId'],
            teamDict[game['home']['teamId']], game['home']['totalPoints'],
            teamDict[game['away']['teamId']], game['away']['totalPoints']
        ] for game in data['schedule']]
    matchupDF = pd.DataFrame(matchupDF, columns=['Week', 'Team1', 'Score1', 'Team2', 'Score2'])
    matchupDF['Type'] = ['Regular' if w<=14 else 'Playoff' for w in matchupDF['Week']]

    #Compare scores to generate win/loss DataFrame
    wlMarginDF = matchupDF.assign(Margin1 = matchupDF['Score1'] - matchupDF['Score2'],
                    Margin2 = matchupDF['Score2'] - matchupDF['Score1'])
    wlMarginDF = (wlMarginDF[['Week', 'Team1', 'Margin1', 'Type']]
    .rename(columns={'Team1': 'Team', 'Margin1': 'Margin'})
    .append(wlMarginDF[['Week', 'Team2', 'Margin2', 'Type']]
    .rename(columns={'Team2': 'Team', 'Margin2': 'Margin'}))
    )

    #Plot results
    fig, ax = plt.subplots(1,1, figsize=(16,6))
    order = [teamDict[1], teamDict[2], teamDict[3], teamDict[4], teamDict[5], teamDict[6], teamDict[7], teamDict[8], teamDict[9], teamDict[10], teamDict[11], teamDict[12]]
    sns.boxplot(x='Team', y='Margin', hue='Type',
                data=wlMarginDF,
                palette='muted',
                order=order)
    ax.axhline(0, ls='--')
    ax.set_xlabel('')
    ax.set_title('Win/Loss Margins')
    plt.show()