from backend.analytics.team_analysis import summarize

def test_metrics_include_goalless_draw_and_use_actual_sample():
    rows = [
        {"result":"D","goals_for":0,"goals_against":0},
        {"result":"W","goals_for":2,"goals_against":1},
        {"result":"L","goals_for":0,"goals_against":3},
    ]
    s = summarize(rows)
    assert s["both_teams_scored"] == 1
    assert s["both_teams_scored_percentage"] == 33.33
    assert s["clean_sheets"] == 1
    assert s["clean_sheet_percentage"] == 33.33
    assert s["average_total_goals"] == 2

def test_missing_sample_is_not_zero():
    s = summarize([])
    for key in ["both_teams_scored", "both_teams_scored_percentage", "clean_sheets", "clean_sheet_percentage", "average_total_goals"]:
        assert s[key] is None
