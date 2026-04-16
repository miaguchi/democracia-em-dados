"""Índice placebo não-educacional por zona eleitoral.

Teste de robustez do índice institucional cultural-progressista:
calcula a fração de locais de votação em categorias NÃO-educacionais
por zona eleitoral e testa se esse índice prediz o escore ideológico.

Se R² ≈ 0, confirma que o efeito do índice original (R²=0,44) é
específico às categorias cultural-progressistas.

Duas versões:
- Estrito: só prisional (CDP, PENIT, FUND CASA, CPP) + saúde (POSTO SAUDE, UBS)
- Amplo: todas as categorias não-educacionais definidas em local_votacao.py
"""

from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import numpy as np
import pandas as pd
import geopandas as gpd

from src.dominio.local_votacao import _NAO_EDUCACIONAL

SHAPEFILE_LV = _ROOT / "data/raw/shapes/EL2022_LV_ESP_CEM_V2/EL2022_LV_ESP_CEM_V2.shp"
CSV_SOCIO = _ROOT / "outputs/socioeconomia_por_zona.csv"
CSV_INDICE_ORIGINAL = _ROOT / "outputs/indice_institucional_por_zona.csv"
SAIDA_CSV = _ROOT / "outputs/tables/indice_placebo_por_zona.csv"

# Placebo estrito: categorias sem qualquer relação teórica com voto progressista
CATEGORIAS_ESTRITO: set[str] = {
    "CDP", "PENIT", "FUND CASA", "CPP",
    "POSTO SAUDE", "UBS",
}

# Placebo amplo: todas as não-educacionais
CATEGORIAS_AMPLO: set[str] = set(_NAO_EDUCACIONAL)


def construir_indice_placebo(
    gdf: pd.DataFrame,
    modo: str = "estrito",
) -> pd.DataFrame:
    """Calcula o índice placebo por zona eleitoral.

    Parameters
    ----------
    gdf : pd.DataFrame
        DataFrame com colunas MUN_NOME, ZE_NUM, ZE_NOME, LV_TIPO, NOME_LV.
    modo : str
        ``"estrito"`` (prisional + saúde) ou ``"amplo"`` (todos não-educacionais).

    Returns
    -------
    pd.DataFrame
        Índice por zona com colunas: n_locais, n_placebo, indice_placebo, nome_ze.
    """
    categorias = CATEGORIAS_ESTRITO if modo == "estrito" else CATEGORIAS_AMPLO

    sp = gdf[gdf["MUN_NOME"] == "SAO PAULO"].copy()
    sp["NR_ZONA"] = sp["ZE_NUM"].astype(int)
    sp["is_placebo"] = sp["LV_TIPO"].isin(categorias).astype(int)

    agg = sp.groupby("NR_ZONA").agg(
        n_locais=("NOME_LV", "count"),
        n_placebo=("is_placebo", "sum"),
        nome_ze=("ZE_NOME", "first"),
    )
    agg["indice_placebo"] = agg["n_placebo"] / agg["n_locais"] * 100
    return agg


def _regressao_ols(X: np.ndarray, y: np.ndarray) -> dict:
    """Regressão OLS simples, retorna coeficientes e R²."""
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    y_hat = X @ beta
    ss_res = ((y - y_hat) ** 2).sum()
    ss_tot = ((y - y.mean()) ** 2).sum()
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return {"beta": beta, "r2": r2}


if __name__ == "__main__":
    # Carregar dados
    print("Carregando base CEM...")
    gdf = gpd.read_file(SHAPEFILE_LV)

    # Calcular índices placebo
    for modo in ["estrito", "amplo"]:
        print(f"\n{'='*60}")
        print(f"PLACEBO {modo.upper()}")
        print(f"{'='*60}")

        idx = construir_indice_placebo(gdf, modo=modo)

        print(f"\nZonas: {len(idx)}")
        print(f"Zonas com pelo menos 1 local placebo: {(idx['n_placebo'] > 0).sum()}")
        print(f"Total locais placebo: {idx['n_placebo'].sum()}")
        print(f"Índice médio: {idx['indice_placebo'].mean():.2f}%")
        print(f"Índice mediana: {idx['indice_placebo'].median():.2f}%")

        # Integrar com socioeconomia + escore
        socio = pd.read_csv(CSV_SOCIO).set_index("NR_ZONA")
        merge = idx.join(socio[["renda_pc_media", "escore_ver_2024", "escore_pref_2024"]])

        # Correlações
        print(f"\n--- Correlações ---")
        for col in ["escore_ver_2024", "escore_pref_2024"]:
            r = merge[["indice_placebo", col]].corr().iloc[0, 1]
            print(f"  indice_placebo × {col}: r = {r:+.3f}")

        # Regressão: escore ~ renda + indice_placebo
        sub = merge.dropna(subset=["escore_ver_2024", "renda_pc_media", "indice_placebo"])
        X = np.column_stack([
            np.ones(len(sub)),
            sub["renda_pc_media"].values,
            sub["indice_placebo"].values,
        ])

        print(f"\n--- Regressão OLS: escore ~ renda + indice_placebo ---")
        for dep in ["escore_ver_2024", "escore_pref_2024"]:
            y = sub[dep].values
            res = _regressao_ols(X, y)
            beta = res["beta"]
            print(f"\n  {dep}:")
            print(f"    intercepto       = {beta[0]:+.4f}")
            print(f"    renda_pc_media   = {beta[1]:+.6f}")
            print(f"    indice_placebo   = {beta[2]:+.4f}")
            print(f"    R²               = {res['r2']:.3f}")

    # Comparação com índice original
    print(f"\n{'='*60}")
    print("COMPARAÇÃO COM ÍNDICE ORIGINAL")
    print(f"{'='*60}")
    try:
        original = pd.read_csv(CSV_INDICE_ORIGINAL, index_col="NR_ZONA")
        socio = pd.read_csv(CSV_SOCIO).set_index("NR_ZONA")
        # Evitar colunas duplicadas se o CSV original já tiver escore/renda
        cols_socio = [c for c in ["renda_pc_media", "escore_ver_2024", "escore_pref_2024"]
                      if c not in original.columns]
        orig_merge = original.join(socio[cols_socio]) if cols_socio else original
        sub_orig = orig_merge.dropna(subset=["escore_ver_2024", "renda_pc_media", "indice_cultural"])
        X_orig = np.column_stack([
            np.ones(len(sub_orig)),
            sub_orig["renda_pc_media"].values,
            sub_orig["indice_cultural"].values,
        ])
        for dep in ["escore_ver_2024", "escore_pref_2024"]:
            y = sub_orig[dep].values
            res = _regressao_ols(X_orig, y)
            print(f"  Índice original — {dep}: R² = {res['r2']:.3f}")

        # Placebo estrito para comparação direta
        idx_est = construir_indice_placebo(gdf, modo="estrito")
        merge_est = idx_est.join(socio[["renda_pc_media", "escore_ver_2024", "escore_pref_2024"]])
        sub_est = merge_est.dropna(subset=["escore_ver_2024", "renda_pc_media", "indice_placebo"])
        X_est = np.column_stack([
            np.ones(len(sub_est)),
            sub_est["renda_pc_media"].values,
            sub_est["indice_placebo"].values,
        ])
        for dep in ["escore_ver_2024", "escore_pref_2024"]:
            y = sub_est[dep].values
            res = _regressao_ols(X_est, y)
            print(f"  Placebo estrito — {dep}: R² = {res['r2']:.3f}")

        idx_amp = construir_indice_placebo(gdf, modo="amplo")
        merge_amp = idx_amp.join(socio[["renda_pc_media", "escore_ver_2024", "escore_pref_2024"]])
        sub_amp = merge_amp.dropna(subset=["escore_ver_2024", "renda_pc_media", "indice_placebo"])
        X_amp = np.column_stack([
            np.ones(len(sub_amp)),
            sub_amp["renda_pc_media"].values,
            sub_amp["indice_placebo"].values,
        ])
        for dep in ["escore_ver_2024", "escore_pref_2024"]:
            y = sub_amp[dep].values
            res = _regressao_ols(X_amp, y)
            print(f"  Placebo amplo   — {dep}: R² = {res['r2']:.3f}")
    except FileNotFoundError as e:
        print(f"  Arquivo não encontrado: {e}")

    # Salvar CSV
    SAIDA_CSV.parent.mkdir(parents=True, exist_ok=True)
    idx_est = construir_indice_placebo(gdf, modo="estrito")
    idx_est.to_csv(SAIDA_CSV)
    print(f"\nCSV salvo: {SAIDA_CSV}")
