"""Relação votos × financiamento dos vereadores eleitos em SP capital, 2024.

Cruza a base de candidatos a vereador (com situação de eleição) com
a base de receitas de campanha. Para cada candidato eleito, calcula:
- Total de votos nominais
- Total de receitas declaradas
- Custo por voto (R$/voto)
- Eficiência (votos por R$ mil)

Compara por partido e por bloco ideológico (Bolognesi).
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

CSV_CAND = _ROOT / "data/processed/votacao_candidato_munzona_2024_SP.parquet"
CSV_REC = _ROOT / "data/processed/receitas_vereador_sp_2024.parquet"
SAIDA_CSV = _ROOT / "outputs/tables/votos_vs_financiamento_eleitos_2024.csv"
SAIDA_FIG = _ROOT / "outputs/figures/votos_vs_financiamento_eleitos_2024.png"


def main() -> None:
    print("=" * 75)
    print("VOTOS × FINANCIAMENTO — vereadores eleitos SP capital 2024")
    print("=" * 75)

    # Candidatos
    cand = pd.read_parquet(CSV_CAND)
    sp = cand[(cand["NM_MUNICIPIO"] == "SÃO PAULO")
              & (cand["DS_CARGO"] == "Vereador")
              & (cand["NR_TURNO"] == 1)].copy()

    # Votos por candidato (somando todas as zonas)
    votos = sp.groupby(
        ["SQ_CANDIDATO", "NM_URNA_CANDIDATO", "SG_PARTIDO", "NR_PARTIDO",
         "DS_SIT_TOT_TURNO"]
    )["QT_VOTOS_NOMINAIS"].sum().reset_index()
    votos = votos.rename(columns={"QT_VOTOS_NOMINAIS": "votos"})
    print(f"\nCandidatos a vereador SP capital: {len(votos)}")

    # Filtrar eleitos
    eleitos = votos[votos["DS_SIT_TOT_TURNO"].isin(
        ["ELEITO POR QP", "ELEITO POR MÉDIA"]
    )].copy()
    print(f"Eleitos (QP + MÉDIA): {len(eleitos)}")

    # Receitas por candidato
    rec = pd.read_parquet(CSV_REC)
    receitas = rec.groupby("SQ_CANDIDATO")["VR_RECEITA"].sum().reset_index()
    receitas = receitas.rename(columns={"VR_RECEITA": "receita_total"})
    print(f"Candidatos com receita declarada: {len(receitas)}")

    # Merge
    df = eleitos.merge(receitas, on="SQ_CANDIDATO", how="left")
    df["receita_total"] = df["receita_total"].fillna(0)
    df["custo_por_voto"] = df["receita_total"] / df["votos"].replace(0, np.nan)
    df["votos_por_milreal"] = df["votos"] / (df["receita_total"] / 1000).replace(0, np.nan)

    # Bloco ideológico
    df["bloco"] = df["SG_PARTIDO"].map(
        lambda s: bloco_tripartite(ESCORE_BOLOGNESI[s])
        if s in ESCORE_BOLOGNESI else "DESCONHECIDO"
    )

    # Estatísticas agregadas
    print(f"\n--- Resumo dos {len(df)} eleitos ---")
    print(f"  Votos totais:              {df['votos'].sum():>12,.0f}")
    print(f"  Receita total declarada:   R$ {df['receita_total'].sum():>14,.2f}")
    print(f"  Custo médio por voto:      R$ {df['custo_por_voto'].mean():>9,.2f}")
    print(f"  Custo mediano por voto:    R$ {df['custo_por_voto'].median():>9,.2f}")
    print(f"  Votos médios por R$ 1.000: {df['votos_por_milreal'].mean():>9,.2f}")

    print(f"\n--- Por bloco ideológico ---")
    by_bloco = df.groupby("bloco").agg(
        n=("SQ_CANDIDATO", "count"),
        votos_med=("votos", "mean"),
        votos_med_str=("votos", lambda x: f"{x.mean():,.0f}"),
        receita_med=("receita_total", "mean"),
        custo_med=("custo_por_voto", "mean"),
        custo_mediano=("custo_por_voto", "median"),
    ).round(2)
    print(by_bloco[["n", "votos_med", "receita_med",
                    "custo_med", "custo_mediano"]].to_string())

    print(f"\n--- Top 10 partidos por número de eleitos ---")
    top_p = df.groupby("SG_PARTIDO").agg(
        n=("SQ_CANDIDATO", "count"),
        votos_total=("votos", "sum"),
        receita_total=("receita_total", "sum"),
        custo_med=("custo_por_voto", "mean"),
    ).round(2).sort_values("n", ascending=False).head(10)
    print(top_p.to_string())

    print(f"\n--- Top 10 vereadores mais votados ---")
    top_v = df.nlargest(10, "votos")[["NM_URNA_CANDIDATO", "SG_PARTIDO",
                                       "votos", "receita_total", "custo_por_voto"]]
    print(top_v.to_string(index=False, float_format=lambda x: f"{x:,.0f}"))

    print(f"\n--- 10 eleitos com MENOR custo por voto ---")
    bot_v = df[df["custo_por_voto"] > 0].nsmallest(
        10, "custo_por_voto"
    )[["NM_URNA_CANDIDATO", "SG_PARTIDO", "votos",
       "receita_total", "custo_por_voto", "bloco"]]
    print(bot_v.to_string(index=False, float_format=lambda x: f"{x:,.2f}"))

    print(f"\n--- 10 eleitos com MAIOR custo por voto ---")
    high_v = df[df["custo_por_voto"] > 0].nlargest(
        10, "custo_por_voto"
    )[["NM_URNA_CANDIDATO", "SG_PARTIDO", "votos",
       "receita_total", "custo_por_voto", "bloco"]]
    print(high_v.to_string(index=False, float_format=lambda x: f"{x:,.2f}"))

    # Salvar
    SAIDA_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.sort_values("votos", ascending=False).to_csv(SAIDA_CSV, index=False)
    print(f"\nCSV salvo: {SAIDA_CSV}")

    # === Visualização — 4 painéis ===
    fig, axes = plt.subplots(2, 2, figsize=(15, 11), dpi=120)
    cores_bloco = {"ESQUERDA": "#d62728", "CENTRO": "#7f7f7f",
                    "DIREITA": "#1f77b4", "DESCONHECIDO": "#cccccc"}

    # Painel 1: scatter votos × receita (colorido por bloco)
    ax = axes[0, 0]
    for b, c in cores_bloco.items():
        sub = df[df["bloco"] == b]
        if sub.empty:
            continue
        ax.scatter(sub["receita_total"] / 1000, sub["votos"],
                   c=c, s=60, alpha=0.7, edgecolor="black",
                   linewidth=0.3, label=f"{b} (n={len(sub)})")

    # Anotar top 5 mais votados
    for _, r in df.nlargest(5, "votos").iterrows():
        ax.annotate(
            r["NM_URNA_CANDIDATO"][:18],
            xy=(r["receita_total"] / 1000, r["votos"]),
            fontsize=7, ha="center", va="bottom",
            xytext=(0, 5), textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                      edgecolor="gray", alpha=0.9),
        )
    ax.set_xlabel("Receita declarada (R$ mil)")
    ax.set_ylabel("Votos nominais")
    ax.set_title("Votos × Receita — vereadores eleitos SP 2024",
                  fontsize=11, fontweight="bold")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3, which="both")

    # Painel 2: boxplot custo/voto por bloco
    ax = axes[0, 1]
    blocos_ord = ["ESQUERDA", "CENTRO", "DIREITA"]
    dados = [df[df["bloco"] == b]["custo_por_voto"].dropna().values
             for b in blocos_ord]
    bp = ax.boxplot(dados, labels=blocos_ord, patch_artist=True,
                     showfliers=True,
                     medianprops=dict(color="black", linewidth=2))
    for patch, b in zip(bp["boxes"], blocos_ord):
        patch.set_facecolor(cores_bloco[b])
        patch.set_alpha(0.7)
    ax.set_ylabel("Custo por voto (R$)")
    ax.set_title("Custo por voto por bloco ideológico",
                  fontsize=11, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)

    # Painel 3: barras por partido — receita/eleito médio
    ax = axes[1, 0]
    p = df.groupby("SG_PARTIDO").agg(
        n=("SQ_CANDIDATO", "count"),
        receita_med=("receita_total", "mean"),
    ).sort_values("n", ascending=False).head(15)
    bars = ax.barh(p.index[::-1], p["receita_med"][::-1] / 1000,
                    color=[cores_bloco.get(
                        bloco_tripartite(ESCORE_BOLOGNESI.get(s, 5.0)),
                        "#cccccc") for s in p.index[::-1]],
                    edgecolor="black", linewidth=0.4, alpha=0.85)
    for bar, n in zip(bars, p["n"][::-1]):
        ax.annotate(f"n={n}", xy=(bar.get_width(), bar.get_y() + bar.get_height()/2),
                    xytext=(3, 0), textcoords="offset points",
                    fontsize=7, va="center")
    ax.set_xlabel("Receita média por eleito (R$ mil)")
    ax.set_title("Receita média por eleito (top 15 partidos)",
                  fontsize=11, fontweight="bold")
    ax.grid(axis="x", alpha=0.3)

    # Painel 4: barras eficiência (votos por R$ mil) por partido
    ax = axes[1, 1]
    e = df.groupby("SG_PARTIDO").agg(
        n=("SQ_CANDIDATO", "count"),
        votos_p_real=("votos_por_milreal", "median"),
    ).sort_values("votos_p_real", ascending=True).tail(15)
    bars = ax.barh(e.index, e["votos_p_real"],
                    color=[cores_bloco.get(
                        bloco_tripartite(ESCORE_BOLOGNESI.get(s, 5.0)),
                        "#cccccc") for s in e.index],
                    edgecolor="black", linewidth=0.4, alpha=0.85)
    for bar, n in zip(bars, e["n"]):
        ax.annotate(f"n={n}", xy=(bar.get_width(), bar.get_y() + bar.get_height()/2),
                    xytext=(3, 0), textcoords="offset points",
                    fontsize=7, va="center")
    ax.set_xlabel("Votos por R$ 1.000 (mediana — maior = mais eficiente)")
    ax.set_title("Eficiência mediana de votos por R$ — top 15",
                  fontsize=11, fontweight="bold")
    ax.grid(axis="x", alpha=0.3)

    fig.suptitle(
        "Votos × Financiamento — Vereadores eleitos SP capital, 2024 (1T)\n"
        f"N={len(df)} eleitos — Receita total: R$ {df['receita_total'].sum()/1e6:.1f}M",
        fontsize=13, fontweight="bold",
    )
    fig.tight_layout()
    fig.savefig(SAIDA_FIG, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Figura salva: {SAIDA_FIG}")


if __name__ == "__main__":
    main()
