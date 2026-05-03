"""TESTE — Casos discordantes entre escolaridade e índice institucional.

Pergunta de identificação:
- Se zonas com ALTA escolaridade mas BAIXO índice institucional
  votam à esquerda → efeito é escolaridade.
- Se essas mesmas zonas NÃO votam à esquerda → efeito é institucional.

Método:
1. Padronizar pct_superior e indice_cultural.
2. Classificar zonas em 4 quadrantes (cortes na mediana).
3. Comparar variação % esquerda 2012→2024 e escore ideológico
   2024 entre os quadrantes.
4. Listar casos discordantes (Q2 = alto sup, baixo índice; e
   Q3 = baixo sup, alto índice).
5. Visualizar.
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
CSV_SOCIO_2010 = _ROOT / "outputs/socioeconomia_por_zona.csv"
CSV_SUPERIOR = _ROOT / "outputs/superior_por_zona_2010.csv"
SAIDA_CSV = _ROOT / "outputs/tables/discordancia_superior_indice.csv"
SAIDA_FIG = _ROOT / "outputs/figures/discordancia_superior_indice.png"

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


def carregar() -> pd.DataFrame:
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

    idx = pd.read_csv(CSV_INDICE)[["NR_ZONA", "nome_ze", "indice_cultural",
                                    "escore_ver_2024", "escore_pref_2024"]]
    idx.columns = ["nr_zona", "nome_ze", "indice_cultural",
                   "escore_ver_2024", "escore_pref_2024"]

    sup = pd.read_csv(CSV_SUPERIOR).rename(columns={"NR_ZONA": "nr_zona"})

    s10 = pd.read_csv(CSV_SOCIO_2010)[["NR_ZONA", "renda_pc_media"]]
    s10.columns = ["nr_zona", "renda_2010"]

    return df.merge(idx, on="nr_zona", how="left") \
             .merge(sup[["nr_zona", "pct_superior"]], on="nr_zona", how="left") \
             .merge(s10, on="nr_zona", how="left") \
             .dropna(subset=["pct_superior", "indice_cultural",
                              "variacao_pct", "escore_ver_2024"])


def main() -> None:
    print("=" * 75)
    print("CASOS DISCORDANTES — escolaridade vs índice institucional")
    print("=" * 75)

    df = carregar()
    print(f"\nN zonas: {len(df)}")

    # Padronizar para classificar em quadrantes
    sup_med = df["pct_superior"].median()
    idx_med = df["indice_cultural"].median()
    print(f"\nMediana pct_superior: {sup_med:.1f}%")
    print(f"Mediana indice_cultural: {idx_med:.1f}%")

    def quadrante(r):
        sup_alto = r["pct_superior"] > sup_med
        idx_alto = r["indice_cultural"] > idx_med
        if sup_alto and idx_alto:
            return "Q1: alto sup + alto índice"
        if sup_alto and not idx_alto:
            return "Q2: alto sup + BAIXO índice (DISCORDANTE)"
        if not sup_alto and idx_alto:
            return "Q3: BAIXO sup + alto índice (raro)"
        return "Q4: baixo sup + baixo índice"

    df["quadrante"] = df.apply(quadrante, axis=1)

    print("\n--- Comportamento eleitoral por quadrante ---")
    print(df.groupby("quadrante").agg(
        n=("nr_zona", "count"),
        var_esq_media=("variacao_pct", "mean"),
        var_esq_mediana=("variacao_pct", "median"),
        escore_ver_media=("escore_ver_2024", "mean"),
        escore_pref_media=("escore_pref_2024", "mean"),
    ).round(2).to_string())

    # Listar zonas Q2 (caso crítico)
    q2 = df[df["quadrante"].str.startswith("Q2")].sort_values("pct_superior", ascending=False)
    print(f"\n=== Q2 — Zonas DISCORDANTES (alto sup, baixo índice) — N={len(q2)} ===")
    print(q2[["nr_zona", "nome_ze", "pct_superior", "indice_cultural",
              "variacao_pct", "escore_ver_2024"]].to_string(index=False))

    # Q1 para comparar (alto sup + alto índice)
    q1 = df[df["quadrante"].str.startswith("Q1")].sort_values("pct_superior", ascending=False)
    print(f"\n=== Q1 — Zonas CONCORDANTES alta (alto sup, alto índice) — N={len(q1)} ===")
    print(q1[["nr_zona", "nome_ze", "pct_superior", "indice_cultural",
              "variacao_pct", "escore_ver_2024"]].head(10).to_string(index=False))

    # Q4 (baixa-baixa, periferia)
    q4 = df[df["quadrante"].str.startswith("Q4")]
    print(f"\n=== Q4 — Zonas concordantes baixa (baixo sup, baixo índice) — N={len(q4)} ===")
    print(f"  Variação média: {q4['variacao_pct'].mean():.1f}%")
    print(f"  Escore médio:   {q4['escore_ver_2024'].mean():.2f}")

    # Salvar
    SAIDA_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.sort_values(["quadrante", "pct_superior"], ascending=[True, False]).to_csv(
        SAIDA_CSV, index=False)
    print(f"\nCSV salvo: {SAIDA_CSV}")

    # === Visualização ===
    fig, axes = plt.subplots(1, 2, figsize=(15, 7), dpi=120)

    # Painel 1: scatter pct_superior × índice, cor = variação esquerda
    cores_q = {
        "Q1: alto sup + alto índice": "#2ca02c",
        "Q2: alto sup + BAIXO índice (DISCORDANTE)": "#d62728",
        "Q3: BAIXO sup + alto índice (raro)": "#9467bd",
        "Q4: baixo sup + baixo índice": "#1f77b4",
    }

    for q, cor in cores_q.items():
        sub = df[df["quadrante"] == q]
        if sub.empty:
            continue
        axes[0].scatter(sub["pct_superior"], sub["indice_cultural"],
                        c=cor, s=80, alpha=0.7, edgecolor="black",
                        linewidth=0.4, label=f"{q.split(':')[0]} (n={len(sub)})")

    axes[0].axhline(idx_med, color="gray", linestyle="--", alpha=0.5)
    axes[0].axvline(sup_med, color="gray", linestyle="--", alpha=0.5)
    axes[0].set_xlabel("% superior completo (Censo 2010)", fontsize=11)
    axes[0].set_ylabel("Índice institucional cultural-progressista", fontsize=11)
    axes[0].set_title("Quadrantes de discordância", fontsize=12, fontweight="bold")
    axes[0].legend(fontsize=8, loc="upper left")
    axes[0].grid(alpha=0.3)

    # Anotar Q2 (zonas discordantes — críticas)
    for _, r in q2.iterrows():
        axes[0].annotate(
            f"Z{int(r['nr_zona'])}\n{r['nome_ze'][:13]}",
            xy=(r["pct_superior"], r["indice_cultural"]),
            fontsize=7, ha="center", va="bottom",
            xytext=(0, 6), textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                      edgecolor="#d62728", linewidth=1, alpha=0.9),
        )

    # Painel 2: boxplot da variação % por quadrante
    ordem_q = ["Q4: baixo sup + baixo índice",
               "Q3: BAIXO sup + alto índice (raro)",
               "Q2: alto sup + BAIXO índice (DISCORDANTE)",
               "Q1: alto sup + alto índice"]
    dados = [df[df["quadrante"] == q]["variacao_pct"].values for q in ordem_q]
    cores_box = [cores_q[q] for q in ordem_q]
    rotulos = [q.split(":")[0] for q in ordem_q]
    bp = axes[1].boxplot(dados, labels=rotulos, patch_artist=True,
                          medianprops=dict(color="black", linewidth=2))
    for patch, c in zip(bp["boxes"], cores_box):
        patch.set_facecolor(c)
        patch.set_alpha(0.7)
    axes[1].axhline(0, color="gray", linestyle="--", alpha=0.5)
    axes[1].set_ylabel("Variação % esquerda vereador (2012→2024)", fontsize=11)
    axes[1].set_title("Comportamento eleitoral por quadrante",
                      fontsize=12, fontweight="bold")
    axes[1].grid(axis="y", alpha=0.3)

    fig.suptitle(
        "Discordância: % superior completo vs índice institucional\n"
        f"Q2 (alto sup, BAIXO índice) = caso crítico — N={len(df)}",
        fontsize=13, fontweight="bold",
    )
    fig.tight_layout()
    fig.savefig(SAIDA_FIG, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Figura salva: {SAIDA_FIG}")

    # Veredito
    print(f"\n--- Veredito ---")
    var_q1 = df[df["quadrante"].str.startswith("Q1")]["variacao_pct"].mean()
    var_q2 = df[df["quadrante"].str.startswith("Q2")]["variacao_pct"].mean()
    var_q4 = df[df["quadrante"].str.startswith("Q4")]["variacao_pct"].mean()
    print(f"  Q1 (alto sup + alto idx): variação média {var_q1:+.1f}%")
    print(f"  Q2 (alto sup, BAIXO idx): variação média {var_q2:+.1f}%")
    print(f"  Q4 (baixo+baixo):         variação média {var_q4:+.1f}%")
    print(f"\n  Se Q2 ~ Q1 → escolaridade é o que importa (índice é proxy)")
    print(f"  Se Q2 ~ Q4 → INSTITUCIONAL é o que importa (escolaridade é proxy)")
    print(f"  Distância Q2-Q1: {abs(var_q2 - var_q1):.1f} pp")
    print(f"  Distância Q2-Q4: {abs(var_q2 - var_q4):.1f} pp")
    if abs(var_q2 - var_q4) < abs(var_q2 - var_q1):
        print(f"  Q2 está mais próximo de Q4 → efeito INSTITUCIONAL")
    else:
        print(f"  Q2 está mais próximo de Q1 → efeito ESCOLARIDADE")


if __name__ == "__main__":
    main()
