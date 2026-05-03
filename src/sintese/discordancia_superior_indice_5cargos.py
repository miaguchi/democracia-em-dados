"""TESTE — Discordância escolaridade × índice institucional, para 5 cargos.

Replica a análise de quadrantes Q1-Q4 para variação % esquerda em
cada um dos 5 cargos. Se o padrão Q2 ~ Q4 (alta escolaridade sem
índice ≈ periferia) se mantém em todos os cargos, o efeito
institucional se confirma como mecanismo geral.

Cargos:
  Vereador      (2012→2024)
  Prefeito      (2012→2024)
  Dep. Federal  (2010→2022)
  Governador    (2010→2022)
  Presidente    (2010→2022)
"""

from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import math, warnings

import matplotlib.pyplot as plt
import mysql.connector
import numpy as np
import pandas as pd

from src.ingestao.carregar_mysql import MYSQL_CONFIG, DATABASE

warnings.filterwarnings("ignore")

CSV_INDICE = _ROOT / "outputs/indice_institucional_por_zona.csv"
CSV_SUPERIOR = _ROOT / "outputs/superior_por_zona_2010.csv"
SAIDA_CSV = _ROOT / "outputs/tables/discordancia_superior_indice_5cargos.csv"
SAIDA_FIG = _ROOT / "outputs/figures/discordancia_superior_indice_5cargos.png"

CD_MUNICIPIO_SP = 71072
PARTIDOS_ESQUERDA = (13, 50, 65, 12, 40, 43, 18, 16, 29, 80)

# (rótulo, cd_cargo, ano_inicio, ano_fim)
CARGOS = [
    ("Vereador",     13, 2012, 2024),
    ("Prefeito",     11, 2012, 2024),
    ("Dep. Federal",  6, 2010, 2022),
    ("Governador",    3, 2010, 2022),
    ("Presidente",    1, 2010, 2022),
]


def fetch(sql: str) -> pd.DataFrame:
    conn = mysql.connector.connect(database=DATABASE, **MYSQL_CONFIG)
    cur = conn.cursor()
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return pd.DataFrame(rows, columns=cols)


def variacao_por_zona(cd_cargo: int, ano_ini: int, ano_fim: int) -> pd.DataFrame:
    sql = f"""
    SELECT v.nr_zona,
        SUM(CASE WHEN e.ano_eleicao={ano_ini} THEN v.qt_votos_nominais ELSE 0 END) AS v_ini,
        SUM(CASE WHEN e.ano_eleicao={ano_fim} THEN v.qt_votos_nominais ELSE 0 END) AS v_fim
    FROM votacao_partido_munzona v
    JOIN eleicao e ON v.cd_eleicao=e.cd_eleicao AND v.nr_turno=e.nr_turno
    WHERE v.nr_partido IN {PARTIDOS_ESQUERDA}
      AND v.cd_cargo={cd_cargo} AND v.cd_municipio={CD_MUNICIPIO_SP}
      AND e.nr_turno=1 AND e.ano_eleicao IN ({ano_ini}, {ano_fim})
    GROUP BY v.nr_zona HAVING v_ini > 0
    """
    df = fetch(sql)
    df["v_ini"] = pd.to_numeric(df["v_ini"])
    df["v_fim"] = pd.to_numeric(df["v_fim"])
    df["variacao_pct"] = (df["v_fim"] - df["v_ini"]) / df["v_ini"] * 100
    return df[["nr_zona", "variacao_pct"]]


def carregar_base() -> pd.DataFrame:
    """Cruza pct_superior + indice + variação % por cargo."""
    idx = pd.read_csv(CSV_INDICE)[["NR_ZONA", "nome_ze", "indice_cultural"]]
    idx.columns = ["nr_zona", "nome_ze", "indice_cultural"]
    sup = pd.read_csv(CSV_SUPERIOR).rename(columns={"NR_ZONA": "nr_zona"})

    base = idx.merge(sup[["nr_zona", "pct_superior"]], on="nr_zona", how="inner")

    for label, cd, a_ini, a_fim in CARGOS:
        df_var = variacao_por_zona(cd, a_ini, a_fim)
        df_var = df_var.rename(columns={"variacao_pct": f"var_{label.replace(' ', '_').replace('.', '')}"})
        base = base.merge(df_var, on="nr_zona", how="left")

    return base.dropna(subset=["pct_superior", "indice_cultural"])


def main() -> None:
    print("=" * 80)
    print("DISCORDÂNCIA escolaridade × índice — 5 cargos")
    print("=" * 80)

    df = carregar_base()
    print(f"\nN zonas: {len(df)}")

    # Quadrantes
    sup_med = df["pct_superior"].median()
    idx_med = df["indice_cultural"].median()
    print(f"Mediana pct_superior: {sup_med:.1f}%")
    print(f"Mediana indice_cultural: {idx_med:.1f}%")

    def quadrante(r):
        sup_alto = r["pct_superior"] > sup_med
        idx_alto = r["indice_cultural"] > idx_med
        if sup_alto and idx_alto: return "Q1"
        if sup_alto and not idx_alto: return "Q2"
        if not sup_alto and idx_alto: return "Q3"
        return "Q4"

    df["quadrante"] = df.apply(quadrante, axis=1)

    var_cols = [f"var_{l.replace(' ', '_').replace('.', '')}" for l, _, _, _ in CARGOS]

    # Tabela: variação média por quadrante × cargo
    tab = df.groupby("quadrante")[var_cols].mean().round(1)
    tab.columns = [l for l, _, _, _ in CARGOS]
    print("\n--- Variação % média (esquerda) por quadrante × cargo ---")
    print(tab.to_string())

    # Distâncias Q2-Q1 e Q2-Q4 por cargo
    print("\n--- Distância Q2→Q1 (escolaridade) vs Q2→Q4 (institucional) ---")
    print(f"  {'Cargo':<14} {'Q1':>8} {'Q2':>8} {'Q4':>8} {'|Q2-Q1|':>9} {'|Q2-Q4|':>9} {'Veredito':>14}")
    resumo = []
    for label, cd, a_ini, a_fim in CARGOS:
        col = f"var_{label.replace(' ', '_').replace('.', '')}"
        q1 = df[df["quadrante"] == "Q1"][col].mean()
        q2 = df[df["quadrante"] == "Q2"][col].mean()
        q4 = df[df["quadrante"] == "Q4"][col].mean()
        d12 = abs(q2 - q1)
        d24 = abs(q2 - q4)
        veredito = "INSTITUCIONAL" if d24 < d12 else "ESCOLARIDADE"
        print(f"  {label:<14} {q1:+8.1f} {q2:+8.1f} {q4:+8.1f} {d12:>9.1f} {d24:>9.1f} {veredito:>14}")
        resumo.append({"cargo": label, "q1": q1, "q2": q2, "q4": q4,
                       "d_q2_q1": d12, "d_q2_q4": d24, "veredito": veredito})

    pd.DataFrame(resumo).to_csv(SAIDA_CSV, index=False)
    print(f"\nCSV salvo: {SAIDA_CSV}")

    # Plot — barras agrupadas por cargo
    fig, ax = plt.subplots(figsize=(13, 6.5), dpi=120)
    cargos_lab = [l for l, _, _, _ in CARGOS]
    x = np.arange(len(cargos_lab))
    w = 0.18
    cores_q = {"Q1": "#2ca02c", "Q2": "#d62728", "Q3": "#9467bd", "Q4": "#1f77b4"}
    for i, q in enumerate(["Q1", "Q2", "Q3", "Q4"]):
        valores = []
        for label, _, _, _ in CARGOS:
            col = f"var_{label.replace(' ', '_').replace('.', '')}"
            valores.append(df[df["quadrante"] == q][col].mean())
        bars = ax.bar(x + (i - 1.5) * w, valores, w, color=cores_q[q],
                       alpha=0.85, edgecolor="black", linewidth=0.4,
                       label=f"{q} (n={(df['quadrante']==q).sum()})")
        for bar, v in zip(bars, valores):
            ax.annotate(f"{v:+.0f}", xy=(bar.get_x() + bar.get_width()/2, v),
                        xytext=(0, 3 if v > 0 else -12), textcoords="offset points",
                        ha="center", fontsize=7, fontweight="bold")

    ax.axhline(0, color="gray", linewidth=0.8, linestyle="--", alpha=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels(cargos_lab, fontsize=10)
    ax.set_ylabel("Variação % esquerda média (zona)", fontsize=11)
    ax.set_title(
        "Discordância escolaridade × índice — comportamento por cargo\n"
        "Q2 (alto sup, BAIXO índice) ≈ Q4 (baixo+baixo) → efeito INSTITUCIONAL",
        fontsize=12, fontweight="bold",
    )
    ax.legend(loc="best", fontsize=9, ncol=4)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(SAIDA_FIG, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Figura salva: {SAIDA_FIG}")


if __name__ == "__main__":
    main()
