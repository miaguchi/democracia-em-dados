"""Classificação de locais de votação da base CEM/USP.

Separa locais em educacionais e não-educacionais com base na coluna
LV_TIPO (e, para FUND, no NOME_LV). A classificação segue decisão
documentada em reports/inventario_cem_placebo.md (2026-04-16).
"""

from pathlib import Path
import sys
from typing import Tuple

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import geopandas as gpd
import pandas as pd

SHAPEFILE_CEM = _ROOT / "data/raw/shapes/EL2022_LV_ESP_CEM_V2/EL2022_LV_ESP_CEM_V2.shp"

# Tipos explicitamente não-educacionais (por LV_TIPO).
_NAO_EDUCACIONAL: set[str] = {
    # Prisional / socioeducativo
    "CDP", "PENIT", "FUND CASA", "CPP",
    # Saúde
    "POSTO SAUDE", "UBS",
    # Associações / cooperativas
    "ASSOC", "ASSOC CULT", "COOP", "ASSIST SOC",
    # Religioso
    "IGREJA", "PASTORAL",
    # Esportivo
    "CLUBE", "CLUBE ATL", "CDC",
    # Assistência social
    "CREAS", "CCA",
    # Administrativo / público
    "AUTARQUIA", "SECRETARIA",
    # Cultural
    "ESP CULT", "BIBLI", "GURI",
    # Equipamento público
    "EQUIP PUB",
    # Comunidade / assentamento
    "BAIRRO", "ASSENT",
    # CEU puro (sem escola no tipo)
    "CEU",
    # Núcleo assistencial
    "NUCLEO",
}


def classificar_local(lv_tipo: str, nome_lv: str) -> str:
    """Classifica um local de votação como educacional ou não-educacional.

    Parameters
    ----------
    lv_tipo : str
        Valor da coluna LV_TIPO na base CEM.
    nome_lv : str
        Valor da coluna NOME_LV (nome do local de votação).

    Returns
    -------
    str
        ``"educacional"`` ou ``"nao_educacional"``.
    """
    if lv_tipo in _NAO_EDUCACIONAL:
        return "nao_educacional"

    # FUND: fundações com "LAR" no nome são assistenciais, não educacionais.
    if lv_tipo == "FUND" and "LAR " in (nome_lv or ""):
        return "nao_educacional"

    return "educacional"


def filtrar_locais_cem(
    gdf: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Separa locais de votação em educacionais e não-educacionais.

    Parameters
    ----------
    gdf : pd.DataFrame or gpd.GeoDataFrame
        DataFrame com ao menos as colunas ``LV_TIPO`` e ``NOME_LV``.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        ``(educacional, nao_educacional)`` — cada um com coluna extra
        ``classificacao``.
    """
    gdf = gdf.copy()
    gdf["classificacao"] = gdf.apply(
        lambda r: classificar_local(r["LV_TIPO"], r["NOME_LV"]),
        axis=1,
    )
    educ = gdf[gdf["classificacao"] == "educacional"]
    nao_educ = gdf[gdf["classificacao"] == "nao_educacional"]
    return educ, nao_educ


def carregar_cem(
    caminho: Path = SHAPEFILE_CEM,
) -> gpd.GeoDataFrame:
    """Carrega a base CEM/USP EL2022_LV_ESP_CEM_V2.

    Parameters
    ----------
    caminho : Path
        Caminho para o shapefile.

    Returns
    -------
    gpd.GeoDataFrame
        GeoDataFrame com todas as colunas originais.
    """
    return gpd.read_file(caminho)
