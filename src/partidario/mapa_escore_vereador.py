"""Mapa contínuo: escore ideológico médio ponderado por zona.

Para cada zona, calcula a média dos escores de Bolognesi et al. (2023)
ponderada pelos votos de cada partido. Resulta num valor entre 0
(extrema-esquerda) e 10 (extrema-direita) por zona. Dois painéis:
2020 e 2024, mesmo intervalo de cor, para comparação direta.
"""

from pathlib import Path

import geopandas as gpd
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import pandas as pd

from src.partidario.analise_volatilidade import carregar_sp_vereador, carregar_sp_prefeito
from src.partidario.ideologia import ESCORE_BOLOGNESI

SHAPEFILE = Path("data/raw/shapes/EL2022_LV_ESP_CEM_V2/EL2022_LV_ESP_CEM_V2.shp")
SAIDA_VEREADOR = Path("outputs/mapa_escore_vereador_2020_2024.png")
SAIDA_PREFEITO = Path("outputs/mapa_escore_prefeito_2020_2024.png")


def escore_por_zona(df: pd.DataFrame) -> pd.Series:
    """Média dos escores ponderada por votos, por zona."""
    df = df.copy()
    df["ESCORE"] = df["PARTIDO"].map(ESCORE_BOLOGNESI)
    df = df.dropna(subset=["ESCORE"])
    return df.groupby("NR_ZONA").apply(
        lambda g: (g["ESCORE"] * g["VOTOS"]).sum() / g["VOTOS"].sum(),
        include_groups=False,
    )


def _anotar_zonas(ax, centroides, zonas_presentes):
    for zona, row in centroides.iterrows():
        if zona not in zonas_presentes:
            continue
        ax.annotate(
            str(row["nome"]).title(),
            xy=(row["lon"], row["lat"]),
            fontsize=5.5,
            ha="center",
            va="center",
            color="black",
            bbox=dict(
                boxstyle="round,pad=0.15",
                facecolor="white",
                edgecolor="none",
                alpha=0.7,
            ),
        )


def gerar_mapa(carregar_fn, saida, cargo_label, vmin, vmax):
    escore_2020 = escore_por_zona(carregar_fn(2020))
    escore_2024 = escore_por_zona(carregar_fn(2024))

    gdf = gpd.read_file(SHAPEFILE)
    sp = gdf[gdf["MUN_NOME"] == "SAO PAULO"].copy()
    sp["NR_ZONA"] = sp["ZE_NUM"].astype(int)
    sp["lon"] = sp.geometry.x
    sp["lat"] = sp.geometry.y
    centroides = sp.groupby("NR_ZONA").agg(
        lon=("lon", "mean"), lat=("lat", "mean"), nome=("ZE_NOME", "first")
    )

    norm = mcolors.TwoSlopeNorm(vcenter=5.0, vmin=vmin, vmax=vmax)

    fig, axes = plt.subplots(1, 2, figsize=(18, 10))
    for ax, escore, ano in [
        (axes[0], escore_2020, 2020),
        (axes[1], escore_2024, 2024),
    ]:
        sp_merged = sp.merge(
            escore.rename("escore"), left_on="NR_ZONA", right_index=True, how="inner"
        )
        sp_merged.plot(
            column="escore",
            ax=ax,
            markersize=11,
            cmap="RdBu",
            norm=norm,
            legend=False,
            alpha=0.85,
        )
        _anotar_zonas(ax, centroides, set(escore.index))
        ax.set_title(
            f"{cargo_label} — {ano}\n"
            f"média {escore.mean():.2f} | mín {escore.min():.2f} | máx {escore.max():.2f}",
            fontsize=11,
        )
        ax.set_axis_off()

    # Barra de cor compartilhada (centralizada em 5 = centro ideológico)
    sm = plt.cm.ScalarMappable(cmap="RdBu", norm=norm)
    cbar = fig.colorbar(sm, ax=axes, shrink=0.6, orientation="horizontal", pad=0.04)
    cbar.set_label(
        "Escore ideológico médio ponderado (Bolognesi et al. 2023; 0 = extrema-esquerda, 10 = extrema-direita)",
        fontsize=9,
    )

    fig.suptitle(
        f"Posicionamento ideológico médio por zona eleitoral — {cargo_label}, São Paulo\n"
        "Média do escore de cada partido ponderada pelos votos recebidos na zona",
        fontsize=13,
    )
    saida.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(saida, dpi=150, bbox_inches="tight")
    plt.close(fig)

    delta = (escore_2024 - escore_2020).sort_values()
    print(f"\n=== {cargo_label} ===")
    print(f"  média da cidade: 2020 = {escore_2020.mean():.3f} | 2024 = {escore_2024.mean():.3f} | Δ = {escore_2024.mean() - escore_2020.mean():+.3f}")
    print(f"  faixa 2020: {escore_2020.min():.3f} – {escore_2020.max():.3f}")
    print(f"  faixa 2024: {escore_2024.min():.3f} – {escore_2024.max():.3f}")
    print(f"  Δ mín/máx: {delta.min():+.3f} (z{delta.idxmin()}) / {delta.max():+.3f} (z{delta.idxmax()})")
    print(f"  mapa salvo: {saida}")


# Escala centralizada em 5 (centro ideológico de Bolognesi).
# TwoSlopeNorm permite vmin/vmax assimétricos em torno de 5.
gerar_mapa(carregar_sp_vereador, SAIDA_VEREADOR, "Vereador", vmin=3.0, vmax=8.0)
gerar_mapa(carregar_sp_prefeito, SAIDA_PREFEITO, "Prefeito 1T", vmin=3.0, vmax=7.0)
