# ⚽ Modelo Copa 2026 — App Web

App interativo (Streamlit) do modelo preditivo da Copa do Mundo 2026.
Simulação de Monte Carlo: probabilidades de classificação por grupo, melhores
terceiros, ranking geral e o caminho de qualquer seleção no mata-mata.

## Estrutura

| Arquivo | O que é |
|---|---|
| `app.py` | Interface web (Streamlit) |
| `modelo.py` | Motor do modelo (mesma matemática do script original, sem prints) |
| `requirements.txt` | Dependências |

## Rodar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

Abre em `http://localhost:8501`.

## Publicar de graça (recomendado: Streamlit Community Cloud)

É o "RPubs do Python": grátis, feito pra Streamlit, link público fixo.

Este projeto já está no GitHub (repositório **público**):
**https://github.com/kleiton-stack/copa_2026_app**

1. Acesse **https://share.streamlit.io** e entre com sua conta GitHub.

2. **New app** → **Deploy a public app from GitHub** e preencha:
   - **Repository:** `kleiton-stack/copa_2026_app`
   - **Branch:** `main`
   - **Main file path:** `app.py`

3. **Deploy**. Em ~1 min você recebe um link público tipo
   `https://....streamlit.app` para compartilhar. 🎉

> Como o repositório é **público**, o app roda nos servidores do Streamlit 24/7 —
> não precisa do seu PC ligado. Toda vez que você der `git push`, o app atualiza
> sozinho. No plano grátis ele "dorme" após inatividade e leva alguns segundos
> para acordar na primeira visita — normal.

### Atualizar o app

Edite os arquivos e rode, no diretório do projeto:

```bash
git add -A && git commit -m "atualiza resultados" && git push
```

### Alternativa: Hugging Face Spaces
huggingface.co → New Space → SDK **Streamlit** → suba os 3 arquivos. Também grátis.

## Como usar o app

- **Barra lateral:** ajuste nº de simulações, rho (Dixon-Coles), peso do prior,
  sensibilidade ao rating e os boosts. O modelo re-roda com cache.
- **Abas:** probabilidades por grupo, ranking geral, jogos restantes,
  **backtesting**, caminho no mata-mata (escolha a seleção), forças estimadas
  e edição dos ratings FIFA.

### Backtesting (fora da amostra / walk-forward)

A aba **🔎 Backtesting** mostra o que o modelo *previa* x o que realmente
aconteceu nos jogos já disputados. É honesto: cada jogo é previsto por um modelo
treinado **apenas com as rodadas anteriores** (a rodada 1 usa só o rating), então
o modelo nunca enxerga o resultado que está tentando prever. Métricas: acurácia
do 1X2, Brier score, log-loss e erro médio de gols, além de tabela jogo a jogo.

> Terminologia: o mata-mata de 48 seleções começa nos **16 avos de final**
> (32 times, no código `R32`), seguido de oitavas, quartas, semi e final.

## Notas metodológicas

Modelo educacional. Placar via Poisson dupla + ajuste Dixon-Coles simplificado;
forças atualizadas pelos jogos já disputados ponderando a força do adversário.
Critérios de desempate simplificados (pontos → saldo → gols pró) e alocação dos
melhores terceiros por *matching* aproximado (pode diferir da tabela oficial da
FIFA em combinações raras).
