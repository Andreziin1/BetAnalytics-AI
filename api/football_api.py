import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

BASE_URL = "https://api.football-data.org/v4/competitions/CL/matches"

headers = {
    "X-Auth-Token": API_KEY
}


def get_matches():
    response = requests.get(BASE_URL, headers=headers)

    if response.status_code != 200:
        print("Erro na API:", response.status_code)
        print(response.text)
        return []

    data = response.json()

    print("DEBUG API:")
    print(data)

    matches = data.get("matches", [])

    formatted_matches = []

    for match in matches:
        formatted_match = {
            "competition": match["competition"]["name"],
            "home_team": match["homeTeam"]["name"],
            "away_team": match["awayTeam"]["name"],
            "date": match["utcDate"],
            "status": match["status"],
            "score_home": match["score"]["fullTime"]["home"],
            "score_away": match["score"]["fullTime"]["away"]
        }

        formatted_matches.append(formatted_match)

    return formatted_matches


def get_upcoming_matches():
    matches = get_matches()

    upcoming_matches = []

    for match in matches:
        if match["status"] in ["TIMED", "SCHEDULED"]:
            upcoming_matches.append(match)

    return upcoming_matches


if __name__ == "__main__":
    matches = get_matches()

    print("\nJOGOS ENCONTRADOS:")
    for match in matches:
        print(
            match["status"],
            "-",
            match["home_team"],
            "x",
            match["away_team"],
            "-",
            match["date"]
        )

    print("\nJOGOS FUTUROS:")
    upcoming = get_upcoming_matches()

    for match in upcoming:
        print(
            match["home_team"],
            "x",
            match["away_team"],
            "-",
            match["date"]
        )