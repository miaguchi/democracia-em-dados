"""TESTE — Correlação da variação da esquerda entre cargos, por zona.

Para cada zona eleitoral de SP capital, calcula a variação percentual
do voto da esquerda completa (Bolognesi) entre o ano de pico e o
ano mais recente disponível, em cada cargo:

- Vereador: 2012 → 2024
- Deputado federal: 2010 → 2022
- Governador: 2010 → 2022
- Presidente: 2010 → 2022
- Prefeito: 2012 → 2024

Em seguida, computa a matriz 5×5 de correlação de Pearson entre as
variações e gera heatmap.

Hipótese: presidente, governador e deputado federal devem formar um
"bloco federal" com correlações altas (~0.9+). Vereador e prefeito
formam o bloco municipal. Correlação entre blocos deve ser moderada,
suportando a tese de voto diferenciado por nível.
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

SAIDA_FIG = _ROOT / "outputs/figures/correlacao_cargos_heatmap.png"
SAIDA_CSV = _ROOT / "outputs/tables/correlacao_cargos.csv"

CD_MUNICIPIO_SP = 71072
PARTIDOS_ESQUERDA = (13, 50, 65, 12, 40, 43, 18, 16, 29, 80)

# (rótulo, cd_cargo, ano_inicio, ano_fim)
CARGOS = [
    ("Vereador",      13, 2012, 2024),
    ("Dep. Federal",   6, 2010, 2022),
    ("Governador",     3, 2010, 2022),
    ("Presidente",     1, 2010, 2022),
    ("Prefeito",      11, 2012, 2024),
]


def variacao_por_zona(cd_cargo: int, ano_ini: int, ano_fim: int) -> pd.DataFrame:
    """Variação % esquerda por zona para um cargo, entre dois anos."""
    conn = mysql.connector.connect(database=DATABASE, **MYSQL_CONFIG)
    sql = f"""
    SELECT
        v.nr_zona,
        SUM(CASE WHEN e.ano_eleicao = {ano_ini} THEN v.qt_votos_nominais ELSE 0 END) AS v_ini,
        SUM(CASE WHEN e.ano_eleicao = {ano_fim} THEN v.qt_votos_nominais ELSE 0 END) AS v_fim
    FROM votacao_partido_munzona v
    JOIN eleicao e ON v.cd_eleicao = e.cd_eleicao AND v.nr_turno = e.nr_turno
    WHERE v.nr_partido IN {PARTIDOS_ESQUERDA}
      AND v.cd_cargo = {cd_cargo}
      AND v.cd_municipio = {CD_MUNICIPIO_SP}
      AND e.nr_turno = 1
      AND e.ano_eleicao IN ({ano_ini}, {ano_fim})
    GROUP BY v.nr_zona
    HAVING v_ini > 0
    """
    df = pd.read_sql(sql, conn)
    conn.close()
    df["variacao_pct"] = (df["v_fim"] - df["v_ini"]) / df["v_ini"] * 100
    return df[["nr_zona", "variacao_pct"]]


def main() -> None:
    print("=" * 65)
    print("TESTE — Correlação da variação da esquerda entre cargos")
    print("=" * 65)

    # Coletar variações por zona, por cargo
    variacoes = {}
    for label, cd, a_ini, a_fim in CARGOS:
        df = variacao_por_zona(cd, a_ini, a_fim)
        variacoes[label] = df.set_index("nr_zona")["variacao_pct"]
        print(f"  {label:<14} ({a_ini}→{a_fim}): {len(df)} zonas")

    # Juntar em DataFrame único (inner join)
    M = pd.concat(variacoes, axis=1).dropna()
    print(f"\nZonas com dados em todos os 4 cargos: {len(M)}")

    # Estatísticas descritivas
    print(f"\n--- Estatísticas das variações (%) ---")
    print(M.describe().round(1).to_string())

    # Matriz de correlação
    corr = M.corr(method="pearson").round(3)
    print(f"\n--- Matriz de correlação (Pearson) ---")
    print(corr.to_string())

    # Pares mais altos / mais baixos
    pairs = []
    cols = corr.columns.tolist()
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            pairs.append((cols[i], cols[j], corr.iloc[i, j]))
    pairs.sort(key=lambda t: t[2], reverse=True)

    print(f"\n--- Pares ordenados por correlação ---")
    for a, b, r in pairs:
        print(f"  {a:<14} × {b:<14} r = {r:+.3f}")

    # Salvar tabelas
    SAIDA_CSV.parent.mkdir(parents=True, exist_ok=True)
    corr.to_csv(SAIDA_CSV)
    M.to_csv(_ROOT / "outputs/tables/variacoes_por_cargo.csv")
    print(f"\nCSV correlação: {SAIDA_CSV}")
    print(f"CSV variações:  outputs/tables/variacoes_por_cargo.csv")

    # Heatmap
    fig, ax = plt.subplots(figsize=(8, 7), dpi=120)
    im = ax.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
    ax.set_xticks(range(len(cols)))
    ax.set_yticks(range(len(cols)))
    ax.set_xticklabels(cols, rotation=20, ha="right")
    ax.set_yticklabels(cols)
    for i in range(len(cols)):
        for j in range(len(cols)):
            v = corr.iloc[i, j]
            color = "white" if abs(v) > 0.55 else "black"
            ax.text(j, i, f"{v:+.2f}", ha="center", va="center",
                    fontsize=11, color=color, fontweight="bold")
    cb = fig.colorbar(im, ax=ax, shrink=0.8)
    cb.set_label("Correlação de Pearson", fontsize=10)
    ax.set_title(
        f"Correlação da variação % da esquerda entre cargos\n"
        f"SP capital — N = {len(M)} zonas",
        fontsize=12, fontweight="bold",
    )
    fig.tight_layout()
    SAIDA_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(SAIDA_FIG, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Figura salva: {SAIDA_FIG}")


if __name__ == "__main__":
    main()
