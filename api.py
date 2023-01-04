import requests
import json
import sys
import signal
import pandas as pd
import nba_web_scraping as nws
from fpdf import FPDF
# from requests.auth import HTTPBasicAuth


def handler_signal(signal, frame):
    print("\n\n [!] Out ....... \n")
    sys.exit(1)


signal.signal(signal.SIGINT, handler_signal)


def extract():
    headers = {"Accept": "application/json"}
    key = "e6ac5a0300f5419bb042259782abc7e8"

    url_teams = f"https://api.sportsdata.io/v3/nba/scores/json/teams?key={key}"
    # auth = HTTPBasicAuth("apikey", "e6ac5a0300f5419bb042259782abc7e8")
    # data = requests.get(url_teams, headers=headers, auth=auth).text
    teams = requests.get(url_teams, headers=headers).text  # teams es un json str
    teams = json.loads(teams)

    # Select the team
    run = True
    while run:
        team_name = input("Enter the team KEY or the CITY plus the NAME (e.g. TOR / Toronto Raptors) -> ")
        for team in teams:
            name = team["City"] + " " + team["Name"]
            if team["Key"] == team_name or name == team_name:
                selected_team = team["Key"]
                run = False
                break
        if run is True:
            print("The team doesn't exist.")

    """
    Player info such as ID, status, TeamID, Names, Position, Photo, Jersey, Team
    """
    url_team_players_info = f"https://api.sportsdata.io/v3/nba/scores/json/Players/{selected_team}?key=" + key
    players = requests.get(url_team_players_info, headers=headers).text
    players = json.loads(players)
    return players, name


def transform(players):
    headers = {"Accept": "application/json"}
    key = "e6ac5a0300f5419bb042259782abc7e8"
    general_data = {"Name": [],
                    "Games": [],
                    "GS": [],
                    "MIN": [],
                    "PTS": [],
                    "OR": [],
                    "DR": [],
                    "REB": [],
                    "AST": [],
                    "STL": [],
                    "BLK": [],
                    "TO": [],
                    "PF": []}

    throw_data = {"Name": [],
                  "FGM": [],
                  "FGA": [],
                  "FG%": [],
                  "3PM": [],
                  "3PA": [],
                  "3P%": [],
                  "FTM": [],
                  "FTA": [],
                  "FT%": [],
                  "2PM": [],
                  "2PA": [],
                  "2P%": []}

    for player in players:
        player_id = player["PlayerID"]
        name = player["FirstName"] + " " + player["LastName"]

        general_data["Name"].append(name)
        throw_data["Name"].append(name)

        url_certain_game = f"https://api.sportsdata.io/v3/nba/stats/json/PlayerGameStatsBySeason/2022/{player_id}/all?key=" + key
        games = requests.get(url_certain_game, headers=headers).text
        games = json.loads(games)

        n_games = 0
        gs = 0
        minutes = 0
        pts = 0
        o_r = 0
        d_r = 0
        reb = 0
        ast = 0
        stl = 0
        blk = 0
        to = 0
        pf = 0
        fgm = 0
        fga = 0
        tpm = 0
        tpa = 0
        ftm = 0
        fta = 0
        twpm = 0
        twpa = 0

        for game in games:
            if game not in ["statusCode", "message"]:
                n_games += 1
                gs += game["Started"]
                minutes += game["Minutes"]
                pts += game["Points"]
                o_r += game["OffensiveRebounds"]
                d_r += game["DefensiveRebounds"]
                reb += game["Rebounds"]
                ast += game["Assists"]
                stl += game["Steals"]
                blk += game["BlockedShots"]
                to += game["Turnovers"]
                pf += game["PersonalFouls"]
                fgm += game["FieldGoalsMade"]
                fga += game["FieldGoalsAttempted"]
                tpm += game["ThreePointersMade"]
                tpa += game["ThreePointersAttempted"]
                ftm += game["FreeThrowsMade"]
                fta += game["FreeThrowsAttempted"]
                twpm += game["TwoPointersMade"]
                twpa += game["TwoPointersAttempted"]

        if n_games != 0:
            general_data["Games"].append(n_games)
            general_data["GS"].append(gs / n_games)
            general_data["MIN"].append(minutes / n_games)
            general_data["PTS"].append(pts / n_games)
            general_data["OR"].append(o_r / n_games)
            general_data["DR"].append(d_r / n_games)
            general_data["REB"].append(reb / n_games)
            general_data["AST"].append(ast / n_games)
            general_data["STL"].append(stl / n_games)
            general_data["BLK"].append(blk / n_games)
            general_data["TO"].append(to / n_games)
            general_data["PF"].append(pf / n_games)

            throw_data["FGM"].append(fgm / n_games)
            throw_data["FGA"].append(fga / n_games)
            if fga != 0:
                throw_data["FG%"].append((fgm / n_games) / (fga / n_games) * 100)
            else:
                throw_data["FG%"].append(0)
            throw_data["3PM"].append(tpm / n_games)
            throw_data["3PA"].append(tpa / n_games)
            if tpa != 0:
                throw_data["3P%"].append((tpm / n_games) / (tpa / n_games) * 100)
            else:
                throw_data["3P%"].append(0)
            throw_data["FTM"].append(ftm / n_games)
            throw_data["FTA"].append(fta / n_games)
            if fta != 0:
                throw_data["FT%"].append((ftm / n_games) / (fta / n_games) * 100)
            else:
                throw_data["FT%"].append(0)
            throw_data["2PM"].append(twpm / n_games)
            throw_data["2PA"].append(twpa / n_games)
            if twpa != 0:
                throw_data["2P%"].append((twpm / n_games) / (twpa / n_games) * 100)
            else:
                throw_data["2P%"].append(0)
        else:
            for key in general_data.keys():
                if key != "Name":
                    general_data[key].append(0)
            for key in throw_data.keys():
                if key != "Name":
                    throw_data[key].append(0)

    per_game_info = pd.DataFrame(general_data).sort_values("PTS", ascending=False).round(2)
    per_game_throws_info = pd.DataFrame(throw_data).sort_values("3P%", ascending=False).round(2)

    return (per_game_info, per_game_throws_info)


def load(per_game_info, per_game_throws_info, team_name):
    pdf = FPDF()
    legend_1 = {
        "GS": "Games Started",
        "Min": "Minutes played",
        "PTS": "Points",
        "OR": "Offensive Rebounds",
        "DR": "Deffensive Rebounds",
        "REB": "Rebounds",
        "AST": "Assists",
        "STL": "Steals",
        "BLK": "Blocks",
        "TO": "Turnovers",
        "PF": "Personal Fouls"
    }

    legend_2 = {
        "FGM": "Field Goals Made",
        "FGA": "Field Goals Attempted",
        "FG%": "Field Goals Percentage",
        "3PM": "Three Point Field Goals Made",
        "3PA": "Three Point Field Goals Attempted",
        "3P%": "Three Point Field Goals Percentage",
        "FTM": "Free Throws Made",
        "FTA": "Free Throws Attempted",
        "FT%": "Free Throws Percentage",
        "2PM": "Two Point Field Goals Made",
        "2PA": "Two Point Field Goals Attempted",
        "2P%": "Two Point Field Goals Percentage"
    }

    # First page
    pdf.add_page(orientation="L")

    pdf.set_font("Times", "b", 18)
    pdf.cell(w=0, h=30, txt="PER-GAME STATS ANALYSIS (2022)", border=0, ln=2, align="L")

    pdf.set_font("Times", "b", 18)
    pdf.set_x(16)
    pdf.cell(w=0, h=15, txt=f"Team: {team_name}", border=0, ln=2, align="L")

    pdf.set_font("arial", "b", 11)
    first_columns = list(per_game_info.columns)
    pdf.set_x(16)
    pdf.cell(w=47, h=9, txt=first_columns[0], border=1, ln=0, align="C")
    for header in first_columns[1:-1]:
        pdf.cell(w=18, h=9, txt=header, border=1, ln=0, align="C")
    pdf.cell(w=18, h=9, txt=first_columns[-1], border=1, ln=2, align="C")

    pdf.set_font("arial", "", 10)
    for row in range(len(per_game_info)):
        pdf.set_x(16)
        pdf.cell(w=47, h=7, txt=str(per_game_info.loc[row, "Name"]), border=1, ln=0, align="C")
        for column in first_columns[1:-1]:
            pdf.cell(w=18, h=7, txt=str(per_game_info.loc[row, column]), border=1, ln=0, align="C")
        pdf.cell(18, 7, str(per_game_info.loc[row, "PF"]), 1, 2, "C")

    # Second page
    pdf.add_page(orientation="L")
    pdf.set_font("Times", "b", 18)
    pdf.cell(0, 30, "PER-GAME THROWS STATS ANALYSIS (2022)", 0, 2, "L")
    pdf.set_font("Times", "b", 18)
    pdf.set_x(16)
    pdf.cell(w=0, h=15, txt=f"Team: {team_name}", border=0, ln=2, align="L")

    pdf.set_font("arial", "b", 11)
    first_columns = list(per_game_throws_info.columns)
    pdf.set_x(16)
    pdf.cell(w=47, h=9, txt=first_columns[0], border=1, ln=0, align="C")
    for header in first_columns[1:-1]:
        pdf.cell(w=18, h=9, txt=header, border=1, ln=0, align="C")
    pdf.cell(w=18, h=9, txt=first_columns[-1], border=1, ln=2, align="C")

    pdf.set_font("arial", "", 10)
    for row in range(len(per_game_throws_info)):
        pdf.set_x(16)
        pdf.cell(47, 7, str(per_game_throws_info.loc[row, "Name"]), 1, 0, "C")
        for column in first_columns[1:-1]:
            pdf.cell(18, 7, str(per_game_throws_info.loc[row, column]), 1, 0, "C")
        pdf.cell(18, 7, str(per_game_throws_info.loc[row, "2P%"]), 1, 2, "C")

    # Third page (legends)
    pdf.add_page(orientation="L")
    pdf.set_x(16)
    pdf.set_font("Times", "", 15)
    pdf.cell(w=0, h=10, txt="Per-game Stats Legend", border=0, ln=2, align="L")

    pdf.set_font("Times", "", 12)
    cont = 0
    for key, value in legend_1.items():
        cont += 1
        if cont % 3 == 0 or cont == len(legend_1):
            pdf.cell(w=80, h=9, txt=f"{key}: {value}", border=1, ln=2, align="C")
            pdf.set_x(16)
        else:
            pdf.cell(w=80, h=9, txt=f"{key}: {value}", border=1, ln=0, align="C")

    pdf.cell(w=0, h=10, txt="", border=0, ln=2, align="L")
    pdf.set_font("Times", "", 15)
    pdf.cell(w=0, h=10, txt="Per-game Throws Stats Legend", border=0, ln=2, align="L")

    pdf.set_font("Times", "", 12)
    cont = 0
    for key, value in legend_2.items():
        cont += 1
        if cont % 3 == 0 or cont == len(legend_2):
            pdf.cell(w=80, h=9, txt=f"{key}: {value}", border=1, ln=2, align="C")
            pdf.set_x(16)
        else:
            pdf.cell(w=80, h=9, txt=f"{key}: {value}", border=1, ln=0, align="C")

    pdf.output("nba_analysis.pdf", "F")


if __name__ == "__main__":
    # First we ask for the team and generate a pdf with stats
    data, team_name = extract()
    dfs = transform(data)
    per_game_info = dfs[0]
    per_game_throws_info = dfs[1]
    load(per_game_info, per_game_throws_info, team_name)

    # Then we make the prediction for the following match
    soup = nws.extract_scraping()
    prediction, opposing = nws.transform_scraping(soup=soup, team=team_name)
    nws.load_scraping(prediction, team_name, opposing)
