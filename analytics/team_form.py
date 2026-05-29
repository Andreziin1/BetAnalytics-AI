def analyze_team_form(matches, team_name):

    wins = 0
    draws = 0
    losses = 0
    goals_scored = 0
    goals_conceded = 0
    games_analyzed = 0

    for match in matches:

        home_team = match.get("home_team")
        away_team = match.get("away_team")

        home_score = match.get("score_home")
        away_score = match.get("score_away")

        if home_score is None or away_score is None:
            continue

        if team_name != home_team and team_name != away_team:
            continue

        games_analyzed += 1

        if team_name == home_team:
            goals_scored += home_score
            goals_conceded += away_score

            if home_score > away_score:
                wins += 1
            elif home_score == away_score:
                draws += 1
            else:
                losses += 1

        elif team_name == away_team:
            goals_scored += away_score
            goals_conceded += home_score

            if away_score > home_score:
                wins += 1
            elif away_score == home_score:
                draws += 1
            else:
                losses += 1

    return {
        "team": team_name,
        "games_analyzed": games_analyzed,
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "goals_scored": goals_scored,
        "goals_conceded": goals_conceded
    }