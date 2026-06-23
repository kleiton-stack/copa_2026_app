"""
App web do modelo preditivo da Copa 2026.

Rode localmente com:
    streamlit run app.py

Publique de graca no Streamlit Community Cloud (veja README.md).
"""

import pandas as pd
import streamlit as st

from modelo import (
    Config, ModeloCopa,
    RATING_PADRAO, FIXTURES_PADRAO, RESULTADOS_PADRAO,
)

st.set_page_config(page_title="Modelo Copa 2026", page_icon="⚽", layout="wide")

# ---------------------------------------------------------------------------
# Cache: a simulacao so re-roda quando algum parametro muda.
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner=False)
def build_modelo(rating_tuple, n_sim, dc_rho, w_prior, c, host_boost, opp_adjust):
    cfg = Config(
        n_sim=n_sim, n_path=n_sim, dc_rho=dc_rho, w_prior=w_prior, c=c,
        use_host_boost=host_boost, opponent_adjust=opp_adjust,
    )
    return ModeloCopa(rating=dict(rating_tuple), config=cfg)


@st.cache_data(show_spinner=False)
def roda_grupos(rating_tuple, n_sim, dc_rho, w_prior, c, host_boost, opp_adjust):
    m = build_modelo(rating_tuple, n_sim, dc_rho, w_prior, c, host_boost, opp_adjust)
    bar = st.progress(0.0, text="Simulando fase de grupos...")
    res = m.simula_fase_grupos(n_sim, progress=lambda f: bar.progress(min(1.0, f)))
    bar.empty()
    pos, top2, best3, qual = res
    return {
        "grupos": m.relatorio_grupos(pos, top2, best3, qual),
        "ranking": m.ranking_geral(top2, best3, qual),
        "standings": m.tabela_standings(),
        "restantes": m.tabela_jogos_restantes(),
        "forcas": m.tabela_forcas(),
    }


@st.cache_data(show_spinner=False)
def roda_backtest(rating_tuple, dc_rho, w_prior, c, host_boost, opp_adjust):
    m = build_modelo(rating_tuple, 5_000, dc_rho, w_prior, c, host_boost, opp_adjust)
    return m.backtest()


@st.cache_data(show_spinner=False)
def roda_path(rating_tuple, n_sim, dc_rho, w_prior, c, host_boost, opp_adjust, time):
    m = build_modelo(rating_tuple, n_sim, dc_rho, w_prior, c, host_boost, opp_adjust)
    bar = st.progress(0.0, text=f"Simulando o caminho de {time}...")
    res = m.simula_path(time=time, n=n_sim, progress=lambda f: bar.progress(min(1.0, f)))
    bar.empty()
    return res


# ---------------------------------------------------------------------------
# Sidebar: parametros
# ---------------------------------------------------------------------------

st.sidebar.header("⚙️ Parametros")

n_sim = st.sidebar.select_slider(
    "Numero de simulacoes (Monte Carlo)",
    options=[5_000, 10_000, 20_000, 50_000, 100_000],
    value=20_000,
    help="Mais simulacoes = mais precisao, porem mais lento.",
)
dc_rho = st.sidebar.slider("Ajuste Dixon-Coles (rho)", -0.20, 0.05, -0.08, 0.01,
                           help="Negativo aumenta empates baixos (0-0, 1-1).")
w_prior = st.sidebar.slider("Peso do prior (jogos-fantasma)", 0.5, 8.0, 3.0, 0.5,
                            help="Quanto o rating FIFA pesa frente aos jogos ja disputados.")
c = st.sidebar.slider("Sensibilidade ao rating (C)", 0.0005, 0.0040, 0.0017, 0.0001,
                      format="%.4f")
host_boost = st.sidebar.checkbox("Boost para anfitrioes (MEX/EUA/CAN)", value=True)
opp_adjust = st.sidebar.checkbox("Ajustar gols pela forca do adversario", value=True)

st.sidebar.markdown("---")
st.sidebar.caption("Ratings editaveis na aba **Ratings**. Modelo: Poisson dupla + Dixon-Coles, "
                   "simulacao de Monte Carlo da fase de grupos e do mata-mata.")

# Ratings editaveis guardados em session_state
if "ratings" not in st.session_state:
    st.session_state.ratings = dict(RATING_PADRAO)

rating_tuple = tuple(sorted(st.session_state.ratings.items()))
params = (rating_tuple, n_sim, dc_rho, w_prior, c, host_boost, opp_adjust)

# ---------------------------------------------------------------------------
# Cabecalho
# ---------------------------------------------------------------------------

st.title("⚽ Modelo Preditivo — Copa do Mundo 2026")
st.caption("Simulacao de Monte Carlo a partir dos resultados ja disputados. "
           "Probabilidades de classificacao por grupo, melhores terceiros e caminho no mata-mata.")

(aba_grupos, aba_ranking, aba_jogos, aba_backtest,
 aba_path, aba_forcas, aba_ratings) = st.tabs(
    ["🏁 Por grupo", "📊 Ranking geral", "🎲 Jogos restantes", "🔎 Backtesting",
     "🇧🇷 Caminho de um time", "💪 Forcas", "✏️ Ratings"]
)

dados = roda_grupos(*params)

# ----- Por grupo -----------------------------------------------------------
with aba_grupos:
    st.subheader("Probabilidades de classificacao por grupo")
    grupos = dados["grupos"]
    cols = st.columns(2)
    for i, grupo in enumerate(sorted(grupos.keys())):
        with cols[i % 2]:
            st.markdown(f"**Grupo {grupo}**")
            df = pd.DataFrame(grupos[grupo])
            st.dataframe(
                df.style.background_gradient(subset=["Classif. %"], cmap="Greens"),
                hide_index=True, use_container_width=True,
            )

    st.markdown("### Standings atuais")
    for grupo in sorted(dados["standings"].keys()):
        s = dados["standings"][grupo]
        st.markdown(f"**Grupo {grupo}** · _Restantes: {', '.join(s['restantes']) or 'nenhum'}_")
        st.dataframe(pd.DataFrame(s["linhas"]), hide_index=True, use_container_width=True)

# ----- Ranking geral -------------------------------------------------------
with aba_ranking:
    st.subheader("Ranking geral por probabilidade de classificacao")
    df = pd.DataFrame(dados["ranking"])
    st.dataframe(
        df.style.background_gradient(subset=["Classif. %"], cmap="Greens"),
        hide_index=True, use_container_width=True, height=600,
    )
    st.bar_chart(df.set_index("Selecao")["Classif. %"])

# ----- Jogos restantes -----------------------------------------------------
with aba_jogos:
    st.subheader("Probabilidade dos jogos restantes da fase de grupos")
    st.dataframe(pd.DataFrame(dados["restantes"]), hide_index=True, use_container_width=True, height=600)

# ----- Backtesting ---------------------------------------------------------
with aba_backtest:
    st.subheader("Backtesting — o que o modelo previa x o que aconteceu")
    st.caption(
        "Validacao **fora da amostra (walk-forward)**: cada jogo ja disputado foi previsto "
        "usando um modelo treinado apenas com as rodadas anteriores. A rodada 1 usa so o "
        "rating (sem jogos previos), entao o modelo nunca 've' o resultado que esta prevendo."
    )
    bt = roda_backtest(rating_tuple, dc_rho, w_prior, c, host_boost, opp_adjust)
    met = bt["metrics"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Acertos de resultado (1X2)", f"{met['acuracia']}%",
              help=f"{met['acertos']} de {met['n']} jogos com o favorito do modelo correto.")
    c2.metric("Brier score", met["brier"], help="Erro das probabilidades (0 = perfeito). Menor e melhor.")
    c3.metric("Log-loss", met["logloss"], help="Penaliza confianca errada. Menor e melhor.")
    c4.metric("Erro medio de gols/time", met["mae_gols"], help="Diferenca media entre gols esperados e reais.")

    st.markdown("#### Acuracia por rodada")
    df_rod = pd.DataFrame(bt["por_rodada"])
    cg1, cg2 = st.columns([1, 2])
    with cg1:
        st.dataframe(df_rod, hide_index=True, use_container_width=True)
    with cg2:
        st.bar_chart(df_rod.set_index("Rodada")["Acuracia %"])
    st.caption("A rodada 1 e' so rating (chute inicial); o modelo aprende e melhora nas rodadas seguintes.")

    st.markdown("#### Jogo a jogo: previsto x real")
    df_bt = pd.DataFrame(bt["jogos"])
    st.dataframe(
        df_bt.style.apply(
            lambda row: ["background-color: #1b3a1b" if row["Acertou"] == "✅"
                         else "background-color: #3a1b1b"] * len(row),
            axis=1,
        ),
        hide_index=True, use_container_width=True, height=600,
    )
    st.caption("V1 = vitoria do 1o time do confronto · V2 = vitoria do 2o time. "
               "'Favorito' = resultado mais provavel segundo o modelo naquele momento.")

# ----- Caminho de um time --------------------------------------------------
with aba_path:
    st.subheader("Caminho no mata-mata")
    m_aux = build_modelo(*params)
    time = st.selectbox("Escolha a selecao", m_aux.all_teams,
                        index=m_aux.all_teams.index("Brasil") if "Brasil" in m_aux.all_teams else 0)
    if st.button("Simular caminho", type="primary"):
        res = roda_path(*params, time)
        n = res["n_valid"]
        st.caption(f"{n:,} simulacoes validas".replace(",", "."))

        fases = [("R32", "16 avos"), ("R16", "Oitavas"),
                 ("QF", "Quartas"), ("SF", "Semifinal"), ("FINAL", "Final"),
                 ("CAMPEAO", "Campeao"), ("VICE", "Vice")]
        cols = st.columns(len(fases))
        for col, (k, label) in zip(cols, fases):
            col.metric(label, f"{res['reached'][k] / n * 100:.1f}%")

        st.markdown("#### Probabilidade de alcancar cada fase")
        df_fase = pd.DataFrame([{"Fase": label, "%": round(res["reached"][k] / n * 100, 2)}
                                for k, label in fases])
        st.bar_chart(df_fase.set_index("Fase")["%"])

        nome_fase = {"R32": "16 avos", "R16": "Oitavas", "QF": "Quartas",
                     "SF": "Semifinal", "FINAL": "Final"}
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Adversarios mais provaveis por fase")
            for stage in ["R32", "R16", "QF", "SF", "FINAL"]:
                denom = res["reached"][stage]
                if denom == 0:
                    continue
                top = res["opponent_by_stage"][stage].most_common(5)
                st.markdown(f"**{nome_fase[stage]}**")
                st.dataframe(pd.DataFrame(
                    [{"Adversario": o, "%": round(cc / denom * 100, 1)} for o, cc in top]),
                    hide_index=True, use_container_width=True)
        with c2:
            st.markdown("#### Caminhos mais frequentes")
            paths = res["path_counter"].most_common(12)
            st.dataframe(pd.DataFrame(
                [{"%": round(cc / n * 100, 2), "Caminho": " → ".join(p)} for p, cc in paths]),
                hide_index=True, use_container_width=True)
    else:
        st.info("Escolha uma selecao e clique em **Simular caminho**.")

# ----- Forcas --------------------------------------------------------------
with aba_forcas:
    st.subheader("Forcas estimadas apos atualizacao")
    st.dataframe(pd.DataFrame(dados["forcas"]), hide_index=True, use_container_width=True, height=600)

# ----- Ratings editaveis ---------------------------------------------------
with aba_ratings:
    st.subheader("Editar ratings FIFA")
    st.caption("Ajuste os valores e clique em salvar para re-rodar o modelo. O importante e a ordem relativa.")
    df_rat = pd.DataFrame(
        [{"Selecao": t, "Rating": r} for t, r in sorted(st.session_state.ratings.items())]
    )
    edit = st.data_editor(df_rat, hide_index=True, use_container_width=True, height=500,
                          num_rows="fixed", disabled=["Selecao"])
    cba, cbb = st.columns(2)
    if cba.button("💾 Salvar ratings e re-rodar"):
        st.session_state.ratings = dict(zip(edit["Selecao"], edit["Rating"].astype(int)))
        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()
    if cbb.button("↩️ Restaurar padrao"):
        st.session_state.ratings = dict(RATING_PADRAO)
        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()

st.markdown("---")
st.caption("Modelo educacional. Criterios de desempate simplificados (pontos, saldo, gols pro). "
           "Alocacao de melhores terceiros por matching aproximado.")
