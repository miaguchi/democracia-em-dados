"""Testes do PCA agnóstico sobre equipamentos CEM."""

from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import numpy as np
import pandas as pd
import pytest

from src.urbano.pca_equipamentos import construir_matriz_equipamentos, rodar_pca


@pytest.fixture
def gdf_fake():
    """GeoDataFrame mínimo com 3 zonas e 4 tipos de equipamento."""
    return pd.DataFrame({
        "MUN_NOME": ["SAO PAULO"] * 12,
        "ZE_NUM": [1]*4 + [2]*4 + [3]*4,
        "ZE_NOME": ["Z1"]*4 + ["Z2"]*4 + ["Z3"]*4,
        "NOME_LV": [f"Local{i}" for i in range(12)],
        "LV_TIPO": [
            "EE", "EE", "FAC", "EMEF",      # Z1: 2 EE, 1 FAC, 1 EMEF
            "EE", "EMEF", "EMEF", "EMEI",    # Z2: 1 EE, 2 EMEF, 1 EMEI
            "FAC", "FAC", "UNIV", "EMEI",    # Z3: 2 FAC, 1 UNIV, 1 EMEI
        ],
    })


def test_construir_matriz_shape(gdf_fake):
    matriz, nomes_cols = construir_matriz_equipamentos(gdf_fake)
    assert matriz.shape[0] == 3  # 3 zonas
    # Categorias presentes: EE, FAC, EMEF, EMEI, UNIV = 5
    assert matriz.shape[1] == 5
    assert len(nomes_cols) == 5


def test_construir_matriz_contagens_corretas(gdf_fake):
    matriz, nomes_cols = construir_matriz_equipamentos(gdf_fake)
    df = pd.DataFrame(matriz, columns=nomes_cols, index=[1, 2, 3])
    # Z1 tem 2 EE
    assert df.loc[1, "EE"] == 2
    # Z3 tem 2 FAC
    assert df.loc[3, "FAC"] == 2
    # Z2 tem 0 FAC
    assert df.loc[2, "FAC"] == 0


def test_rodar_pca_retorna_componentes(gdf_fake):
    matriz, nomes_cols = construir_matriz_equipamentos(gdf_fake)
    resultado = rodar_pca(matriz, nomes_cols)
    assert "pc1" in resultado
    assert "loadings" in resultado
    assert "variancia_explicada" in resultado
    assert len(resultado["pc1"]) == 3


def test_pca_variancia_explicada_soma_1(gdf_fake):
    matriz, nomes_cols = construir_matriz_equipamentos(gdf_fake)
    resultado = rodar_pca(matriz, nomes_cols)
    assert resultado["variancia_explicada"].sum() == pytest.approx(1.0, abs=0.01)


def test_pca_loadings_tem_todas_categorias(gdf_fake):
    matriz, nomes_cols = construir_matriz_equipamentos(gdf_fake)
    resultado = rodar_pca(matriz, nomes_cols)
    assert len(resultado["loadings"]) == len(nomes_cols)
