def analyze_recent_trends(matches):

    recent_matches = matches[-5:]

    total_recent_matches = 0
    recent_over_2_5 = 0
    recent_under_2_5 = 0
    total_recent_goals = 0

    for match in recent_matches:

        home_score = match.get("home_score")
        away_score = match.get("away_score")

        if home_score is None or away_score is None:
            continue

        goals = home_score + away_score

        total_recent_goals += goals
        total_recent_matches += 1

        if goals > 2.5:
            recent_over_2_5 += 1
        else:
            recent_under_2_5 += 1

    if total_recent_matches == 0:
        return {
            "recent_average_goals": 0,
            "recent_over_2_5": 0,
            "recent_under_2_5": 0
        }

    return {
        "recent_average_goals": round(total_recent_goals / total_recent_matches, 2),
        "recent_over_2_5": round((recent_over_2_5 / total_recent_matches) * 100, 2),
        "recent_under_2_5": round((recent_under_2_5 / total_recent_matches) * 100, 2)
    }