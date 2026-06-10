import requests
import os

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

BASE_URL = "https://api.football-data.org/v4/competitions/PL/matches?status=FINISHED"

UPCOMING_URL = "https://api.football-data.org/v4/competitions/WC/matches?status=TIMED"

headers = {
    "X-Auth-Token": API_KEY
}


def get_matches():

    response = requests.get(
        BASE_URL,
        headers=headers
    )

    if response.status_code != 200:
        print("Erro:", response.status_code)
        return []

    data = response.json()

    matches = data.get("matches", [])

    formatted_matches = []

    for match in matches[:20]:

        home_score = match["score"]["fullTime"]["home"]
        away_score = match["score"]["fullTime"]["away"]

        if home_score is None or away_score is None:
            continue

        formatted_matches.append({

            "competition": match["competition"]["name"],

            "home_team": match["homeTeam"]["name"],

            "away_team": match["awayTeam"]["name"],

            "date": match["utcDate"],

            "status": match["status"],

            "score_home": home_score,

            "score_away": away_score
        })

    return formatted_matches


def get_upcoming_matches():

    response = requests.get(
        UPCOMING_URL,
        headers=headers
    )

    if response.status_code != 200:
        print("Erro:", response.status_code)
        return []

    data = response.json()

    matches = data.get("matches", [])

    formatted_matches = []

    for match in matches[:20]:

        formatted_matches.append({

            "competition": match["competition"]["name"],

            "home_team": match["homeTeam"]["name"],

            "away_team": match["awayTeam"]["name"],

            "date": match["utcDate"],

            "status": match["status"]
        })

    return formatted_matches