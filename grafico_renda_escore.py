"""Scatter renda per capita × escore ideológico por zona eleitoral de SP."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

CSV = Path("outputs/socioeconomia_por_zona.csv")
SAIDA = Path("outputs/scatter_renda_escore.png")


tab = pd.read_csv(CSV).set_index("NR_ZONA")

# Zonas do corredor universitário para destaque
corredor = {
    1: "Bela Vista",
    2: "Perdizes",
    5: "Jd Paulista",
    6: "Vila Mariana",
    251: "Pinheiros",
    258: "Indianópolis",
    346: "Butantã",
}

fig, axes = plt.subplots(1, 2, figsize=(14, 7))

for ax, col_escore, titulo in [
    (axes[0], "escore_ver_2024", "Vereador 2024"),
    (axes[1], "escore_pref_2024", "Prefeito 1T 2024"),
]:
    sub = tab.dropna(subset=[col_escore]).copy()

    # Correlação
    r = sub[["renda_pc_media", col_escore]].corr().iloc[0, 1]

    # Linha de regressão
    import numpy as np
    x = sub["renda_pc_media"].values
    y = sub[col_escore].values
    m, b = np.polyfit(x, y, 1)

    ax.scatter(x, y, s=70, alpha=0.5, color="#888", edgecolor="black", linewidth=0.5)

    # Destaca as 8 zonas-alvo
    for zona, nome in corredor.items():
        if zona not in sub.index:
            continue
        row = sub.loc[zona]
        cor = "#d62728" if row[col_escore] < 5.7 else "#2166ac"
        ax.scatter(
            row["renda_pc_media"],
            row[col_escore],
            s=200,
            color=cor,
            edgecolor="black",
            linewidth=1.5,
            zorder=5,
        )
        ax.annotate(
            f"Z{zona} {nome}",
            xy=(row["renda_pc_media"], row[col_escore]),
            xytext=(8, 4),
            textcoords="offset points",
            fontsize=9,
            fontweight="bold",
        )

    x_line = sub["renda_pc_media"].values
    ax.plot(
        x_line,
        m * x_line + b,
        "--",
        color="red",
        linewidth=1.5,
        label=f"regressão linear: r = {r:.3f}",
    )

    ax.axhline(y=5.0, color="gray", linestyle=":", linewidth=0.8)
    ax.set_xlabel("Renda per capita média do setor censitário (R$, 2010)", fontsize=10)
    ax.set_ylabel("Escore ideológico médio (0=ext-esq, 10=ext-dir)", fontsize=10)
    ax.set_title(f"{titulo}\ncorrelação = {r:+.3f}", fontsize=12)
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right", fontsize=9)
    ax.set_ylim(4.9, 6.7)

fig.suptitle(
    "Renda × voto ideológico nas zonas eleitorais de São Paulo (2024)\n"
    "Correlação NEGATIVA: zonas mais ricas votam mais à esquerda",
    fontsize=13,
)
plt.tight_layout()
SAIDA.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(SAIDA, dpi=150, bbox_inches="tight")
print(f"Gráfico salvo: {SAIDA}")
