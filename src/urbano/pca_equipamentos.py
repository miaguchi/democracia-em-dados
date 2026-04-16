"""PCA agnóstico sobre equipamentos do CEM por zona eleitoral.

Teste de robustez: extrai PC1 de todos os tipos de equipamento (LV_TIPO)
por zona, sem usar a classificação manual cultural-progressista.

Se PC1 correlaciona com o índice manual e prediz escore ideológico,
confirma que a dimensão capturada pelo índice existe nos dados
independente da classificação subjetiva do pesquisador.
"""

from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

SHAPEFILE_LV = _ROOT / "data/raw/shapes/EL2022_LV_ESP_CEM_V2/EL2022_LV_ESP_CEM_V2.shp"
SETORES_CACHE = _ROOT / "data/raw/shapes/setores_2022_sp.gpkg"
CSV_INDICE = _ROOT / "outputs/indice_institucional_por_zona.csv"
CSV_SOCIO = _ROOT / "outputs/socioeconomia_por_zona.csv"
SAIDA_CSV = _ROOT / "outputs/tables/pca_equipamentos.csv"
SAIDA_FIG = _ROOT / "outputs/figures/scatter_pc1_vs_indice.png"


def construir_matriz_equipamentos(
    gdf: pd.DataFrame,
) -> tuple[np.ndarray, list[str]]:
    """Constrói matriz zonas × categorias de equipamento.

    Parameters
    ----------
    gdf : pd.DataFrame
        DataFrame com colunas MUN_NOME, ZE_NUM, LV_TIPO.

    Returns
    -------
    tuple[np.ndarray, list[str]]
        Matriz (n_zonas × n_categorias) e lista de nomes das categorias.
    """
    sp = gdf[gdf["MUN_NOME"] == "SAO PAULO"].copy()
    sp["NR_ZONA"] = sp["ZE_NUM"].astype(int)

    # Pivot: contagem de locais por zona × LV_TIPO
    pivot = sp.groupby(["NR_ZONA", "LV_TIPO"]).size().unstack(fill_value=0)

    nomes_cols = list(pivot.columns)
    matriz = pivot.values.astype(float)
    return matriz, nomes_cols


def rodar_pca(
    matriz: np.ndarray,
    nomes_cols: list[str],
) -> dict:
    """Roda PCA na matriz de equipamentos.

    Parameters
    ----------
    matriz : np.ndarray
        Matriz (n_zonas × n_categorias).
    nomes_cols : list[str]
        Nomes das categorias.

    Returns
    -------
    dict
        pc1, loadings, variancia_explicada.
    """
    # Normalizar
    scaler = StandardScaler()
    X = scaler.fit_transform(matriz)

    # PCA completo
    n_components = min(X.shape)
    pca = PCA(n_components=n_components)
    scores = pca.fit_transform(X)

    # Loadings de PC1
    loadings_pc1 = pd.Series(
        pca.components_[0], index=nomes_cols, name="loading_pc1"
    ).sort_values(key=abs, ascending=False)

    return {
        "pc1": scores[:, 0],
        "scores": scores,
        "loadings": loadings_pc1,
        "variancia_explicada": pca.explained_variance_ratio_,
        "pca": pca,
    }


if __name__ == "__main__":
    # Carregar dados
    print("Carregando base CEM...")
    gdf = gpd.read_file(SHAPEFILE_LV)
    sp = gdf[gdf["MUN_NOME"] == "SAO PAULO"].copy()
    sp["NR_ZONA"] = sp["ZE_NUM"].astype(int)

    # Construir matriz e rodar PCA
    matriz, nomes_cols = construir_matriz_equipamentos(gdf)
    resultado = rodar_pca(matriz, nomes_cols)

    # Índices das zonas (para merge)
    pivot = sp.groupby(["NR_ZONA", "LV_TIPO"]).size().unstack(fill_value=0)
    zonas = pivot.index

    print(f"\nMatriz: {matriz.shape[0]} zonas × {matriz.shape[1]} categorias")
    print(f"Variância explicada por PC1: {resultado['variancia_explicada'][0]:.1%}")
    print(f"Variância explicada por PC1-3: {resultado['variancia_explicada'][:3].sum():.1%}")

    # Top 15 loadings de PC1
    print(f"\n{'='*65}")
    print("TOP 15 LOADINGS DE PC1 (em valor absoluto)")
    print(f"{'='*65}")
    for cat, loading in resultado["loadings"].head(15).items():
        print(f"  {cat:<25} {loading:+.3f}")

    # Correlação PC1 × índice manual
    print(f"\n{'='*65}")
    print("CORRELAÇÃO PC1 × ÍNDICE MANUAL")
    print(f"{'='*65}")
    try:
        idx_orig = pd.read_csv(CSV_INDICE, index_col="NR_ZONA")
        pc1_series = pd.Series(resultado["pc1"], index=zonas, name="PC1")
        merged = idx_orig.join(pc1_series)

        r_pc1_indice = merged[["indice_cultural", "PC1"]].corr().iloc[0, 1]
        print(f"  PC1 × indice_cultural: r = {r_pc1_indice:+.3f}")
    except FileNotFoundError:
        print("  indice_institucional_por_zona.csv não encontrado")
        r_pc1_indice = np.nan
        merged = None

    # R² de PC1 contra escore
    print(f"\n{'='*65}")
    print("REGRESSÃO: ESCORE ~ PC1")
    print(f"{'='*65}")
    try:
        socio = pd.read_csv(CSV_SOCIO, index_col="NR_ZONA")
        pc1_df = pd.DataFrame({"PC1": resultado["pc1"]}, index=zonas)
        reg_df = pc1_df.join(socio[["escore_ver_2024", "escore_pref_2024"]]).dropna()

        X = np.column_stack([np.ones(len(reg_df)), reg_df["PC1"].values])
        for dep in ["escore_ver_2024", "escore_pref_2024"]:
            y = reg_df[dep].values
            beta, *_ = np.linalg.lstsq(X, y, rcond=None)
            y_hat = X @ beta
            r2 = 1 - ((y - y_hat) ** 2).sum() / ((y - y.mean()) ** 2).sum()
            print(f"\n  {dep} ~ PC1:")
            print(f"    R² = {r2:.3f}")
    except FileNotFoundError:
        print("  socioeconomia_por_zona.csv não encontrado")

    # Comparação direta
    print(f"\n{'='*65}")
    print("COMPARAÇÃO")
    print(f"{'='*65}")
    if merged is not None:
        # R² do índice manual (já conhecido)
        cols_add = [c for c in ["escore_ver_2024"] if c not in merged.columns]
        reg_manual = merged.join(socio[cols_add]) if cols_add else merged.copy()
        reg_manual = reg_manual.dropna(subset=["indice_cultural", "escore_ver_2024"])
        X_m = np.column_stack([np.ones(len(reg_manual)), reg_manual["indice_cultural"].values])
        y_m = reg_manual["escore_ver_2024"].values
        beta_m, *_ = np.linalg.lstsq(X_m, y_m, rcond=None)
        r2_manual = 1 - ((y_m - X_m @ beta_m) ** 2).sum() / ((y_m - y_m.mean()) ** 2).sum()

        X_p = np.column_stack([np.ones(len(reg_df)), reg_df["PC1"].values])
        y_p = reg_df["escore_ver_2024"].values
        beta_p, *_ = np.linalg.lstsq(X_p, y_p, rcond=None)
        r2_pc1 = 1 - ((y_p - X_p @ beta_p) ** 2).sum() / ((y_p - y_p.mean()) ** 2).sum()

        print(f"  Índice manual × vereador 2024:  R² = {r2_manual:.3f}")
        print(f"  PC1 × vereador 2024:            R² = {r2_pc1:.3f}")
        print(f"  PC1 × índice manual:            r  = {r_pc1_indice:+.3f}")

    # Salvar CSV
    SAIDA_CSV.parent.mkdir(parents=True, exist_ok=True)
    out_df = pd.DataFrame({
        "NR_ZONA": zonas,
        "PC1": resultado["pc1"],
    }).set_index("NR_ZONA")
    if merged is not None:
        out_df = out_df.join(idx_orig[["indice_cultural", "nome_ze"]])
    out_df.to_csv(SAIDA_CSV)
    print(f"\nCSV salvo: {SAIDA_CSV}")

    # Scatter PC1 vs índice manual
    if merged is not None and not np.isnan(r_pc1_indice):
        fig, ax = plt.subplots(figsize=(8, 6), dpi=120)
        ax.scatter(merged["indice_cultural"], merged["PC1"],
                   s=40, alpha=0.7, edgecolor="black", linewidth=0.3)
        ax.set_xlabel("Índice institucional manual (%)", fontsize=11)
        ax.set_ylabel("PC1 (agnóstico)", fontsize=11)
        ax.set_title(
            f"PC1 agnóstico vs índice manual\n"
            f"r = {r_pc1_indice:+.3f}  "
            f"(var. explicada PC1 = {resultado['variancia_explicada'][0]:.1%})",
            fontsize=12,
        )
        ax.grid(alpha=0.3)

        # Anotar zonas extremas
        for zona in [5, 251, 346, 1, 2, 6, 258]:
            if zona in merged.index:
                row = merged.loc[zona]
                nome = row.get("nome_ze", f"Z{zona}")
                ax.annotate(
                    f"Z{zona}",
                    xy=(row["indice_cultural"], row["PC1"]),
                    fontsize=7, ha="center", va="bottom",
                    bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                              edgecolor="gray", alpha=0.8),
                )

        fig.tight_layout()
        SAIDA_FIG.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(SAIDA_FIG, dpi=300, bbox_inches="tight")
        plt.show()
        print(f"Figura salva: {SAIDA_FIG}")
