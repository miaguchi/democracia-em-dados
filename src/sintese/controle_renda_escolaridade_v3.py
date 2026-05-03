"""Controle por renda + escolaridade SUPERIOR (Censo 2010 amostra) no
efeito do índice institucional.

Substitui alfabetização (proxy fraco) por % de pessoas 10+ com
SUPERIOR COMPLETO, derivado da Tabela 3.5.4 do Censo 2010 amostra
por área de ponderação (310 áreas em SP capital).

Pipeline:
1. Tabela 3.5.4 do Censo 2010 → % superior por área de ponderação.
2. Shapefile geobr das áreas de ponderação 2010.
3. Spatial join: zonas eleitorais (via locais de votação) → área.
4. Agrega % superior por zona (média ponderada por população).
5. Roda regressões OLS comparando.

Justificativa: 2010 vs 2022. Padrão socioespacial de escolaridade
em SP é altamente estável — Pinheiros/Perdizes eram zonas elite
em 2010 e continuam em 2022. O que importa para a regressão é a
ordenação relativa entre zonas, não níveis absolutos.
"""

from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import math
import warnings

import matplotlib.pyplot as plt
import mysql.connector
import numpy as np
import pandas as pd
import geopandas as gpd

from src.ingestao.carregar_mysql import MYSQL_CONFIG, DATABASE

warnings.filterwarnings("ignore")

CSV_INDICE = _ROOT / "outputs/indice_institucional_por_zona.csv"
CSV_SOCIO_2010 = _ROOT / "outputs/socioeconomia_por_zona.csv"
CSV_SOCIO_2022 = _ROOT / "outputs/socioeconomia_por_zona_2022.csv"
TABELA_INSTRUCAO = Path("/tmp/XLS/Tabela 3.5.4.xls")
SHP_AREAS = _ROOT / "data/raw/shapes/areas_ponderacao_sp_2010.gpkg"
SHP_LV = _ROOT / "data/raw/shapes/EL2022_LV_ESP_CEM_V2/EL2022_LV_ESP_CEM_V2.shp"
SAIDA_SUPERIOR = _ROOT / "outputs/superior_por_zona_2010.csv"
SAIDA_CSV = _ROOT / "outputs/tables/controle_renda_escolaridade_v3.csv"
SAIDA_FIG = _ROOT / "outputs/figures/controle_renda_escolaridade_v3.png"

CD_MUNICIPIO_SP = 71072
PARTIDOS_ESQUERDA = (13, 50, 65, 12, 40, 43, 18, 16, 29, 80)


def fetch(sql: str) -> pd.DataFrame:
    conn = mysql.connector.connect(database=DATABASE, **MYSQL_CONFIG)
    cur = conn.cursor()
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return pd.DataFrame(rows, columns=cols)


def calcular_superior_por_zona() -> pd.DataFrame:
    """% pessoas 10+ com superior completo por zona eleitoral (SP cap)."""
    print("Carregando Tabela 3.5.4 do Censo 2010...")
    df = pd.read_excel(TABELA_INSTRUCAO, header=None, skiprows=6)
    df.columns = ["nome", "total", "sem_instr", "fund_compl",
                  "medio_compl", "superior", "nao_det", "codigo"]
    df["codigo_str"] = df["codigo"].astype(str)
    sp = df[df["codigo_str"].str.startswith("35503080") &
            (df["codigo_str"].str.len() > 8)].copy()
    sp["code_weighting"] = sp["codigo_str"].str.replace(".0", "", regex=False).astype(np.int64)
    sp["pct_superior"] = sp["superior"] / sp["total"] * 100
    sp["pct_medio_ou_mais"] = (sp["superior"] + sp["medio_compl"]) / sp["total"] * 100
    sp = sp[["code_weighting", "total", "superior", "pct_superior",
             "pct_medio_ou_mais"]].rename(columns={"total": "pop_10mais"})
    print(f"  Áreas de ponderação SP capital: {len(sp)}")
    print(f"  pct_superior: min={sp['pct_superior'].min():.1f} "
          f"mediana={sp['pct_superior'].median():.1f} "
          f"max={sp['pct_superior'].max():.1f}")

    print("Carregando shapefile das áreas de ponderação 2010...")
    areas = gpd.read_file(SHP_AREAS)
    areas["code_weighting"] = areas["code_weighting"].astype(np.int64)
    areas = areas.merge(sp, on="code_weighting", how="inner")
    print(f"  Áreas com geometria + dados: {len(areas)}")

    print("Carregando locais de votação...")
    lv = gpd.read_file(SHP_LV)
    sp_lv = lv[lv["MUN_NOME"] == "SAO PAULO"].copy()
    sp_lv["NR_ZONA"] = sp_lv["ZE_NUM"].astype(int)
    sp_lv = sp_lv[["NR_ZONA", "NOME_LV", "geometry"]]

    # Spatial join: cada local pega a área de ponderação onde está
    areas = areas.to_crs("EPSG:4326")
    sp_lv = sp_lv.to_crs("EPSG:4326")
    print("Spatial join locais × áreas de ponderação...")
    locais = gpd.sjoin(sp_lv, areas, how="left", predicate="within")
    n_match = locais["code_weighting"].notna().sum()
    print(f"  Locais com área encontrada: {n_match}/{len(locais)}")

    # Agrega por zona — média ponderada pela população 10+ da área
    locais = locais.dropna(subset=["code_weighting", "pct_superior"])
    grouped = locais.groupby("NR_ZONA").apply(
        lambda g: pd.Series({
            "pct_superior": (g["pct_superior"] * g["pop_10mais"]).sum() /
                             g["pop_10mais"].sum() if g["pop_10mais"].sum() > 0
                             else np.nan,
            "pct_medio_ou_mais": (g["pct_medio_ou_mais"] * g["pop_10mais"]).sum() /
                                  g["pop_10mais"].sum() if g["pop_10mais"].sum() > 0
                                  else np.nan,
        }), include_groups=False,
    ).reset_index()

    print(f"  Zonas com pct_superior calculado: {len(grouped)}")
    print(f"  Distribuição pct_superior por zona:")
    print(f"    min={grouped['pct_superior'].min():.1f} "
          f"mediana={grouped['pct_superior'].median():.1f} "
          f"max={grouped['pct_superior'].max():.1f}")
    grouped.to_csv(SAIDA_SUPERIOR, index=False)
    return grouped.rename(columns={"NR_ZONA": "nr_zona"})


def carregar_base() -> pd.DataFrame:
    """Une variação esquerda + renda 2010/2022 + índice + pct_superior."""
    sql = f"""
    SELECT v.nr_zona,
        SUM(CASE WHEN e.ano_eleicao=2012 THEN v.qt_votos_nominais ELSE 0 END) AS esq_2012,
        SUM(CASE WHEN e.ano_eleicao=2024 THEN v.qt_votos_nominais ELSE 0 END) AS esq_2024
    FROM votacao_partido_munzona v
    JOIN eleicao e ON v.cd_eleicao=e.cd_eleicao AND v.nr_turno=e.nr_turno
    WHERE v.nr_partido IN {PARTIDOS_ESQUERDA}
      AND v.cd_cargo=13 AND v.cd_municipio={CD_MUNICIPIO_SP}
      AND e.nr_turno=1 AND e.ano_eleicao IN (2012, 2024)
    GROUP BY v.nr_zona HAVING esq_2012 > 0
    """
    df = fetch(sql)
    df["esq_2012"] = pd.to_numeric(df["esq_2012"])
    df["esq_2024"] = pd.to_numeric(df["esq_2024"])
    df["variacao_pct"] = (df["esq_2024"] - df["esq_2012"]) / df["esq_2012"] * 100

    idx = pd.read_csv(CSV_INDICE)[["NR_ZONA", "nome_ze", "indice_cultural"]]
    idx.columns = ["nr_zona", "nome_ze", "indice_cultural"]

    s10 = pd.read_csv(CSV_SOCIO_2010)[["NR_ZONA", "renda_pc_media"]]
    s10.columns = ["nr_zona", "renda_2010"]

    s22 = pd.read_csv(CSV_SOCIO_2022)[["NR_ZONA", "renda_resp_2022"]]
    s22.columns = ["nr_zona", "renda_2022"]

    sup = calcular_superior_por_zona()

    df = df.merge(idx, on="nr_zona", how="left") \
           .merge(s10, on="nr_zona", how="left") \
           .merge(s22, on="nr_zona", how="left") \
           .merge(sup, on="nr_zona", how="left")
    return df.dropna(subset=["variacao_pct", "indice_cultural",
                              "renda_2010", "renda_2022", "pct_superior"])


def ols(X: np.ndarray, y: np.ndarray) -> dict:
    n, p = X.shape
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    y_hat = X @ beta
    rss = float(((y - y_hat) ** 2).sum())
    tss = float(((y - y.mean()) ** 2).sum())
    r2 = 1 - rss / tss if tss > 0 else 0.0
    df_res = n - p
    r2_adj = 1 - (1 - r2) * (n - 1) / df_res if df_res > 0 else r2
    F = ((tss - rss) / (p - 1)) / (rss / df_res) if df_res > 0 and rss > 0 else np.nan
    return {"beta": beta, "r2": r2, "r2_adj": r2_adj, "F": F}


def main() -> None:
    print("=" * 75)
    print("CONTROLE POR RENDA + SUPERIOR COMPLETO (Censo 2010 amostra)")
    print("=" * 75)

    df = carregar_base()
    print(f"\nN zonas com todos os dados: {len(df)}")

    y = df["variacao_pct"].values

    modelos = [
        ("M1: só índice",
         ["indice_cultural"]),
        ("M2: só renda 2010",
         ["renda_2010"]),
        ("M3: só renda 2022",
         ["renda_2022"]),
        ("M4: só pct_superior",
         ["pct_superior"]),
        ("M5: renda 2010 + 2022",
         ["renda_2010", "renda_2022"]),
        ("M6: renda + superior (sem índice)",
         ["renda_2010", "renda_2022", "pct_superior"]),
        ("M7: renda + superior + índice (completo)",
         ["renda_2010", "renda_2022", "pct_superior", "indice_cultural"]),
    ]

    resultados = []
    print(f"\n{'Modelo':<45} {'R²':>8} {'R²-adj':>8} {'F':>8}")
    print("-" * 75)
    for nome, cols in modelos:
        X = np.column_stack([np.ones(len(df))] + [df[c].values for c in cols])
        res = ols(X, y)
        print(f"{nome:<45} {res['r2']:>8.3f} {res['r2_adj']:>8.3f} {res['F']:>8.2f}")
        resultados.append({
            "modelo": nome, "r2": res["r2"], "r2_adj": res["r2_adj"],
            "F": res["F"], "n_params": len(cols) + 1,
            "betas": res["beta"].tolist(),
            "vars": ["intercepto"] + cols,
        })

    df_out = pd.DataFrame(resultados)
    SAIDA_CSV.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(SAIDA_CSV, index=False)
    print(f"\nCSV salvo: {SAIDA_CSV}")

    # Coeficientes padronizados M7
    print("\n--- Coeficientes padronizados (M7 completo) ---")
    cols_m7 = ["renda_2010", "renda_2022", "pct_superior", "indice_cultural"]
    df_z = df.copy()
    for c in cols_m7:
        df_z[c + "_z"] = (df[c] - df[c].mean()) / df[c].std()
    Xz = np.column_stack([np.ones(len(df_z))] + [df_z[c + "_z"].values for c in cols_m7])
    res_z = ols(Xz, y)
    for nome_var, b in zip(["intercepto"] + cols_m7, res_z["beta"]):
        print(f"  {nome_var:<25} = {b:+.3f}")

    # Comparações
    print("\n--- Comparações ---")
    r2_idx = resultados[0]["r2"]
    r2_renda_2 = resultados[4]["r2"]
    r2_renda_sup = resultados[5]["r2"]
    r2_completo = resultados[6]["r2"]
    print(f"  Só índice:                       {r2_idx:.3f}")
    print(f"  Renda (2010+2022):               {r2_renda_2:.3f}")
    print(f"  Renda + superior:                {r2_renda_sup:.3f}")
    print(f"  Completo (renda+sup+índice):     {r2_completo:.3f}")
    print(f"  Ganho marginal superior s/renda: {r2_renda_sup - r2_renda_2:+.3f}")
    print(f"  Ganho marginal índice s/tudo:    {r2_completo - r2_renda_sup:+.3f}")

    # Plot
    fig, ax = plt.subplots(figsize=(11, 6), dpi=120)
    nomes = [r["modelo"].split(":", 1)[0] for r in resultados]
    r2s = [r["r2"] for r in resultados]
    r2_adjs = [r["r2_adj"] for r in resultados]
    cores = ["#1f77b4", "#ff7f0e", "#ff7f0e", "#9467bd",
             "#ff7f0e", "#8c564b", "#2ca02c"]
    x = np.arange(len(nomes))
    w = 0.4
    bars1 = ax.bar(x - w/2, r2s, w, label="R²", color=cores, alpha=0.85,
                    edgecolor="black", linewidth=0.4)
    ax.bar(x + w/2, r2_adjs, w, label="R² ajustado",
           color=cores, alpha=0.5, edgecolor="black", linewidth=0.4)
    for bar, val in zip(bars1, r2s):
        ax.annotate(f"{val:.3f}", xy=(bar.get_x() + bar.get_width()/2, val),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", fontsize=9, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels([r["modelo"] for r in resultados],
                        rotation=15, ha="right", fontsize=8)
    ax.set_ylabel("R²", fontsize=11)
    ax.set_title(
        "Controle por renda + % superior completo (Censo 2010)\n"
        f"Variação % esquerda vereador (2012→2024) — N={len(df)}",
        fontsize=12, fontweight="bold",
    )
    ax.set_ylim(0, max(r2s) * 1.15)
    ax.grid(axis="y", alpha=0.3)
    ax.legend(loc="upper left", fontsize=10)
    fig.tight_layout()
    fig.savefig(SAIDA_FIG, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Figura salva: {SAIDA_FIG}")


if __name__ == "__main__":
    main()
