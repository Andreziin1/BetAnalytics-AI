import streamlit as st

from api.football_api import get_matches, get_upcoming_matches

from analytics.probability import calculate_basic_probability

from analytics.goals_analysis import calculate_goal_statistics

from analytics.trend_analysis import analyze_recent_trends

from analytics.goal_suggestions import generate_goal_suggestion

from analytics.match_prediction import predict_match

from analytics import confidence


st.set_page_config(
    page_title="BetAnalytics IA",
    layout="wide"
)

st.title("⚽ BetAnalytics IA")

st.write("Plataforma de análise estatística esportiva")


matches = get_matches()

upcoming_matches = get_upcoming_matches()


st.subheader("📋 Partidas Analisadas")

if matches:
    matches_table = []

    for match in matches:
        matches_table.append({
            "Mandante": match["home_team"],
            "Visitante": match["away_team"],
            "Data": match["date"],
            "Status": match["status"]
        })

    st.table(matches_table)

else:
    st.warning("Nenhuma partida encontrada.")


st.subheader("🔮 Próximas Partidas")

if upcoming_matches:
    upcoming_table = []

    for match in upcoming_matches:
        upcoming_table.append({
            "Mandante": match["home_team"],
            "Visitante": match["away_team"],
            "Data": match["date"],
            "Status": match["status"]
        })

    st.table(upcoming_table)

else:
    st.warning("Nenhuma partida futura encontrada.")


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

with col1:
    st.metric(
        label="🏠 Vitória Mandante",
        value=f"{probabilities['home_win']}%"
    )

with col2:
    st.metric(
        label="🤝 Empate",
        value=f"{probabilities['draw']}%"
    )

with col3:
    st.metric(
        label="✈️ Vitória Visitante",
        value=f"{probabilities['away_win']}%"
    )


st.subheader("⚽ Estatísticas de Gols")

col4, col5, col6 = st.columns(3)

with col4:
    st.metric(
        label="Média de Gols",
        value=goal_statistics["average_goals"]
    )

with col5:
    st.metric(
        label="Over 2.5",
        value=f"{goal_statistics['over_2_5_percentage']}%"
    )

with col6:
    st.metric(
        label="Under 2.5",
        value=f"{goal_statistics['under_2_5_percentage']}%"
    )


st.subheader("🔥 Tendências Recentes")

col7, col8 = st.columns(2)

with col7:
    st.metric(
        label="Média recente de gols",
        value=trend_statistics["recent_average_goals"]
    )

with col8:
    st.metric(
        label="Over 2.5 recente",
        value=f"{trend_statistics['recent_over_2_5']}%"
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


st.subheader("🔍 Análise de Jogo Futuro")

if upcoming_matches:

    selected_match = st.selectbox(
        "Selecione uma partida futura",
        upcoming_matches,
        format_func=lambda match: f"{match['home_team']} vs {match['away_team']}"
    )

    prediction = predict_match(
        selected_match,
        matches,
        probabilities,
        goal_statistics,
        trend_statistics,
        confidence_result
    )

    st.write(f"**Jogo:** {prediction['match']}")

    col9, col10, col11 = st.columns(3)

    with col9:
        st.metric(
            "Vitória Mandante",
            f"{prediction['home_win_probability']}%"
        )

    with col10:
        st.metric(
            "Empate",
            f"{prediction['draw_probability']}%"
        )

    with col11:
        st.metric(
            "Vitória Visitante",
            f"{prediction['away_win_probability']}%"
        )

    st.metric(
        "Over 2.5 gols",
        f"{prediction['over_2_5_probability']}%"
    )

    st.success(f"Sugestão: {prediction['suggestion']}")

    st.write(prediction["explanation"])

    st.info(f"Nível de confiança: {prediction['confidence_level']}")


    st.subheader("⚔️ Confronto Direto")

    st.write(f"Jogos encontrados: {prediction['head_to_head']['total_matches']}")
    st.write(f"Vitórias mandante: {prediction['head_to_head']['home_team_wins']}")
    st.write(f"Vitórias visitante: {prediction['head_to_head']['away_team_wins']}")
    st.write(f"Empates: {prediction['head_to_head']['draws']}")
    st.write(f"Média de gols no confronto: {prediction['head_to_head']['average_goals']}")
    st.write(prediction["head_to_head"]["explanation"])


    st.subheader("📈 Forma Recente")

    col12, col13 = st.columns(2)

    with col12:

        st.markdown(f"### 🏠 {prediction['home_team']}")

        st.write(f"Vitórias: {prediction['home_team_form']['wins']}")
        st.write(f"Empates: {prediction['home_team_form']['draws']}")
        st.write(f"Derrotas: {prediction['home_team_form']['losses']}")
        st.write(f"Gols marcados: {prediction['home_team_form']['goals_scored']}")
        st.write(f"Gols sofridos: {prediction['home_team_form']['goals_conceded']}")

    with col13:

        st.markdown(f"### ✈️ {prediction['away_team']}")

        st.write(f"Vitórias: {prediction['away_team_form']['wins']}")
        st.write(f"Empates: {prediction['away_team_form']['draws']}")
        st.write(f"Derrotas: {prediction['away_team_form']['losses']}")
        st.write(f"Gols marcados: {prediction['away_team_form']['goals_scored']}")
        st.write(f"Gols sofridos: {prediction['away_team_form']['goals_conceded']}")

else:

    st.warning("Nenhuma partida futura disponível para análise.")


st.warning(
    "As análises apresentadas são baseadas em "
    "dados históricos e probabilidades estatísticas. "
    "Não representam garantia de resultado."
)