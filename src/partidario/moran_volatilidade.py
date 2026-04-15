"""Moran's I da volatilidade eleitoral por zona — São Paulo, vereador 2020→2024.

A unidade de análise é a zona eleitoral, mas a geometria disponível é de pontos
(locais de votação do CEM). Construímos um centroide por zona — média das
coordenadas dos locais — e rodamos Moran I global com matriz de vizinhança
k-nearest neighbors (k=6). Também plotamos o diagrama de dispersão de Moran.
"""

from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from esda.moran import Moran
from libpysal.weights import KNN
from splot.esda import moran_scatterplot

from src.partidario.analise_volatilidade import (
    carregar_sp_vereador,
    pedersen_por_zona,
    votos_por_zona_partido,
)

SHAPEFILE = Path("data/raw/shapes/EL2022_LV_ESP_CEM_V2/EL2022_LV_ESP_CEM_V2.shp")
SAIDA_SCATTER = Path("outputs/moran_scatter_volatilidade.png")
K_VIZINHOS = 6
N_PERMUTACOES = 999

df_2020 = carregar_sp_vereador(2020)
df_2024 = carregar_sp_vereador(2024)
vol_zona = pedersen_por_zona(
    votos_por_zona_partido(df_2020), votos_por_zona_partido(df_2024)
).rename("volatilidade")

gdf = gpd.read_file(SHAPEFILE)
sp_cidade = gdf[gdf["MUN_NOME"] == "SAO PAULO"].copy()
sp_cidade["NR_ZONA"] = sp_cidade["ZE_NUM"].astype(int)

# Centroide de cada zona: média das coordenadas dos locais de votação
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
print(f"Zonas com centroide e volatilidade: {len(zonas_gdf)}")

w = KNN.from_dataframe(zonas_gdf, k=K_VIZINHOS)
w.transform = "R"

moran = Moran(zonas_gdf["volatilidade"].values, w, permutations=N_PERMUTACOES)

print(f"\nMoran I = {moran.I:.4f}")
print(f"E[I]   = {moran.EI:.4f}  (valor esperado sob nulo)")
print(f"z-score = {moran.z_sim:.3f}")
print(f"p-value = {moran.p_sim:.4f}  (com {N_PERMUTACOES} permutações)")

if moran.p_sim < 0.05:
    direcao = "positiva (clusters)" if moran.I > moran.EI else "negativa (dispersão)"
    print(f"→ Autocorrelação espacial {direcao} significativa a 5%.")
else:
    print("→ Sem evidência de autocorrelação espacial a 5%.")

fig, ax = moran_scatterplot(moran, aspect_equal=True)
ax.set_xlabel("Volatilidade (padronizada)")
ax.set_ylabel("Média dos vizinhos (padronizada)")
ax.set_title(
    f"Diagrama de Moran — volatilidade por zona (k={K_VIZINHOS})\n"
    f"I = {moran.I:.3f}, p = {moran.p_sim:.4f}"
)
SAIDA_SCATTER.parent.mkdir(parents=True, exist_ok=True)
plt.tight_layout()
plt.savefig(SAIDA_SCATTER, dpi=150, bbox_inches="tight")
print(f"\nScatter salvo em: {SAIDA_SCATTER}")
