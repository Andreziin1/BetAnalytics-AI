def _get_score(match):
    """
    Retorna os gols do mandante e visitante.
    """

    full_time = match.get(
        "score",
        {}
    ).get(
        "fullTime",
        {}
    )

    home_score = full_time.get("home")
    away_score = full_time.get("away")

    return home_score, away_score


def _get_team_result(match, team_id):
    """
    Determina o resultado da partida para o time analisado.
    """

    home_team_id = match.get(
        "homeTeam",
        {}
    ).get("id")

    away_team_id = match.get(
        "awayTeam",
        {}
    ).get("id")

    home_score, away_score = _get_score(match)

    if home_score is None or away_score is None:
        return None

    if team_id == home_team_id:

        if home_score > away_score:
            return "W"

        if home_score == away_score:
            return "D"

        return "L"

    if team_id == away_team_id:

        if away_score > home_score:
            return "W"

        if away_score == home_score:
            return "D"

        return "L"

    return None


def analyze_team(
    team_id,
    team_name,
    matches
):
    """
    Analisa os últimos 10 jogos de um time.
    """

    valid_matches = []

    for match in matches:

        if match.get("status") != "FINISHED":
            continue

        home_score, away_score = _get_score(
            match
        )

        if home_score is None or away_score is None:
            continue

        result = _get_team_result(
            match,
            team_id
        )

        if result is None:
            continue

        valid_matches.append(match)

    valid_matches.sort(
        key=lambda match: match.get(
            "utcDate",
            ""
        ),
        reverse=True
    )

    last_10 = valid_matches[:10]

    wins = 0
    draws = 0
    losses = 0

    goals_scored = 0
    goals_conceded = 0

    recent_matches = []

    for match in last_10:

        home_team = match.get(
            "homeTeam",
            {}
        )

        away_team = match.get(
            "awayTeam",
            {}
        )

        home_score, away_score = _get_score(
            match
        )

        result = _get_team_result(
            match,
            team_id
        )

        if team_id == home_team.get("id"):

            goals_for = home_score
            goals_against = away_score

        else:

            goals_for = away_score
            goals_against = home_score

        goals_scored += goals_for
        goals_conceded += goals_against

        if result == "W":
            wins += 1

        elif result == "D":
            draws += 1

        elif result == "L":
            losses += 1

        recent_matches.append({

            "date": match.get(
                "utcDate"
            ),

            "home_team": home_team.get(
                "name"
            ),

            "away_team": away_team.get(
                "name"
            ),

            "home_score": home_score,

            "away_score": away_score,

            "result": result

        })

    total_matches = len(
        recent_matches
    )

    average_goals_scored = 0
    average_goals_conceded = 0

    if total_matches > 0:

        average_goals_scored = round(
            goals_scored / total_matches,
            2
        )

        average_goals_conceded = round(
            goals_conceded / total_matches,
            2
        )

    return {

        "team_id": team_id,

        "team": team_name,

        "matches_analyzed": total_matches,

        "wins": wins,

        "draws": draws,

        "losses": losses,

        "goals_scored": goals_scored,

        "goals_conceded": goals_conceded,

        "average_goals_scored":
            average_goals_scored,

        "average_goals_conceded":
            average_goals_conceded,

        "form": [
            match["result"]
            for match in recent_matches
        ],

        "last_10": recent_matches

    }


def analyze_head_to_head(data):
    """
    Organiza os últimos 5 confrontos diretos.
    """

    matches = data.get(
        "matches",
        []
    )

    valid_matches = []

    for match in matches:

        home_team = match.get(
            "homeTeam",
            {}
        )

        away_team = match.get(
            "awayTeam",
            {}
        )

        home_score, away_score = _get_score(
            match
        )

        if (
            home_score is None
            or away_score is None
        ):
            continue

        valid_matches.append(match)

    valid_matches.sort(
        key=lambda match: match.get(
            "utcDate",
            ""
        ),
        reverse=True
    )

    valid_matches = valid_matches[:5]

    formatted_matches = []

    for match in valid_matches:

        home_team = match.get(
            "homeTeam",
            {}
        )

        away_team = match.get(
            "awayTeam",
            {}
        )

        home_score, away_score = _get_score(
            match
        )

        formatted_matches.append({

            "date": match.get(
                "utcDate"
            ),

            "home_team": home_team.get(
                "name"
            ),

            "away_team": away_team.get(
                "name"
            ),

            "home_score": home_score,

            "away_score": away_score

        })

    return formatted_matches