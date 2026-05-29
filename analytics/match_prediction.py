from analytics.head_to_head import analyze_head_to_head

from analytics.team_form import analyze_team_form


def predict_match(
    match,
    matches,
    probabilities,
    goal_statistics,
    trend_statistics,
    confidence_result
):

    home_team = match["home_team"]

    away_team = match["away_team"]

    head_to_head = analyze_head_to_head(
        matches,
        home_team,
        away_team
    )

    home_team_form = analyze_team_form(
        matches,
        home_team
    )

    away_team_form = analyze_team_form(
        matches,
        away_team
    )

    prediction = {
        "match": f"{home_team} vs {away_team}",
        "home_team": home_team,
        "away_team": away_team,
        "home_win_probability": probabilities["home_win"],
        "draw_probability": probabilities["draw"],
        "away_win_probability": probabilities["away_win"],
        "over_2_5_probability": goal_statistics["over_2_5_percentage"],
        "recent_over_2_5": trend_statistics["recent_over_2_5"],
        "confidence_level": confidence_result["level"],
        "head_to_head": head_to_head,
        "home_team_form": home_team_form,
        "away_team_form": away_team_form,
        "suggestion": "",
        "explanation": ""
    }

    if (
        home_team_form["wins"]
        > away_team_form["wins"]
    ):

        prediction["suggestion"] = "Vitória do mandante"

        prediction["explanation"] = (
            "O mandante apresenta melhor forma recente."
        )

    elif (
        away_team_form["wins"]
        > home_team_form["wins"]
    ):

        prediction["suggestion"] = "Vitória do visitante"

        prediction["explanation"] = (
            "O visitante apresenta melhor forma recente."
        )

    elif (
        head_to_head["total_matches"] > 0
        and head_to_head["home_team_wins"]
        > head_to_head["away_team_wins"]
    ):

        prediction["suggestion"] = "Vitória do mandante"

        prediction["explanation"] = (
            "O mandante apresenta vantagem nos confrontos diretos."
        )

    elif trend_statistics["recent_over_2_5"] >= 70:

        prediction["suggestion"] = "Over 2.5 gols"

        prediction["explanation"] = (
            "A tendência recente mostra alta ocorrência de jogos com mais de 2.5 gols."
        )

    else:

        prediction["suggestion"] = "Nenhuma sugestão forte encontrada"

        prediction["explanation"] = (
            "Os dados analisados não apresentam uma tendência estatística forte o suficiente."
        )

    return prediction