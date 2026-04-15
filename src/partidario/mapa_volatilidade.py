"""Mapa de pontos: locais de votação de SP coloridos pela volatilidade da zona.

Fonte da geometria: base de locais de votação georreferenciados do CEM/USP
(EL2022_LV_ESP_CEM_V2). Cada local é um ponto com coluna ZE_NUM (zona eleitoral).
A volatilidade vem do vetor calculado em analise_volatilidade.py.
"""

from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt

from src.partidario.analise_volatilidade import (
    carregar_sp_vereador,
    pedersen_por_zona,
    votos_por_zona_partido,
)

SHAPEFILE = Path("data/raw/shapes/EL2022_LV_ESP_CEM_V2/EL2022_LV_ESP_CEM_V2.shp")
SAIDA = Path("outputs/mapa_volatilidade_sp_vereador_2020_2024.png")

# 1. Volatilidade por zona (reusa o pipeline do analise_volatilidade)
df_2020 = carregar_sp_vereador(2020)
df_2024 = carregar_sp_vereador(2024)
vol_zona = pedersen_por_zona(
    votos_por_zona_partido(df_2020), votos_por_zona_partido(df_2024)
).rename("volatilidade")

# 2. Carrega shape e filtra para o município de São Paulo
gdf = gpd.read_file(SHAPEFILE)
sp_cidade = gdf[gdf["MUN_NOME"] == "SAO PAULO"].copy()
sp_cidade["NR_ZONA"] = sp_cidade["ZE_NUM"].astype(int)

# 3. Join: cada ponto recebe a volatilidade da sua zona
sp_cidade = sp_cidade.merge(vol_zona, left_on="NR_ZONA", right_index=True, how="inner")
print(f"Locais de votação em SP: {len(sp_cidade)}")
print(f"Zonas cobertas: {sp_cidade['NR_ZONA'].nunique()}")

# 4. Plota
fig, ax = plt.subplots(figsize=(11, 11))
sp_cidade.plot(
    column="volatilidade",
    ax=ax,
    markersize=12,
    cmap="RdYlBu_r",
    legend=True,
    legend_kwds={
        "label": "Volatilidade de Pedersen (2020→2024)",
        "shrink": 0.6,
    },
    alpha=0.75,
)
ax.set_title(
    "Volatilidade eleitoral por zona — vereador, São Paulo, 2020→2024\n"
    "Cada ponto é um local de votação, colorido pela volatilidade da sua zona",
    fontsize=12,
)
ax.set_axis_off()
SAIDA.parent.mkdir(parents=True, exist_ok=True)
plt.tight_layout()
plt.savefig(SAIDA, dpi=150, bbox_inches="tight")
print(f"Mapa salvo em: {SAIDA}")
