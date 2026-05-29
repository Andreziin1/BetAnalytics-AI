def calculate_confidence(probabilities, trend_statistics):

    highest_probability = max(probabilities.values())

    recent_over = trend_statistics["recent_over_2_5"]

    confidence_score = 0

    if highest_probability >= 60:
        confidence_score += 2

    elif highest_probability >= 50:
        confidence_score += 1

    if recent_over >= 70:
        confidence_score += 2

    elif recent_over >= 50:
        confidence_score += 1

    if confidence_score >= 4:

        return {
            "level": "HIGH",
            "score": confidence_score,
            "explanation": "The analysis shows strong statistical consistency."
        }

    elif confidence_score >= 2:

        return {
            "level": "MEDIUM",
            "score": confidence_score,
            "explanation": "The analysis shows moderate statistical consistency."
        }

    else:

        return {
            "level": "LOW",
            "score": confidence_score,
            "explanation": "The analysis shows low statistical consistency."
        }