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

1. **Crie um repositório no GitHub** com estes 3 arquivos (`app.py`,
   `modelo.py`, `requirements.txt`). Pelo navegador: github.com → New
   repository → arraste os arquivos. Ou pelo terminal:

   ```bash
   cd copa2026_app
   git init && git add . && git commit -m "App Copa 2026"
   git branch -M main
   git remote add origin https://github.com/SEU_USUARIO/copa2026.git
   git push -u origin main
   ```

2. Acesse **https://share.streamlit.io** e entre com sua conta GitHub.

3. **New app** → escolha o repositório, branch `main`, arquivo `app.py` → **Deploy**.

4. Em ~1 min você recebe um link público tipo
   `https://copa2026.streamlit.app` para compartilhar. 🎉

> Toda vez que você der `git push`, o app atualiza sozinho.
> No plano grátis o app "dorme" após inatividade e leva alguns segundos
> para acordar na primeira visita — normal.

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
