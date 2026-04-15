"""Gráfico: convergência temporal dos três eixos (Peres, Speck, Marques).

Mostra como os indicadores-chave das três frentes empíricas se ativam
entre 2016 e 2020, consolidando-se em 2024.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

anos = [2012, 2016, 2020, 2024]

# Eixo Peres (sistema partidário): PSDB % em Pinheiros → queda
psdb_pinheiros = [48, 36, 18, 0]
psol_pinheiros = [0, 12, 28, 28]

# Eixo Speck (financiamento): % PF média dos top-6 candidatos em Pinheiros
pf_pinheiros = [0, 68, 59, 18]
partido_pinheiros = [51, 2, 29, 77]

# Eixo Marques (índice institucional × voto): R² vereador
r2_indice = [None, 0.012, 0.250, 0.437]

fig, axes = plt.subplots(2, 2, figsize=(14, 9), sharex=True)

# Painel 1: sistema partidário em Pinheiros
ax = axes[0, 0]
ax.plot(anos, psdb_pinheiros, "s-", color="#4daf4a", markersize=11,
        linewidth=2.5, label="PSDB (% voto vereador)")
ax.plot(anos, psol_pinheiros, "o-", color="#e41a1c", markersize=11,
        linewidth=2.5, label="PSOL (% voto vereador)")
ax.set_title("Eixo I — Sistema partidário (Pinheiros)", fontsize=12, fontweight="bold")
ax.set_ylabel("% do voto em vereador", fontsize=10)
ax.legend(loc="upper right", fontsize=9)
ax.grid(alpha=0.3)
ax.set_ylim(-5, 55)

# Painel 2: financiamento dos top-6 em Pinheiros
ax = axes[0, 1]
ax.plot(anos, pf_pinheiros, "D-", color="#d62728", markersize=11,
        linewidth=2.5, label="% Pessoa Física")
ax.plot(anos, partido_pinheiros, "s-", color="#1f77b4", markersize=11,
        linewidth=2.5, label="% Partido (FEFC)")
ax.set_title("Eixo II — Financiamento dos top-6 (Pinheiros)", fontsize=12, fontweight="bold")
ax.set_ylabel("% da receita média ponderada", fontsize=10)
ax.legend(loc="upper right", fontsize=9)
ax.grid(alpha=0.3)
ax.set_ylim(-5, 100)

# Painel 3: R² do índice institucional
ax = axes[1, 0]
anos_r2 = [a for a, r in zip(anos, r2_indice) if r is not None]
r2_vals = [r for r in r2_indice if r is not None]
ax.plot(anos_r2, r2_vals, "o-", color="#1a4dd0", markersize=13,
        linewidth=3, label="R² (vereador)")
ax.fill_between(anos_r2, 0, r2_vals, alpha=0.15, color="#1a4dd0")
ax.set_title("Eixo III — Poder explicativo do índice institucional",
             fontsize=12, fontweight="bold")
ax.set_ylabel("R² da regressão escore ~ índice", fontsize=10)
ax.set_ylim(0, 0.5)
ax.grid(alpha=0.3)
for a, r in zip(anos_r2, r2_vals):
    ax.annotate(f"{r:.2f}", xy=(a, r), xytext=(0, 10),
                textcoords="offset points", fontsize=10, ha="center",
                fontweight="bold", color="#1a4dd0")

# Painel 4: síntese normalizada (0-1)
ax = axes[1, 1]
# Normaliza cada série entre 0 e 1 de acordo com seu eixo substantivo
# Sistema partidário: 1 - PSDB/48 (0 = ainda com PSDB, 1 = PSDB morto)
pardq = [1 - p/48 for p in psdb_pinheiros]
# Financiamento: partido/100 (0 = pouco partido, 1 = todo partido)
fin = [p/100 for p in partido_pinheiros]
# Institucional: R² direto
inst = [r if r is not None else 0 for r in r2_indice]

ax.plot(anos, pardq, "s-", color="#4daf4a", markersize=10, linewidth=2.5,
        label="Colapso do PSDB (1 − PSDB/48%)")
ax.plot(anos, fin, "D-", color="#1f77b4", markersize=10, linewidth=2.5,
        label="Dominância do FEFC (% partido)")
ax.plot(anos, inst, "o-", color="#d62728", markersize=10, linewidth=2.5,
        label="Ativação institucional (R² índice)")
ax.axvspan(2016, 2020, alpha=0.15, color="yellow")
ax.text(2018, 0.92, "CHOQUE POLÍTICO\n2016–2018",
        ha="center", fontsize=10, fontweight="bold", color="#666")
ax.set_title("Síntese — três indicadores ativam-se simultaneamente",
             fontsize=12, fontweight="bold")
ax.set_ylabel("Indicador normalizado (0 = 2012, 1 = saturação)", fontsize=10)
ax.legend(loc="lower right", fontsize=9, framealpha=0.95)
ax.grid(alpha=0.3)
ax.set_ylim(-0.05, 1.05)

for ax in axes.flat:
    ax.set_xticks(anos)
    ax.set_xlabel("")

axes[1, 0].set_xlabel("Ano da eleição municipal", fontsize=10)
axes[1, 1].set_xlabel("Ano da eleição municipal", fontsize=10)

fig.suptitle(
    "Convergência temporal dos três eixos empíricos — Pinheiros, 2012–2024",
    fontsize=14, fontweight="bold",
)
plt.tight_layout()
saida = Path("outputs/grafico_convergencia_temporal.png")
plt.savefig(saida, dpi=150, bbox_inches="tight")
print(f"Gráfico salvo: {saida}")
