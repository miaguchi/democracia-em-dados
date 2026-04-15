"""Mapa focado no corredor das universidades + zonas-chave do projeto.

Polígono da cidade de São Paulo + pontos dos locais de votação das 8 zonas
ricas, coloridos por escore ideológico médio ponderado. Recorte visual
no bounding box dessas zonas para destaque.
"""

from pathlib import Path

import geobr
import geopandas as gpd
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import pandas as pd

from src.partidario.analise_volatilidade import carregar_sp_prefeito, carregar_sp_vereador
from src.partidario.ideologia import ESCORE_BOLOGNESI

ZONAS_ALVO = {
    1: "Bela Vista",
    2: "Perdizes",
    3: "Santa Ifigênia",
    5: "Jardim Paulista",
    6: "Vila Mariana",
    251: "Pinheiros",
    258: "Indianópolis",
    346: "Butantã",
}

SHAPEFILE_LV = Path("data/raw/shapes/EL2022_LV_ESP_CEM_V2/EL2022_LV_ESP_CEM_V2.shp")
SAIDA = Path("outputs/mapa_corredor_universitario_2024.png")
CODIGO_IBGE_SP = 3550308


def escore_por_zona(df):
    df = df.copy()
    df["ESCORE"] = df["PARTIDO"].map(ESCORE_BOLOGNESI)
    df = df.dropna(subset=["ESCORE"])
    return df.groupby("NR_ZONA").apply(
        lambda g: (g["ESCORE"] * g["VOTOS"]).sum() / g["VOTOS"].sum(),
        include_groups=False,
    )


# Polígono SP
print("Baixando polígono IBGE de SP...")
sp_poly = geobr.read_municipality(code_muni=CODIGO_IBGE_SP, year=2020)

# Locais de votação das zonas-alvo
gdf = gpd.read_file(SHAPEFILE_LV)
sp_lv = gdf[gdf["MUN_NOME"] == "SAO PAULO"].copy()
sp_lv["NR_ZONA"] = sp_lv["ZE_NUM"].astype(int)
sp_lv = sp_lv[sp_lv["NR_ZONA"].isin(ZONAS_ALVO.keys())].copy()
print(f"Locais nas zonas-alvo: {len(sp_lv)}")

# Escores vereador e prefeito 2024
esc_ver = escore_por_zona(carregar_sp_vereador(2024))
esc_pref = escore_por_zona(carregar_sp_prefeito(2024))

# Escala centralizada em 5.0
vmin, vcenter, vmax = 3.5, 5.0, 7.5
norm = mcolors.TwoSlopeNorm(vcenter=vcenter, vmin=vmin, vmax=vmax)

# Bounding box das zonas-alvo
bbox = sp_lv.total_bounds
padding = 0.015  # ~1.5 km
xlim = (bbox[0] - padding, bbox[2] + padding)
ylim = (bbox[1] - padding, bbox[3] + padding)

fig, axes = plt.subplots(1, 2, figsize=(18, 10))

for ax, escore, titulo in [
    (axes[0], esc_pref, "Prefeito 1T — 2024"),
    (axes[1], esc_ver, "Vereador — 2024"),
]:
    sp_poly.boundary.plot(ax=ax, color="#555555", linewidth=1.0)
    sp_poly.plot(ax=ax, color="#f8f8f8", alpha=0.5)

    merged = sp_lv.merge(escore.rename("escore"), left_on="NR_ZONA", right_index=True)
    merged.plot(
        ax=ax,
        column="escore",
        cmap="RdBu",
        norm=norm,
        markersize=28,
        edgecolor="black",
        linewidth=0.25,
        alpha=0.9,
    )
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    # Rótulos nas zonas (centroide)
    for zona, nome in ZONAS_ALVO.items():
        pontos = merged[merged["NR_ZONA"] == zona]
        if pontos.empty:
            continue
        cx, cy = pontos.geometry.x.mean(), pontos.geometry.y.mean()
        score = escore[zona] if zona in escore.index else None
        texto = f"Z{zona}\n{nome}"
        if score is not None:
            texto += f"\n{score:.2f}"
        ax.annotate(
            texto,
            xy=(cx, cy),
            fontsize=9,
            ha="center",
            va="center",
            fontweight="bold",
            bbox=dict(
                boxstyle="round,pad=0.3",
                facecolor="white",
                edgecolor="black",
                alpha=0.9,
            ),
        )

    ax.set_title(
        f"{titulo}\nmédia {escore.loc[list(ZONAS_ALVO.keys())].mean():.2f} "
        f"(cidade = {escore.mean():.2f})",
        fontsize=12,
    )
    ax.set_axis_off()

sm = plt.cm.ScalarMappable(cmap="RdBu", norm=norm)
cbar = fig.colorbar(sm, ax=axes, shrink=0.6, orientation="horizontal", pad=0.04)
cbar.set_label(
    "Escore ideológico médio ponderado (vermelho=esquerda, azul=direita)",
    fontsize=10,
)

fig.suptitle(
    "Corredor das universidades + zonas-chave do projeto\n"
    "Locais de votação coloridos pelo escore ideológico da sua zona — 2024",
    fontsize=14,
)
SAIDA.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(SAIDA, dpi=150, bbox_inches="tight")
print(f"\nMapa salvo: {SAIDA}")
print(f"\nEscore por zona (2024):")
for zona, nome in ZONAS_ALVO.items():
    ep = esc_pref.get(zona, float("nan"))
    ev = esc_ver.get(zona, float("nan"))
    print(f"  Z{zona:>3} {nome:<17} pref={ep:.3f} ver={ev:.3f}")
