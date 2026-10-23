"""Bounded cache and rate limiter, shared by one application process."""

from collections import OrderedDict, deque
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from threading import Lock
from time import monotonic

import requests

from backend.analytics.team_analysis import identity, parse_date


DEFAULT_COMPETITIONS = (
    "PL", "PD", "SA", "BL1", "FL1", "CL", "PPL", "BSA", "DED"
)

COMPETITION_NAMES = {
    "PL": "Premier League",
    "PD": "La Liga",
    "SA": "Serie A",
    "BL1": "Bundesliga",
    "FL1": "Ligue 1",
    "CL": "Champions League",
    "PPL": "Primeira Liga",
    "BSA": "Brasileirão Série A",
    "DED": "Eredivisie",
}

BASE_URL = "https://api.football-data.org/v4"


class ProviderError(Exception):
    def __init__(self, code, message, status=502, retry_after=None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status
        self.retry_after = retry_after


class FootballClient:
    def __init__(self, settings, session=None, clock=monotonic):
        self.settings = settings
        self.session = session or requests.Session()
        self.clock = clock
        self.lock = Lock()
        self.cache = OrderedDict()
        self.calls = deque()
        self.blocked_until = 0

    def close(self):
        self.session.close()

    def get(self, endpoint, params=None):
        if not self.settings.api_key:
            raise ProviderError(
                "not_configured",
                "Configure API_KEY no servidor.",
                503,
            )

        key = (endpoint, tuple(sorted((params or {}).items())))

        with self.lock:
            now = self.clock()
            cached = self.cache.get(key)

            if cached and now - cached[0] < self.settings.cache_ttl:
                self.cache.move_to_end(key)
                return deepcopy(cached[1])

            if now < self.blocked_until:
                raise ProviderError("rate_limit", "Limite da fonte de dados atingido. Tente novamente.",
                                    429, max(1, int(self.blocked_until - now) + 1))

            while self.calls and now - self.calls[0] >= 60:
                self.calls.popleft()

            if len(self.calls) >= self.settings.requests_per_minute:
                retry = max(1, int(60 - (now - self.calls[0])) + 1)
                raise ProviderError(
                    "rate_limit",
                    "Limite temporário de consultas. Tente novamente.",
                    429,
                    retry,
                )

            self.calls.append(now)

            try:
                response = self.session.get(
                    BASE_URL + endpoint,
                    params=params,
                    headers={"X-Auth-Token": self.settings.api_key},
                    timeout=(20, 20),
                    allow_redirects=False,
                )
            except requests.Timeout:
                raise ProviderError(
                    "timeout",
                    "A fonte de dados demorou para responder.",
                    504,
                ) from None
            except requests.RequestException:
                raise ProviderError(
                    "connection_error",
                    "Não foi possível consultar a fonte de dados.",
                    502,
                ) from None

            status = response.status_code

            if status != 200:
                # O fornecedor também usa HTTP 400 para token inválido.
                # Classificar a mensagem conhecida sem expor o corpo externo.
                if status == 400:
                    try:
                        failure = response.json()
                    except ValueError:
                        failure = {}
                    if isinstance(failure, dict) and failure.get("message") == "Your API token is invalid.":
                        raise ProviderError(
                            "provider_auth", "Credencial da fonte de dados inválida. Confira API_KEY no .env do backend.", 503
                        )
                errors = {
                    400: (
                        "provider_bad_request",
                        "A fonte rejeitou os parâmetros da consulta (HTTP 400).",
                        502,
                    ),
                    401: (
                        "provider_auth",
                        "Credencial da fonte de dados inválida.",
                        503,
                    ),
                    403: (
                        "provider_forbidden",
                        "Recurso indisponível para a assinatura configurada.",
                        503,
                    ),
                    404: (
                        "not_found",
                        "Recurso não encontrado na fonte de dados.",
                        404,
                    ),
                    429: (
                        "rate_limit",
                        "Limite da fonte de dados atingido. Tente novamente.",
                        429,
                    ),
                }

                code, message, public_status = errors.get(
                    status,
                    (
                        "provider_error",
                        "A fonte de dados recusou a consulta.",
                        502,
                    ),
                )

                retry = None
                if status == 429:
                    raw = response.headers.get("Retry-After", "60")
                    retry = (
                        min(3600, max(1, int(raw)))
                        if raw.isdigit()
                        else 60
                    )

                if retry is not None:
                    self.blocked_until = self.clock() + retry

                raise ProviderError(
                    code, message, public_status, retry
                )

            try:
                data = response.json()
            except ValueError:
                raise ProviderError(
                    "invalid_payload",
                    "Resposta inválida da fonte de dados.",
                ) from None

            if not isinstance(data, dict):
                raise ProviderError(
                    "invalid_payload",
                    "Formato inesperado da fonte de dados.",
                )

            if "matches" in data and not isinstance(data["matches"], list):
                raise ProviderError(
                    "invalid_payload",
                    "Lista de partidas inválida.",
                )

            data["_retrieved_at"] = datetime.now(timezone.utc).isoformat()

            self.cache[key] = (self.clock(), deepcopy(data))
            self.cache.move_to_end(key)

            while len(self.cache) > 256:
                self.cache.popitem(last=False)

            return data

    def match_list(self, endpoint, params):
        data = self.get(endpoint, params)

        if not isinstance(data.get("matches"), list):
            raise ProviderError(
                "invalid_payload",
                "A fonte não retornou uma lista de partidas.",
            )

        return data

    def upcoming(self, days, competitions, now):
        start = now.date()
        end = start + timedelta(days=days)

        rows = []
        seen = set()
        discarded = 0
        warnings = []
        retrieved_at = {}
        first_error = None

        for code in competitions:
            try:
                data = self.match_list(
                    f"/competitions/{code}/matches",
                    {"dateFrom": start.isoformat(), "dateTo": end.isoformat()},
                )
            except ProviderError as error:
                if error.code in {"provider_auth", "not_configured"}:
                    raise
                first_error = first_error or error
                warning = {"code": error.code, "section": code, "message": error.message}
                if error.retry_after:
                    warning["retry_after"] = error.retry_after
                warnings.append(warning)
                continue
            retrieved_at[code] = data.get("_retrieved_at")

            for match in data["matches"]:
                if not identity(match):
                    discarded += 1
                    continue

                date = parse_date(match["utcDate"])
                competition = match.get("competition")

                if (
                    not isinstance(competition, dict)
                    or competition.get("code") != code
                ):
                    continue

                if (
                    match["id"] in seen
                    or match.get("status") not in ("SCHEDULED", "TIMED")
                ):
                    continue

                if date < now or date.date() >= end:
                    continue

                seen.add(match["id"])

                rows.append(
                    {
                        "id": match["id"],
                        "date": date.isoformat(),
                        "status": match["status"],
                        "competition": competition,
                        "home_team": match["homeTeam"],
                        "away_team": match["awayTeam"],
                    }
                )

        if not retrieved_at and first_error:
            raise first_error

        return {
            "warnings": warnings, "partial": bool(warnings), "retrieved_at": retrieved_at,
            "matches": sorted(
                rows,
                key=lambda match: (match["date"], match["id"]),
            ),
            "discarded": discarded,
            "timezone": "UTC",
            "days": days,
        }

    def team_history(self, team_id, cutoff):
        start = cutoff.date() - timedelta(
            days=self.settings.history_days
        )

        return self.match_list(
            f"/teams/{team_id}/matches",
            {
                "status": "FINISHED",
                "dateFrom": start.isoformat(),
                # dateTo é exclusivo; o corte exato por horário ocorre na análise.
                "dateTo": (cutoff.date() + timedelta(days=1)).isoformat(),
                "limit": 500,
            },
        )

    def h2h(self, match_id):
        return self.match_list(
            f"/matches/{match_id}/head2head",
            {"limit": 100},
        )
