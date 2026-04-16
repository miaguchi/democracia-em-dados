"""Cross-validation do índice institucional cultural-progressista.

Teste de robustez: verificar se o R²=0.44 do modelo
escore ~ renda + indice_cultural é estável ou resultado de overfit.

Métodos:
- Leave-One-Out (LOO): cada zona é prevista pelo modelo treinado nas 57 restantes
- K-Fold (k=5, k=10): partições aleatórias

Se R² out-of-sample ≈ R² in-sample, o modelo generaliza bem.
Se R² out-of-sample << R² in-sample, há overfit.
"""

from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import numpy as np
import pandas as pd

CSV_INDICE = _ROOT / "outputs/indice_institucional_por_zona.csv"
CSV_SOCIO = _ROOT / "outputs/socioeconomia_por_zona.csv"


def _ols_predict(X_train: np.ndarray, y_train: np.ndarray,
                 X_test: np.ndarray) -> np.ndarray:
    """Treina OLS no train e prediz no test."""
    beta, *_ = np.linalg.lstsq(X_train, y_train, rcond=None)
    return X_test @ beta


def loo_cv(df: pd.DataFrame, y_col: str, x_cols: list[str]) -> dict:
    """Leave-One-Out cross-validation.

    Parameters
    ----------
    df : pd.DataFrame
        Dados com colunas y_col e x_cols.
    y_col : str
        Nome da coluna dependente.
    x_cols : list[str]
        Nomes das colunas independentes.

    Returns
    -------
    dict
        r2_loo, r2_insample, y_pred, residuos.
    """
    df = df.dropna(subset=[y_col] + x_cols).reset_index(drop=True)
    n = len(df)
    y = df[y_col].values
    X = np.column_stack([np.ones(n)] + [df[c].values for c in x_cols])

    # In-sample R²
    beta_full, *_ = np.linalg.lstsq(X, y, rcond=None)
    y_hat_full = X @ beta_full
    ss_tot = ((y - y.mean()) ** 2).sum()
    r2_insample = 1 - ((y - y_hat_full) ** 2).sum() / ss_tot

    # LOO
    y_pred = np.zeros(n)
    for i in range(n):
        mask = np.ones(n, dtype=bool)
        mask[i] = False
        y_pred[i] = _ols_predict(X[mask], y[mask], X[i:i+1, :])[0]

    ss_res_loo = ((y - y_pred) ** 2).sum()
    r2_loo = 1 - ss_res_loo / ss_tot

    return {
        "r2_loo": r2_loo,
        "r2_insample": r2_insample,
        "y_pred": y_pred,
        "residuos": y - y_pred,
        "n": n,
    }


def kfold_cv(df: pd.DataFrame, y_col: str, x_cols: list[str],
             k: int = 5, seed: int = 42) -> dict:
    """K-Fold cross-validation.

    Parameters
    ----------
    df : pd.DataFrame
        Dados com colunas y_col e x_cols.
    y_col : str
        Nome da coluna dependente.
    x_cols : list[str]
        Nomes das colunas independentes.
    k : int
        Número de folds.
    seed : int
        Semente para reprodutibilidade.

    Returns
    -------
    dict
        r2_medio, r2_std, r2_folds.
    """
    df = df.dropna(subset=[y_col] + x_cols).reset_index(drop=True)
    n = len(df)
    y = df[y_col].values
    X = np.column_stack([np.ones(n)] + [df[c].values for c in x_cols])

    rng = np.random.default_rng(seed)
    indices = rng.permutation(n)
    folds = np.array_split(indices, k)

    r2_folds = []
    for fold in folds:
        mask = np.ones(n, dtype=bool)
        mask[fold] = False
        y_pred = _ols_predict(X[mask], y[mask], X[fold])
        ss_res = ((y[fold] - y_pred) ** 2).sum()
        ss_tot = ((y[fold] - y[fold].mean()) ** 2).sum()
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
        r2_folds.append(r2)

    return {
        "r2_medio": np.mean(r2_folds),
        "r2_std": np.std(r2_folds),
        "r2_folds": r2_folds,
        "k": k,
    }


if __name__ == "__main__":
    # Carregar dados
    idx = pd.read_csv(CSV_INDICE, index_col="NR_ZONA")
    socio = pd.read_csv(CSV_SOCIO).set_index("NR_ZONA")

    # Evitar duplicatas
    cols_socio = [c for c in ["renda_pc_media", "escore_ver_2024", "escore_pref_2024"]
                  if c not in idx.columns]
    df = idx.join(socio[cols_socio]) if cols_socio else idx.copy()

    print("=" * 65)
    print("CROSS-VALIDATION DO ÍNDICE INSTITUCIONAL")
    print("=" * 65)

    for dep in ["escore_ver_2024", "escore_pref_2024"]:
        print(f"\n--- {dep} ---")

        # Modelo completo: escore ~ renda + indice_cultural
        x_cols = ["renda_pc_media", "indice_cultural"]

        # LOO
        res_loo = loo_cv(df, y_col=dep, x_cols=x_cols)
        print(f"\n  LOO (N={res_loo['n']}):")
        print(f"    R² in-sample:     {res_loo['r2_insample']:.3f}")
        print(f"    R² LOO:           {res_loo['r2_loo']:.3f}")
        print(f"    Diferença:        {res_loo['r2_insample'] - res_loo['r2_loo']:+.3f}")
        print(f"    RMSE LOO:         {np.sqrt((res_loo['residuos']**2).mean()):.4f}")

        # 5-Fold
        for k in [5, 10]:
            res_kf = kfold_cv(df, y_col=dep, x_cols=x_cols, k=k)
            print(f"\n  {k}-Fold CV:")
            print(f"    R² médio:         {res_kf['r2_medio']:.3f} ± {res_kf['r2_std']:.3f}")
            print(f"    R² por fold:      {', '.join(f'{r:.3f}' for r in res_kf['r2_folds'])}")

        # Modelo só renda (baseline)
        print(f"\n  --- Baseline: escore ~ renda ---")
        res_loo_renda = loo_cv(df, y_col=dep, x_cols=["renda_pc_media"])
        print(f"    R² in-sample:     {res_loo_renda['r2_insample']:.3f}")
        print(f"    R² LOO:           {res_loo_renda['r2_loo']:.3f}")

        # Modelo só índice
        print(f"\n  --- Alternativo: escore ~ indice_cultural ---")
        res_loo_idx = loo_cv(df, y_col=dep, x_cols=["indice_cultural"])
        print(f"    R² in-sample:     {res_loo_idx['r2_insample']:.3f}")
        print(f"    R² LOO:           {res_loo_idx['r2_loo']:.3f}")

    # Síntese
    print(f"\n{'='*65}")
    print("SÍNTESE")
    print(f"{'='*65}")
    res = loo_cv(df, y_col="escore_ver_2024", x_cols=["renda_pc_media", "indice_cultural"])
    delta = res["r2_insample"] - res["r2_loo"]
    if delta < 0.05:
        veredicto = "ESTÁVEL — sem evidência de overfit"
    elif delta < 0.10:
        veredicto = "LEVE SHRINKAGE — aceitável para N=58"
    else:
        veredicto = "ATENÇÃO — possível overfit"
    print(f"  R² in-sample: {res['r2_insample']:.3f}")
    print(f"  R² LOO:       {res['r2_loo']:.3f}")
    print(f"  Shrinkage:    {delta:+.3f}")
    print(f"  Veredicto:    {veredicto}")
