import streamlit as st

from api.football_api import get_matches

from analytics.probability import calculate_basic_probability

from analytics.goals_analysis import calculate_goal_statistics

from analytics.trend_analysis import analyze_recent_trends

from analytics.goal_suggestions import generate_goal_suggestion

from analytics import confidence


st.set_page_config(
    page_title="BetAnalytics IA",
    layout="wide"
)

st.title("⚽ BetAnalytics IA")

st.write("Plataforma de análise estatística esportiva")


matches = get_matches()

probabilities = calculate_basic_probability(matches)

goal_statistics = calculate_goal_statistics(matches)

trend_statistics = analyze_recent_trends(matches)

goal_suggestion = generate_goal_suggestion(
    goal_statistics,
    trend_statistics
)

confidence_result = confidence.calculate_confidence(
    probabilities,
    trend_statistics
)


st.subheader("📊 Probabilidades")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Vitória Mandante",
    f"{probabilities['home_win']}%"
)

col2.metric(
    "Empate",
    f"{probabilities['draw']}%"
)

col3.metric(
    "Vitória Visitante",
    f"{probabilities['away_win']}%"
)


st.subheader("⚽ Estatísticas de Gols")

col4, col5, col6 = st.columns(3)

col4.metric(
    "Média de Gols",
    goal_statistics["average_goals"]
)

col5.metric(
    "Over 2.5",
    f"{goal_statistics['over_2_5_percentage']}%"
)

col6.metric(
    "Under 2.5",
    f"{goal_statistics['under_2_5_percentage']}%"
)


st.subheader("🔥 Tendências Recentes")

st.write(
    f"Média recente de gols: "
    f"{trend_statistics['recent_average_goals']}"
)

st.write(
    f"Over 2.5 recente: "
    f"{trend_statistics['recent_over_2_5']}%"
)


st.subheader("🎯 Sugestão Estatística")

st.success(
    f"{goal_suggestion['market']} "
    f"({goal_suggestion['probability']}%)"
)

st.write(goal_suggestion["explanation"])


st.subheader("🧠 Nível de Confiança")

st.info(
    f"{confidence_result['level']} "
    f"(Score: {confidence_result['score']})"
)

st.write(confidence_result["explanation"])


st.warning(
    "As análises apresentadas são baseadas em "
    "dados históricos e probabilidades estatísticas. "
    "Não representam garantia de resultado."
)