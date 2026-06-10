def calculate_probabilities(matches):

    total_matches = 0
    home_wins = 0
    away_wins = 0
    draws = 0

    for match in matches:

        home_score = match.get("home_score")
        away_score = match.get("away_score")

        if home_score is None or away_score is None:
            continue

        total_matches += 1

        if home_score > away_score:
            home_wins += 1

        elif away_score > home_score:
            away_wins += 1

        else:
            draws += 1

    if total_matches == 0:
        return {
            "home_win": 0,
            "draw": 0,
            "away_win": 0
        }

    return {
        "home_win": round((home_wins / total_matches) * 100, 2),
        "draw": round((draws / total_matches) * 100, 2),
        "away_win": round((away_wins / total_matches) * 100, 2)
    }