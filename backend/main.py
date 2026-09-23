from fastapi import FastAPI, HTTPException

from api.football_api import (
    get_upcoming_matches,
    get_match,
    get_team_matches,
    get_head_to_head
)

from analytics.team_analysis import (
    analyze_team,
    analyze_head_to_head
)


app = FastAPI(
    title="BetAnalytics IA",
    description=(
        "API de análise estatística "
        "pré-jogo de futebol."
    ),
    version="1.0.0"
)


@app.get("/")
def root():

    return {
        "message": "BetAnalytics IA API",
        "status": "online"
    }


@app.get("/health")
def health():

    return {
        "status": "online",
        "service": "BetAnalytics IA"
    }


@app.get("/matches")
def matches(days: int = 7):

    try:

        if days < 1 or days > 30:

            raise HTTPException(
                status_code=400,
                detail=(
                    "O período deve estar "
                    "entre 1 e 30 dias."
                )
            )

        return get_upcoming_matches(
            days=days
        )

    except HTTPException:
        raise

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:

        raise HTTPException(
            status_code=502,
            detail=str(error)
        )


@app.get(
    "/matches/{match_id}/analysis"
)
def match_analysis(match_id: int):

    try:

        match = get_match(
            match_id
        )

        home_team = match.get(
            "homeTeam",
            {}
        )

        away_team = match.get(
            "awayTeam",
            {}
        )

        home_team_id = home_team.get(
            "id"
        )

        away_team_id = away_team.get(
            "id"
        )

        home_team_name = home_team.get(
            "name"
        )

        away_team_name = away_team.get(
            "name"
        )

        if not home_team_id or not away_team_id:

            raise HTTPException(
                status_code=500,
                detail=(
                    "Não foi possível "
                    "identificar os times "
                    "da partida."
                )
            )

        home_matches = get_team_matches(
            home_team_id,
            limit=10
        )

        away_matches = get_team_matches(
            away_team_id,
            limit=10
        )

        head_to_head_data = get_head_to_head(
            match_id,
            limit=5
        )

        return {

            "match": {

                "id": match.get(
                    "id"
                ),

                "date": match.get(
                    "utcDate"
                ),

                "competition": match.get(
                    "competition",
                    {}
                ).get(
                    "name"
                ),

                "home_team": home_team_name,

                "away_team": away_team_name

            },

            "home_team_analysis":
                analyze_team(
                    home_team_id,
                    home_team_name,
                    home_matches
                ),

            "away_team_analysis":
                analyze_team(
                    away_team_id,
                    away_team_name,
                    away_matches
                ),

            "head_to_head":
                analyze_head_to_head(
                    head_to_head_data
                )

        }

    except HTTPException:
        raise

    except Exception as error:

        raise HTTPException(
            status_code=502,
            detail=str(error)
        )