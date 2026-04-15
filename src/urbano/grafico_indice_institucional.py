"""Scatter: índice institucional × escore ideológico."""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

CSV = Path("outputs/indice_institucional_por_zona.csv")
SAIDA = Path("outputs/scatter_indice_institucional.png")


tab = pd.read_csv(CSV).set_index("NR_ZONA")

corredor = {
    1: "Bela Vista",
    2: "Perdizes",
    5: "Jd Paulista",
    6: "Vila Mariana",
    251: "Pinheiros",
    258: "Indianópolis",
    346: "Butantã",
}

fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# Painel esquerdo: índice institucional (o achado forte)
ax = axes[0]
sub = tab.dropna(subset=["escore_ver_2024"])
x = sub["indice_cultural"].values
y = sub["escore_ver_2024"].values
r = np.corrcoef(x, y)[0, 1]
m, b = np.polyfit(x, y, 1)

ax.scatter(x, y, s=70, alpha=0.5, color="#888", edgecolor="black", linewidth=0.5)

for zona, nome in corredor.items():
    if zona not in sub.index:
        continue
    row = sub.loc[zona]
    cor = "#d62728" if row["escore_ver_2024"] < 5.7 else "#2166ac"
    ax.scatter(
        row["indice_cultural"], row["escore_ver_2024"],
        s=200, color=cor, edgecolor="black", linewidth=1.5, zorder=5,
    )
    ax.annotate(
        f"Z{zona} {nome}",
        xy=(row["indice_cultural"], row["escore_ver_2024"]),
        xytext=(6, 4), textcoords="offset points",
        fontsize=9, fontweight="bold",
    )

xs = np.linspace(x.min(), x.max(), 50)
ax.plot(xs, m * xs + b, "--", color="red", linewidth=1.8, label=f"r = {r:.3f}, R² = {r**2:.3f}")
ax.axhline(y=5.0, color="gray", linestyle=":", linewidth=0.8)
ax.set_xlabel("Índice de densidade cultural-progressista (% de locais)", fontsize=10)
ax.set_ylabel("Escore ideológico vereador 2024", fontsize=10)
ax.set_title(
    "Voto × ambiente institucional\n"
    f"correlação = {r:+.3f} (R² = {r**2:.3f})",
    fontsize=12,
)
ax.grid(alpha=0.3)
ax.legend(loc="upper right", fontsize=9)
ax.set_ylim(4.9, 6.7)

# Painel direito: renda (o achado fraco, para comparação)
ax = axes[1]
x2 = sub["renda_pc_media"].values
y2 = sub["escore_ver_2024"].values
r2 = np.corrcoef(x2, y2)[0, 1]
m2, b2 = np.polyfit(x2, y2, 1)

ax.scatter(x2, y2, s=70, alpha=0.5, color="#888", edgecolor="black", linewidth=0.5)
for zona, nome in corredor.items():
    if zona not in sub.index:
        continue
    row = sub.loc[zona]
    cor = "#d62728" if row["escore_ver_2024"] < 5.7 else "#2166ac"
    ax.scatter(
        row["renda_pc_media"], row["escore_ver_2024"],
        s=200, color=cor, edgecolor="black", linewidth=1.5, zorder=5,
    )
    ax.annotate(
        f"Z{zona} {nome}",
        xy=(row["renda_pc_media"], row["escore_ver_2024"]),
        xytext=(6, 4), textcoords="offset points",
        fontsize=9, fontweight="bold",
    )

xs = np.linspace(x2.min(), x2.max(), 50)
ax.plot(xs, m2 * xs + b2, "--", color="red", linewidth=1.8, label=f"r = {r2:.3f}, R² = {r2**2:.3f}")
ax.axhline(y=5.0, color="gray", linestyle=":", linewidth=0.8)
ax.set_xlabel("Renda per capita média (Censo 2010, R$)", fontsize=10)
ax.set_ylabel("Escore ideológico vereador 2024", fontsize=10)
ax.set_title(
    "Voto × renda\n"
    f"correlação = {r2:+.3f} (R² = {r2**2:.3f})",
    fontsize=12,
)
ax.grid(alpha=0.3)
ax.legend(loc="upper right", fontsize=9)
ax.set_ylim(4.9, 6.7)

fig.suptitle(
    "Dois preditores do voto ideológico nas zonas eleitorais de SP (2024)\n"
    "Densidade institucional cultural-progressista explica ~44% da variância; renda explica ~9%",
    fontsize=13,
)
plt.tight_layout()
SAIDA.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(SAIDA, dpi=150, bbox_inches="tight")
print(f"Gráfico salvo: {SAIDA}")
