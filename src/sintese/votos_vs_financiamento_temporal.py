"""Trajetória votos × financiamento — vereadores eleitos SP, 2012-2024.

Estende a análise pontual de 2024 para os 4 ciclos municipais
disponíveis (2012, 2016, 2020, 2024). Permite ver:
- Evolução do custo por voto ao longo do tempo
- Mudança na eficiência relativa entre blocos
- Trajetória dos principais partidos
- Concentração de receita nos eleitos
"""

from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import warnings
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.partidario.ideologia import ESCORE_BOLOGNESI, bloco_tripartite

warnings.filterwarnings("ignore")

CSV_REC = _ROOT / "data/processed/receitas_vereador_sp_2012_2024.parquet"
SAIDA_CSV = _ROOT / "outputs/tables/votos_vs_financiamento_temporal.csv"
SAIDA_FIG = _ROOT / "outputs/figures/votos_vs_financiamento_temporal.png"

# Inflação acumulada IPCA até 2024 (base = 2024). Aproximação:
# 2012→2024: ~107% (multiplicador 2.07)
# 2016→2024: ~52% (multiplicador 1.52)
# 2020→2024: ~28% (multiplicador 1.28)
INFLACAO = {2012: 2.07, 2016: 1.52, 2020: 1.28, 2024: 1.00}

ANOS = [2012, 2016, 2020, 2024]


def carregar_votos(ano: int) -> pd.DataFrame:
    """Votos por candidato eleito a vereador em SP capital."""
    f = _ROOT / f"data/processed/votacao_candidato_munzona_{ano}_SP.parquet"
    df = pd.read_parquet(f)
    sp = df[(df["NM_MUNICIPIO"] == "SÃO PAULO")
            & (df["DS_CARGO"] == "Vereador")
            & (df["NR_TURNO"] == 1)].copy()
    eleitos_status = ["ELEITO POR QP", "ELEITO POR MÉDIA", "ELEITO"]
    sp = sp[sp["DS_SIT_TOT_TURNO"].isin(eleitos_status)]
    g = sp.groupby(["SQ_CANDIDATO", "NM_URNA_CANDIDATO", "SG_PARTIDO"])[
        "QT_VOTOS_NOMINAIS"
    ].sum().reset_index()
    g.columns = ["sq_candidato", "nome", "partido", "votos"]
    g["ano"] = ano
    return g


def main() -> None:
    print("=" * 75)
    print("VOTOS × FINANCIAMENTO — vereadores eleitos SP, 2012-2024")
    print("=" * 75)

    # Receitas
    rec = pd.read_parquet(CSV_REC)
    rec["sq_candidato"] = rec["sq_candidato"].astype(np.int64)
    rec_total = rec.groupby(["ano", "sq_candidato"])["valor"].sum().reset_index()
    rec_total.columns = ["ano", "sq_candidato", "receita_total"]

    # Votos por ano
    votos = pd.concat([carregar_votos(a) for a in ANOS], ignore_index=True)
    votos["sq_candidato"] = votos["sq_candidato"].astype(np.int64)
    print(f"\nEleitos por ano:")
    print(votos.groupby("ano")["sq_candidato"].nunique().to_string())

    # Merge
    df = votos.merge(rec_total, on=["ano", "sq_candidato"], how="left")
    df["receita_total"] = df["receita_total"].fillna(0)

    # Ajuste por inflação (valores em R$ de 2024)
    df["receita_2024"] = df.apply(
        lambda r: r["receita_total"] * INFLACAO.get(r["ano"], 1.0), axis=1
    )
    df["custo_por_voto"] = df["receita_2024"] / df["votos"].replace(0, np.nan)

    # Bloco
    df["bloco"] = df["partido"].map(
        lambda s: bloco_tripartite(ESCORE_BOLOGNESI[s])
        if s in ESCORE_BOLOGNESI else "DESCONHECIDO"
    )

    # Estatísticas por ano
    print(f"\n--- Resumo por ano (R$ corrigidos para 2024) ---")
    res = df.groupby("ano").agg(
        n_eleitos=("sq_candidato", "count"),
        votos_total=("votos", "sum"),
        receita_total=("receita_2024", "sum"),
        custo_med=("custo_por_voto", "median"),
    ).round(2)
    print(res.to_string())

    # Por bloco × ano
    print(f"\n--- Custo mediano por voto (R$ 2024) por bloco × ano ---")
    pivot = df.groupby(["ano", "bloco"])["custo_por_voto"].median().unstack().round(2)
    print(pivot.to_string())

    print(f"\n--- N eleitos por bloco × ano ---")
    pivot_n = df.groupby(["ano", "bloco"])["sq_candidato"].count().unstack(fill_value=0)
    print(pivot_n.to_string())

    print(f"\n--- Receita total por bloco × ano (R$ milhões 2024) ---")
    pivot_r = (df.groupby(["ano", "bloco"])["receita_2024"].sum() / 1e6).unstack().round(2)
    print(pivot_r.to_string())

    # Salvar
    SAIDA_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(SAIDA_CSV, index=False)
    print(f"\nCSV salvo: {SAIDA_CSV}")

    # ===== Visualização — 4 painéis =====
    fig, axes = plt.subplots(2, 2, figsize=(15, 11), dpi=120)
    cores_bloco = {"ESQUERDA": "#d62728", "CENTRO": "#7f7f7f",
                    "DIREITA": "#1f77b4", "DESCONHECIDO": "#cccccc"}

    # Painel 1: custo mediano por voto, por bloco × ano
    ax = axes[0, 0]
    for b in ["ESQUERDA", "CENTRO", "DIREITA"]:
        if b in pivot.columns:
            ax.plot(pivot.index, pivot[b], "o-", color=cores_bloco[b],
                     linewidth=2.5, markersize=10, label=b)
            for ano, val in pivot[b].items():
                if not np.isnan(val):
                    ax.annotate(f"R$ {val:.0f}",
                                xy=(ano, val), xytext=(0, 8),
                                textcoords="offset points", ha="center",
                                fontsize=8, color=cores_bloco[b],
                                fontweight="bold")
    ax.set_xticks(ANOS)
    ax.set_xlabel("Ano")
    ax.set_ylabel("Custo mediano por voto (R$ 2024)")
    ax.set_title("Trajetória do custo por voto, por bloco",
                  fontsize=11, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(alpha=0.3)

    # Painel 2: N de eleitos por bloco × ano
    ax = axes[0, 1]
    bot = np.zeros(len(ANOS))
    for b in ["ESQUERDA", "CENTRO", "DIREITA", "DESCONHECIDO"]:
        if b in pivot_n.columns:
            valores = pivot_n[b].reindex(ANOS, fill_value=0).values
            bars = ax.bar(ANOS, valores, bottom=bot, color=cores_bloco[b],
                           label=b, alpha=0.85, edgecolor="black", linewidth=0.4)
            for i, (bar, v) in enumerate(zip(bars, valores)):
                if v > 1:
                    ax.annotate(f"{int(v)}",
                                xy=(bar.get_x() + bar.get_width()/2,
                                    bot[i] + v/2),
                                ha="center", va="center",
                                fontsize=9, fontweight="bold", color="white")
            bot += valores
    ax.set_xticks(ANOS)
    ax.set_xlabel("Ano")
    ax.set_ylabel("N de eleitos a vereador SP")
    ax.set_title("Composição da Câmara SP, por bloco",
                  fontsize=11, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(axis="y", alpha=0.3)

    # Painel 3: receita total por bloco × ano (R$ milhões 2024)
    ax = axes[1, 0]
    bot = np.zeros(len(ANOS))
    for b in ["ESQUERDA", "CENTRO", "DIREITA", "DESCONHECIDO"]:
        if b in pivot_r.columns:
            valores = pivot_r[b].reindex(ANOS, fill_value=0).values
            bars = ax.bar(ANOS, valores, bottom=bot, color=cores_bloco[b],
                           label=b, alpha=0.85, edgecolor="black", linewidth=0.4)
            for i, (bar, v) in enumerate(zip(bars, valores)):
                if v > 2:
                    ax.annotate(f"{v:.0f}",
                                xy=(bar.get_x() + bar.get_width()/2,
                                    bot[i] + v/2),
                                ha="center", va="center",
                                fontsize=9, fontweight="bold", color="white")
            bot += valores
    ax.set_xticks(ANOS)
    ax.set_xlabel("Ano")
    ax.set_ylabel("Receita total dos eleitos (R$ milhões 2024)")
    ax.set_title("Receita total dos eleitos, por bloco",
                  fontsize=11, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(axis="y", alpha=0.3)

    # Painel 4: votos por R$ mil — eficiência por bloco × ano
    ax = axes[1, 1]
    df["eficiencia"] = df["votos"] / (df["receita_2024"] / 1000).replace(0, np.nan)
    pivot_e = df.groupby(["ano", "bloco"])["eficiencia"].median().unstack().round(2)
    for b in ["ESQUERDA", "CENTRO", "DIREITA"]:
        if b in pivot_e.columns:
            ax.plot(pivot_e.index, pivot_e[b], "o-", color=cores_bloco[b],
                     linewidth=2.5, markersize=10, label=b)
    ax.set_xticks(ANOS)
    ax.set_xlabel("Ano")
    ax.set_ylabel("Votos por R$ 1.000 (mediana)")
    ax.set_title("Eficiência de votos por R$ — maior = melhor",
                  fontsize=11, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(alpha=0.3)

    fig.suptitle(
        "Trajetória votos × financiamento — Vereadores eleitos SP, 2012-2024\n"
        f"N total: {len(df)} eleitos | R$ corrigidos pela inflação para 2024",
        fontsize=13, fontweight="bold",
    )
    fig.tight_layout()
    fig.savefig(SAIDA_FIG, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Figura salva: {SAIDA_FIG}")


if __name__ == "__main__":
    main()
