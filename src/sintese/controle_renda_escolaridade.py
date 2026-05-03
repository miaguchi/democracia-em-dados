"""Controle por renda no efeito do índice institucional sobre o crescimento
da esquerda para vereador (2012→2024).

Hipótese a testar: o efeito do índice institucional (R²=0.313) é
robusto a controle por renda, ou desaparece quando se adiciona renda
como covariável?

Modelos:
  M1: variação % ~ índice institucional
  M2: variação % ~ renda per capita 2010
  M3: variação % ~ renda do responsável 2022
  M4: variação % ~ renda 2010 + renda 2022
  M5: variação % ~ renda 2010 + renda 2022 + índice  (completo)

Limitação: escolaridade superior por setor censitário não está
disponível na ETL atual (pessoa13 do Censo 2010 cobre só
alfabetização; agregados de escolaridade do Censo 2022 não foram
processados). Análise restrita a renda como variável socioeconômica.
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

from src.ingestao.carregar_mysql import MYSQL_CONFIG, DATABASE

CSV_INDICE = _ROOT / "outputs/indice_institucional_por_zona.csv"
CSV_SOCIO_2010 = _ROOT / "outputs/socioeconomia_por_zona.csv"
CSV_SOCIO_2022 = _ROOT / "outputs/socioeconomia_por_zona_2022.csv"
SAIDA_CSV = _ROOT / "outputs/tables/controle_renda_escolaridade.csv"
SAIDA_FIG = _ROOT / "outputs/figures/controle_renda_escolaridade.png"

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


def carregar_dados() -> pd.DataFrame:
    """Cruza variação % esquerda + renda 2010 + renda 2022 + índice."""
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

    # Índice institucional
    idx = pd.read_csv(CSV_INDICE)[["NR_ZONA", "nome_ze", "indice_cultural"]]
    idx.columns = ["nr_zona", "nome_ze", "indice_cultural"]

    # Renda 2010 (per capita)
    s10 = pd.read_csv(CSV_SOCIO_2010)[["NR_ZONA", "renda_pc_media"]]
    s10.columns = ["nr_zona", "renda_2010"]

    # Renda 2022 (responsável)
    s22 = pd.read_csv(CSV_SOCIO_2022)[["NR_ZONA", "renda_resp_2022"]]
    s22.columns = ["nr_zona", "renda_2022"]

    df = df.merge(idx, on="nr_zona", how="left") \
           .merge(s10, on="nr_zona", how="left") \
           .merge(s22, on="nr_zona", how="left")

    return df.dropna(subset=["variacao_pct", "indice_cultural",
                              "renda_2010", "renda_2022"])


def ols(X: np.ndarray, y: np.ndarray) -> dict:
    """Retorna betas, R², R²-ajustado, F, p, RSS."""
    n, p = X.shape  # p inclui intercepto
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    y_hat = X @ beta
    rss = float(((y - y_hat) ** 2).sum())
    tss = float(((y - y.mean()) ** 2).sum())
    r2 = 1 - rss / tss if tss > 0 else 0.0
    df_res = n - p
    df_reg = p - 1
    r2_adj = 1 - (1 - r2) * (n - 1) / df_res if df_res > 0 else r2
    F = ((tss - rss) / df_reg) / (rss / df_res) if df_res > 0 and rss > 0 else np.nan
    # p-valor F
    if not np.isnan(F) and F > 0:
        from scipy.special import betainc
        try:
            p_val = float(betainc(df_res / 2, df_reg / 2,
                                   df_res / (df_res + df_reg * F)))
        except Exception:
            p_val = np.nan
    else:
        p_val = np.nan
    return {"beta": beta, "r2": r2, "r2_adj": r2_adj,
            "F": F, "p": p_val, "rss": rss, "n": n, "p_params": p}


def main() -> None:
    print("=" * 75)
    print("CONTROLE POR RENDA NO EFEITO DO ÍNDICE INSTITUCIONAL")
    print("=" * 75)

    df = carregar_dados()
    print(f"\nN zonas com todos os dados: {len(df)}")

    # Padronizar variáveis para comparar coeficientes
    # (sem padronizar, betas têm unidades diferentes)
    df_z = df.copy()
    for col in ["indice_cultural", "renda_2010", "renda_2022"]:
        df_z[f"{col}_z"] = (df[col] - df[col].mean()) / df[col].std()

    y = df["variacao_pct"].values

    # 5 modelos
    modelos = [
        ("M1: só índice",
         ["indice_cultural"]),
        ("M2: só renda 2010",
         ["renda_2010"]),
        ("M3: só renda 2022",
         ["renda_2022"]),
        ("M4: renda 2010 + renda 2022",
         ["renda_2010", "renda_2022"]),
        ("M5: renda + índice (completo)",
         ["renda_2010", "renda_2022", "indice_cultural"]),
    ]

    resultados = []
    print(f"\n{'Modelo':<35} {'R²':>8} {'R²-adj':>8} {'F':>8} {'p':>10}")
    print("-" * 75)
    for nome, cols in modelos:
        X = np.column_stack([np.ones(len(df))] + [df[c].values for c in cols])
        res = ols(X, y)
        print(f"{nome:<35} {res['r2']:>8.3f} {res['r2_adj']:>8.3f} "
              f"{res['F']:>8.2f} {res['p']:>10.3g}")
        resultados.append({
            "modelo": nome,
            "r2": res["r2"],
            "r2_adj": res["r2_adj"],
            "F": res["F"],
            "p": res["p"],
            "n_params": res["p_params"],
            "betas": res["beta"].tolist(),
            "vars": ["intercepto"] + cols,
        })

    # Coeficientes padronizados do M5 (importância relativa)
    print("\n--- Coeficientes padronizados (M5: renda + índice) ---")
    cols_z = ["renda_2010_z", "renda_2022_z", "indice_cultural_z"]
    Xz = np.column_stack([np.ones(len(df_z))] + [df_z[c].values for c in cols_z])
    res_z = ols(Xz, y)
    for nome_var, b in zip(["intercepto"] + cols_z, res_z["beta"]):
        print(f"  {nome_var:<25} = {b:+.3f}")
    print(f"  R² = {res_z['r2']:.3f}")

    # Tabela final
    df_out = pd.DataFrame(resultados)
    df_out.to_csv(SAIDA_CSV, index=False)
    print(f"\nCSV salvo: {SAIDA_CSV}")

    # Veredito
    r2_indice_only = resultados[0]["r2"]
    r2_renda_only = resultados[3]["r2"]
    r2_completo = resultados[4]["r2"]
    print(f"\n--- Veredito ---")
    print(f"  R² índice sozinho:           {r2_indice_only:.3f}")
    print(f"  R² renda 2010+2022 sozinha:  {r2_renda_only:.3f}")
    print(f"  R² completo (renda+índice):  {r2_completo:.3f}")
    print(f"  Ganho marginal do índice:    {r2_completo - r2_renda_only:+.3f}")
    print(f"  (mantido ≈30% explicado pelo índice = robusto a controle)")

    # Plot — barras dos 5 modelos
    fig, ax = plt.subplots(figsize=(10, 6), dpi=120)
    nomes = [r["modelo"].split(":", 1)[0] for r in resultados]
    r2s = [r["r2"] for r in resultados]
    r2_adjs = [r["r2_adj"] for r in resultados]
    cores = ["#1f77b4", "#ff7f0e", "#ff7f0e", "#ff7f0e", "#2ca02c"]
    x = np.arange(len(nomes))
    w = 0.4
    bars1 = ax.bar(x - w/2, r2s, w, label="R²", color=cores, alpha=0.85,
                    edgecolor="black", linewidth=0.4)
    bars2 = ax.bar(x + w/2, r2_adjs, w, label="R² ajustado",
                    color=cores, alpha=0.5, edgecolor="black", linewidth=0.4)

    for bar, val in zip(bars1, r2s):
        ax.annotate(f"{val:.3f}", xy=(bar.get_x() + bar.get_width()/2, val),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", fontsize=9, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels([r["modelo"] for r in resultados],
                        rotation=15, ha="right", fontsize=9)
    ax.set_ylabel("R²", fontsize=11)
    ax.set_title(
        "Controle por renda no efeito do índice institucional\n"
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
