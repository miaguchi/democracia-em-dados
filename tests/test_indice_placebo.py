"""Testes do índice placebo não-educacional."""

from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import pandas as pd
import pytest

from src.urbano.indice_placebo import construir_indice_placebo, CATEGORIAS_ESTRITO


def test_categorias_estrito_contem_prisional_e_saude():
    assert "CDP" in CATEGORIAS_ESTRITO
    assert "PENIT" in CATEGORIAS_ESTRITO
    assert "FUND CASA" in CATEGORIAS_ESTRITO
    assert "CPP" in CATEGORIAS_ESTRITO
    assert "POSTO SAUDE" in CATEGORIAS_ESTRITO
    assert "UBS" in CATEGORIAS_ESTRITO


def test_categorias_estrito_nao_contem_educacional():
    assert "EE" not in CATEGORIAS_ESTRITO
    assert "EMEF" not in CATEGORIAS_ESTRITO
    assert "CEU" not in CATEGORIAS_ESTRITO


@pytest.fixture
def gdf_fake():
    """GeoDataFrame mínimo com 3 zonas, simulando SP."""
    return pd.DataFrame({
        "MUN_NOME": ["SAO PAULO"] * 10,
        "ZE_NUM": [1, 1, 1, 1, 1, 2, 2, 2, 3, 3],
        "ZE_NOME": ["Z1"] * 5 + ["Z2"] * 3 + ["Z3"] * 2,
        "NOME_LV": ["A"] * 10,
        "LV_TIPO": [
            # Z1: 5 locais, 2 prisionais
            "EE", "EMEF", "CDP", "PENIT", "COLEGIO",
            # Z2: 3 locais, 0 prisionais
            "EE", "EMEF", "FAC",
            # Z3: 2 locais, 1 saúde
            "EE", "POSTO SAUDE",
        ],
    })


def test_indice_placebo_calcula_fracao_correta(gdf_fake):
    resultado = construir_indice_placebo(gdf_fake, modo="estrito")
    # Z1: 2/5 = 40%
    assert resultado.loc[1, "indice_placebo"] == pytest.approx(40.0)
    # Z2: 0/3 = 0%
    assert resultado.loc[2, "indice_placebo"] == pytest.approx(0.0)
    # Z3: 1/2 = 50%
    assert resultado.loc[3, "indice_placebo"] == pytest.approx(50.0)


def test_indice_placebo_contagem_nao_educacional(gdf_fake):
    resultado = construir_indice_placebo(gdf_fake, modo="estrito")
    assert resultado.loc[1, "n_placebo"] == 2
    assert resultado.loc[2, "n_placebo"] == 0
    assert resultado.loc[3, "n_placebo"] == 1


def test_indice_placebo_modo_amplo_inclui_mais_categorias(gdf_fake):
    # Adicionar um local tipo IGREJA na zona 2
    extra = pd.DataFrame({
        "MUN_NOME": ["SAO PAULO"],
        "ZE_NUM": [2],
        "ZE_NOME": ["Z2"],
        "NOME_LV": ["METODISTA"],
        "LV_TIPO": ["IGREJA"],
    })
    gdf = pd.concat([gdf_fake, extra], ignore_index=True)
    estrito = construir_indice_placebo(gdf, modo="estrito")
    amplo = construir_indice_placebo(gdf, modo="amplo")
    # IGREJA não está no estrito, mas está no amplo
    assert estrito.loc[2, "n_placebo"] == 0
    assert amplo.loc[2, "n_placebo"] == 1


def test_indice_placebo_retorna_todas_zonas(gdf_fake):
    resultado = construir_indice_placebo(gdf_fake, modo="estrito")
    assert len(resultado) == 3
    assert set(resultado.index) == {1, 2, 3}
