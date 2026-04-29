"""TESTE B — Regressão: crescimento da esquerda 2010→2022 × índice institucional.

Replica o Teste A (variação % × índice institucional) mas para
deputado federal em vez de vereador.

Janela: 2010 (pico federal) → 2022 (recuperação após o piso de 2018).

Hipótese a testar: o efeito do índice institucional é específico do
nível municipal (Teste A: R²=0.31, p<0.001) ou aparece também no
nível federal? Se R² for similar, o ambiente institucional prediz
voto progressista em qualquer nível. Se for menor, o efeito é
específico ao "voto local pensado" — coerente com voto diferenciado
por nível (Zolnerkevic & Guarnieri 2023).
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
SAIDA_FIG = _ROOT / "outputs/figures/regressao_crescimento_indice_dep_federal.png"
SAIDA_CSV = _ROOT / "outputs/tables/regressao_crescimento_indice_dep_federal.csv"

CD_MUNICIPIO_SP = 71072
PARTIDOS_ESQUERDA = (13, 50, 65, 12, 40, 43, 18, 16, 29, 80)


def carregar_variacao_esquerda_dep_federal() -> pd.DataFrame:
    """Variação % dos votos da esquerda 2010→2022 por zona, dep. federal SP capital."""
    conn = mysql.connector.connect(database=DATABASE, **MYSQL_CONFIG)

    sql = f"""
    SELECT
        v.nr_zona,
        SUM(CASE WHEN e.ano_eleicao = 2010 THEN v.qt_votos_nominais ELSE 0 END) AS esq_2010,
        SUM(CASE WHEN e.ano_eleicao = 2022 THEN v.qt_votos_nominais ELSE 0 END) AS esq_2022
    FROM votacao_partido_munzona v
    JOIN eleicao e ON v.cd_eleicao = e.cd_eleicao AND v.nr_turno = e.nr_turno
    WHERE v.nr_partido IN {PARTIDOS_ESQUERDA}
      AND v.cd_cargo = 6                       -- Deputado Federal
      AND v.cd_municipio = {CD_MUNICIPIO_SP}   -- SP capital
      AND e.nr_turno = 1
      AND e.ano_eleicao IN (2010, 2022)
    GROUP BY v.nr_zona
    HAVING esq_2010 > 0
    """
    df = pd.read_sql(sql, conn)
    conn.close()

    df["variacao_pct"] = (df["esq_2022"] - df["esq_2010"]) / df["esq_2010"] * 100
    return df


def main() -> None:
    print("=" * 65)
    print("TESTE B — Crescimento dep. federal × índice institucional")
    print("=" * 65)

    df_var = carregar_variacao_esquerda_dep_federal()
    print(f"\nZonas com dados (dep. federal 2010 e 2022 em SP): {len(df_var)}")

    idx = pd.read_csv(CSV_INDICE)[["NR_ZONA", "nome_ze", "indice_cultural"]]
    idx.columns = ["nr_zona", "nome_ze", "indice_cultural"]

    df = df_var.merge(idx, on="nr_zona", how="inner")
    df = df.dropna(subset=["variacao_pct", "indice_cultural"])
    print(f"Zonas com índice institucional: {len(df)}")

    # Regressão
    x = df["indice_cultural"].values
    y = df["variacao_pct"].values
    res = stats.linregress(x, y)

    print(f"\n--- Regressão: variação % dep. federal ~ índice institucional ---")
    print(f"  N                 = {len(df)}")
    print(f"  Coeficiente (β)   = {res.slope:+.3f}  (variação % por ponto do índice)")
    print(f"  Intercepto        = {res.intercept:+.3f}")
    print(f"  R                 = {res.rvalue:+.3f}")
    print(f"  R²                = {res.rvalue**2:.3f}")
    print(f"  p-valor           = {res.pvalue:.4g}")
    print(f"  Erro-padrão (β)   = {res.stderr:.3f}")

    if res.pvalue < 0.001:
        sig = "*** (p < 0.001)"
    elif res.pvalue < 0.01:
        sig = "** (p < 0.01)"
    elif res.pvalue < 0.05:
        sig = "* (p < 0.05)"
    else:
        sig = "n.s."
    print(f"  Significância     = {sig}")

    # Comparação com Teste A
    print(f"\n--- Comparação Teste A (vereador 2012→2024) vs B (dep. fed. 2010→2022) ---")
    try:
        a = pd.read_csv(_ROOT / "outputs/tables/regressao_crescimento_indice.csv")
        # rerun OLS on test A from saved data
        x_a = a["indice_cultural"].values
        y_a = a["variacao_pct"].values
        res_a = stats.linregress(x_a, y_a)
        print(f"  TESTE A (vereador): β={res_a.slope:+.2f}, R²={res_a.rvalue**2:.3f}, p={res_a.pvalue:.2g}")
        print(f"  TESTE B (dep fed):  β={res.slope:+.2f}, R²={res.rvalue**2:.3f}, p={res.pvalue:.2g}")
    except Exception as e:
        print(f"  (não foi possível carregar Teste A: {e})")

    # Salvar CSV
    SAIDA_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.sort_values("variacao_pct", ascending=False).to_csv(SAIDA_CSV, index=False)
    print(f"\nCSV salvo: {SAIDA_CSV}")

    # Plot
    fig, ax = plt.subplots(figsize=(9, 7), dpi=120)
    ax.scatter(x, y, s=60, alpha=0.7, edgecolor="black", linewidth=0.4,
               color="#2ca02c")

    x_line = np.linspace(x.min(), x.max(), 100)
    y_line = res.slope * x_line + res.intercept
    ax.plot(x_line, y_line, color="#d62728", linewidth=2,
            label=f"β = {res.slope:+.2f}, R² = {res.rvalue**2:.3f}")

    ax.axhline(0, color="gray", linewidth=0.8, linestyle="--", alpha=0.6)

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
    ax.set_ylabel("Variação % esquerda dep. federal (2010→2022)", fontsize=11)
    ax.set_title(
        f"Crescimento dep. federal × índice institucional — SP capital\n"
        f"R² = {res.rvalue**2:.3f}   p = {res.pvalue:.3g}   N = {len(df)}",
        fontsize=12, fontweight="bold",
    )
    ax.legend(loc="best", fontsize=10)
    ax.grid(alpha=0.3)

    fig.tight_layout()
    SAIDA_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(SAIDA_FIG, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Figura salva: {SAIDA_FIG}")


if __name__ == "__main__":
    main()
