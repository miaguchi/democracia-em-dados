"""LISA (Moran Local) da volatilidade por zona — São Paulo, vereador 2020→2024.

Classifica cada zona em HH / LL / HL / LH (quadrante de Moran) e destaca apenas
as significativas (p < 0.05 por permutação). O mapa de pontos é colorido pela
classe LISA da zona a que cada local de votação pertence.
"""

from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
from esda.moran import Moran_Local
from libpysal.weights import KNN

from analise_volatilidade import (
    carregar_sp_vereador,
    pedersen_por_zona,
    votos_por_zona_partido,
)

SHAPEFILE = Path("data/raw/shapes/EL2022_LV_ESP_CEM_V2/EL2022_LV_ESP_CEM_V2.shp")
SAIDA = Path("outputs/lisa_volatilidade_sp_vereador_2020_2024.png")
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
CORES = {
    0: "#cccccc",
    1: "#d7191c",  # HH - vermelho
    2: "#abd9e9",  # LH
    3: "#2c7bb6",  # LL - azul
    4: "#fdae61",  # HL
}

df_2020 = carregar_sp_vereador(2020)
df_2024 = carregar_sp_vereador(2024)
vol_zona = pedersen_por_zona(
    votos_por_zona_partido(df_2020), votos_por_zona_partido(df_2024)
).rename("volatilidade")

gdf = gpd.read_file(SHAPEFILE)
sp_cidade = gdf[gdf["MUN_NOME"] == "SAO PAULO"].copy()
sp_cidade["NR_ZONA"] = sp_cidade["ZE_NUM"].astype(int)
sp_cidade["lon"] = sp_cidade.geometry.x
sp_cidade["lat"] = sp_cidade.geometry.y

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

lisa = Moran_Local(
    zonas_gdf["volatilidade"].values, w, permutations=N_PERMUTACOES
)
# q: quadrante (1=HH, 2=LH, 3=LL, 4=HL). Zera onde não for significativo.
classes = lisa.q.copy()
classes[lisa.p_sim >= ALPHA] = 0
zonas_gdf["lisa_classe"] = classes

contagem = zonas_gdf["lisa_classe"].value_counts().sort_index()
print("Distribuição LISA (zonas):")
for k, v in contagem.items():
    print(f"  {ROTULOS[k]:<32} {v}")

# Propaga a classe para os locais de votação
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
    f"Vereador, São Paulo, 2020→2024 (k={K_VIZINHOS}, α={ALPHA})",
    fontsize=12,
)
ax.set_axis_off()
ax.legend(loc="lower left", fontsize=9, framealpha=0.9)
SAIDA.parent.mkdir(parents=True, exist_ok=True)
plt.tight_layout()
plt.savefig(SAIDA, dpi=150, bbox_inches="tight")
print(f"\nMapa LISA salvo em: {SAIDA}")
