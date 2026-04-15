"""Teste temporal: o índice institucional é preditor estável do voto ao longo de 2016-2024?

O índice é construído sobre a geometria dos locais de votação do CEM
(base 2022, fixa). O voto é calculado para cada ano. Se a correlação
for estável, o índice é um preditor <i>estrutural</i> — não uma
especificidade de 2024. Se variar fortemente, o padrão é recente.
"""

from pathlib import Path
import numpy as np
import pandas as pd

from src.partidario.analise_volatilidade import carregar_sp_vereador, carregar_sp_prefeito
from src.partidario.ideologia import ESCORE_BOLOGNESI
from src.partidario.indice_institucional import construir_indice

SAIDA_CSV = Path("outputs/indice_temporal_correlacoes.csv")


def escore_medio_ponderado_por_zona(ano: int, cargo: str) -> pd.Series:
    fn = carregar_sp_vereador if cargo == "vereador" else carregar_sp_prefeito
    df = fn(ano)
    df["ESCORE"] = df["PARTIDO"].map(ESCORE_BOLOGNESI)
    df = df.dropna(subset=["ESCORE"])
    return df.groupby("NR_ZONA").apply(
        lambda g: (g["ESCORE"] * g["VOTOS"]).sum() / g["VOTOS"].sum(),
        include_groups=False,
    )


def correlacao(a: pd.Series, b: pd.Series) -> tuple[float, int]:
    df = pd.concat([a, b], axis=1).dropna()
    if len(df) < 3:
        return (np.nan, 0)
    return (df.iloc[:, 0].corr(df.iloc[:, 1]), len(df))


if __name__ == "__main__":
    print("Construindo índice institucional (base CEM/USP 2022, fixa)...")
    idx = construir_indice()["indice_cultural"]
    print(f"  Zonas com índice: {len(idx)}")

    resultados = []
    for ano in [2016, 2020, 2024]:
        for cargo in ["vereador", "prefeito"]:
            escore = escore_medio_ponderado_por_zona(ano, cargo)
            r, n = correlacao(idx, escore)
            r2 = r ** 2 if not np.isnan(r) else np.nan
            resultados.append({
                "ano": ano,
                "cargo": cargo,
                "n": n,
                "r": r,
                "r_quadrado": r2,
                "escore_medio_cidade": escore.mean(),
                "escore_dp": escore.std(),
            })
            print(
                f"  {ano} {cargo:<9}: r = {r:+.3f}  R² = {r2:.3f}  "
                f"(n = {n}, escore médio = {escore.mean():.3f} ± {escore.std():.3f})"
            )

    tab = pd.DataFrame(resultados)
    tab.to_csv(SAIDA_CSV, index=False)
    print(f"\nCSV: {SAIDA_CSV}")

    # Plot
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 6))
    for cargo, cor, marker in [("vereador", "#1f77b4", "o"), ("prefeito", "#d62728", "s")]:
        sub = tab[tab["cargo"] == cargo]
        ax.plot(
            sub["ano"], sub["r"],
            marker=marker, markersize=14, linewidth=2.5,
            color=cor, label=cargo.capitalize(),
        )
        for _, row in sub.iterrows():
            ax.annotate(
                f"r={row['r']:+.2f}\nR²={row['r_quadrado']:.2f}",
                xy=(row["ano"], row["r"]),
                xytext=(6, -4 if cargo == "vereador" else 12),
                textcoords="offset points",
                fontsize=9,
            )
    ax.axhline(y=0, color="black", linewidth=0.8)
    ax.axhline(y=-0.5, color="gray", linestyle=":", linewidth=0.8)
    ax.set_xticks([2016, 2020, 2024])
    ax.set_xlabel("Ano da eleição municipal", fontsize=11)
    ax.set_ylabel("Correlação de Pearson (índice × escore ideológico)", fontsize=11)
    ax.set_title(
        "Estabilidade temporal do poder preditivo do índice institucional\n"
        "sobre o escore ideológico das zonas eleitorais de São Paulo",
        fontsize=12,
    )
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right", fontsize=10)
    ax.set_ylim(-0.75, 0.1)

    Path("outputs").mkdir(exist_ok=True)
    plt.tight_layout()
    plt.savefig("outputs/indice_temporal_trajetoria.png", dpi=150, bbox_inches="tight")
    print("Gráfico: outputs/indice_temporal_trajetoria.png")
