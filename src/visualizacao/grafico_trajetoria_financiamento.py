"""Gráfico de trajetória de financiamento SP vereador 2012-2024."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

SAIDA = Path("outputs/grafico_trajetoria_financiamento.png")
CSV = Path("outputs/financiamento_trajetoria_pct.csv")

pct = pd.read_csv(CSV, index_col=0)
pct.columns = pct.columns.str.strip()

rotulos = {
    "partido": "Recursos de partido (FEFC + FP)",
    "pf": "Pessoa física (PF)",
    "pj": "Pessoa jurídica (PJ) — proibida em 2015",
    "proprio": "Recursos próprios",
    "outros_cand": "Outros candidatos/comitês",
    "crowdfund": "Financiamento coletivo",
}
cores = {
    "partido": "#1f77b4",
    "pf": "#d62728",
    "pj": "#8c564b",
    "proprio": "#ff7f0e",
    "outros_cand": "#9467bd",
    "crowdfund": "#2ca02c",
}
ordem = ["partido", "pf", "pj", "proprio", "outros_cand", "crowdfund"]

fig, ax = plt.subplots(figsize=(11, 6.5))
for col in ordem:
    if col not in pct.columns:
        continue
    ax.plot(pct.index, pct[col], "o-", linewidth=2.5, markersize=10,
            label=rotulos[col], color=cores[col])

ax.axvline(x=2014, color="gray", linestyle="--", linewidth=1, alpha=0.6)
ax.text(2014.1, ax.get_ylim()[1] * 0.88, "Reforma 2015\n(proíbe PJ)",
        fontsize=9, color="gray", ha="left")

ax.set_xticks([2012, 2016, 2020, 2024])
ax.set_xlabel("Ano de eleição municipal", fontsize=11)
ax.set_ylabel("% da receita total dos vereadores de SP", fontsize=11)
ax.set_title(
    "Trajetória das fontes de financiamento dos vereadores — São Paulo, 2012–2024\n"
    "Eras: PJ (2012) → Transição (2016) → FEFC consolidado (2020/2024)",
    fontsize=12,
)
ax.grid(alpha=0.3)
ax.legend(loc="upper left", fontsize=9, framealpha=0.95)
ax.set_ylim(0, 100)

SAIDA.parent.mkdir(parents=True, exist_ok=True)
plt.tight_layout()
plt.savefig(SAIDA, dpi=150, bbox_inches="tight")
print(f"Gráfico salvo: {SAIDA}")
