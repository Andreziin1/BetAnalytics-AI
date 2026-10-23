"""Pure, deterministic calculations. Scores refer to regular time only."""
from collections import Counter
from datetime import datetime, timezone

def parse_date(value):
    if not isinstance(value, str):
        return None
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return result.astimezone(timezone.utc) if result.tzinfo else None
    except (ValueError, OverflowError):
        return None

def positive_id(value):
    return type(value) is int and value > 0

def identity(match):
    if not isinstance(match, dict) or not positive_id(match.get("id")):
        return False
    for field in ("homeTeam", "awayTeam"):
        team = match.get(field)
        if not isinstance(team, dict) or not positive_id(team.get("id")):
            return False
        if not isinstance(team.get("name"), str) or not team["name"].strip():
            return False
    return match["homeTeam"]["id"] != match["awayTeam"]["id"] and parse_date(match.get("utcDate")) is not None

def score(match):
    data = match.get("score")
    if not isinstance(data, dict):
        return None
    # fullTime can include extra time/penalties. Never infer a 90-minute score.
    field = "fullTime" if data.get("duration") == "REGULAR" else "regularTime"
    values = data.get(field)
    if not isinstance(values, dict):
        return None
    pair = values.get("home"), values.get("away")
    return pair if all(type(x) is int and x >= 0 for x in pair) else None

def select_matches(matches, team_id, cutoff, limit=10, opponent_id=None, exclude_id=None):
    reasons = Counter()
    candidates = {}
    conflicts = set()
    for match in matches:
        if not identity(match):
            reasons["invalid_identity_or_date"] += 1
            continue
        mid = match["id"]
        if mid == exclude_id or parse_date(match["utcDate"]) >= cutoff:
            reasons["outside_cutoff"] += 1
            continue
        ids = {match["homeTeam"]["id"], match["awayTeam"]["id"]}
        if team_id not in ids or (opponent_id is not None and ids != {team_id, opponent_id}):
            reasons["wrong_teams"] += 1
            continue
        if match.get("status") != "FINISHED":
            reasons["not_finished"] += 1
            continue
        if score(match) is None:
            reasons["invalid_or_missing_regular_time_score"] += 1
            continue
        competition = match.get("competition")
        if not isinstance(competition, dict) or not positive_id(competition.get("id")):
            reasons["missing_competition"] += 1
            continue
        if competition.get("type") not in {"LEAGUE", "LEAGUE_CUP", "CUP", "SUPER_CUP", "PLAYOFFS"}:
            reasons["unsupported_competition_type"] += 1
            continue
        if mid in candidates:
            old = candidates[mid]
            fingerprint = lambda m: (parse_date(m["utcDate"]), m["homeTeam"]["id"], m["awayTeam"]["id"], score(m), m["competition"]["id"])
            if fingerprint(old) != fingerprint(match):
                conflicts.add(mid)
                reasons["conflicting_duplicate"] += 1
            else:
                reasons["duplicate"] += 1
        else:
            candidates[mid] = match
    valid = [m for mid, m in candidates.items() if mid not in conflicts]
    valid.sort(key=lambda m: (parse_date(m["utcDate"]), m["id"]), reverse=True)
    selected = valid[:limit]
    return selected, dict(reasons)

def format_match(match, team_id):
    home, away = score(match)
    at_home = match["homeTeam"]["id"] == team_id
    gf, ga = (home, away) if at_home else (away, home)
    season = match.get("season") or {}
    return {
        "id": match["id"], "date": parse_date(match["utcDate"]).isoformat(),
        "competition": match["competition"],
        "season": season.get("startDate") if isinstance(season, dict) else None,
        "home_team": match["homeTeam"]["name"], "away_team": match["awayTeam"]["name"],
        "home_team_id": match["homeTeam"]["id"], "away_team_id": match["awayTeam"]["id"],
        "home_score": home, "away_score": away,
        "venue": "HOME" if at_home else "AWAY",
        "goals_for": gf, "goals_against": ga,
        "result": "W" if gf > ga else "D" if gf == ga else "L",
    }

def summarize(rows):
    n = len(rows)
    counts = Counter(m["result"] for m in rows)
    gf = sum(m["goals_for"] for m in rows)
    ga = sum(m["goals_against"] for m in rows)
    return {
        "matches_analyzed": n, "wins": counts["W"], "draws": counts["D"], "losses": counts["L"],
        "goals_scored": gf if n else None, "goals_conceded": ga if n else None,
        "average_goals_scored": round(gf / n, 2) if n else None,
        "average_goals_conceded": round(ga / n, 2) if n else None,
        "win_percentage": round(100 * counts["W"] / n, 2) if n else None,
        "draw_percentage": round(100 * counts["D"] / n, 2) if n else None,
        "loss_percentage": round(100 * counts["L"] / n, 2) if n else None,
    }

def analyze_team(team_id, team_name, matches, *, cutoff, exclude_id=None):
    selected, discarded = select_matches(matches, team_id, cutoff, exclude_id=exclude_id)
    rows = [format_match(m, team_id) for m in selected]
    return {
        "team_id": team_id, "team": team_name, **summarize(rows),
        "form": [r["result"] for r in rows], "last_10": rows,
        "sample_complete": len(rows) == 10, "discarded": discarded,
        "home": summarize([r for r in rows if r["venue"] == "HOME"]),
        "away": summarize([r for r in rows if r["venue"] == "AWAY"]),
    }

def analyze_head_to_head(matches, home_id, away_id, *, cutoff, exclude_id=None):
    selected, discarded = select_matches(matches, home_id, cutoff, limit=5, opponent_id=away_id, exclude_id=exclude_id)
    rows = [format_match(m, home_id) for m in selected]
    total = sum(r["home_score"] + r["away_score"] for r in rows)
    return {
        "matches": rows, "matches_analyzed": len(rows), "sample_complete": len(rows) == 5,
        "home_team_wins": sum(r["result"] == "W" for r in rows),
        "draws": sum(r["result"] == "D" for r in rows),
        "away_team_wins": sum(r["result"] == "L" for r in rows),
        "total_goals": total if rows else None,
        "average_total_goals": round(total / len(rows), 2) if rows else None,
        "discarded": discarded,
    }

