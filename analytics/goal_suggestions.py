def generate_goal_suggestion(goal_statistics, trend_statistics):

    over_percentage = goal_statistics["over_2_5_percentage"]
    recent_over_percentage = trend_statistics["recent_over_2_5"]

    if recent_over_percentage >= 70:
        return {
            "market": "Over 2.5 goals",
            "probability": recent_over_percentage,
            "explanation": "Over 2.5 goals occurred frequently in the most recent analyzed matches."
        }

    elif over_percentage >= 60:
        return {
            "market": "Over 2.5 goals",
            "probability": over_percentage,
            "explanation": "Over 2.5 goals showed a strong tendency in the overall analyzed matches."
        }

    else:
        return {
            "market": "No strong goal market found",
            "probability": 0,
            "explanation": "The analyzed matches did not show a strong enough goal trend."
        }