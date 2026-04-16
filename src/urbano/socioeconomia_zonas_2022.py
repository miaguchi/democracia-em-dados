"""Cruzamento renda × escore ideológico por zona eleitoral — Censo 2022.

Replica o pipeline de socioeconomia_zonas.py (Censo 2010) usando dados
de rendimento do responsável do Censo 2022, divulgados em 30/04/2025.

Pipeline:
1. Carrega setores censitários de SP (geobr, Censo 2022) — 27.301 polígonos
2. Carrega dados de rendimento do responsável (IBGE FTP, Censo 2022)
3. Join espacial: local de votação → setor censitário → renda
4. Agrega por zona eleitoral
5. Cruza com escore ideológico
6. Compara R² com versão Censo 2010
"""

from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import numpy as np
import geobr
import geopandas as gpd
import pandas as pd

from src.partidario.analise_volatilidade import carregar_sp_vereador, carregar_sp_prefeito
from src.partidario.ideologia import ESCORE_BOLOGNESI

CSV_RENDA_2022 = (
    _ROOT / "data/raw/censo2022/extraido_renda"
    / "Agregados_por_setores_renda_responsavel_BR.csv"
)
SHAPEFILE_LV = _ROOT / "data/raw/shapes/EL2022_LV_ESP_CEM_V2/EL2022_LV_ESP_CEM_V2.shp"
SAIDA_CSV = _ROOT / "outputs/socioeconomia_por_zona_2022.csv"


def carregar_renda_2022() -> pd.DataFrame:
    """Rendimento médio do responsável por setor censitário, Censo 2022."""
    print("Carregando rendimento do responsável (Censo 2022)...")
    df = pd.read_csv(
        CSV_RENDA_2022, sep=";", encoding="latin-1", dtype={"CD_SETOR": str}
    )
    # Filtrar SP capital (código IBGE começa com 355030)
    sp = df[df["CD_SETOR"].str.startswith("355030")].copy()

    # V06004 = rendimento médio mensal do responsável (string com vírgula)
    # "X" = sigilo estatístico — substituir por NaN
    sp["renda_resp_2022"] = pd.to_numeric(
        sp["V06004"].str.replace(",", "."), errors="coerce"
    )
    # V06001 = pessoas responsáveis (para ponderação)
    sp["n_responsaveis"] = pd.to_numeric(
        sp["V06001"].str.replace(",", "."), errors="coerce"
    )

    print(f"  Setores em SP capital: {len(sp)}")
    print(f"  Com renda válida: {sp['renda_resp_2022'].notna().sum()}")
    print(f"  Sigilo ('X'): {(df['V06004'] == 'X').sum()} (BR), "
          f"{(sp['V06004'] == 'X').sum() if 'V06004' in sp.columns else '?'} (SP)")

    return sp[["CD_SETOR", "renda_resp_2022", "n_responsaveis"]]


def carregar_setores_geo_2022() -> gpd.GeoDataFrame:
    """Polígonos dos setores censitários de SP capital, Censo 2022."""
    print("Baixando setores censitários 2022 (geobr)...")
    gdf = geobr.read_census_tract(code_tract=3550308, year=2022)
    gdf["CD_SETOR"] = gdf["code_tract"].astype(np.int64).astype(str)
    return gdf[["CD_SETOR", "name_district", "geometry"]]


def carregar_locais_votacao() -> gpd.GeoDataFrame:
    """Locais de votação de SP capital (base CEM)."""
    gdf = gpd.read_file(SHAPEFILE_LV)
    sp = gdf[gdf["MUN_NOME"] == "SAO PAULO"].copy()
    sp["NR_ZONA"] = sp["ZE_NUM"].astype(int)
    return sp[["NR_ZONA", "NOME_LV", "ZE_NOME", "geometry"]]


def escore_por_zona(ano: int, cargo: str = "vereador") -> pd.Series:
    """Escore ideológico médio ponderado por zona."""
    fn = carregar_sp_vereador if cargo == "vereador" else carregar_sp_prefeito
    df = fn(ano)
    df["ESCORE"] = df["PARTIDO"].map(ESCORE_BOLOGNESI)
    df = df.dropna(subset=["ESCORE"])
    return df.groupby("NR_ZONA").apply(
        lambda g: (g["ESCORE"] * g["VOTOS"]).sum() / g["VOTOS"].sum(),
        include_groups=False,
    )


def pipeline() -> pd.DataFrame:
    """Executa o pipeline completo: renda 2022 × escore por zona."""
    renda = carregar_renda_2022()
    setores = carregar_setores_geo_2022()

    # Match setores × renda
    setores = setores.merge(renda, on="CD_SETOR", how="inner")
    print(f"Setores com dados de renda: {len(setores)}")
    setores = setores.dropna(subset=["renda_resp_2022"])
    print(f"Setores com renda válida: {len(setores)}")

    # Locais de votação
    locais = carregar_locais_votacao()

    # CRS
    setores = setores.to_crs("EPSG:4326")
    locais = locais.to_crs("EPSG:4326")

    # Spatial join
    print("Spatial join locais × setores 2022...")
    locais_com_renda = gpd.sjoin(locais, setores, how="left", predicate="within")
    matched = locais_com_renda["CD_SETOR"].notna().sum()
    print(f"Locais com setor identificado: {matched}/{len(locais_com_renda)}")

    # Agrega por zona
    agg = (
        locais_com_renda.dropna(subset=["CD_SETOR"])
        .groupby("NR_ZONA")
        .agg(
            renda_resp_2022=("renda_resp_2022", "mean"),
            n_locais=("NOME_LV", "count"),
            nome_ze=("ZE_NOME", "first"),
        )
    )

    # Escores ideológicos
    esc_ver_24 = escore_por_zona(2024, "vereador").rename("escore_ver_2024")
    esc_pref_24 = escore_por_zona(2024, "prefeito").rename("escore_pref_2024")

    tab = agg.join(esc_ver_24).join(esc_pref_24)
    return tab


if __name__ == "__main__":
    tab = pipeline()
    print(f"\nTabela final: {len(tab)} zonas")

    # Correlações Censo 2022
    print("\n" + "=" * 65)
    print("CORRELAÇÕES — RENDA CENSO 2022 × ESCORE")
    print("=" * 65)
    for col in ["escore_ver_2024", "escore_pref_2024"]:
        r = tab[["renda_resp_2022", col]].corr().iloc[0, 1]
        print(f"  renda_resp_2022 × {col}: r = {r:+.3f}  (R² = {r**2:.3f})")

    # Regressão OLS: escore ~ renda_2022
    sub = tab.dropna(subset=["escore_ver_2024", "renda_resp_2022"])
    X = np.column_stack([np.ones(len(sub)), sub["renda_resp_2022"].values])
    for dep in ["escore_ver_2024", "escore_pref_2024"]:
        y = sub[dep].values
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        y_hat = X @ beta
        r2 = 1 - ((y - y_hat) ** 2).sum() / ((y - y.mean()) ** 2).sum()
        print(f"\n  OLS {dep} ~ renda_resp_2022:")
        print(f"    intercepto     = {beta[0]:+.4f}")
        print(f"    renda_resp     = {beta[1]:+.8f}")
        print(f"    R²             = {r2:.3f}")

    # Comparação com Censo 2010
    print("\n" + "=" * 65)
    print("COMPARAÇÃO COM CENSO 2010")
    print("=" * 65)
    try:
        socio_2010 = pd.read_csv(
            _ROOT / "outputs/socioeconomia_por_zona.csv", index_col="NR_ZONA"
        )
        for col in ["escore_ver_2024", "escore_pref_2024"]:
            r_2010 = socio_2010[["renda_pc_media", col]].corr().iloc[0, 1]
            r_2022 = tab[["renda_resp_2022", col]].corr().iloc[0, 1]
            print(f"\n  {col}:")
            print(f"    Renda Censo 2010 (per capita):     r = {r_2010:+.3f}  R² = {r_2010**2:.3f}")
            print(f"    Renda Censo 2022 (responsável):    r = {r_2022:+.3f}  R² = {r_2022**2:.3f}")
            print(f"    Diferença R²:                      {r_2022**2 - r_2010**2:+.3f}")
    except FileNotFoundError:
        print("  socioeconomia_por_zona.csv não encontrado — pule comparação")

    # Salvar
    SAIDA_CSV.parent.mkdir(parents=True, exist_ok=True)
    tab.sort_values("renda_resp_2022", ascending=False).to_csv(SAIDA_CSV)
    print(f"\nCSV salvo: {SAIDA_CSV}")
