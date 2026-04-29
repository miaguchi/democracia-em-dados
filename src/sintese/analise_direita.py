"""ANÁLISE SIMÉTRICA — bloco de direita.

Replica os Testes A (regressão crescimento × índice institucional) e
C (concentração territorial HHI/Gini) usando partidos de direita,
para comparação com os resultados da esquerda.

Partidos de direita selecionados (Bolognesi, Ribeiro & Codato 2023):
  22 (PL),  11 (PP),  10 (REPUBLICANOS),  44 (UNIÃO),  25 (DEM),
  28 (PRTB), 14 (PTB), 55 (PSD), 20 (PODE)

Hipóteses:
- Se a tese institucional for específica à esquerda: R² do Teste A
  para a direita deve ser próximo de zero (índice cultural-progressista
  não prediz crescimento da direita) ou negativo (zonas de alto
  índice cresceram MENOS para a direita).
- Se for proxy genérico de "perfil ideológico", o sinal do β deveria
  ser invertido — zonas com alto índice perdem direita.
- Concentração territorial: hipótese é assimetria — direita pode ter
  trajetória diferente (talvez crescimento concentrado em periferia).
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
from src.sintese.concentracao_territorial import hhi, gini

CSV_INDICE = _ROOT / "outputs/indice_institucional_por_zona.csv"
SAIDA_FIG_REG = _ROOT / "outputs/figures/regressao_crescimento_indice_direita.png"
SAIDA_FIG_CONC = _ROOT / "outputs/figures/concentracao_territorial_direita.png"
SAIDA_FIG_COMP = _ROOT / "outputs/figures/comparacao_esq_dir.png"
SAIDA_CSV_REG = _ROOT / "outputs/tables/regressao_crescimento_indice_direita.csv"
SAIDA_CSV_CONC = _ROOT / "outputs/tables/concentracao_territorial_direita.csv"

CD_MUNICIPIO_SP = 71072
PARTIDOS_DIREITA = (22, 11, 10, 44, 25, 28, 14, 55, 20)
ANOS = [2000, 2004, 2008, 2012, 2016, 2020, 2024]


def variacao_direita_2012_2024() -> pd.DataFrame:
    """Variação % dos votos da direita 2012→2024 por zona, vereador SP."""
    conn = mysql.connector.connect(database=DATABASE, **MYSQL_CONFIG)
    sql = f"""
    SELECT
        v.nr_zona,
        SUM(CASE WHEN e.ano_eleicao = 2012 THEN v.qt_votos_nominais ELSE 0 END) AS dir_2012,
        SUM(CASE WHEN e.ano_eleicao = 2024 THEN v.qt_votos_nominais ELSE 0 END) AS dir_2024
    FROM votacao_partido_munzona v
    JOIN eleicao e ON v.cd_eleicao = e.cd_eleicao AND v.nr_turno = e.nr_turno
    WHERE v.nr_partido IN {PARTIDOS_DIREITA}
      AND v.cd_cargo = 13
      AND v.cd_municipio = {CD_MUNICIPIO_SP}
      AND e.nr_turno = 1
      AND e.ano_eleicao IN (2012, 2024)
    GROUP BY v.nr_zona
    HAVING dir_2012 > 0
    """
    df = pd.read_sql(sql, conn)
    conn.close()
    df["variacao_pct"] = (df["dir_2024"] - df["dir_2012"]) / df["dir_2012"] * 100
    return df


def votos_direita_por_zona(ano: int) -> pd.Series:
    """Votos da direita por zona, vereador SP capital."""
    conn = mysql.connector.connect(database=DATABASE, **MYSQL_CONFIG)
    sql = f"""
    SELECT v.nr_zona, SUM(v.qt_votos_nominais) AS votos
    FROM votacao_partido_munzona v
    JOIN eleicao e ON v.cd_eleicao = e.cd_eleicao AND v.nr_turno = e.nr_turno
    WHERE v.nr_partido IN {PARTIDOS_DIREITA}
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


def teste_a_direita() -> dict:
    """Regressão variação % direita 2012→2024 ~ índice institucional."""
    df_var = variacao_direita_2012_2024()
    idx = pd.read_csv(CSV_INDICE)[["NR_ZONA", "nome_ze", "indice_cultural"]]
    idx.columns = ["nr_zona", "nome_ze", "indice_cultural"]
    df = df_var.merge(idx, on="nr_zona", how="inner")
    df = df.dropna(subset=["variacao_pct", "indice_cultural"])

    x = df["indice_cultural"].values
    y = df["variacao_pct"].values
    res = stats.linregress(x, y)

    df.sort_values("variacao_pct", ascending=False).to_csv(SAIDA_CSV_REG, index=False)

    # Plot
    fig, ax = plt.subplots(figsize=(9, 7), dpi=120)
    ax.scatter(x, y, s=60, alpha=0.7, edgecolor="black", linewidth=0.4,
               color="#9467bd")
    x_line = np.linspace(x.min(), x.max(), 100)
    ax.plot(x_line, res.slope * x_line + res.intercept, color="#d62728",
            linewidth=2, label=f"β={res.slope:+.2f}, R²={res.rvalue**2:.3f}")
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
    ax.set_ylabel("Variação % direita vereador (2012→2024)", fontsize=11)
    ax.set_title(
        f"Crescimento da direita × índice institucional — SP capital\n"
        f"R²={res.rvalue**2:.3f}  p={res.pvalue:.3g}  N={len(df)}",
        fontsize=12, fontweight="bold",
    )
    ax.legend(loc="best", fontsize=10)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(SAIDA_FIG_REG, dpi=300, bbox_inches="tight")
    plt.close()

    return {
        "n": len(df),
        "slope": res.slope,
        "intercept": res.intercept,
        "r2": res.rvalue ** 2,
        "p": res.pvalue,
    }


def teste_c_direita() -> pd.DataFrame:
    """Concentração territorial da direita por ano (HHI e Gini)."""
    resultados = []
    for ano in ANOS:
        v = votos_direita_por_zona(ano)
        if len(v) == 0 or v.sum() == 0:
            continue
        shares = (v / v.sum()).values
        resultados.append({
            "ano": ano,
            "n_zonas": len(v),
            "total_votos": int(v.sum()),
            "hhi": hhi(shares),
            "gini": gini(v.values),
        })
    df = pd.DataFrame(resultados)
    df.to_csv(SAIDA_CSV_CONC, index=False)

    # Plot
    fig, ax1 = plt.subplots(figsize=(10, 6), dpi=120)
    ax2 = ax1.twinx()
    line1 = ax1.plot(df["ano"], df["hhi"], "o-", color="#9467bd",
                     linewidth=2, markersize=8, label="HHI (direita)")
    line2 = ax2.plot(df["ano"], df["gini"], "s-", color="#ff7f0e",
                     linewidth=2, markersize=8, label="Gini (direita)")
    ax1.set_xlabel("Ano da eleição (vereador)", fontsize=11)
    ax1.set_ylabel("HHI", fontsize=11, color="#9467bd")
    ax2.set_ylabel("Gini", fontsize=11, color="#ff7f0e")
    ax1.tick_params(axis="y", labelcolor="#9467bd")
    ax2.tick_params(axis="y", labelcolor="#ff7f0e")
    ax1.set_xticks(df["ano"])
    ax1.grid(alpha=0.3)
    ax1.set_title(
        "Concentração territorial da DIREITA — SP capital\n"
        f"Vereador, partidos selecionados, 2000-2024",
        fontsize=12, fontweight="bold",
    )
    lines = line1 + line2
    ax1.legend(lines, [l.get_label() for l in lines], loc="best", fontsize=10)
    fig.tight_layout()
    fig.savefig(SAIDA_FIG_CONC, dpi=300, bbox_inches="tight")
    plt.close()
    return df


def comparativo_esquerda_direita(res_a_dir: dict, conc_dir: pd.DataFrame) -> None:
    """Painel duplo comparando esquerda e direita."""
    # Carregar resultados da esquerda
    esq_reg = pd.read_csv(_ROOT / "outputs/tables/regressao_crescimento_indice.csv")
    res_esq = stats.linregress(esq_reg["indice_cultural"], esq_reg["variacao_pct"])
    conc_esq = pd.read_csv(_ROOT / "outputs/tables/concentracao_territorial.csv")

    fig, axes = plt.subplots(1, 2, figsize=(15, 6), dpi=120)

    # Painel A: regressão crescimento × índice
    for label, df_in, color, marker, res in [
        ("Esquerda", esq_reg, "#1f77b4", "o", res_esq),
        ("Direita", pd.read_csv(SAIDA_CSV_REG), "#9467bd", "s", None),
    ]:
        if res is None:
            res = stats.linregress(df_in["indice_cultural"], df_in["variacao_pct"])
        axes[0].scatter(df_in["indice_cultural"], df_in["variacao_pct"],
                        s=40, alpha=0.6, edgecolor="black", linewidth=0.3,
                        marker=marker, color=color,
                        label=f"{label}: β={res.slope:+.2f}, R²={res.rvalue**2:.3f}")
        x_line = np.linspace(df_in["indice_cultural"].min(),
                             df_in["indice_cultural"].max(), 100)
        axes[0].plot(x_line, res.slope * x_line + res.intercept,
                     color=color, linewidth=2, alpha=0.8)
    axes[0].axhline(0, color="gray", linewidth=0.8, linestyle="--", alpha=0.6)
    axes[0].set_xlabel("Índice institucional cultural-progressista (%)")
    axes[0].set_ylabel("Variação % vereador (2012→2024)")
    axes[0].set_title("TESTE A — Crescimento × índice institucional",
                      fontsize=12, fontweight="bold")
    axes[0].legend(loc="best", fontsize=9)
    axes[0].grid(alpha=0.3)

    # Painel B: concentração territorial (Gini ao longo do tempo)
    axes[1].plot(conc_esq["ano"], conc_esq["gini"], "o-", color="#1f77b4",
                 linewidth=2, markersize=8, label="Gini esquerda")
    axes[1].plot(conc_dir["ano"], conc_dir["gini"], "s-", color="#9467bd",
                 linewidth=2, markersize=8, label="Gini direita")
    axes[1].set_xlabel("Ano da eleição (vereador)")
    axes[1].set_ylabel("Coeficiente de Gini")
    axes[1].set_xticks(conc_esq["ano"])
    axes[1].set_title("TESTE C — Concentração territorial (Gini)",
                      fontsize=12, fontweight="bold")
    axes[1].legend(loc="best", fontsize=10)
    axes[1].grid(alpha=0.3)

    fig.suptitle("Comparação esquerda × direita — SP capital, vereador",
                 fontsize=13, fontweight="bold")
    fig.tight_layout()
    fig.savefig(SAIDA_FIG_COMP, dpi=300, bbox_inches="tight")
    plt.close()


def main() -> None:
    print("=" * 65)
    print("ANÁLISE SIMÉTRICA — bloco de direita")
    print("=" * 65)

    # ========== TESTE A ==========
    print("\n--- TESTE A: regressão crescimento × índice institucional ---")
    res_a = teste_a_direita()
    print(f"  N                 = {res_a['n']}")
    print(f"  Coeficiente (β)   = {res_a['slope']:+.3f}")
    print(f"  Intercepto        = {res_a['intercept']:+.3f}")
    print(f"  R²                = {res_a['r2']:.3f}")
    print(f"  p-valor           = {res_a['p']:.4g}")

    # Compare com esquerda
    esq_reg = pd.read_csv(_ROOT / "outputs/tables/regressao_crescimento_indice.csv")
    res_esq = stats.linregress(esq_reg["indice_cultural"], esq_reg["variacao_pct"])
    print(f"\n  --- Comparação Teste A (esquerda vs direita) ---")
    print(f"  Esquerda: β={res_esq.slope:+.2f}, R²={res_esq.rvalue**2:.3f}, p={res_esq.pvalue:.2g}")
    print(f"  Direita:  β={res_a['slope']:+.2f}, R²={res_a['r2']:.3f}, p={res_a['p']:.2g}")

    # ========== TESTE C ==========
    print("\n--- TESTE C: concentração territorial (HHI e Gini) ---")
    conc_dir = teste_c_direita()
    print(conc_dir.to_string(index=False, float_format=lambda x: f"{x:.4f}"))

    # Compare com esquerda
    conc_esq = pd.read_csv(_ROOT / "outputs/tables/concentracao_territorial.csv")
    print(f"\n  --- Comparação Teste C (Gini ao longo do tempo) ---")
    print(f"  {'Ano':>6}  {'Gini ESQ':>10}  {'Gini DIR':>10}")
    for ano in ANOS:
        g_esq = conc_esq[conc_esq["ano"] == ano]["gini"]
        g_dir = conc_dir[conc_dir["ano"] == ano]["gini"]
        ge = g_esq.iloc[0] if not g_esq.empty else np.nan
        gd = g_dir.iloc[0] if not g_dir.empty else np.nan
        print(f"  {ano:>6}  {ge:>10.4f}  {gd:>10.4f}")

    # Variações 2000→2024
    g_esq_0 = conc_esq[conc_esq["ano"] == 2000]["gini"].iloc[0]
    g_esq_f = conc_esq[conc_esq["ano"] == 2024]["gini"].iloc[0]
    g_dir_0 = conc_dir[conc_dir["ano"] == 2000]["gini"].iloc[0]
    g_dir_f = conc_dir[conc_dir["ano"] == 2024]["gini"].iloc[0]
    print(f"\n  ΔGini esquerda 2000→2024: {g_esq_f - g_esq_0:+.4f} ({(g_esq_f-g_esq_0)/g_esq_0*100:+.1f}%)")
    print(f"  ΔGini direita  2000→2024: {g_dir_f - g_dir_0:+.4f} ({(g_dir_f-g_dir_0)/g_dir_0*100:+.1f}%)")

    # Gerar painel comparativo
    print("\n--- Gerando figura comparativa ---")
    comparativo_esquerda_direita(res_a, conc_dir)
    print(f"  {SAIDA_FIG_REG}")
    print(f"  {SAIDA_FIG_CONC}")
    print(f"  {SAIDA_FIG_COMP}")


if __name__ == "__main__":
    main()
