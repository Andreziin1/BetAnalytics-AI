import requests

API_KEY = "171a4dacd5ca454a986e2eabaa48a2ed"

BASE_URL = "https://api.football-data.org/v4/competitions/PL/matches?status=FINISHED"

headers = {
    "X-Auth-Token": API_KEY
}


def get_matches():

    response = requests.get(BASE_URL, headers=headers)

    if response.status_code == 200:

        data = response.json()

        matches = data.get("matches", [])

        formatted_matches = []

        for match in matches[:10]:

            formatted_match = {

                "competition": match["competition"]["name"],

                "home_team": match["homeTeam"]["name"],

                "away_team": match["awayTeam"]["name"],

                "date": match["utcDate"],

                "status": match["status"],

                "home_score": match["score"]["fullTime"]["home"],

                "away_score": match["score"]["fullTime"]["away"]

            }

            formatted_matches.append(formatted_match)

        return formatted_matches

    else:

        print(f"Error: {response.status_code}")

        return []


if __name__ == "__main__":

    matches = get_matches()

    for match in matches:

        print("=" * 50)

        print(f"Competition: {match['competition']}")

        print(f"Match: {match['home_team']} vs {match['away_team']}")

        print(f"Date: {match['date']}")

        print(f"Status: {match['status']}")

        print(f"Score: {match['home_score']} x {match['away_score']}")