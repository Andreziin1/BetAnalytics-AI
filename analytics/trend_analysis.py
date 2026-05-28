def analyze_recent_trends(matches):

    finished_matches = []

    for match in matches:

        if match["status"] == "FINISHED":

            if match["home_score"] is not None and match["away_score"] is not None:

                finished_matches.append(match)

    recent_matches = finished_matches[-5:]

    total_matches = len(recent_matches)

    if total_matches == 0:

        return {
            "recent_average_goals": 0,
            "recent_over_2_5": 0
        }

    total_goals = 0
    over_2_5 = 0

    for match in recent_matches:

        match_goals = match["home_score"] + match["away_score"]

        total_goals += match_goals

        if match_goals > 2.5:
            over_2_5 += 1

    return {

        "recent_average_goals": round(total_goals / total_matches, 2),

        "recent_over_2_5": round((over_2_5 / total_matches) * 100, 2)

    }