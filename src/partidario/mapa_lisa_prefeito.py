"""Mapa de pontos + LISA para prefeito 1T, SP, 2020→2024.

Reaproveita os helpers de analise_volatilidade e a mesma geometria do CEM.
"""

from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
from esda.moran import Moran_Local
from libpysal.weights import KNN

from src.partidario.analise_volatilidade import (
    carregar_sp_prefeito,
    pedersen_por_zona,
    votos_por_zona_partido,
)

SHAPEFILE = Path("data/raw/shapes/EL2022_LV_ESP_CEM_V2/EL2022_LV_ESP_CEM_V2.shp")
SAIDA_MAPA = Path("outputs/mapa_volatilidade_sp_prefeito_2020_2024.png")
SAIDA_LISA = Path("outputs/lisa_volatilidade_sp_prefeito_2020_2024.png")
K_VIZINHOS = 6
N_PERMUTACOES = 999
ALPHA = 0.05

ROTULOS = {
    0: "Não significativo",
    1: "Alta-Alta (cluster volátil)",
    2: "Baixa-Alta (outlier)",
    3: "Baixa-Baixa (cluster estável)",
    4: "Alta-Baixa (outlier)",
}
CORES = {0: "#cccccc", 1: "#d7191c", 2: "#abd9e9", 3: "#2c7bb6", 4: "#fdae61"}

df_2020 = carregar_sp_prefeito(2020)
df_2024 = carregar_sp_prefeito(2024)
vol_zona = pedersen_por_zona(
    votos_por_zona_partido(df_2020), votos_por_zona_partido(df_2024)
).rename("volatilidade")

gdf = gpd.read_file(SHAPEFILE)
sp_cidade = gdf[gdf["MUN_NOME"] == "SAO PAULO"].copy()
sp_cidade["NR_ZONA"] = sp_cidade["ZE_NUM"].astype(int)
sp_cidade["lon"] = sp_cidade.geometry.x
sp_cidade["lat"] = sp_cidade.geometry.y

# --- Mapa de pontos -----------------------------------------------------------
sp_com_vol = sp_cidade.merge(
    vol_zona, left_on="NR_ZONA", right_index=True, how="inner"
)

fig, ax = plt.subplots(figsize=(11, 11))
sp_com_vol.plot(
    column="volatilidade",
    ax=ax,
    markersize=12,
    cmap="RdYlBu_r",
    legend=True,
    legend_kwds={"label": "Volatilidade de Pedersen (2020→2024)", "shrink": 0.6},
    alpha=0.75,
)
ax.set_title(
    "Volatilidade eleitoral por zona — prefeito 1T, São Paulo, 2020→2024\n"
    "Cada ponto é um local de votação, colorido pela volatilidade da sua zona",
    fontsize=12,
)
ax.set_axis_off()
SAIDA_MAPA.parent.mkdir(parents=True, exist_ok=True)
plt.tight_layout()
plt.savefig(SAIDA_MAPA, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Mapa salvo: {SAIDA_MAPA}")

# --- LISA ---------------------------------------------------------------------
zonas = (
    sp_cidade.groupby("NR_ZONA")[["lon", "lat"]]
    .mean()
    .join(vol_zona, how="inner")
    .dropna()
)
zonas_gdf = gpd.GeoDataFrame(
    zonas,
    geometry=gpd.points_from_xy(zonas["lon"], zonas["lat"]),
    crs="EPSG:4326",
)
w = KNN.from_dataframe(zonas_gdf, k=K_VIZINHOS)
w.transform = "R"

lisa = Moran_Local(zonas_gdf["volatilidade"].values, w, permutations=N_PERMUTACOES)
classes = lisa.q.copy()
classes[lisa.p_sim >= ALPHA] = 0
zonas_gdf["lisa_classe"] = classes

contagem = zonas_gdf["lisa_classe"].value_counts().sort_index()
print("\nDistribuição LISA (zonas) — prefeito:")
for k, v in contagem.items():
    print(f"  {ROTULOS[k]:<32} {v}")

sp_plot = sp_cidade.merge(
    zonas_gdf[["lisa_classe"]], left_on="NR_ZONA", right_index=True, how="inner"
)
fig, ax = plt.subplots(figsize=(11, 11))
for classe, cor in CORES.items():
    sub = sp_plot[sp_plot["lisa_classe"] == classe]
    if sub.empty:
        continue
    sub.plot(
        ax=ax,
        color=cor,
        markersize=10 if classe == 0 else 18,
        alpha=0.4 if classe == 0 else 0.85,
        label=f"{ROTULOS[classe]} ({sub['NR_ZONA'].nunique()} zonas)",
    )
ax.set_title(
    "LISA — clusters locais de volatilidade eleitoral\n"
    f"Prefeito 1T, São Paulo, 2020→2024 (k={K_VIZINHOS}, α={ALPHA})",
    fontsize=12,
)
ax.set_axis_off()
ax.legend(loc="lower left", fontsize=9, framealpha=0.9)
plt.tight_layout()
plt.savefig(SAIDA_LISA, dpi=150, bbox_inches="tight")
print(f"Mapa LISA salvo: {SAIDA_LISA}")

# --- Zonas nominais dos clusters ----------------------------------------------
nomes = sp_cidade.groupby("NR_ZONA")["ZE_NOME"].first()
zonas_gdf["nome"] = nomes
zonas_gdf["p"] = lisa.p_sim

print("\nCluster HH (voláteis) — prefeito:")
hh = zonas_gdf[(zonas_gdf.lisa_classe == 1)].sort_values("volatilidade", ascending=False)
for zona, r in hh.iterrows():
    print(f"  Zona {zona:>4}  {r['nome']:<22}  vol={r['volatilidade']:.3f}  p={r['p']:.3f}")

print("\nCluster LL (estáveis) — prefeito:")
ll = zonas_gdf[(zonas_gdf.lisa_classe == 3)].sort_values("volatilidade")
for zona, r in ll.iterrows():
    print(f"  Zona {zona:>4}  {r['nome']:<22}  vol={r['volatilidade']:.3f}  p={r['p']:.3f}")
