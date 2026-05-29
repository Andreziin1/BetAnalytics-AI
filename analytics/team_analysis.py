def analyze_team_performance(matches, team_name):

    finished_matches = []

    for match in matches:

        if match["status"] == "FINISHED":

            if match["home_score"] is not None and match["away_score"] is not None:

                if (
                    match["home_team"] == team_name
                    or match["away_team"] == team_name
                ):

                    finished_matches.append(match)

    total_matches = len(finished_matches)

    if total_matches == 0:

        return {
            "team": team_name,
            "matches": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "average_goals_scored": 0
        }

    wins = 0
    draws = 0
    losses = 0
    total_goals_scored = 0

    for match in finished_matches:

        home_score = match["home_score"]
        away_score = match["away_score"]

        if match["home_team"] == team_name:

            total_goals_scored += home_score

            if home_score > away_score:
                wins += 1
            elif home_score == away_score:
                draws += 1
            else:
                losses += 1

        else:

            total_goals_scored += away_score

            if away_score > home_score:
                wins += 1
            elif away_score == home_score:
                draws += 1
            else:
                losses += 1

    return {
        "team": team_name,
        "matches": total_matches,
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "average_goals_scored": round(total_goals_scored / total_matches, 2)
    }