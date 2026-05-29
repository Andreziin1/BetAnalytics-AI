def analyze_head_to_head(matches, home_team, away_team):

    direct_matches = []

    for match in matches:

        if match["status"] == "FINISHED":

            if (
                match["home_team"] == home_team and match["away_team"] == away_team
            ) or (
                match["home_team"] == away_team and match["away_team"] == home_team
            ):

                direct_matches.append(match)

    total_matches = len(direct_matches)

    if total_matches == 0:

        return {
            "total_matches": 0,
            "home_team_wins": 0,
            "away_team_wins": 0,
            "draws": 0,
            "average_goals": 0,
            "explanation": "Nenhum confronto direto recente encontrado nos dados analisados."
        }

    home_team_wins = 0
    away_team_wins = 0
    draws = 0
    total_goals = 0

    for match in direct_matches:

        home_score = match["home_score"]
        away_score = match["away_score"]

        total_goals += home_score + away_score

        if match["home_team"] == home_team:

            if home_score > away_score:
                home_team_wins += 1
            elif home_score < away_score:
                away_team_wins += 1
            else:
                draws += 1

        else:

            if away_score > home_score:
                home_team_wins += 1
            elif away_score < home_score:
                away_team_wins += 1
            else:
                draws += 1

    return {
        "total_matches": total_matches,
        "home_team_wins": home_team_wins,
        "away_team_wins": away_team_wins,
        "draws": draws,
        "average_goals": round(total_goals / total_matches, 2),
        "explanation": "Análise baseada nos confrontos diretos encontrados entre as equipes."
    }