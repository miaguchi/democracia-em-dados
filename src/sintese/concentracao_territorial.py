"""TESTE — Concentração territorial da esquerda em SP, 2000-2024.

Para cada eleição municipal de vereador, calcula:
- Distribuição de votos da esquerda por zona (share da zona no total).
- Índice Herfindahl-Hirschman (HHI = Σ s_i²).
- Coeficiente de Gini da distribuição.

Plota HHI e Gini ao longo do tempo.

Hipótese: se a esquerda concentrou-se territorialmente em zonas
específicas (corredor universitário, bairros progressistas), HHI e
Gini sobem ao longo do tempo. Se a queda foi homogênea, ficam
estáveis.
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

from src.ingestao.carregar_mysql import MYSQL_CONFIG, DATABASE

SAIDA_FIG = _ROOT / "outputs/figures/concentracao_territorial.png"
SAIDA_CSV = _ROOT / "outputs/tables/concentracao_territorial.csv"

CD_MUNICIPIO_SP = 71072
PARTIDOS_ESQUERDA = (13, 50, 65, 12, 40, 43, 18, 16, 29, 80)
ANOS = [2000, 2004, 2008, 2012, 2016, 2020, 2024]


def votos_por_zona(ano: int) -> pd.Series:
    """Votos da esquerda por zona, vereador SP capital, 1º turno."""
    conn = mysql.connector.connect(database=DATABASE, **MYSQL_CONFIG)
    sql = f"""
    SELECT v.nr_zona, SUM(v.qt_votos_nominais) AS votos
    FROM votacao_partido_munzona v
    JOIN eleicao e ON v.cd_eleicao = e.cd_eleicao AND v.nr_turno = e.nr_turno
    WHERE v.nr_partido IN {PARTIDOS_ESQUERDA}
      AND v.cd_cargo = 13
      AND v.cd_municipio = {CD_MUNICIPIO_SP}
      AND e.nr_turno = 1
      AND e.ano_eleicao = {ano}
    GROUP BY v.nr_zona
    HAVING votos > 0
    """
    df = pd.read_sql(sql, conn)
    conn.close()
    return df.set_index("nr_zona")["votos"]


def hhi(shares: np.ndarray) -> float:
    """Herfindahl-Hirschman: soma dos quadrados das participações.

    shares deve somar 1. Retorna entre 1/N (uniforme) e 1 (concentrado).
    """
    return float(np.sum(shares ** 2))


def gini(values: np.ndarray) -> float:
    """Coeficiente de Gini de uma distribuição de valores não-negativos.

    Implementação direta da fórmula:
        G = (Σ_i Σ_j |x_i - x_j|) / (2 N² x̄)
    """
    x = np.sort(np.asarray(values, dtype=float))
    n = len(x)
    if n == 0 or x.sum() == 0:
        return 0.0
    # Fórmula otimizada equivalente à de Lorenz
    cum = np.cumsum(x)
    # G = (n + 1 - 2 * Σ((n+1-i)*x_i)/Σx_i) / n  (com índices 1..n após sort)
    i = np.arange(1, n + 1)
    g = (np.sum((2 * i - n - 1) * x)) / (n * x.sum())
    return float(g)


def main() -> None:
    print("=" * 65)
    print("TESTE — Concentração territorial da esquerda (SP, vereador)")
    print("=" * 65)

    resultados = []
    for ano in ANOS:
        v = votos_por_zona(ano)
        shares = (v / v.sum()).values
        h = hhi(shares)
        g = gini(v.values)
        n_zonas = len(v)
        # HHI normalizado entre 0 (uniforme) e 1
        hhi_norm = (h - 1 / n_zonas) / (1 - 1 / n_zonas) if n_zonas > 1 else 0.0
        resultados.append({
            "ano": ano,
            "n_zonas": n_zonas,
            "total_votos": int(v.sum()),
            "hhi": h,
            "hhi_norm": hhi_norm,
            "gini": g,
        })
        print(f"  {ano}: N={n_zonas:>3}  total={v.sum():>10,.0f}  "
              f"HHI={h:.4f}  HHI_norm={hhi_norm:.4f}  Gini={g:.4f}")

    df = pd.DataFrame(resultados)

    # Salvar
    SAIDA_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(SAIDA_CSV, index=False)
    print(f"\nCSV salvo: {SAIDA_CSV}")

    # Variação
    print(f"\n--- Variação 2000 → 2024 ---")
    delta_hhi = df["hhi"].iloc[-1] - df["hhi"].iloc[0]
    delta_gini = df["gini"].iloc[-1] - df["gini"].iloc[0]
    print(f"  ΔHHI:   {delta_hhi:+.4f}  ({delta_hhi/df['hhi'].iloc[0]*100:+.1f}%)")
    print(f"  ΔGini:  {delta_gini:+.4f}  ({delta_gini/df['gini'].iloc[0]*100:+.1f}%)")

    # Plot
    fig, ax1 = plt.subplots(figsize=(10, 6), dpi=120)
    ax2 = ax1.twinx()

    line1 = ax1.plot(df["ano"], df["hhi"], "o-", color="#1f77b4",
                     linewidth=2, markersize=8, label="HHI (Herfindahl)")
    line2 = ax2.plot(df["ano"], df["gini"], "s-", color="#d62728",
                     linewidth=2, markersize=8, label="Gini")

    # Linha de uniformidade (HHI = 1/N)
    n_med = df["n_zonas"].median()
    ax1.axhline(1 / n_med, color="#1f77b4", linestyle=":", alpha=0.4,
                label=f"HHI uniforme (1/N≈{1/n_med:.4f})")

    ax1.set_xlabel("Ano da eleição (vereador)", fontsize=11)
    ax1.set_ylabel("HHI (Herfindahl-Hirschman)", fontsize=11, color="#1f77b4")
    ax2.set_ylabel("Coeficiente de Gini", fontsize=11, color="#d62728")
    ax1.tick_params(axis="y", labelcolor="#1f77b4")
    ax2.tick_params(axis="y", labelcolor="#d62728")

    ax1.set_xticks(df["ano"])
    ax1.grid(alpha=0.3)

    ax1.set_title(
        f"Concentração territorial da esquerda — SP capital\n"
        f"Vereador, partidos Bolognesi, 2000-2024 — N≈{int(df['n_zonas'].mean())} zonas",
        fontsize=12, fontweight="bold",
    )
    # Combinar legendas
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="best", fontsize=10)

    fig.tight_layout()
    SAIDA_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(SAIDA_FIG, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"\nFigura salva: {SAIDA_FIG}")


if __name__ == "__main__":
    main()
