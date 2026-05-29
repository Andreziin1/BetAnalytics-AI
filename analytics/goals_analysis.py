def calculate_goal_statistics(matches):

    total_goals = 0
    total_matches = 0
    over_2_5_matches = 0
    under_2_5_matches = 0

    for match in matches:

        home_score = match.get("score_home")
        away_score = match.get("score_away")

        if home_score is None or away_score is None:
            continue

        goals = home_score + away_score

        total_goals += goals
        total_matches += 1

        if goals > 2.5:
            over_2_5_matches += 1
        else:
            under_2_5_matches += 1

    if total_matches == 0:
        return {
            "average_goals": 0,
            "over_2_5_percentage": 0,
            "under_2_5_percentage": 0
        }

    return {
        "average_goals": round(total_goals / total_matches, 2),
        "over_2_5_percentage": round((over_2_5_matches / total_matches) * 100, 2),
        "under_2_5_percentage": round((under_2_5_matches / total_matches) * 100, 2)
    }