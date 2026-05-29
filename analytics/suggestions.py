def generate_suggestion(probabilities):

    best_option = max(probabilities, key=probabilities.get)
    best_value = probabilities[best_option]

    suggestions_text = {
        "home_win": "Home team victory",
        "draw": "Draw",
        "away_win": "Away team victory"
    }

    explanations_text = {
        "home_win": "The home team victory has the highest calculated probability based on the analyzed matches.",
        "draw": "The draw has the highest calculated probability based on the analyzed matches.",
        "away_win": "The away team victory has the highest calculated probability based on the analyzed matches."
    }

    return {
        "suggestion": suggestions_text[best_option],
        "probability": best_value,
        "explanation": explanations_text[best_option]
    }