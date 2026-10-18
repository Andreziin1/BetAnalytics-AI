"""Run from project root: python -m uvicorn backend.main:app --reload."""
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Annotated
from fastapi import FastAPI, Path, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from backend.config import Settings
from backend.api.football_api import FootballClient, ProviderError, DEFAULT_COMPETITIONS, COMPETITION_NAMES
from backend.analytics.team_analysis import identity, parse_date, analyze_team, analyze_head_to_head

logger = logging.getLogger("betanalytics")

def create_app(settings=None, client=None, now_fn=None):
    settings = settings or Settings.from_env()
    client = client or FootballClient(settings)
    now_fn = now_fn or (lambda: datetime.now(timezone.utc))

    @asynccontextmanager
    async def lifespan(app):
        yield
        client.close()

    app = FastAPI(title="BetAnalytics IA", version="1.1.0",
                  description="Análise descritiva pré-jogo de futebol. Sem previsões.", lifespan=lifespan)
    app.add_middleware(CORSMiddleware, allow_origins=list(settings.cors_origins),
                       allow_methods=["GET"], allow_headers=["Content-Type"], allow_credentials=False)

    @app.exception_handler(ProviderError)
    async def provider_error(request, error):
        headers = {"Retry-After": str(error.retry_after)} if error.retry_after else {}
        return JSONResponse(status_code=error.status, headers=headers,
            content={"error": {"code": error.code, "message": error.message}})

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, error):
        return JSONResponse(status_code=422, content={"error": {
            "code": "validation_error", "message": "Parâmetros inválidos.",
            "fields": [{"location": list(e["loc"]), "message": e["msg"]} for e in error.errors()]}})

    @app.exception_handler(Exception)
    async def unexpected_error(request, error):
        logger.error("Erro interno: %s", type(error).__name__)
        return JSONResponse(status_code=500, content={"error": {
            "code": "internal_error", "message": "Falha interna ao processar a solicitação."}})

    @app.get("/")
    def root():
        return {"message": "BetAnalytics IA API", "version": "1.1.0", "docs": "/docs"}

    @app.get("/health")
    def health():
        return {"status": "online", "service": "BetAnalytics IA", "api_configured": bool(settings.api_key)}

    @app.get("/competitions")
    def competitions():
        return {
            "competitions": [{"code": code, "name": COMPETITION_NAMES[code]} for code in DEFAULT_COMPETITIONS],
            "codes": DEFAULT_COMPETITIONS,
            "note": "Cobertura depende da assinatura da fonte.",
        }

    @app.get("/matches")
    def matches(days: Annotated[int, Query(ge=1, le=30)] = 7,
                competitions: Annotated[str | None, Query(max_length=100)] = None):
        codes = tuple(dict.fromkeys(c.strip().upper() for c in competitions.split(","))) if competitions else DEFAULT_COMPETITIONS
        if any(c not in DEFAULT_COMPETITIONS for c in codes):
            raise ProviderError("invalid_competitions", "Competição inválida. Consulte /competitions.", 422)
        return client.upcoming(days, codes, now_fn())

    @app.get("/matches/{match_id}/analysis")
    def analysis(match_id: Annotated[int, Path(gt=0)]):
        match = client.get(f"/matches/{match_id}")
        if not identity(match) or match["id"] != match_id:
            raise ProviderError("invalid_match", "A fonte retornou uma partida inválida.")
        now = now_fn()
        cutoff = min(now, parse_date(match["utcDate"]))
        home, away = match["homeTeam"], match["awayTeam"]
        warnings = []
        sources = {"match": match.get("_retrieved_at")}
        results = []
        for side, team in (("home", home), ("away", away)):
            try:
                data = client.team_history(team["id"], cutoff)
                result = analyze_team(team["id"], team["name"], data["matches"], cutoff=cutoff, exclude_id=match_id)
                sources[side] = data.get("_retrieved_at")
                if len(data["matches"]) >= 500:
                    warnings.append({"code": "history_limit", "section": side, "message": "A fonte atingiu o limite de 500 registros; cobertura pode ser incompleta."})
            except ProviderError as error:
                if error.code in {"provider_auth", "not_configured"}:
                    raise
                result = analyze_team(team["id"], team["name"], [], cutoff=cutoff)
                warnings.append({"code": error.code, "section": side, "message": error.message})
                result["available"] = False
            else:
                result["available"] = True
            if not result["sample_complete"]:
                warnings.append({"code": "insufficient_history", "section": side, "message": f'Somente {result["matches_analyzed"]} jogos válidos disponíveis.'})
            results.append(result)
        try:
            data = client.h2h(match_id)
            h2h = analyze_head_to_head(data["matches"], home["id"], away["id"], cutoff=cutoff, exclude_id=match_id)
            h2h["available"] = True
            sources["head_to_head"] = data.get("_retrieved_at")
            if len(data["matches"]) >= 100:
                warnings.append({"code": "h2h_limit", "section": "head_to_head", "message": "Consulta limitada a 100 confrontos candidatos."})
        except ProviderError as error:
            if error.code in {"provider_auth", "not_configured"}:
                raise
            h2h = analyze_head_to_head([], home["id"], away["id"], cutoff=cutoff)
            h2h["available"] = False
            warnings.append({"code": error.code, "section": "head_to_head", "message": error.message})
        if not h2h["sample_complete"]:
            warnings.append({"code": "insufficient_history", "section": "head_to_head", "message": f'Somente {h2h["matches_analyzed"]} confrontos válidos disponíveis.'})
        for side, result in zip(("home", "away", "head_to_head"), [*results, h2h]):
            if result["discarded"]:
                warnings.append({"code": "discarded_records", "section": side, "message": "Registros excluídos; consulte discarded."})
        return {
            "match": {"id": match_id, "date": match["utcDate"], "status": match.get("status"),
                      "competition": match.get("competition"), "home_team": home, "away_team": away},
            "home_team_analysis": results[0], "away_team_analysis": results[1], "head_to_head": h2h,
            "metadata": {"source": "football-data.org", "generated_at": now.isoformat(),
                         "cutoff": cutoff.isoformat(), "timezone": "UTC", "retrieved_at": sources,
                         "history_days": settings.history_days, "score_basis": "regular_time",
                         "form_order": "newest_first", "competition_policy": "official_competitions_combined",
                         "partial": bool(warnings),
                         "historical_caveat": "Dados atuais filtrados por data; não são snapshots históricos do fornecedor."},
            "warnings": warnings,
        }
    return app

app = create_app()

