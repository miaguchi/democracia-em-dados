"""Testes da cross-validation do índice institucional."""

from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import numpy as np
import pandas as pd
import pytest

from src.urbano.crossval_indice import loo_cv, kfold_cv


@pytest.fixture
def dados_sinteticos():
    """Dados com relação linear forte (R² alto, sem overfit)."""
    rng = np.random.default_rng(42)
    n = 50
    x1 = rng.uniform(0, 100, n)
    x2 = rng.uniform(500, 3000, n)
    y = 5.0 - 0.02 * x1 + 0.0001 * x2 + rng.normal(0, 0.2, n)
    return pd.DataFrame({"indice": x1, "renda": x2, "escore": y})


def test_loo_retorna_r2_e_previsoes(dados_sinteticos):
    resultado = loo_cv(dados_sinteticos, y_col="escore", x_cols=["indice", "renda"])
    assert "r2_loo" in resultado
    assert "r2_insample" in resultado
    assert "y_pred" in resultado
    assert len(resultado["y_pred"]) == len(dados_sinteticos)


def test_loo_r2_proximo_do_insample_quando_sinal_forte(dados_sinteticos):
    resultado = loo_cv(dados_sinteticos, y_col="escore", x_cols=["indice", "renda"])
    # Com sinal forte e N=50, LOO R² deve ser próximo do in-sample
    assert resultado["r2_loo"] > 0.5
    assert abs(resultado["r2_loo"] - resultado["r2_insample"]) < 0.15


def test_kfold_retorna_r2_medio_e_desvio(dados_sinteticos):
    resultado = kfold_cv(dados_sinteticos, y_col="escore", x_cols=["indice", "renda"], k=5)
    assert "r2_medio" in resultado
    assert "r2_std" in resultado
    assert "r2_folds" in resultado
    assert len(resultado["r2_folds"]) == 5


def test_kfold_r2_positivo_quando_sinal_forte(dados_sinteticos):
    resultado = kfold_cv(dados_sinteticos, y_col="escore", x_cols=["indice", "renda"], k=5)
    assert resultado["r2_medio"] > 0.3


def test_loo_com_ruido_puro_r2_baixo():
    """Se y é ruído puro, LOO R² deve ser negativo ou muito baixo."""
    rng = np.random.default_rng(99)
    n = 50
    df = pd.DataFrame({
        "indice": rng.uniform(0, 100, n),
        "renda": rng.uniform(500, 3000, n),
        "escore": rng.normal(5, 1, n),
    })
    resultado = loo_cv(df, y_col="escore", x_cols=["indice", "renda"])
    assert resultado["r2_loo"] < 0.15
