"""TESTE A — Regressão: crescimento da esquerda 2012→2024 × índice institucional.

Para cada zona eleitoral de SP capital:
- Variável dependente: variação percentual dos votos para vereador da
  esquerda completa (Bolognesi) entre 2012 e 2024.
- Variável independente: índice institucional cultural-progressista
  (Cap. III, fração de locais educacionais cultural-progressistas).

Hipótese: zonas com maior densidade institucional cultural-progressista
sofreram menor queda (ou maior crescimento) da esquerda.
"""

from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import matplotlib.pyplot as plt
import mysql.connector
import numpy as np
import pandas as pd
from scipy import stats

from src.ingestao.carregar_mysql import MYSQL_CONFIG, DATABASE

CSV_INDICE = _ROOT / "outputs/indice_institucional_por_zona.csv"
SAIDA_FIG = _ROOT / "outputs/figures/regressao_crescimento_indice.png"
SAIDA_CSV = _ROOT / "outputs/tables/regressao_crescimento_indice.csv"

CD_MUNICIPIO_SP = 71072
PARTIDOS_ESQUERDA = (13, 50, 65, 12, 40, 43, 18, 16, 29, 80)


def carregar_variacao_esquerda() -> pd.DataFrame:
    """Variação % dos votos da esquerda 2012→2024 por zona, SP capital."""
    conn = mysql.connector.connect(database=DATABASE, **MYSQL_CONFIG)

    sql = f"""
    SELECT
        v.nr_zona,
        SUM(CASE WHEN e.ano_eleicao = 2012 THEN v.qt_votos_nominais ELSE 0 END) AS esq_2012,
        SUM(CASE WHEN e.ano_eleicao = 2024 THEN v.qt_votos_nominais ELSE 0 END) AS esq_2024
    FROM votacao_partido_munzona v
    JOIN eleicao e ON v.cd_eleicao = e.cd_eleicao AND v.nr_turno = e.nr_turno
    WHERE v.nr_partido IN {PARTIDOS_ESQUERDA}
      AND v.cd_cargo = 13
      AND v.cd_municipio = {CD_MUNICIPIO_SP}
      AND e.nr_turno = 1
      AND e.ano_eleicao IN (2012, 2024)
    GROUP BY v.nr_zona
    HAVING esq_2012 > 0
    """
    df = pd.read_sql(sql, conn)
    conn.close()

    df["variacao_pct"] = (df["esq_2024"] - df["esq_2012"]) / df["esq_2012"] * 100
    return df


def main() -> None:
    print("=" * 65)
    print("TESTE A — Regressão crescimento × índice institucional")
    print("=" * 65)

    # Variação por zona
    df_var = carregar_variacao_esquerda()
    print(f"\nZonas com dados (vereador 2012 e 2024 em SP): {len(df_var)}")

    # Índice institucional
    idx = pd.read_csv(CSV_INDICE)[["NR_ZONA", "nome_ze", "indice_cultural"]]
    idx.columns = ["nr_zona", "nome_ze", "indice_cultural"]

    # Merge
    df = df_var.merge(idx, on="nr_zona", how="inner")
    df = df.dropna(subset=["variacao_pct", "indice_cultural"])
    print(f"Zonas com índice institucional: {len(df)}")

    # Regressão OLS
    x = df["indice_cultural"].values
    y = df["variacao_pct"].values
    res = stats.linregress(x, y)

    print(f"\n--- Regressão: variação % ~ índice institucional ---")
    print(f"  N                 = {len(df)}")
    print(f"  Coeficiente (β)   = {res.slope:+.3f}  (variação % por ponto do índice)")
    print(f"  Intercepto        = {res.intercept:+.3f}")
    print(f"  R                 = {res.rvalue:+.3f}")
    print(f"  R²                = {res.rvalue**2:.3f}")
    print(f"  p-valor           = {res.pvalue:.4g}")
    print(f"  Erro-padrão (β)   = {res.stderr:.3f}")

    # Significância
    if res.pvalue < 0.001:
        sig = "*** (p < 0.001)"
    elif res.pvalue < 0.01:
        sig = "** (p < 0.01)"
    elif res.pvalue < 0.05:
        sig = "* (p < 0.05)"
    else:
        sig = "n.s."
    print(f"  Significância     = {sig}")

    # Salvar tabela
    SAIDA_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.sort_values("variacao_pct", ascending=False).to_csv(SAIDA_CSV, index=False)
    print(f"\nCSV salvo: {SAIDA_CSV}")

    # Plot
    fig, ax = plt.subplots(figsize=(9, 7), dpi=120)
    ax.scatter(x, y, s=60, alpha=0.7, edgecolor="black", linewidth=0.4,
               color="#1f77b4")

    # Linha de regressão
    x_line = np.linspace(x.min(), x.max(), 100)
    y_line = res.slope * x_line + res.intercept
    ax.plot(x_line, y_line, color="#d62728", linewidth=2,
            label=f"β = {res.slope:+.2f}, R² = {res.rvalue**2:.3f}")

    # Linha y = 0 (sem mudança)
    ax.axhline(0, color="gray", linewidth=0.8, linestyle="--", alpha=0.6)

    # Anotar zonas-alvo (corredor universitário) e extremos
    zonas_destaque = {1: "Bela Vista", 2: "Perdizes", 5: "Jd Paulista",
                      6: "V. Mariana", 251: "Pinheiros", 258: "Indianópolis",
                      346: "Butantã", 3: "Sta Ifigênia"}
    for zona, nome in zonas_destaque.items():
        row = df[df["nr_zona"] == zona]
        if row.empty:
            continue
        ax.annotate(
            f"Z{zona}\n{nome}",
            xy=(row["indice_cultural"].iloc[0], row["variacao_pct"].iloc[0]),
            fontsize=7, ha="center", va="bottom",
            xytext=(0, 6), textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                      edgecolor="gray", alpha=0.9),
        )

    ax.set_xlabel("Índice institucional cultural-progressista (%)", fontsize=11)
    ax.set_ylabel("Variação % esquerda vereador (2012→2024)", fontsize=11)
    ax.set_title(
        f"Crescimento da esquerda × índice institucional — SP capital\n"
        f"R² = {res.rvalue**2:.3f}   p = {res.pvalue:.3g}   N = {len(df)}",
        fontsize=12, fontweight="bold",
    )
    ax.legend(loc="best", fontsize=10)
    ax.grid(alpha=0.3)

    fig.tight_layout()
    SAIDA_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(SAIDA_FIG, dpi=300, bbox_inches="tight")
    plt.show()
    print(f"Figura salva: {SAIDA_FIG}")


if __name__ == "__main__":
    main()
