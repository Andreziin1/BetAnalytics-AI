import streamlit as st
import pandas as pd

from api.football_api import (
    get_matches,
    get_upcoming_matches
)

from analytics.probability import calculate_basic_probability
from analytics.goals_analysis import calculate_goal_statistics
from analytics.trend_analysis import analyze_recent_trends
from analytics.suggestions import generate_suggestion
from analytics.confidence import calculate_confidence

# ==================================================
# CONFIGURAÇÃO DA PÁGINA
# ==================================================

st.set_page_config(
    page_title="BetAnalytics IA",
    page_icon="⚽",
    layout="wide"
)

# ==================================================
# CABEÇALHO
# ==================================================

st.title("⚽ BetAnalytics IA")
st.caption("Plataforma de análise estatística esportiva")

# ==================================================
# DADOS
# ==================================================

matches = get_matches()
upcoming_matches = get_upcoming_matches()

# ==================================================
# PARTIDAS ANALISADAS
# ==================================================

st.subheader("📋 Partidas Analisadas")

if matches:

    df_matches = pd.DataFrame(matches)

    st.dataframe(
        df_matches,
        use_container_width=True
    )

else:

    st.warning("Nenhuma partida encontrada.")

# ==================================================
# PRÓXIMAS PARTIDAS
# ==================================================

st.subheader("🔮 Próximas Partidas")

if upcoming_matches:

    df_upcoming = pd.DataFrame(upcoming_matches)

    st.dataframe(
        df_upcoming,
        use_container_width=True
    )

else:

    st.warning("Nenhuma partida futura encontrada.")

# ==================================================
# ANÁLISES
# ==================================================

if matches:

    probabilities = calculate_basic_probability(matches)

    goals_stats = calculate_goal_statistics(matches)

    trends = analyze_recent_trends(matches)

    suggestion = generate_suggestion(probabilities)

    confidence = calculate_confidence(
        probabilities,
        trends
    )

    # ==========================================
    # PROBABILIDADES
    # ==========================================

    st.subheader("📊 Probabilidades")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "🏠 Vitória Mandante",
            f"{probabilities['home_win']}%"
        )

    with col2:
        st.metric(
            "🤝 Empate",
            f"{probabilities['draw']}%"
        )

    with col3:
        st.metric(
            "✈️ Vitória Visitante",
            f"{probabilities['away_win']}%"
        )

    # ==========================================
    # ESTATÍSTICAS DE GOLS
    # ==========================================

    st.subheader("⚽ Estatísticas de Gols")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Média de Gols",
            goals_stats["average_goals"]
        )

    with col2:
        st.metric(
            "Over 2.5",
            f"{goals_stats['over_2_5_percentage']}%"
        )

    with col3:
        st.metric(
            "Under 2.5",
            f"{goals_stats['under_2_5_percentage']}%"
        )

    # ==========================================
    # TENDÊNCIAS
    # ==========================================

    st.subheader("🔥 Tendências Recentes")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Média recente de gols",
            trends["recent_average_goals"]
        )

    with col2:
        st.metric(
            "Over 2.5 recente",
            f"{trends['recent_over_2_5']}%"
        )

    # ==========================================
    # SUGESTÃO
    # ==========================================

    st.subheader("🎯 Sugestão Estatística")

    st.success(
        f"{suggestion['suggestion']} ({suggestion['probability']}%)"
    )

    st.write(
        suggestion["explanation"]
    )

    # ==========================================
    # CONFIANÇA
    # ==========================================

    st.subheader("🧠 Nível de Confiança")

    score = confidence["score"]

    if confidence["level"] == "HIGH":

        st.success(
            f"ALTA (Score: {score})"
        )

    elif confidence["level"] == "MEDIUM":

        st.warning(
            f"MÉDIA (Score: {score})"
        )

    else:

        st.info(
            f"BAIXA (Score: {score})"
        )

    st.write(
        confidence["explanation"]
    )

# ==================================================
# ANÁLISE FUTURA
# ==================================================

st.subheader("🔍 Análise de Jogo Futuro")

if upcoming_matches:

    selected_match = st.selectbox(
        "Escolha uma partida",
        [
            f"{match['home_team']} x {match['away_team']}"
            for match in upcoming_matches
        ]
    )

    st.info(
        f"Partida selecionada: {selected_match}"
    )

else:

    st.warning(
        "Nenhuma partida futura disponível para análise."
    )

# ==================================================
# RODAPÉ
# ==================================================

st.markdown("---")

st.caption(
    "As análises apresentadas são baseadas em dados históricos e probabilidades estatísticas. Não representam garantia de resultado."
)