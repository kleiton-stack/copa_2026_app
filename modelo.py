"""
Motor do modelo preditivo da Copa 2026 (refatorado a partir de modelo_copa2026_v3.py).

Mesma matematica do script original, porem:
  - sem prints (retorna estruturas de dados);
  - encapsulado numa classe parametrizavel (ratings, N_SIM, ajustes, etc.);
  - pronto para ser chamado por uma interface web (Streamlit).
"""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from math import factorial

import numpy as np


# ----------------------------------------------------------------------------
# Dados padrao (editaveis pela interface)
# ----------------------------------------------------------------------------

RATING_PADRAO = {
    "Argentina": 1890, "Espanha": 1875, "Franca": 1870, "Inglaterra": 1820,
    "Portugal": 1780, "Brasil": 1760, "Holanda": 1750, "Belgica": 1740,
    "Alemanha": 1720, "Croacia": 1700, "Marrocos": 1700, "Colombia": 1690,
    "Uruguai": 1680, "Mexico": 1655, "Japao": 1650, "Senegal": 1640,
    "Estados Unidos": 1640, "Suica": 1635, "Ira": 1630, "Austria": 1580,
    "Coreia do Sul": 1575, "Equador": 1560, "Noruega": 1555, "Suecia": 1540,
    "Australia": 1530, "Canada": 1530, "Egito": 1520, "Tunisia": 1500,
    "Republica Tcheca": 1500, "Escocia": 1500, "Argelia": 1500,
    "Costa do Marfim": 1490, "Turquia": 1490, "Paraguai": 1480, "Bosnia": 1455,
    "Gana": 1450, "Panama": 1450, "Africa do Sul": 1440, "Arabia Saudita": 1430,
    "Uzbequistao": 1430, "R.D. Congo": 1420, "Catar": 1400, "Jordania": 1390,
    "Cabo Verde": 1380, "Iraque": 1380, "Haiti": 1320, "Curacao": 1310,
    "Nova Zelandia": 1300,
}

FIXTURES_PADRAO = {
    "A": [("Mexico", "Africa do Sul"), ("Coreia do Sul", "Republica Tcheca"),
          ("Republica Tcheca", "Africa do Sul"), ("Mexico", "Coreia do Sul"),
          ("Republica Tcheca", "Mexico"), ("Africa do Sul", "Coreia do Sul")],
    "B": [("Bosnia", "Canada"), ("Suica", "Catar"), ("Canada", "Catar"),
          ("Suica", "Bosnia"), ("Suica", "Canada"), ("Bosnia", "Catar")],
    "C": [("Brasil", "Marrocos"), ("Escocia", "Haiti"), ("Brasil", "Haiti"),
          ("Marrocos", "Escocia"), ("Escocia", "Brasil"), ("Marrocos", "Haiti")],
    "D": [("Australia", "Turquia"), ("Estados Unidos", "Paraguai"),
          ("Estados Unidos", "Australia"), ("Paraguai", "Turquia"),
          ("Turquia", "Estados Unidos"), ("Paraguai", "Australia")],
    "E": [("Alemanha", "Curacao"), ("Costa do Marfim", "Equador"),
          ("Alemanha", "Costa do Marfim"), ("Equador", "Curacao"),
          ("Equador", "Alemanha"), ("Curacao", "Costa do Marfim")],
    "F": [("Holanda", "Japao"), ("Suecia", "Tunisia"), ("Holanda", "Suecia"),
          ("Tunisia", "Japao"), ("Tunisia", "Holanda"), ("Japao", "Suecia")],
    "G": [("Ira", "Nova Zelandia"), ("Belgica", "Egito"), ("Belgica", "Ira"),
          ("Nova Zelandia", "Egito"), ("Nova Zelandia", "Belgica"), ("Egito", "Ira")],
    "H": [("Espanha", "Cabo Verde"), ("Arabia Saudita", "Uruguai"),
          ("Espanha", "Arabia Saudita"), ("Uruguai", "Cabo Verde"),
          ("Uruguai", "Espanha"), ("Cabo Verde", "Arabia Saudita")],
    "I": [("Noruega", "Iraque"), ("Franca", "Senegal"), ("Franca", "Iraque"),
          ("Noruega", "Senegal"), ("Noruega", "Franca"), ("Senegal", "Iraque")],
    "J": [("Argentina", "Argelia"), ("Austria", "Jordania"),
          ("Argentina", "Austria"), ("Jordania", "Argelia"),
          ("Jordania", "Argentina"), ("Argelia", "Austria")],
    "K": [("Colombia", "Uzbequistao"), ("Portugal", "R.D. Congo"),
          ("Portugal", "Uzbequistao"), ("Colombia", "R.D. Congo"),
          ("Colombia", "Portugal"), ("R.D. Congo", "Uzbequistao")],
    "L": [("Inglaterra", "Croacia"), ("Gana", "Panama"), ("Inglaterra", "Gana"),
          ("Panama", "Croacia"), ("Panama", "Inglaterra"), ("Croacia", "Gana")],
}

RESULTADOS_PADRAO = [
    ("Mexico", 2, "Africa do Sul", 0), ("Coreia do Sul", 2, "Republica Tcheca", 1),
    ("Republica Tcheca", 1, "Africa do Sul", 1), ("Mexico", 1, "Coreia do Sul", 0),
    ("Bosnia", 1, "Canada", 1), ("Suica", 1, "Catar", 1),
    ("Canada", 6, "Catar", 0), ("Suica", 4, "Bosnia", 1),
    ("Brasil", 1, "Marrocos", 1), ("Escocia", 1, "Haiti", 0),
    ("Brasil", 3, "Haiti", 0), ("Marrocos", 1, "Escocia", 0),
    ("Australia", 2, "Turquia", 0), ("Estados Unidos", 4, "Paraguai", 1),
    ("Estados Unidos", 2, "Australia", 0), ("Paraguai", 1, "Turquia", 0),
    ("Alemanha", 7, "Curacao", 1), ("Costa do Marfim", 1, "Equador", 0),
    ("Alemanha", 2, "Costa do Marfim", 1), ("Equador", 0, "Curacao", 0),
    ("Holanda", 2, "Japao", 2), ("Suecia", 5, "Tunisia", 1),
    ("Holanda", 5, "Suecia", 1), ("Tunisia", 0, "Japao", 4),
    ("Ira", 2, "Nova Zelandia", 2), ("Belgica", 1, "Egito", 1),
    ("Belgica", 0, "Ira", 0), ("Nova Zelandia", 1, "Egito", 3),
    ("Espanha", 0, "Cabo Verde", 0), ("Arabia Saudita", 1, "Uruguai", 1),
    ("Espanha", 4, "Arabia Saudita", 0), ("Uruguai", 2, "Cabo Verde", 2),
    ("Noruega", 4, "Iraque", 1), ("Franca", 3, "Senegal", 1),
    ("Franca", 3, "Iraque", 0), ("Noruega", 3, "Senegal", 2),
    ("Argentina", 3, "Argelia", 0), ("Austria", 3, "Jordania", 1),
    ("Argentina", 2, "Austria", 0), ("Jordania", 1, "Argelia", 2),
    ("Colombia", 3, "Uzbequistao", 1), ("Portugal", 1, "R.D. Congo", 1),
    ("Portugal", 5, "Uzbequistao", 0),
    ("Inglaterra", 4, "Croacia", 2), ("Gana", 1, "Panama", 0),
]


# ----------------------------------------------------------------------------
# Chaveamento do mata-mata (snapshot atual)
# ----------------------------------------------------------------------------

R32_MATCHES = [
    ("45", "2A", "2B"), ("57", "1C", "2F"), ("41", "1E", "3ABCDF"),
    ("47", "1F", "2C"), ("61", "2E", "2I"), ("43", "1I", "3CDFGH"),
    ("63", "1A", "3CEFHI"), ("65", "1L", "3EHIJK"), ("55", "1G", "3AEHIJ"),
    ("53", "1D", "3BEFIJ"), ("51", "1H", "2J"), ("49", "2K", "2L"),
    ("05", "1B", "3EFGIJ"), ("03", "2D", "2G"), ("69", "1J", "2H"),
    ("07", "1K", "3DEIJL"),
]
R16_MATCHES = [
    ("11", "W45", "W47"), ("09", "W41", "W43"), ("17", "W57", "W61"),
    ("19", "W63", "W65"), ("13", "W49", "W51"), ("15", "W53", "W55"),
    ("21", "W69", "W03"), ("23", "W05", "W07"),
]
QF_MATCHES = [("25", "W09", "W11"), ("27", "W13", "W15"),
              ("29", "W17", "W19"), ("31", "W21", "W23")]
SF_MATCHES = [("33", "W25", "W27"), ("35", "W29", "W31")]
FINAL_MATCHES = [("37", "W33", "W35")]

STAGE_MATCHES = [
    ("R32", R32_MATCHES), ("R16", R16_MATCHES), ("QF", QF_MATCHES),
    ("SF", SF_MATCHES), ("FINAL", FINAL_MATCHES),
]

THIRD_SLOTS = {
    "3ABCDF": set("ABCDF"), "3CDFGH": set("CDFGH"), "3CEFHI": set("CEFHI"),
    "3EHIJK": set("EHIJK"), "3AEHIJ": set("AEHIJ"), "3BEFIJ": set("BEFIJ"),
    "3EFGIJ": set("EFGIJ"), "3DEIJL": set("DEIJL"),
}


@dataclass
class Config:
    n_sim: int = 50_000
    n_path: int = 50_000
    mu0: float = 1.35
    c: float = 0.0017
    w_prior: float = 3.0
    maxg: int = 12
    dc_rho: float = -0.08
    lambda_min: float = 0.05
    lambda_max: float = 5.50
    use_host_boost: bool = True
    host_boost_log: float = 0.08
    opponent_adjust: bool = True
    seed: int = 42
    seed_path: int = 20260623
    hosts: frozenset = frozenset({"Mexico", "Estados Unidos", "Canada"})


class ModeloCopa:
    def __init__(self, rating=None, fixtures=None, resultados=None, config: Config | None = None):
        self.rating = dict(rating or RATING_PADRAO)
        self.fixtures = {g: list(j) for g, j in (fixtures or FIXTURES_PADRAO).items()}
        self.resultados = list(resultados or RESULTADOS_PADRAO)
        self.cfg = config or Config()

        self.r_avg = float(np.mean(list(self.rating.values())))
        self.team_to_group = self._mapa_time_grupo()
        self.all_teams = self._todos_os_times()
        self._factorials = np.array([factorial(k) for k in range(self.cfg.maxg + 1)], dtype=float)

        self._atualiza_forcas()
        self.standings_atual = self._standings_iniciais()
        self.restantes = self._jogos_restantes_por_grupo()

    # ----- dados auxiliares ------------------------------------------------
    def _todos_os_times(self):
        times = set()
        for jogos in self.fixtures.values():
            for a, b in jogos:
                times.add(a); times.add(b)
        return sorted(times)

    def _mapa_time_grupo(self):
        out = {}
        for grupo, jogos in self.fixtures.items():
            for a, b in jogos:
                out[a] = grupo; out[b] = grupo
        return out

    @staticmethod
    def _par(a, b):
        return frozenset((a, b))

    def validar(self):
        avisos = []
        sem_rating = [t for t in self.all_teams if t not in self.rating]
        if sem_rating:
            avisos.append("Times sem rating (usando media): " + ", ".join(sem_rating))
        fixture_pairs = set()
        for jogos in self.fixtures.values():
            for a, b in jogos:
                fixture_pairs.add(self._par(a, b))
        fora = [(a, b) for a, ga, b, gb in self.resultados if self._par(a, b) not in fixture_pairs]
        if fora:
            avisos.append("Resultados fora dos fixtures: " + ", ".join(f"{a} x {b}" for a, b in fora))
        return avisos

    # ----- forcas ----------------------------------------------------------
    def prior_rates(self, t):
        r = self.rating.get(t, self.r_avg)
        a0 = self.cfg.mu0 * np.exp(self.cfg.c * (r - self.r_avg))
        d0 = self.cfg.mu0 * np.exp(-self.cfg.c * (r - self.r_avg))
        return a0, d0

    def _atualiza_forcas(self):
        self.gf_adj = defaultdict(float)
        self.ga_adj = defaultdict(float)
        self.jogos_disputados = defaultdict(int)
        for a, ga, b, gb in self.resultados:
            a0_a, d0_a = self.prior_rates(a)
            a0_b, d0_b = self.prior_rates(b)
            if self.cfg.opponent_adjust:
                self.gf_adj[a] += ga * self.cfg.mu0 / max(d0_b, 1e-9)
                self.ga_adj[a] += gb * self.cfg.mu0 / max(a0_b, 1e-9)
                self.gf_adj[b] += gb * self.cfg.mu0 / max(d0_a, 1e-9)
                self.ga_adj[b] += ga * self.cfg.mu0 / max(a0_a, 1e-9)
            else:
                self.gf_adj[a] += ga; self.ga_adj[a] += gb
                self.gf_adj[b] += gb; self.ga_adj[b] += ga
            self.jogos_disputados[a] += 1
            self.jogos_disputados[b] += 1

    def forcas(self, t):
        a0, d0 = self.prior_rates(t)
        j = self.jogos_disputados.get(t, 0)
        ataque = (self.gf_adj.get(t, 0.0) + self.cfg.w_prior * a0) / (j + self.cfg.w_prior)
        defesa = (self.ga_adj.get(t, 0.0) + self.cfg.w_prior * d0) / (j + self.cfg.w_prior)
        return ataque, defesa

    def lambdas(self, a, b):
        aa, da = self.forcas(a)
        ab, db = self.forcas(b)
        la = aa * db / self.cfg.mu0
        lb = ab * da / self.cfg.mu0
        if self.cfg.use_host_boost:
            if a in self.cfg.hosts:
                la *= np.exp(self.cfg.host_boost_log)
            if b in self.cfg.hosts:
                lb *= np.exp(self.cfg.host_boost_log)
        la = float(np.clip(la, self.cfg.lambda_min, self.cfg.lambda_max))
        lb = float(np.clip(lb, self.cfg.lambda_min, self.cfg.lambda_max))
        return la, lb

    # ----- placar ----------------------------------------------------------
    def poisson_pmf_vec(self, lam):
        maxg = self.cfg.maxg
        ks = np.arange(maxg + 1)
        return np.exp(-lam) * lam ** ks / self._factorials[:maxg + 1]

    def matriz_placares(self, a, b):
        rho = self.cfg.dc_rho
        la, lb = self.lambdas(a, b)
        pa = self.poisson_pmf_vec(la)
        pb = self.poisson_pmf_vec(lb)
        m = np.outer(pa, pb)
        tau = np.ones_like(m)
        tau[0, 0] = 1.0 - la * lb * rho
        tau[0, 1] = 1.0 + la * rho
        tau[1, 0] = 1.0 + lb * rho
        tau[1, 1] = 1.0 - rho
        tau = np.maximum(tau, 0.01)
        m = m * tau
        m = m / m.sum()
        return la, lb, m

    def prob_jogo(self, a, b):
        la, lb, m = self.matriz_placares(a, b)
        p_a = np.tril(m, -1).sum()
        p_e = np.trace(m)
        p_b = np.triu(m, 1).sum()
        gols = np.arange(self.cfg.maxg + 1)
        exp_a = (m * gols[:, None]).sum()
        exp_b = (m * gols[None, :]).sum()
        return la, lb, exp_a, exp_b, p_a, p_e, p_b

    def sorteia_placar(self, m, rng):
        flat = m.ravel()
        k = rng.choice(flat.size, p=flat)
        ga, gb = np.unravel_index(k, m.shape)
        return int(ga), int(gb)

    # ----- standings -------------------------------------------------------
    def _standings_iniciais(self):
        standings = {}
        for grupo, jogos in self.fixtures.items():
            times = sorted(set(x for jogo in jogos for x in jogo))
            standings[grupo] = {t: {"pts": 0, "gf": 0, "ga": 0, "gd": 0, "pj": 0} for t in times}
        for a, ga, b, gb in self.resultados:
            grupo = self.team_to_group[a]
            self._aplica(standings[grupo], a, b, ga, gb)
        return standings

    @staticmethod
    def _aplica(st, a, b, ga, gb):
        st[a]["gf"] += ga; st[a]["ga"] += gb; st[a]["gd"] += ga - gb; st[a]["pj"] += 1
        st[b]["gf"] += gb; st[b]["ga"] += ga; st[b]["gd"] += gb - ga; st[b]["pj"] += 1
        if ga > gb:
            st[a]["pts"] += 3
        elif gb > ga:
            st[b]["pts"] += 3
        else:
            st[a]["pts"] += 1; st[b]["pts"] += 1

    def _jogos_restantes_por_grupo(self):
        played = {self._par(a, b) for a, ga, b, gb in self.resultados}
        return {g: [(a, b) for a, b in jogos if self._par(a, b) not in played]
                for g, jogos in self.fixtures.items()}

    @staticmethod
    def chave_classificacao(reg, ruido=0.0):
        return reg["pts"] * 1_000_000 + reg["gd"] * 1_000 + reg["gf"] + ruido

    def ordena_grupo(self, st, rng):
        times = list(st.keys())
        ru = rng.random(len(times)) * 1e-6
        idx = {t: i for i, t in enumerate(times)}
        return sorted(times, key=lambda t: self.chave_classificacao(st[t], ru[idx[t]]), reverse=True)

    @staticmethod
    def _copia(st):
        return {g: {t: dict(v) for t, v in tab.items()} for g, tab in st.items()}

    # ----- relatorios estaticos -------------------------------------------
    def tabela_standings(self):
        """Standings atuais ordenados, por grupo."""
        rng = np.random.default_rng(self.cfg.seed)
        out = {}
        for grupo in sorted(self.standings_atual.keys()):
            st = self.standings_atual[grupo]
            ordem = self.ordena_grupo(st, rng)
            linhas = []
            for t in ordem:
                r = st[t]
                linhas.append({"Selecao": t, "PJ": r["pj"], "Pts": r["pts"],
                               "GP": r["gf"], "GC": r["ga"], "SG": r["gd"]})
            restantes = [f"{a} x {b}" for a, b in self.restantes[grupo]]
            out[grupo] = {"linhas": linhas, "restantes": restantes}
        return out

    def tabela_jogos_restantes(self):
        linhas = []
        for grupo in sorted(self.restantes.keys()):
            for a, b in self.restantes[grupo]:
                la, lb, ea, eb, pa, pe, pb = self.prob_jogo(a, b)
                linhas.append({
                    "Grupo": grupo, "Confronto": f"{a} x {b}",
                    "Gols esp. A": round(float(ea), 2), "Gols esp. B": round(float(eb), 2),
                    "Vit A %": round(float(pa) * 100, 1),
                    "Empate %": round(float(pe) * 100, 1),
                    "Vit B %": round(float(pb) * 100, 1),
                })
        return linhas

    def tabela_forcas(self):
        linhas = []
        for t in sorted(self.all_teams, key=lambda x: self.forcas(x)[0] - self.forcas(x)[1], reverse=True):
            a, d = self.forcas(t)
            linhas.append({
                "Selecao": t, "Grupo": self.team_to_group[t],
                "Rating": round(self.rating.get(t, self.r_avg)),
                "Ataque": round(float(a), 3), "Defesa (GC)": round(float(d), 3),
                "Jogos": self.jogos_disputados.get(t, 0),
            })
        return linhas

    # ----- monte carlo da fase de grupos ----------------------------------
    def simula_fase_grupos(self, n=None, progress=None):
        n = n or self.cfg.n_sim
        rng = np.random.default_rng(self.cfg.seed)

        # pre-computa matrizes de placar dos jogos restantes (acelera muito)
        matrizes = {}
        for grupo, jogos in self.restantes.items():
            for a, b in jogos:
                _, _, m = self.matriz_placares(a, b)
                matrizes[(grupo, a, b)] = m

        pos_count = {t: np.zeros(4) for t in self.all_teams}
        top2_count = defaultdict(float)
        best3_count = defaultdict(float)
        qual_count = defaultdict(float)

        step = max(1, n // 100)
        for i in range(n):
            st = self._copia(self.standings_atual)
            for grupo, jogos in self.restantes.items():
                for a, b in jogos:
                    ga, gb = self.sorteia_placar(matrizes[(grupo, a, b)], rng)
                    self._aplica(st[grupo], a, b, ga, gb)

            terceiros = []
            for grupo in sorted(st.keys()):
                ordem = self.ordena_grupo(st[grupo], rng)
                for pos, t in enumerate(ordem):
                    pos_count[t][pos] += 1
                for t in ordem[:2]:
                    top2_count[t] += 1; qual_count[t] += 1
                t3 = ordem[2]
                terceiros.append((t3, grupo, st[grupo][t3]))

            ruido = rng.random(len(terceiros)) * 1e-6
            terceiros_ord = sorted(zip(terceiros, ruido),
                                   key=lambda x: self.chave_classificacao(x[0][2], x[1]), reverse=True)
            for (t, grupo, r), _ru in terceiros_ord[:8]:
                best3_count[t] += 1; qual_count[t] += 1

            if progress and i % step == 0:
                progress(i / n)
        if progress:
            progress(1.0)

        pos_probs = {t: pos_count[t] / n for t in self.all_teams}
        top2_probs = {t: top2_count[t] / n for t in self.all_teams}
        best3_probs = {t: best3_count[t] / n for t in self.all_teams}
        qual_probs = {t: qual_count[t] / n for t in self.all_teams}
        return pos_probs, top2_probs, best3_probs, qual_probs

    def relatorio_grupos(self, pos_probs, top2_probs, best3_probs, qual_probs):
        out = {}
        for grupo in sorted(self.fixtures.keys()):
            times = sorted(set(x for jogo in self.fixtures[grupo] for x in jogo))
            ordem = sorted(times, key=lambda t: qual_probs[t], reverse=True)
            linhas = []
            for t in ordem:
                p = pos_probs[t]
                linhas.append({
                    "Selecao": t,
                    "1o %": round(float(p[0]) * 100, 1), "2o %": round(float(p[1]) * 100, 1),
                    "3o %": round(float(p[2]) * 100, 1), "4o %": round(float(p[3]) * 100, 1),
                    "Top-2 %": round(float(top2_probs[t]) * 100, 1),
                    "Melhor 3o %": round(float(best3_probs[t]) * 100, 1),
                    "Classif. %": round(float(qual_probs[t]) * 100, 1),
                })
            out[grupo] = linhas
        return out

    def ranking_geral(self, top2_probs, best3_probs, qual_probs):
        ordem = sorted(self.all_teams, key=lambda t: qual_probs[t], reverse=True)
        return [{
            "Selecao": t, "Grupo": self.team_to_group[t],
            "Top-2 %": round(float(top2_probs[t]) * 100, 1),
            "Melhor 3o %": round(float(best3_probs[t]) * 100, 1),
            "Classif. %": round(float(qual_probs[t]) * 100, 1),
        } for t in ordem]

    # ----- backtesting (walk-forward / out-of-sample) ---------------------
    def _rodada_dos_fixtures(self):
        """Mapeia cada confronto (par) para sua rodada (1, 2 ou 3) na fase de grupos."""
        pair_round = {}
        for jogos in self.fixtures.values():
            for i, (a, b) in enumerate(jogos):
                pair_round[self._par(a, b)] = i // 2 + 1
        return pair_round

    def backtest(self):
        """
        Backtesting honesto (walk-forward / fora da amostra):

        Cada jogo ja disputado e' previsto usando um modelo treinado SOMENTE com
        os resultados das rodadas anteriores. A rodada 1 e' prevista apenas pelo
        rating (nenhum jogo anterior), evitando que o modelo "veja" o proprio
        resultado que esta tentando prever.

        Retorna {"jogos": [...], "metrics": {...}, "por_rodada": [...]}.
        """
        pair_round = self._rodada_dos_fixtures()
        by_round = defaultdict(list)
        for a, ga, b, gb in self.resultados:
            r = pair_round.get(self._par(a, b))
            if r is not None:
                by_round[r].append((a, ga, b, gb))

        rows = []
        brier_sum = logloss_sum = mae_gols = 0.0
        acertos = n = 0
        acc_por_rodada = defaultdict(lambda: [0, 0])  # rodada -> [acertos, total]

        for r in sorted(by_round):
            subset = [res for rr in by_round if rr < r for res in by_round[rr]]
            # Modelo treinado so com rodadas anteriores (fora da amostra).
            temp = ModeloCopa(self.rating, self.fixtures, subset, self.cfg)

            for a, ga, b, gb in by_round[r]:
                la, lb, ea, eb, pa, pe, pb = temp.prob_jogo(a, b)
                probs = {"A": float(pa), "E": float(pe), "B": float(pb)}

                if ga > gb:
                    actual = "A"
                elif gb > ga:
                    actual = "B"
                else:
                    actual = "E"

                pred = max(probs, key=probs.get)
                acertou = pred == actual
                rotulo = {"A": a, "E": "Empate", "B": b}

                acertos += int(acertou)
                n += 1
                acc_por_rodada[r][0] += int(acertou)
                acc_por_rodada[r][1] += 1
                for k in ("A", "E", "B"):
                    y = 1.0 if k == actual else 0.0
                    brier_sum += (probs[k] - y) ** 2
                logloss_sum += -math.log(max(probs[actual], 1e-12))
                mae_gols += abs(float(ea) - ga) + abs(float(eb) - gb)

                rows.append({
                    "Rodada": r,
                    "Grupo": self.team_to_group[a],
                    "Confronto": f"{a} x {b}",
                    "Prev. V1 %": round(probs["A"] * 100, 1),
                    "Prev. Empate %": round(probs["E"] * 100, 1),
                    "Prev. V2 %": round(probs["B"] * 100, 1),
                    "Favorito": rotulo[pred],
                    "Gols esp.": f"{float(ea):.1f} x {float(eb):.1f}",
                    "Placar real": f"{ga} x {gb}",
                    "Resultado": rotulo[actual],
                    "Acertou": "✅" if acertou else "❌",
                })

        metrics = {
            "n": n,
            "acertos": acertos,
            "acuracia": round(acertos / n * 100, 1) if n else 0.0,
            "brier": round(brier_sum / n, 4) if n else None,
            "logloss": round(logloss_sum / n, 4) if n else None,
            "mae_gols": round(mae_gols / (2 * n), 2) if n else None,
        }
        por_rodada = [
            {"Rodada": r, "Acertos": v[0], "Jogos": v[1],
             "Acuracia %": round(v[0] / v[1] * 100, 1) if v[1] else 0.0}
            for r, v in sorted(acc_por_rodada.items())
        ]
        return {"jogos": rows, "metrics": metrics, "por_rodada": por_rodada}

    # ----- path do Brasil (mata-mata) -------------------------------------
    @staticmethod
    def _sigmoid(x):
        return 1.0 / (1.0 + math.exp(-x))

    def _penalty_prob(self, a, b):
        ra = self.rating.get(a, self.r_avg)
        rb = self.rating.get(b, self.r_avg)
        return self._sigmoid(0.001 * (ra - rb))

    def _simula_vencedor(self, a, b, rng):
        la, lb, ea, eb, p_a, p_e, p_b = self.prob_jogo(a, b)
        p_a_total = p_a + p_e * self._penalty_prob(a, b)
        return a if rng.random() < p_a_total else b

    def _assign_third_slots(self, third_teams, rng):
        slots = list(THIRD_SLOTS.keys())
        assignment = {}
        used = set()

        def rec():
            if len(assignment) == len(slots):
                return True
            remaining = [s for s in slots if s not in assignment]
            remaining.sort(key=lambda s: sum(1 for g in THIRD_SLOTS[s] if g in third_teams and g not in used))
            slot = remaining[0]
            cand = [g for g in THIRD_SLOTS[slot] if g in third_teams and g not in used]
            rng.shuffle(cand)
            for g in cand:
                assignment[slot] = third_teams[g]; used.add(g)
                if rec():
                    return True
                used.remove(g); del assignment[slot]
            return False

        return assignment if rec() else None

    @staticmethod
    def _resolve_slot(token, posicoes, third_assignment, winners):
        if token.startswith("W"):
            return winners[token[1:]]
        if token[0] in "12":
            return posicoes[token[1]][int(token[0]) - 1]
        if token.startswith("3"):
            return third_assignment[token]
        return token

    def simula_path(self, time="Brasil", n=None, progress=None):
        n = n or self.cfg.n_path
        rng = np.random.default_rng(self.cfg.seed_path)

        matrizes = {}
        for grupo, jogos in self.restantes.items():
            for a, b in jogos:
                _, _, m = self.matriz_placares(a, b)
                matrizes[(grupo, a, b)] = m

        reached = Counter()
        eliminated_by_stage = Counter()
        eliminated_by_opponent = defaultdict(Counter)
        opponent_by_stage = defaultdict(Counter)
        route_counter = Counter()
        path_counter = Counter()

        grupo_time = self.team_to_group[time]
        valid = 0
        attempts = 0
        max_attempts = n * 10
        step = max(1, n // 100)

        while valid < n and attempts < max_attempts:
            attempts += 1
            st = self._copia(self.standings_atual)
            for grupo, jogos in self.restantes.items():
                for a, b in jogos:
                    ga, gb = self.sorteia_placar(matrizes[(grupo, a, b)], rng)
                    self._aplica(st[grupo], a, b, ga, gb)

            posicoes = {}
            terceiros = []
            for grupo in sorted(st.keys()):
                ordem = self.ordena_grupo(st[grupo], rng)
                posicoes[grupo] = ordem
                terceiros.append((grupo, ordem[2], st[grupo][ordem[2]]))
            ruido = rng.random(len(terceiros)) * 1e-6
            melhores = sorted(zip(terceiros, ruido),
                              key=lambda x: self.chave_classificacao(x[0][2], x[1]), reverse=True)[:8]
            best3_groups = {g for (g, t, r), _ru in melhores}
            third_teams = {g: t for (g, t, r), _ru in melhores}

            pos = posicoes[grupo_time].index(time) + 1
            if pos == 1:
                route_counter[f"1{grupo_time}"] += 1
            elif pos == 2:
                route_counter[f"2{grupo_time}"] += 1
            elif pos == 3 and grupo_time in best3_groups:
                route_counter["3_classificado"] += 1
            else:
                route_counter["eliminado_grupos"] += 1
                eliminated_by_stage["GRUPOS"] += 1
                path_counter[("ELIMINADO_GRUPOS",)] += 1
                valid += 1
                if progress and valid % step == 0:
                    progress(valid / n)
                continue

            third_assignment = self._assign_third_slots(third_teams, rng)
            if third_assignment is None:
                continue

            valid += 1
            reached["R32"] += 1
            winners = {}
            alive = True
            path = []

            for stage, matches in STAGE_MATCHES:
                for match_id, lt, rt in matches:
                    a = self._resolve_slot(lt, posicoes, third_assignment, winners)
                    b = self._resolve_slot(rt, posicoes, third_assignment, winners)
                    winner = self._simula_vencedor(a, b, rng)
                    winners[match_id] = winner
                    if alive and time in (a, b):
                        opp = b if a == time else a
                        opponent_by_stage[stage][opp] += 1
                        path.append(f"{stage}:{opp}")
                        if winner == time:
                            nxt = {"R32": "R16", "R16": "QF", "QF": "SF", "SF": "FINAL", "FINAL": "CAMPEAO"}[stage]
                            reached[nxt] += 1
                            if stage == "FINAL":
                                path_counter[tuple(path + ["CAMPEAO"])] += 1
                                alive = False
                        else:
                            eliminated_by_stage[stage] += 1
                            eliminated_by_opponent[stage][opp] += 1
                            if stage == "FINAL":
                                reached["VICE"] += 1
                                path_counter[tuple(path + [f"VICE_perdeu_para:{opp}"])] += 1
                            else:
                                path_counter[tuple(path + [f"ELIMINADO_{stage}_por:{opp}"])] += 1
                            alive = False
            if progress and valid % step == 0:
                progress(valid / n)
        if progress:
            progress(1.0)

        return {
            "time": time, "n_valid": valid, "attempts": attempts,
            "reached": reached, "eliminated_by_stage": eliminated_by_stage,
            "eliminated_by_opponent": eliminated_by_opponent,
            "opponent_by_stage": opponent_by_stage,
            "route_counter": route_counter, "path_counter": path_counter,
        }
