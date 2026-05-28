from api.football_api import get_matches
from analytics.probability import calculate_basic_probability
from analytics.suggestions import generate_suggestion


matches = get_matches()
probabilities = calculate_basic_probability(matches)

suggestion = generate_suggestion(probabilities)

print("\nSTATISTICAL SUGGESTION\n")
print(f"Suggestion: {suggestion['suggestion']}")
print(f"Probability: {suggestion['probability']}%")
print(f"Explanation: {suggestion['explanation']}")

print("\nMATCHES\n")

for match in matches:
    print(f"{match['home_team']} vs {match['away_team']}")

print("\nPROBABILITIES\n")
print(f"Home win: {probabilities['home_win']}%")
print(f"Draw: {probabilities['draw']}%")
print(f"Away win: {probabilities['away_win']}%")