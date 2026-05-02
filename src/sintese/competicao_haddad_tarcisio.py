"""Teste: gap Tarcísio-Bolsonaro por zona é explicado pela força do Haddad?

Hipótese: nas zonas onde o PT/Haddad foi forte para governador, sobra
menos espaço para Tarcísio (concorrência estrutural). Isso, mais do
que "personalismo militante", explicaria por que a transferência
presidente→governador (Bolso→Tarc) é menor na periferia.

Método:
- Para cada zona de SP capital, calcular Haddad votos (gov, PT, 2022)
  e gap% = (Tarc/Bolso - 1) × 100.
- Correlação Haddad × gap%.
- Regressão multivariada: gap% ~ haddad_share + indice_cultural.

Se r negativo e p < 0.05: hipótese confirmada (Haddad forte → gap maior).
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
SAIDA_CSV = _ROOT / "outputs/tables/competicao_haddad_tarcisio.csv"
SAIDA_FIG = _ROOT / "outputs/figures/competicao_haddad_tarcisio.png"

CD_MUNICIPIO_SP = 71072


def pearsonr(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """Pearson r e p-valor (aprox via t-Student)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    n = len(x)
    mx, my = x.mean(), y.mean()
    den = np.sqrt(((x - mx) ** 2).sum() * ((y - my) ** 2).sum())
    r = ((x - mx) * (y - my)).sum() / den if den > 0 else 0.0
    if abs(r) >= 1:
        return r, 0.0
    t = r * np.sqrt(n - 2) / np.sqrt(1 - r ** 2)
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(t) / math.sqrt(2))))
    return float(r), float(p)


def fetch(sql: str) -> pd.DataFrame:
    """Executa SQL e retorna DataFrame, sem usar pd.read_sql."""
    conn = mysql.connector.connect(database=DATABASE, **MYSQL_CONFIG)
    cur = conn.cursor()
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return pd.DataFrame(rows, columns=cols)


def main() -> None:
    print("=" * 65)
    print("TESTE — Competição Haddad × gap Tarcísio-Bolsonaro")
    print("=" * 65)

    sql = f"""
    SELECT v.nr_zona,
        SUM(CASE WHEN v.cd_cargo=1 AND v.nr_partido=22 THEN v.qt_votos_nominais ELSE 0 END) AS bolso,
        SUM(CASE WHEN v.cd_cargo=3 AND v.nr_partido=10 THEN v.qt_votos_nominais ELSE 0 END) AS tarc,
        SUM(CASE WHEN v.cd_cargo=3 AND v.nr_partido=13 THEN v.qt_votos_nominais ELSE 0 END) AS haddad
    FROM votacao_partido_munzona v
    JOIN eleicao e ON v.cd_eleicao=e.cd_eleicao AND v.nr_turno=e.nr_turno
    WHERE v.cd_municipio={CD_MUNICIPIO_SP}
      AND e.ano_eleicao=2022 AND e.nr_turno=1
    GROUP BY v.nr_zona
    HAVING bolso > 0
    """
    df = fetch(sql)
    for c in ["bolso", "tarc", "haddad"]:
        df[c] = pd.to_numeric(df[c])

    df["gap_pct"] = (df["tarc"] / df["bolso"] - 1) * 100
    df["haddad_share"] = df["haddad"] / (df["haddad"] + df["bolso"] + df["tarc"]) * 100

    idx = pd.read_csv(CSV_INDICE)[["NR_ZONA", "nome_ze", "indice_cultural"]]
    idx.columns = ["nr_zona", "nome_ze", "indice_cultural"]
    df = df.merge(idx, on="nr_zona", how="left")

    print(f"\nN zonas: {len(df)}")
    print(f"Total Haddad gov:  {df['haddad'].sum():>10,.0f}")
    print(f"Total Bolso pres:  {df['bolso'].sum():>10,.0f}")
    print(f"Total Tarc gov:    {df['tarc'].sum():>10,.0f}")

    # Correlações
    print(f"\n--- Correlações (gap% = (Tarc/Bolso - 1) × 100) ---")
    r1, p1 = pearsonr(df["haddad"], df["gap_pct"])
    print(f"  Haddad votos       × gap%: r = {r1:+.3f}  (p = {p1:.2g})")
    r2, p2 = pearsonr(df["haddad_share"], df["gap_pct"])
    print(f"  Haddad share %     × gap%: r = {r2:+.3f}  (p = {p2:.2g})")

    # OLS multivariado
    print(f"\n--- OLS gap% ~ haddad_share + indice_cultural ---")
    sub = df.dropna(subset=["indice_cultural"]).copy()
    y = sub["gap_pct"].values
    for nome, cols in [
        ("só índice",                ["indice_cultural"]),
        ("só haddad_share",          ["haddad_share"]),
        ("haddad_share + índice",    ["haddad_share", "indice_cultural"]),
    ]:
        X = np.column_stack([np.ones(len(sub))] + [sub[c].values for c in cols])
        b, *_ = np.linalg.lstsq(X, y, rcond=None)
        yh = X @ b
        r2v = 1 - ((y - yh) ** 2).sum() / ((y - y.mean()) ** 2).sum()
        betas_str = ", ".join(f"{c}={bi:+.3f}" for c, bi in zip(cols, b[1:]))
        print(f"  {nome:<28}  R² = {r2v:.3f}   intercepto={b[0]:+.2f}   {betas_str}")

    # Veredito
    print(f"\n--- Veredito ---")
    if r2 < -0.3 and p2 < 0.01:
        print(f"  HIPÓTESE CONFIRMADA: r = {r2:+.3f}, p = {p2:.2g}")
        print(f"  Quanto mais forte Haddad numa zona, maior o gap de Tarcísio")
        print(f"  vs Bolsonaro — competição estrutural pelo espaço da disputa.")
    elif p2 > 0.05:
        print(f"  Hipótese NÃO confirmada (p = {p2:.2g}).")
    else:
        print(f"  Resultado misto: r = {r2:+.3f}, p = {p2:.2g}")

    # Salvar tabela
    SAIDA_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.sort_values("haddad_share", ascending=False).to_csv(SAIDA_CSV, index=False)
    print(f"\nCSV salvo: {SAIDA_CSV}")

    # Plot scatter colorido pelo índice institucional
    fig, ax = plt.subplots(figsize=(9, 7), dpi=120)
    sc = ax.scatter(df["haddad_share"], df["gap_pct"],
                    c=df["indice_cultural"].fillna(0),
                    s=80, alpha=0.8, cmap="viridis",
                    edgecolor="black", linewidth=0.4)
    cb = fig.colorbar(sc, ax=ax)
    cb.set_label("Índice institucional (%)", fontsize=10)

    # Reta de regressão simples
    coef = np.polyfit(df["haddad_share"], df["gap_pct"], 1)
    xs = np.linspace(df["haddad_share"].min(), df["haddad_share"].max(), 100)
    ax.plot(xs, np.polyval(coef, xs), "r-", linewidth=2,
            label=f"OLS: y={coef[0]:+.2f}x+{coef[1]:+.1f},  r={r2:+.3f}")

    # Anotar zonas-alvo
    zonas_destaque = {1: "Bela Vista", 2: "Perdizes", 251: "Pinheiros",
                      258: "Indianópolis", 5: "Jd Paulista", 346: "Butantã",
                      404: "C. Tiradentes", 381: "Parelheiros",
                      376: "Brasilândia", 372: "Pirapora SP"}
    for z, nome in zonas_destaque.items():
        row = df[df["nr_zona"] == z]
        if row.empty:
            continue
        ax.annotate(
            f"Z{z}\n{nome}",
            xy=(row["haddad_share"].iloc[0], row["gap_pct"].iloc[0]),
            fontsize=7, ha="center", va="bottom",
            xytext=(0, 6), textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                      edgecolor="gray", alpha=0.9),
        )

    ax.set_xlabel("Haddad share (%) — fração do total Haddad+Bolso+Tarc", fontsize=11)
    ax.set_ylabel("Gap % Tarcísio relativo a Bolsonaro\n(negativo = Tarc fica atrás)", fontsize=11)
    ax.set_title(
        "Hipótese: força do Haddad explica o gap Tarc-Bolso\n"
        f"r = {r2:+.3f}  p = {p2:.2g}  N = {len(df)}",
        fontsize=12, fontweight="bold",
    )
    ax.legend(loc="best", fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(SAIDA_FIG, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Figura salva: {SAIDA_FIG}")


if __name__ == "__main__":
    main()
