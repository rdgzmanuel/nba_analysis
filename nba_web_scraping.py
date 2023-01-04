import requests
import re
from bs4 import BeautifulSoup


def extract_scraping():
    # We extract the data from sportytrader
    r = requests.get("https://www.sportytrader.es/pronosticos/baloncesto/usa/nba-306/").text
    soup = BeautifulSoup(r, "lxml")
    return soup


def transform_scraping(soup, team):
    pattern = re.compile(r">.*<")
    spans = soup.find_all("span")

    prediction = None
    run = True
    i = 0
    while run and i < len(spans):
        if team in str(spans[i]):
            # We read the two teams facing each other
            span_game = str(spans[i])
            matches = pattern.finditer(span_game)
            for match in matches:
                game = match.group(0)[1:-1]  # To read only the information we want
                teams = game.split(" - ")
                if teams[0] == team:
                    team_number = "1"
                    opposing = teams[1]
                else:
                    team_number = "2"
                    opposing = teams[0]

            # We read the prediction. Again, the info we want is surrounded by >...<
            # so we can use the same re pattern
            span_1 = str(spans[i + 2])
            matches = pattern.finditer(span_1)
            for match in matches:
                share_1 = match.group(0)[1:-1]
            span_2 = str(spans[i + 4])
            matches = pattern.finditer(span_2)
            for match in matches:
                share_2 = match.group(0)[1:-1]

            if team_number == "1":
                if share_1 > share_2:
                    prediction = "lose"
                elif share_1 < share_2:
                    prediction = "win"
                else:
                    prediction = "draw"
            else:
                if share_1 < share_2:
                    prediction = "lose"
                elif share_1 > share_2:
                    prediction = "win"
                else:
                    prediction = "draw"
        i += 1
    return prediction, opposing


def load_scraping(prediction, team, opposing):
    if prediction is not None:
        print(f"According to the data extracted from sportytrader, {team} are expected to {prediction} their next match agains {opposing}.")
    else:
        print("The selected team does not play any time soon.")
