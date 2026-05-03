"""Controle por renda + alfabetização no efeito do índice institucional.

Atualiza controle_renda_escolaridade.py adicionando taxa de alfabetização
(15+ anos) do Censo 2022 como covariável de "escolaridade".

Observação importante: % com superior completo não está disponível
nos agregados por setor do Censo 2022 (dados de amostra ainda não
foram agregados por setor). Alfabetização é proxy fraco em SP capital
(varia tipicamente entre 96-99%) mas é o melhor indicador de
escolaridade disponível por setor.

Pipeline:
1. Soma alfabetizadas 15+ por setor (V00644..V00656).
2. Divide por moradores (V06002 do arquivo de renda).
3. Spatial join setor → zona (via shapefile CEM).
4. Agrega por zona (média ponderada pela população).
5. Roda 6 modelos OLS comparando.
"""

from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import math

import matplotlib.pyplot as plt
import mysql.connector
import numpy as np
import pandas as pd
import geopandas as gpd
import geobr

from src.ingestao.carregar_mysql import MYSQL_CONFIG, DATABASE

CSV_INDICE = _ROOT / "outputs/indice_institucional_por_zona.csv"
CSV_SOCIO_2010 = _ROOT / "outputs/socioeconomia_por_zona.csv"
CSV_SOCIO_2022 = _ROOT / "outputs/socioeconomia_por_zona_2022.csv"
CSV_ALFAB = _ROOT / "data/raw/censo2022/extraido_alfabetizacao" \
                   "/Agregados_por_setores_alfabetizacao_BR.csv"
CSV_RENDA = _ROOT / "data/raw/censo2022/extraido_renda" \
                   "/Agregados_por_setores_renda_responsavel_BR.csv"
SHAPEFILE_LV = _ROOT / "data/raw/shapes/EL2022_LV_ESP_CEM_V2/EL2022_LV_ESP_CEM_V2.shp"
SAIDA_ALFAB = _ROOT / "outputs/alfabetizacao_por_zona_2022.csv"
SAIDA_CSV = _ROOT / "outputs/tables/controle_renda_escolaridade_v2.csv"
SAIDA_FIG = _ROOT / "outputs/figures/controle_renda_escolaridade_v2.png"

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


def calcular_alfabetizacao_por_zona() -> pd.DataFrame:
    """Calcula taxa de alfabetização 15+ por zona eleitoral em SP capital."""
    print("Carregando alfabetização por setor...")
    cols_alf = ["CD_setor"] + [f"V00{i}" for i in range(644, 657)]
    alf = pd.read_csv(CSV_ALFAB, sep=";", encoding="latin-1",
                      usecols=cols_alf, dtype={"CD_setor": str})
    alf = alf[alf["CD_setor"].str.startswith("355030")]
    # Substituir 'X' (sigilo) por NaN e converter
    for c in cols_alf[1:]:
        alf[c] = pd.to_numeric(alf[c].astype(str).str.replace(",", "."),
                                errors="coerce")
    alf["alf_15mais"] = alf[cols_alf[1:]].sum(axis=1)
    alf = alf[["CD_setor", "alf_15mais"]].rename(columns={"CD_setor": "CD_SETOR"})

    print("Carregando moradores (denominador) do arquivo de renda...")
    pop = pd.read_csv(CSV_RENDA, sep=";", encoding="latin-1",
                      usecols=["CD_SETOR", "V06002"],
                      dtype={"CD_SETOR": str})
    pop = pop[pop["CD_SETOR"].str.startswith("355030")]
    pop["moradores"] = pd.to_numeric(pop["V06002"].astype(str).str.replace(",", "."),
                                      errors="coerce")
    pop = pop[["CD_SETOR", "moradores"]]

    setores_dados = alf.merge(pop, on="CD_SETOR")
    setores_dados["taxa_alfab_15mais"] = (
        setores_dados["alf_15mais"] / setores_dados["moradores"]
    ).clip(0, 1)
    print(f"  Setores em SP capital com alfab + pop: {len(setores_dados)}")
    print(f"  Taxa alfab 15+/moradores — distrib SP setor:")
    print(f"    min={setores_dados['taxa_alfab_15mais'].min():.3f} "
          f"mediana={setores_dados['taxa_alfab_15mais'].median():.3f} "
          f"max={setores_dados['taxa_alfab_15mais'].max():.3f}")

    # Geometria dos setores 2022 (cache local — evita download repetido)
    cache_setores = _ROOT / "data/raw/shapes/setores_2022_sp.gpkg"
    if cache_setores.exists():
        print(f"Lendo setores 2022 do cache: {cache_setores.name}")
        setores_geo = gpd.read_file(cache_setores)
    else:
        print("Baixando setores 2022 (geobr) e salvando cache...")
        setores_geo = geobr.read_census_tract(code_tract=3550308, year=2022)
        cache_setores.parent.mkdir(parents=True, exist_ok=True)
        setores_geo.to_file(cache_setores, driver="GPKG")
    setores_geo["CD_SETOR"] = setores_geo["code_tract"].astype(np.int64).astype(str)
    setores_geo = setores_geo[["CD_SETOR", "geometry"]].merge(
        setores_dados, on="CD_SETOR", how="inner"
    )
    print(f"  Setores com geometria + dados: {len(setores_geo)}")

    # Locais de votação por zona (centróides)
    print("Carregando locais de votação...")
    lv = gpd.read_file(SHAPEFILE_LV)
    sp_lv = lv[lv["MUN_NOME"] == "SAO PAULO"].copy()
    sp_lv["NR_ZONA"] = sp_lv["ZE_NUM"].astype(int)
    sp_lv = sp_lv[["NR_ZONA", "NOME_LV", "geometry"]]

    # Spatial join: cada local pega o setor onde está
    setores_geo = setores_geo.to_crs("EPSG:4326")
    sp_lv = sp_lv.to_crs("EPSG:4326")
    locais = gpd.sjoin(sp_lv, setores_geo, how="left", predicate="within")
    n_match = locais["CD_SETOR"].notna().sum()
    print(f"  Locais com setor encontrado: {n_match}/{len(locais)}")

    # Agrega por zona — média ponderada pela população
    locais = locais.dropna(subset=["CD_SETOR", "taxa_alfab_15mais"])
    grouped = locais.groupby("NR_ZONA").apply(
        lambda g: pd.Series({
            "taxa_alfab": (g["taxa_alfab_15mais"] * g["moradores"]).sum() / g["moradores"].sum()
                          if g["moradores"].sum() > 0 else np.nan,
            "n_locais_join": len(g),
        }),
        include_groups=False,
    ).reset_index()
    print(f"  Zonas com taxa_alfab calculada: {len(grouped)}")

    grouped.to_csv(SAIDA_ALFAB, index=False)
    return grouped[["NR_ZONA", "taxa_alfab"]].rename(columns={"NR_ZONA": "nr_zona"})


def carregar_base() -> pd.DataFrame:
    """Une variação esquerda + renda 2010/2022 + índice + alfabetização."""
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

    alf = calcular_alfabetizacao_por_zona()

    df = df.merge(idx, on="nr_zona", how="left") \
           .merge(s10, on="nr_zona", how="left") \
           .merge(s22, on="nr_zona", how="left") \
           .merge(alf, on="nr_zona", how="left")
    return df.dropna(subset=["variacao_pct", "indice_cultural",
                              "renda_2010", "renda_2022", "taxa_alfab"])


def ols(X: np.ndarray, y: np.ndarray) -> dict:
    n, p = X.shape
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    y_hat = X @ beta
    rss = float(((y - y_hat) ** 2).sum())
    tss = float(((y - y.mean()) ** 2).sum())
    r2 = 1 - rss / tss if tss > 0 else 0.0
    df_res = n - p
    df_reg = p - 1
    r2_adj = 1 - (1 - r2) * (n - 1) / df_res if df_res > 0 else r2
    F = ((tss - rss) / df_reg) / (rss / df_res) if df_res > 0 and rss > 0 else np.nan
    return {"beta": beta, "r2": r2, "r2_adj": r2_adj, "F": F}


def main() -> None:
    print("=" * 75)
    print("CONTROLE POR RENDA + ALFABETIZAÇÃO NO EFEITO DO ÍNDICE")
    print("=" * 75)

    df = carregar_base()
    print(f"\nN zonas com todos os dados: {len(df)}")
    print(f"Distribuição taxa_alfab por zona: "
          f"min={df['taxa_alfab'].min():.3f} "
          f"mediana={df['taxa_alfab'].median():.3f} "
          f"max={df['taxa_alfab'].max():.3f}")

    y = df["variacao_pct"].values

    modelos = [
        ("M1: só índice",
         ["indice_cultural"]),
        ("M2: só renda 2010",
         ["renda_2010"]),
        ("M3: só renda 2022",
         ["renda_2022"]),
        ("M4: só alfabetização",
         ["taxa_alfab"]),
        ("M5: renda 2010 + 2022",
         ["renda_2010", "renda_2022"]),
        ("M6: renda + alfab (sem índice)",
         ["renda_2010", "renda_2022", "taxa_alfab"]),
        ("M7: renda + alfab + índice (completo)",
         ["renda_2010", "renda_2022", "taxa_alfab", "indice_cultural"]),
    ]

    resultados = []
    print(f"\n{'Modelo':<40} {'R²':>8} {'R²-adj':>8} {'F':>8}")
    print("-" * 75)
    for nome, cols in modelos:
        X = np.column_stack([np.ones(len(df))] + [df[c].values for c in cols])
        res = ols(X, y)
        print(f"{nome:<40} {res['r2']:>8.3f} {res['r2_adj']:>8.3f} {res['F']:>8.2f}")
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
    cols_m7 = ["renda_2010", "renda_2022", "taxa_alfab", "indice_cultural"]
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
    r2_renda_alf = resultados[5]["r2"]
    r2_completo = resultados[6]["r2"]
    print(f"  Só índice:                       {r2_idx:.3f}")
    print(f"  Renda (2010+2022):               {r2_renda_2:.3f}")
    print(f"  Renda + alfabetização:           {r2_renda_alf:.3f}")
    print(f"  Completo (renda+alfab+índice):   {r2_completo:.3f}")
    print(f"  Ganho marginal alfab sobre renda: {r2_renda_alf - r2_renda_2:+.3f}")
    print(f"  Ganho marginal índice sobre tudo: {r2_completo - r2_renda_alf:+.3f}")

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
        "Controle por renda + alfabetização no efeito do índice\n"
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
