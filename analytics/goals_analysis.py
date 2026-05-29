def calculate_goal_statistics(matches):

    finished_matches = []

    for match in matches:
        if match["status"] == "FINISHED":
            if match["home_score"] is not None and match["away_score"] is not None:
                finished_matches.append(match)

    total_matches = len(finished_matches)

    if total_matches == 0:
        return {
            "average_goals": 0,
            "over_2_5_percentage": 0,
            "under_2_5_percentage": 0
        }

    total_goals = 0
    over_2_5 = 0
    under_2_5 = 0

    for match in finished_matches:
        match_goals = match["home_score"] + match["away_score"]

        total_goals += match_goals

        if match_goals > 2.5:
            over_2_5 += 1
        else:
            under_2_5 += 1

    return {
        "average_goals": round(total_goals / total_matches, 2),
        "over_2_5_percentage": round((over_2_5 / total_matches) * 100, 2),
        "under_2_5_percentage": round((under_2_5 / total_matches) * 100, 2)
    }