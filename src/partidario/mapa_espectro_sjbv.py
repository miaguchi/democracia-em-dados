"""SJBV 2024 — espectro ideológico contínuo por local de votação.

Escore médio ponderado por local, plotado sobre o polígono da cidade
(shapefile IBGE via geobr). Painéis lado a lado: prefeito e vereador.
"""

from pathlib import Path

import geobr
import geopandas as gpd
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import pandas as pd

from src.partidario.analise_secao_sjbv import carregar_sjbv_secao
from src.partidario.ideologia import ESCORE_BOLOGNESI

SHAPEFILE_LV = Path("data/raw/shapes/EL2022_LV_ESP_CEM_V2/EL2022_LV_ESP_CEM_V2.shp")
SAIDA = Path("outputs/mapa_espectro_sjbv_2024.png")
CODIGO_IBGE_SJBV = 3549102


def escore_por_local(df: pd.DataFrame, cargo: str) -> pd.Series:
    sub = df[df["DS_CARGO"].str.upper() == cargo.upper()].copy()
    sub["ESCORE"] = sub["PARTIDO"].map(ESCORE_BOLOGNESI)
    sub = sub.dropna(subset=["ESCORE"])
    return sub.groupby("NR_LOCAL_VOTACAO").apply(
        lambda g: (g["ESCORE"] * g["QT_VOTOS"]).sum() / g["QT_VOTOS"].sum(),
        include_groups=False,
    )


df_2024 = carregar_sjbv_secao(2024)
escore_pref = escore_por_local(df_2024, "PREFEITO")
escore_ver = escore_por_local(df_2024, "VEREADOR")

print("Escore prefeito por local:")
print(escore_pref.sort_values())
print("\nEscore vereador por local:")
print(escore_ver.sort_values())

# Polígono da cidade
print("\nBaixando polígono IBGE de SJBV...")
municipio = geobr.read_municipality(code_muni=CODIGO_IBGE_SJBV, year=2020)

# Pontos dos locais de votação
gdf = gpd.read_file(SHAPEFILE_LV)
sj = gdf[gdf["MUN_NOME"] == "SAO JOAO DA BOA VISTA"].copy()

# Match por nome (idêntico ao analise_secao_sjbv)
import re
import unicodedata


def normalizar(s):
    if not isinstance(s, str):
        return ""
    s = unicodedata.normalize("NFKD", s).encode("ASCII", "ignore").decode()
    s = re.sub(r"[^A-Z ]", " ", s.upper())
    return re.sub(r"\s+", " ", s).strip()


nomes_votacao = df_2024[["NR_LOCAL_VOTACAO", "NM_LOCAL_VOTACAO"]].drop_duplicates()
nomes_votacao["nome_norm"] = nomes_votacao["NM_LOCAL_VOTACAO"].map(normalizar)
sj["nome_norm"] = sj["NOME_LV"].map(normalizar)


def casar(nome_shape):
    tokens = set(nome_shape.split())
    melhor, score = None, 0
    for _, row in nomes_votacao.iterrows():
        s = len(tokens & set(row["nome_norm"].split()))
        if s > score:
            score, melhor = s, int(row["NR_LOCAL_VOTACAO"])
    return melhor if score >= 1 else None


sj["NR_LOCAL_VOTACAO"] = sj["nome_norm"].map(casar)
sj = sj.dropna(subset=["NR_LOCAL_VOTACAO"])

# Escala centralizada em 5 (centro ideológico), invertida
# para convenção política brasileira (vermelho=esquerda, azul=direita)
vmin, vmax = 3.0, 8.0
norm = mcolors.TwoSlopeNorm(vcenter=5.0, vmin=vmin, vmax=vmax)

fig, axes = plt.subplots(1, 2, figsize=(16, 9))
for ax, escore, titulo in [
    (axes[0], escore_pref, "Prefeito 1T — 2024"),
    (axes[1], escore_ver, "Vereador — 2024"),
]:
    municipio.boundary.plot(ax=ax, color="#333333", linewidth=1.2)
    municipio.plot(ax=ax, color="#f5f5f5", alpha=0.6)
    merged = sj.merge(escore.rename("escore"), on="NR_LOCAL_VOTACAO", how="left")
    merged.plot(
        ax=ax,
        column="escore",
        cmap="RdBu",
        norm=norm,
        markersize=160,
        edgecolor="black",
        linewidth=0.5,
        alpha=0.95,
        missing_kwds={"color": "#cccccc"},
    )
    for _, row in merged.iterrows():
        if pd.isna(row["escore"]):
            continue
        ax.annotate(
            str(row["NOME_LV"]).title()[:22],
            xy=(row.geometry.x, row.geometry.y),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=6,
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none", alpha=0.8),
        )
    ax.set_title(
        f"{titulo}\nmédia {escore.mean():.2f} | mín {escore.min():.2f} | máx {escore.max():.2f}",
        fontsize=11,
    )
    ax.set_axis_off()

sm = plt.cm.ScalarMappable(cmap="RdBu", norm=norm)
cbar = fig.colorbar(sm, ax=axes, shrink=0.6, orientation="horizontal", pad=0.04)
cbar.set_label(
    "Escore ideológico médio ponderado "
    "(Bolognesi et al. 2023; 0 = extrema-esquerda, 10 = extrema-direita; vermelho = esquerda, azul = direita)",
    fontsize=9,
)
fig.suptitle(
    "São João da Boa Vista — espectro ideológico por local de votação (2024)",
    fontsize=13,
)
SAIDA.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(SAIDA, dpi=150, bbox_inches="tight")
print(f"\nMapa salvo: {SAIDA}")
