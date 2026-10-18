from copy import deepcopy
from datetime import datetime, timezone
from unittest.mock import Mock
import pytest
import requests
from fastapi.testclient import TestClient
from backend.config import Settings
from backend.main import create_app
from backend.api.football_api import FootballClient, ProviderError
from backend.analytics.team_analysis import analyze_team, analyze_head_to_head, parse_date

CUT = datetime(2026, 10, 10, 12, tzinfo=timezone.utc)

def game(mid=1, date="2026-10-01T12:00:00Z", home=1, away=2, goals=(2, 1), status="FINISHED"):
    return {"id": mid, "utcDate": date, "status": status,
            "homeTeam": {"id": home, "name": f"Time {home}"},
            "awayTeam": {"id": away, "name": f"Time {away}"},
            "competition": {"id": 2021, "code": "PL", "type": "LEAGUE", "name": "Liga"},
            "score": {"duration": "REGULAR", "fullTime": {"home": goals[0], "away": goals[1]}}}

def analyze(rows):
    return analyze_team(1, "Time 1", rows, cutoff=CUT)

def test_results_and_denominators():
    result = analyze([game(1), game(2, home=3, away=1, goals=(1, 1)), game(3, goals=(0, 3))])
    assert (result["wins"], result["draws"], result["losses"]) == (1, 1, 1)
    assert result["goals_scored"] == 3 and result["goals_conceded"] == 5
    assert result["average_goals_scored"] == 1
    assert result["average_goals_conceded"] == 1.67
    assert result["win_percentage"] == 33.33
    assert result["home"]["matches_analyzed"] == 2
    assert result["away"]["matches_analyzed"] == 1

def test_empty_is_unknown_not_zero():
    result = analyze([])
    assert result["matches_analyzed"] == 0
    assert result["average_goals_scored"] is None
    assert result["goals_scored"] is None
    assert result["win_percentage"] is None

def test_six_matches_report_real_denominator():
    result = analyze([game(i, goals=(0, 0)) for i in range(1, 7)])
    assert result["matches_analyzed"] == 6
    assert result["sample_complete"] is False
    assert result["average_goals_scored"] == 0
    assert result["draw_percentage"] == 100

def test_h2h_limit_and_order():
    rows = [game(i, f"2026-09-{i:02}T12:00:00Z") for i in range(1, 9)]
    result = analyze_head_to_head(rows, 1, 2, cutoff=CUT)
    assert [r["id"] for r in result["matches"]] == [8, 7, 6, 5, 4]
    assert result["sample_complete"]

def test_target_id_excluded_even_with_wrong_old_date():
    result = analyze_team(1, "Time 1", [game()], cutoff=CUT, exclude_id=1)
    assert result["matches_analyzed"] == 0

def test_missing_competition_and_friendly_excluded():
    one, two = game(), game(2)
    one["competition"] = None
    two["competition"]["type"] = "FRIENDLY"
    assert analyze([one, two])["matches_analyzed"] == 0

@pytest.mark.parametrize("goals", [(None, 0), (-1, 2), ("2", 1), (True, 0), (1.5, 0)])
def test_invalid_scores(goals):
    assert analyze([game(goals=goals)])["matches_analyzed"] == 0

@pytest.mark.parametrize("status", ["SCHEDULED", "TIMED", "IN_PLAY", "POSTPONED", "CANCELLED"])
def test_only_finished(status):
    assert analyze([game(status=status)])["matches_analyzed"] == 0

def test_temporal_cutoff_and_timezone():
    rows = [game(1, "2026-10-10T09:00:00-03:00"), game(2, "2026-10-11T12:00:00Z"), game(3)]
    assert [m["id"] for m in analyze(rows)["last_10"]] == [3]

def test_invalid_structure_never_crashes():
    assert analyze([None, [], {}, {"id": 2, "homeTeam": None}, game(date="bad"), game(home=3, away=4)])["matches_analyzed"] == 0

def test_dedup_and_conflict():
    one = game()
    assert analyze([one, deepcopy(one)])["matches_analyzed"] == 1
    assert analyze([one, game(goals=(4, 1))])["matches_analyzed"] == 0

def test_last_ten_order():
    rows = [game(i, f"2026-09-{i:02}T12:00:00Z") for i in range(1, 16)]
    result = analyze(rows)
    assert [m["id"] for m in result["last_10"]] == list(range(15, 5, -1))
    assert result["sample_complete"]

def test_missing_duration_and_extra_time():
    extra = game()
    extra["score"]["duration"] = "EXTRA_TIME"
    assert analyze([extra])["matches_analyzed"] == 0
    extra["score"]["regularTime"] = {"home": 1, "away": 1}
    assert analyze([extra])["draws"] == 1

def test_h2h_checks_pair_and_status():
    rows = [game(), game(2, home=2, away=1), game(3, home=1, away=3), game(4, status="IN_PLAY"), game()]
    result = analyze_head_to_head(rows, 1, 2, cutoff=CUT)
    assert result["matches_analyzed"] == 2
    assert result["home_team_wins"] == result["away_team_wins"] == 1
    assert result["average_total_goals"] == 3

def response(status=200, data=None):
    r = Mock(status_code=status, headers={})
    r.json.return_value = data if data is not None else {"matches": []}
    return r

def provider(reply=None, **kwargs):
    session = Mock()
    session.get.return_value = reply or response()
    return FootballClient(Settings(api_key="test-secret", **kwargs), session=session), session

@pytest.mark.parametrize("status,public", [(400,502),(401,503),(403,503),(404,404),(429,429),(500,502),(302,502)])
def test_provider_error_mapping(status, public):
    client, session = provider(response(status))
    with pytest.raises(ProviderError) as error:
        client.get("/matches")
    assert error.value.status == public
    assert "test-secret" not in str(error.value)

@pytest.mark.parametrize("error,status", [(requests.Timeout(),504),(requests.ConnectionError("secret"),502)])
def test_network_errors_sanitized(error, status):
    client, session = provider()
    session.get.side_effect = error
    with pytest.raises(ProviderError) as caught:
        client.get("/matches")
    assert caught.value.status == status and "secret" not in str(caught.value)

@pytest.mark.parametrize("data", [[], {"matches": None}, {"matches": "bad"}])
def test_bad_payload(data):
    client, _ = provider(response(data=data))
    with pytest.raises(ProviderError):
        client.get("/matches")

def test_invalid_json():
    client, session = provider()
    session.get.return_value.json.side_effect = ValueError("secret")
    with pytest.raises(ProviderError):
        client.get("/matches")

def test_provider_400_invalid_token_is_auth_error():
    client, _ = provider(response(400, {'message': 'Your API token is invalid.', 'errorCode': 400}))
    with pytest.raises(ProviderError) as caught:
        client.get('/competitions/PL/matches')
    assert caught.value.code == 'provider_auth'
    assert caught.value.status == 503
    assert 'test-secret' not in str(caught.value)

def test_placeholder_key_is_not_configured(monkeypatch):
    monkeypatch.setenv('API_KEY', 'SUA_CHAVE_AQUI')
    settings = Settings.from_env()
    assert settings.api_key == ''
    with TestClient(create_app(settings)) as http:
        assert http.get('/health').json()['api_configured'] is False
        r = http.get('/matches?competitions=PL')
        assert r.status_code == 503
        assert r.json()['error']['code'] == 'not_configured'

def test_cache_and_expiration():
    client, session = provider(cache_ttl=10)
    clock = [0]
    client.clock = lambda: clock[0]
    first = client.get("/matches")
    first["matches"].append("mutation")
    assert client.get("/matches")["matches"] == []
    assert session.get.call_count == 1
    clock[0] = 11
    client.get("/matches")
    assert session.get.call_count == 2

def test_quota_and_recovery():
    client, session = provider(requests_per_minute=1, cache_ttl=0)
    clock = [0]
    client.clock = lambda: clock[0]
    client.get("/one")
    with pytest.raises(ProviderError) as error:
        client.get("/two")
    assert error.value.status == 429 and error.value.retry_after
    clock[0] = 61
    client.get("/two")

def test_upcoming_competition_route_and_window():
    client, session = provider()
    session.get.return_value = response(data={"matches": [
        game(1, "2026-10-10T18:00:00Z", status="TIMED"),
        game(2, "2026-10-10T11:00:00Z", status="TIMED"),
        game(3, "2026-11-09T00:00:00Z", status="TIMED"), game(4)]})
    result = client.upcoming(30, ("PL",), CUT)
    assert [m["id"] for m in result["matches"]] == [1]
    assert session.get.call_count == 1
    assert session.get.call_args.args[0].endswith('/competitions/PL/matches')
    assert 'competitions' not in session.get.call_args.kwargs['params']

def test_history_date_filter():
    client, session = provider()
    client.team_history(1, CUT)
    params = session.get.call_args.kwargs["params"]
    assert params["dateTo"] == "2026-10-11"
    assert params["status"] == "FINISHED" and params["limit"] == 500

def test_history_keeps_same_day_before_cutoff_only():
    client, session = provider()
    rows = [game(1, '2026-10-10T09:00:00Z'), game(2, '2026-10-10T14:00:00Z')]
    def upstream(url, **kwargs):
        # Simula o limite exclusivo documentado pelo fornecedor.
        end = kwargs['params']['dateTo']
        return response(data={'matches': [m for m in rows if m['utcDate'][:10] < end]})
    session.get.side_effect = upstream
    data = client.team_history(1, CUT)
    result = analyze(data['matches'])
    assert [m['id'] for m in result['last_10']] == [1]

def test_league_cup_is_official():
    row = game()
    row['competition']['type'] = 'LEAGUE_CUP'
    assert analyze([row])['matches_analyzed'] == 1

def fake_client():
    client = Mock()
    client.get.return_value = game(999, "2026-10-09T12:00:00Z")
    client.team_history.return_value = {"matches": [game(), game(2, "2026-10-10T10:00:00Z")]}
    client.h2h.return_value = {"matches": [game()]}
    return client

def test_analysis_route_and_historical_cutoff():
    client = fake_client()
    with TestClient(create_app(Settings(api_key="test"), client, lambda: CUT)) as http:
        r = http.get("/matches/999/analysis")
    assert r.status_code == 200
    data = r.json()
    assert data["home_team_analysis"]["matches_analyzed"] == 1
    assert data["metadata"]["cutoff"] == "2026-10-09T12:00:00+00:00"
    assert data["warnings"]

def test_partial_h2h_failure():
    client = fake_client()
    client.h2h.side_effect = ProviderError("provider_forbidden", "Indisponível.", 503)
    with TestClient(create_app(Settings(api_key="test"), client, lambda: CUT)) as http:
        data = http.get("/matches/999/analysis").json()
    assert data["home_team_analysis"]["matches_analyzed"] == 1
    assert not data["head_to_head"]["available"]
    assert data["metadata"]["partial"]

@pytest.mark.parametrize("url", ["/matches?days=0", "/matches?days=31", "/matches?days=abc", "/matches/-1/analysis", "/matches?competitions=FAKE"])
def test_route_validation(url):
    client = fake_client()
    with TestClient(create_app(Settings(), client)) as http:
        assert http.get(url).status_code == 422
    client.upcoming.assert_not_called()

def test_health_without_secret():
    with TestClient(create_app(Settings())) as http:
        assert http.get("/health").json()["api_configured"] is False
        competitions = http.get("/competitions").json()
        assert competitions["competitions"][0] == {"code": "PL", "name": "Premier League"}
        assert "BSA" in competitions["codes"]
        assert http.get("/matches").status_code == 503
        assert http.get("/openapi.json").status_code == 200

def test_cors():
    with TestClient(create_app(Settings())) as http:
        r = http.get("/health", headers={"Origin": "http://localhost:5173"})
        assert r.headers["access-control-allow-origin"] == "http://localhost:5173"
        r = http.get("/health", headers={"Origin": "https://unknown.example"})
        assert "access-control-allow-origin" not in r.headers

def test_unknown_exception_is_sanitized():
    client = fake_client()
    client.get.side_effect = RuntimeError("private-token")
    with TestClient(create_app(Settings(), client), raise_server_exceptions=False) as http:
        r = http.get("/matches/1/analysis")
    assert r.status_code == 500
    assert "private-token" not in r.text

