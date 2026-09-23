import os
from datetime import datetime, timedelta, timezone

import requests
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("API_KEY")

BASE_URL = "https://api.football-data.org/v4"

HEADERS = {
    "X-Auth-Token": API_KEY
}


# Competições disponíveis no Free Tier
DEFAULT_COMPETITIONS = [
    "PL",   # Premier League
    "PD",   # La Liga
    "SA",   # Serie A
    "BL1",  # Bundesliga
    "FL1",  # Ligue 1
    "CL",   # Champions League
    "PPL",  # Primeira Liga
    "BSA",  # Brasileirão
    "DED"   # Eredivisie
]


def _get(endpoint, params=None):
    """
    Realiza uma requisição GET para a API football-data.org.
    """

    if not API_KEY:
        raise RuntimeError(
            "API_KEY não encontrada no arquivo .env"
        )

    url = f"{BASE_URL}{endpoint}"

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            params=params,
            timeout=15
        )

    except requests.RequestException as error:

        raise RuntimeError(
            f"Não foi possível conectar à API football-data.org: {error}"
        )

    if response.status_code == 200:
        return response.json()

    if response.status_code == 400:
        raise RuntimeError(
            f"Requisição inválida para a API football-data.org: "
            f"{response.text}"
        )

    if response.status_code == 403:
        raise RuntimeError(
            "A API football-data.org recusou o acesso a este recurso "
            "para a assinatura atual."
        )

    if response.status_code == 404:
        raise RuntimeError(
            "Recurso não encontrado na API football-data.org."
        )

    if response.status_code == 429:
        raise RuntimeError(
            "Limite de chamadas da API football-data.org atingido. "
            "Tente novamente em alguns segundos."
        )

    raise RuntimeError(
        f"Erro na API football-data.org: "
        f"{response.status_code}"
    )


def _get_upcoming_matches_window(
    date_from,
    date_to,
    competitions
):
    """
    Busca partidas dentro de uma janela de no máximo 10 dias.

    A API football-data.org possui uma limitação de período
    para determinadas consultas.
    """

    competition_codes = ",".join(competitions)

    data = _get(
        "/matches",
        params={
            "competitions": competition_codes,
            "dateFrom": date_from.isoformat(),
            "dateTo": date_to.isoformat()
        }
    )

    return data.get("matches", [])


def get_upcoming_matches(days=7, competitions=None):
    """
    Retorna partidas futuras das competições selecionadas.

    O usuário pode solicitar até 30 dias.
    Internamente, as consultas são divididas em janelas
    de no máximo 10 dias para respeitar a API.
    """

    if competitions is None:
        competitions = DEFAULT_COMPETITIONS

    if days < 1:
        raise ValueError(
            "O número de dias deve ser maior que zero."
        )

    if days > 30:
        raise ValueError(
            "O período máximo permitido é de 30 dias."
        )

    today = datetime.now(
        timezone.utc
    ).date()

    end_date = today + timedelta(
        days=days
    )

    all_matches = []

    current_start = today

    while current_start <= end_date:

        current_end = min(
            current_start + timedelta(days=9),
            end_date
        )

        matches = _get_upcoming_matches_window(
            current_start,
            current_end,
            competitions
        )

        all_matches.extend(matches)

        current_start = current_end + timedelta(days=1)

    formatted_matches = []

    seen_ids = set()

    for match in all_matches:

        match_id = match.get("id")

        if match_id in seen_ids:
            continue

        seen_ids.add(match_id)

        status = match.get("status")

        # Apenas partidas que ainda irão acontecer
        if status not in [
            "SCHEDULED",
            "TIMED"
        ]:
            continue

        home_team = match.get(
            "homeTeam",
            {}
        )

        away_team = match.get(
            "awayTeam",
            {}
        )

        competition = match.get(
            "competition",
            {}
        )

        formatted_matches.append({

            "id": match_id,

            "competition": {
                "id": competition.get("id"),
                "name": competition.get("name"),
                "code": competition.get("code")
            },

            "home_team": {
                "id": home_team.get("id"),
                "name": home_team.get("name")
            },

            "away_team": {
                "id": away_team.get("id"),
                "name": away_team.get("name")
            },

            "date": match.get("utcDate"),

            "status": status
        })

    formatted_matches.sort(
        key=lambda match: match.get(
            "date",
            ""
        )
    )

    return formatted_matches


def get_match(match_id):
    """
    Retorna os dados de uma partida específica.
    """

    return _get(
        f"/matches/{match_id}"
    )


def get_team_matches(team_id, limit=10):
    """
    Retorna as partidas finalizadas de um time.
    """

    if limit < 1:
        limit = 1

    if limit > 100:
        limit = 100

    data = _get(
        f"/teams/{team_id}/matches",
        params={
            "status": "FINISHED",
            "limit": limit
        }
    )

    return data.get(
        "matches",
        []
    )


def get_head_to_head(match_id, limit=5):
    """
    Retorna os confrontos diretos anteriores da partida.
    """

    data = _get(
        f"/matches/{match_id}/head2head",
        params={
            "limit": limit
        }
    )

    return data