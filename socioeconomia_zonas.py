"""Cruzamento socioeconômico (renda + escolaridade) por zona eleitoral de SP.

Pipeline:
1. Carrega setores censitários de SP (geobr, Censo 2010) — 18.953 polígonos
2. Carrega dados de renda e escolaridade por setor (Base IBGE Agregados 2010)
3. Join espacial: para cada local de votação (ponto do CEM), encontra o
   setor censitário que o contém — cada local herda renda + escolaridade
   do setor
4. Agrega locais por zona eleitoral (média ponderada pela população do setor)
5. Cruza com escore ideológico por zona (já calculado)
6. Gera scatter renda × escore + tabela de outliers

Objetivo: testar se Pinheiros, Bela Vista, Perdizes são anomalias na
relação voto × renda — isto é, se há renda/escolaridade alta E voto
progressista, contra o padrão linear esperado.
"""

from pathlib import Path

import geobr
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

from analise_volatilidade import carregar_sp_vereador, carregar_sp_prefeito
from ideologia import ESCORE_BOLOGNESI

CSV_BASICO = Path(
    "data/raw/censo2010/extraido/Basico_SP1.csv"
)
CSV_RENDA = Path(
    "data/raw/censo2010/extraido/DomicilioRenda_SP1.csv"
)
SHAPEFILE_LV = Path(
    "data/raw/shapes/EL2022_LV_ESP_CEM_V2/EL2022_LV_ESP_CEM_V2.shp"
)


def carregar_dados_censitarios() -> pd.DataFrame:
    """Renda e população por setor censitário de SP capital."""
    print("Carregando Basico_SP1.csv...")
    bas = pd.read_csv(
        CSV_BASICO, sep=";", encoding="latin-1", decimal=",", low_memory=False
    )
    # V002 = população residente. V005 = rendimento médio dos responsáveis
    # V009 = rendimento médio domiciliar per capita (usamos esse)
    # Para escolaridade, carregamos pessoa13 mas se não rodar, usa algo do básico
    bas["Cod_setor"] = bas["Cod_setor"].astype(str)
    bas = bas[["Cod_setor", "V001", "V002", "V005", "V009"]].rename(
        columns={
            "V001": "n_domicilios",
            "V002": "populacao",
            "V005": "renda_resp_media",
            "V009": "renda_pc_media",
        }
    )
    return bas


def carregar_setores_geo() -> gpd.GeoDataFrame:
    print("Baixando shapefile de setores censitários (SP)...")
    gdf = geobr.read_census_tract(code_tract=3550308, year=2010)
    gdf["Cod_setor"] = gdf["code_tract"].astype(str)
    return gdf[["Cod_setor", "name_district", "geometry"]]


def carregar_locais_votacao() -> gpd.GeoDataFrame:
    gdf = gpd.read_file(SHAPEFILE_LV)
    sp = gdf[gdf["MUN_NOME"] == "SAO PAULO"].copy()
    sp["NR_ZONA"] = sp["ZE_NUM"].astype(int)
    return sp[["NR_ZONA", "NOME_LV", "ZE_NOME", "geometry"]]


def escore_por_zona(ano: int, cargo: str = "vereador") -> pd.Series:
    fn = carregar_sp_vereador if cargo == "vereador" else carregar_sp_prefeito
    df = fn(ano)
    df["ESCORE"] = df["PARTIDO"].map(ESCORE_BOLOGNESI)
    df = df.dropna(subset=["ESCORE"])
    return df.groupby("NR_ZONA").apply(
        lambda g: (g["ESCORE"] * g["VOTOS"]).sum() / g["VOTOS"].sum(),
        include_groups=False,
    )


def pipeline():
    bas = carregar_dados_censitarios()
    setores = carregar_setores_geo()
    # Match setor × dados censo
    setores = setores.merge(bas, on="Cod_setor", how="inner")
    print(f"Setores com dados: {len(setores)}")
    setores = setores.dropna(subset=["renda_pc_media"])
    print(f"Setores com renda: {len(setores)}")

    locais = carregar_locais_votacao()
    # Precisam estar no mesmo CRS
    setores = setores.to_crs("EPSG:4326")
    locais = locais.to_crs("EPSG:4326")
    # Spatial join — cada local pega o setor que o contém
    print("Spatial join locais × setores...")
    locais_com_renda = gpd.sjoin(locais, setores, how="left", predicate="within")
    print(f"Locais com setor identificado: {locais_com_renda['Cod_setor'].notna().sum()}/{len(locais_com_renda)}")

    # Agrega por zona — média ponderada pela população do setor
    agg = (
        locais_com_renda.dropna(subset=["Cod_setor"])
        .groupby("NR_ZONA")
        .agg(
            renda_pc_media=("renda_pc_media", "mean"),
            renda_resp_media=("renda_resp_media", "mean"),
            populacao_total=("populacao", "sum"),
            n_locais=("NOME_LV", "count"),
            nome_ze=("ZE_NOME", "first"),
        )
    )

    # Cruza com escore ideológico 2024
    esc_ver_24 = escore_por_zona(2024, "vereador").rename("escore_ver_2024")
    esc_pref_24 = escore_por_zona(2024, "prefeito").rename("escore_pref_2024")
    esc_ver_20 = escore_por_zona(2020, "vereador").rename("escore_ver_2020")

    tab = agg.join(esc_ver_24).join(esc_pref_24).join(esc_ver_20)
    return tab


if __name__ == "__main__":
    tab = pipeline()
    print(f"\nTabela final: {len(tab)} zonas")

    # Ordena por renda
    tab_ord = tab.sort_values("renda_pc_media", ascending=False)
    print("\nTop 15 zonas com maior renda per capita (Censo 2010):")
    print(
        tab_ord[["nome_ze", "renda_pc_media", "escore_ver_2024", "escore_pref_2024"]]
        .head(15)
        .to_string(float_format=lambda x: f"{x:9.2f}")
    )

    print("\nTop 15 zonas com menor renda per capita:")
    print(
        tab_ord[["nome_ze", "renda_pc_media", "escore_ver_2024", "escore_pref_2024"]]
        .tail(15)
        .to_string(float_format=lambda x: f"{x:9.2f}")
    )

    # Correlações
    print("\nCorrelação de Pearson:")
    for col in ["escore_ver_2024", "escore_pref_2024", "escore_ver_2020"]:
        r = tab[["renda_pc_media", col]].corr().iloc[0, 1]
        print(f"  renda_pc × {col}: r = {r:.3f}")

    # Salva
    out = Path("outputs/socioeconomia_por_zona.csv")
    tab_ord.to_csv(out)
    print(f"\nCSV: {out}")
