# Modelo Copa 2026

Modelo preditivo da Copa do Mundo de 2026 com interface web em Streamlit.
Simulação de Monte Carlo da fase de grupos e do mata-mata: probabilidades de
classificação por grupo, melhores terceiros, ranking geral, backtesting e o
caminho de qualquer seleção até o título.

## Estrutura

| Arquivo | Descrição |
|---|---|
| `app.py` | Interface Streamlit |
| `modelo.py` | Motor do modelo (mesma matemática do script original, sem prints) |
| `requirements.txt` | Dependências |

## Execução local

```bash
pip install -r requirements.txt
streamlit run app.py
```

Abre em `http://localhost:8501`.

## Deploy (Streamlit Community Cloud)

Repositório: https://github.com/kleiton-stack/copa_2026_app

1. Em https://share.streamlit.io, autentique com o GitHub.
2. **New app** apontando para:
   - Repository: `kleiton-stack/copa_2026_app`
   - Branch: `main`
   - Main file path: `app.py`
3. **Deploy**. O app passa a rodar nos servidores do Streamlit; cada `git push`
   dispara um redeploy automático. No plano gratuito o app hiberna após
   inatividade e leva alguns segundos para responder na primeira visita.

Atualização do conteúdo (resultados, ratings):

```bash
git add -A && git commit -m "atualiza resultados" && git push
```

## Funcionalidades

- **Barra lateral:** número de simulações, rho (Dixon-Coles), peso do prior,
  sensibilidade ao rating e boosts. Resultados em cache.
- **Abas:** probabilidades por grupo, ranking geral, jogos restantes,
  backtesting, caminho no mata-mata, forças estimadas e edição de ratings.

### Backtesting

Validação fora da amostra (walk-forward): cada jogo já disputado é previsto por
um modelo treinado apenas com as rodadas anteriores — a rodada 1 usa somente o
rating. O modelo nunca observa o resultado que está prevendo. Métricas: acurácia
do 1X2, Brier score, log-loss e erro médio de gols, com tabela jogo a jogo.

## Notas metodológicas

- Placar via Poisson dupla com ajuste Dixon-Coles simplificado.
- Forças atualizadas pelos jogos já disputados, ponderando a força do adversário.
- Critérios de desempate simplificados (pontos, saldo, gols pró).
- Alocação dos melhores terceiros por *matching* aproximado — pode divergir da
  tabela oficial da FIFA em combinações raras.
- O mata-mata de 48 seleções começa nos 16 avos de final (32 times; `R32` no
  código), seguido de oitavas, quartas, semifinal e final.
