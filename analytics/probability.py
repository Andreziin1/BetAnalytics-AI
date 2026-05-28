def calculate_basic_probability(matches):

    finished_matches = []

    for match in matches:

        if match["status"] == "FINISHED":

            if match["home_score"] is not None and match["away_score"] is not None:

                finished_matches.append(match)

    total_matches = len(finished_matches)

    if total_matches == 0:

        return {
            "home_win": 0,
            "draw": 0,
            "away_win": 0
        }

    home_wins = 0
    draws = 0
    away_wins = 0

    for match in finished_matches:

        home_score = match["home_score"]
        away_score = match["away_score"]

        if home_score > away_score:
            home_wins += 1

        elif home_score == away_score:
            draws += 1

        else:
            away_wins += 1

    probabilities = {

        "home_win": round((home_wins / total_matches) * 100, 2),

        "draw": round((draws / total_matches) * 100, 2),

        "away_win": round((away_wins / total_matches) * 100, 2)

    }

    return probabilities