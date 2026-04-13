# Democracia em Dados

Projeto de ciência política computacional brasileira: variação territorial do voto, sucesso eleitoral e posicionamento discursivo, construído como laboratório de ciência de dados ponta a ponta (Python → SQL → estatística → ML → NLP → deploy).

*A Brazilian computational political science project: territorial variation in voting, electoral success and discursive positioning, built as an end-to-end data science lab.*

---

## Objetivo / Goal

Construir uma plataforma de análise eleitoral brasileira que integre dados do TSE, IBGE, BCB e Câmara dos Deputados, respondendo a três perguntas:

1. **Competição** — como varia territorialmente a competitividade eleitoral?
2. **Recursos** — o financiamento de campanha causa sucesso eleitoral? A reforma de 2015 mudou a representação feminina?
3. **Discurso** — é possível posicionar candidatos no espectro ideológico a partir de textos?

*Build a platform for Brazilian electoral analysis integrating TSE, IBGE, BCB and Chamber of Deputies data, answering three questions: how electoral competition varies territorially, whether campaign finance causes electoral success, and whether candidates can be ideologically positioned from text.*

---

## Estrutura / Structure

```
democracia-em-dados/
├── src/
│   └── dominio/
│       ├── __init__.py       # reexporta Candidato, ResultadoEleitoral
│       ├── candidato.py      # Candidato + UFS_VALIDAS
│       └── resultado.py      # ResultadoEleitoral
├── tests/
│   └── test_resultado.py     # pytest — 19 testes
├── exemplo.py                # uso mínimo das classes
└── README.md
```

Planejado: `src/ingestao/` (TSE/BCB), `src/analise/` (SQL + estatística), `src/nlp/`, `docs/ementas/`.

---

## Como rodar / How to run

```bash
conda activate radiografia
pip install pytest
pytest tests/ -q
python exemplo.py
```

---

## Roadmap — 16 semanas / 16-week roadmap

| Semana | Foco | Entregável |
|---|---|---|
| 1 | POO + testes + Git | `Candidato`, `ResultadoEleitoral`, 19 testes ✅ |
| 2 | Composição + pacote `src/` | `EleicaoMunicipal`, fragmentação, volatilidade |
| 3 | Ingestão TSE via API | `TSEDownloader` (POO), dados em parquet |
| 4 | SQL — modelagem | Schema MySQL normalizado, carga inicial |
| 5 | SQL — eixo competição | Window functions, CTEs, 10 queries |
| 6 | SQL — eixo financiamento | Gap de gênero, custo por voto |
| 7 | Regressão linear + diagnóstico | VIF, Breusch-Pagan, resíduos |
| 8 | Regressão logística | Odds ratios, efeitos marginais |
| 9 | Inferência causal (DiD) | Efeito da reforma de 2015 |
| 10 | Pipeline ML | ColumnTransformer, CV estratificada |
| 11 | Comparação de modelos | LogReg, RF, XGBoost, LightGBM + SHAP |
| 12 | NLP baseline + deploy | TF-IDF, FastAPI, Docker |
| 13 | Análise espacial | Moran I, LISA, mapas coropléticos |
| 14 | PCA + índices sintéticos | Índice socioeconômico municipal |
| 15 | Modelos de contagem | Poisson, NB, Zero-inflated |
| 16 | Multinível + cloud | Modelo hierárquico, deploy AWS |

---

## Stack

Python 3.11, pandas, scikit-learn, statsmodels, pytest, MySQL, FastAPI, Docker.

---

## Licença / License

MIT
