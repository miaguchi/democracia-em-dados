"""Votos × financiamento dos eleitos — todos os cargos disponíveis em SP.

Cargos × anos cobertos:
  Vereador     (SP capital):     2012, 2016, 2020, 2024
  Prefeito     (SP capital):     2012, 2016, 2020, 2024
  Dep. Estadual (estado de SP):  2018, 2022
  Dep. Federal  (estado de SP):  2018, 2022
  Senador       (estado de SP):  2018, 2022
  Governador    (estado de SP):  2018, 2022

Presidente fica de fora — não há receitas filtradas por SP no FTP
(é cargo nacional, fica no arquivo BR).

Para cada caso, cruza receitas declaradas × votos do eleito.
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

SAIDA_CSV = _ROOT / "outputs/tables/votos_vs_financiamento_todos_cargos.csv"
SAIDA_FIG = _ROOT / "outputs/figures/votos_vs_financiamento_todos_cargos.png"

INFLACAO = {2012: 2.07, 2016: 1.52, 2018: 1.42, 2020: 1.28, 2022: 1.13, 2024: 1.00}

# (cargo, ano, escopo) — escopo: "SP_CAPITAL" (cd_municipio==71072) ou "SP_ESTADO"
ANALISES = [
    ("Vereador",      2012, "SP_CAPITAL"),
    ("Vereador",      2016, "SP_CAPITAL"),
    ("Vereador",      2020, "SP_CAPITAL"),
    ("Vereador",      2024, "SP_CAPITAL"),
    ("Prefeito",      2012, "SP_CAPITAL"),
    ("Prefeito",      2016, "SP_CAPITAL"),
    ("Prefeito",      2020, "SP_CAPITAL"),
    ("Prefeito",      2024, "SP_CAPITAL"),
    ("Deputado Estadual", 2018, "SP_ESTADO"),
    ("Deputado Estadual", 2022, "SP_ESTADO"),
    ("Deputado Federal",  2018, "SP_ESTADO"),
    ("Deputado Federal",  2022, "SP_ESTADO"),
    ("Senador",          2018, "SP_ESTADO"),
    ("Senador",          2022, "SP_ESTADO"),
    ("Governador",       2018, "SP_ESTADO"),
    ("Governador",       2022, "SP_ESTADO"),
]


def carregar_votos_eleitos(cargo: str, ano: int, escopo: str) -> pd.DataFrame:
    """Votos por candidato eleito para um cargo/ano.

    Para prefeito/governador/presidente, considera 2T se foi para
    segundo turno, somando votos de 1T+2T do vencedor.
    """
    f = _ROOT / f"data/processed/votacao_candidato_munzona_{ano}_SP.parquet"
    df = pd.read_parquet(f)
    sub_all = df[df["DS_CARGO"] == cargo].copy()
    if escopo == "SP_CAPITAL":
        sub_all = sub_all[sub_all["NM_MUNICIPIO"] == "SÃO PAULO"]

    # Quem foi eleito? Pode aparecer com "ELEITO" no 1T ou no 2T
    eleitos_2t = sub_all[
        (sub_all["NR_TURNO"] == 2) & (sub_all["DS_SIT_TOT_TURNO"] == "ELEITO")
    ]
    eleitos_1t = sub_all[
        (sub_all["NR_TURNO"] == 1) &
        (sub_all["DS_SIT_TOT_TURNO"].isin(["ELEITO POR QP", "ELEITO POR MÉDIA", "ELEITO"]))
    ]

    sqs_2t = set(eleitos_2t["SQ_CANDIDATO"].unique())
    sqs_1t = set(eleitos_1t["SQ_CANDIDATO"].unique())
    sqs_eleitos = sqs_2t | sqs_1t

    if not sqs_eleitos:
        return pd.DataFrame(columns=["sq_candidato", "nome", "partido", "situacao", "votos"])

    # Para cada eleito, somar votos do 1T (votos pessoais)
    sub_1t = sub_all[(sub_all["SQ_CANDIDATO"].isin(sqs_eleitos)) &
                     (sub_all["NR_TURNO"] == 1)]
    g = sub_1t.groupby(
        ["SQ_CANDIDATO", "NM_URNA_CANDIDATO", "SG_PARTIDO"]
    )["QT_VOTOS_NOMINAIS"].sum().reset_index()
    g.columns = ["sq_candidato", "nome", "partido", "votos"]
    g["situacao"] = g["sq_candidato"].apply(
        lambda x: "ELEITO 2T" if x in sqs_2t else "ELEITO 1T"
    )
    return g[["sq_candidato", "nome", "partido", "situacao", "votos"]]


PARQUET_VEREADOR = _ROOT / "data/processed/receitas_vereador_sp_2012_2024.parquet"


def carregar_receitas(cargo: str, ano: int) -> pd.DataFrame:
    """Receitas totais por candidato em SP para um cargo/ano.

    Para vereador, usa o parquet consolidado (cobre 2012-2024).
    Para demais cargos, lê o CSV moderno (apenas 2020+, 2024 e federal).
    """
    if cargo == "Vereador":
        rec = pd.read_parquet(PARQUET_VEREADOR)
        sub = rec[rec["ano"] == ano]
        g = sub.groupby("sq_candidato")["valor"].sum().reset_index()
        g.columns = ["sq_candidato", "receita_total"]
        return g

    f = _ROOT / f"data/raw/prestacao_contas/{ano}_SP/receitas_candidatos_{ano}_SP.csv"
    if not f.exists():
        return pd.DataFrame(columns=["sq_candidato", "receita_total"])
    df = pd.read_csv(f, sep=";", encoding="latin-1", low_memory=False,
                      usecols=["SQ_CANDIDATO", "DS_CARGO", "VR_RECEITA"])
    df["VR_RECEITA"] = pd.to_numeric(
        df["VR_RECEITA"].astype(str).str.replace(",", ".").str.replace("#NULO", "0"),
        errors="coerce",
    ).fillna(0.0)
    sub = df[df["DS_CARGO"] == cargo]
    g = sub.groupby("SQ_CANDIDATO")["VR_RECEITA"].sum().reset_index()
    g.columns = ["sq_candidato", "receita_total"]
    return g


def analisar(cargo: str, ano: int, escopo: str) -> pd.DataFrame:
    """Cruza votos e receitas para os eleitos."""
    votos = carregar_votos_eleitos(cargo, ano, escopo)
    rec = carregar_receitas(cargo, ano)
    votos["sq_candidato"] = votos["sq_candidato"].astype(np.int64)
    rec["sq_candidato"] = rec["sq_candidato"].astype(np.int64)
    df = votos.merge(rec, on="sq_candidato", how="left")
    df["receita_total"] = df["receita_total"].fillna(0)
    df["receita_2024"] = df["receita_total"] * INFLACAO.get(ano, 1.0)
    df["custo_por_voto"] = df["receita_2024"] / df["votos"].replace(0, np.nan)
    df["bloco"] = df["partido"].map(
        lambda s: bloco_tripartite(ESCORE_BOLOGNESI[s])
        if s in ESCORE_BOLOGNESI else "DESCONHECIDO"
    )
    df["cargo"] = cargo
    df["ano"] = ano
    df["escopo"] = escopo
    return df


def main() -> None:
    print("=" * 80)
    print("VOTOS × FINANCIAMENTO — todos os cargos (SP)")
    print("=" * 80)

    todos = []
    for cargo, ano, escopo in ANALISES:
        df = analisar(cargo, ano, escopo)
        if len(df) == 0:
            continue
        todos.append(df)
        print(f"  {cargo:<20} {ano} ({escopo}): {len(df)} eleitos, "
              f"R$ {df['receita_2024'].sum()/1e6:>6.1f}M, "
              f"custo med R$ {df['custo_por_voto'].median():>6.2f}/voto")

    big = pd.concat(todos, ignore_index=True)
    SAIDA_CSV.parent.mkdir(parents=True, exist_ok=True)
    big.to_csv(SAIDA_CSV, index=False)
    print(f"\nCSV salvo: {SAIDA_CSV}")

    # Resumo agregado por cargo × ano
    print(f"\n--- Custo mediano por voto (R$ 2024) por cargo × ano ---")
    pivot = big.groupby(["cargo", "ano"])["custo_por_voto"].median().unstack().round(2)
    print(pivot.to_string())

    print(f"\n--- N eleitos por cargo × ano ---")
    print(big.groupby(["cargo", "ano"])["sq_candidato"].count().unstack(fill_value=0).to_string())

    print(f"\n--- Receita média por eleito (R$ milhões 2024) por cargo × ano ---")
    pivot_r = (big.groupby(["cargo", "ano"])["receita_2024"].mean() / 1e6).unstack().round(2)
    print(pivot_r.to_string())

    # Custo mediano por voto, por cargo × bloco (todos os anos juntos)
    print(f"\n--- Custo mediano por voto (R$ 2024) por cargo × bloco ---")
    pb = big.groupby(["cargo", "bloco"])["custo_por_voto"].median().unstack().round(2)
    print(pb.to_string())

    # ===== Visualização =====
    fig, axes = plt.subplots(2, 2, figsize=(16, 11), dpi=120)
    cores_bloco = {"ESQUERDA": "#d62728", "CENTRO": "#7f7f7f",
                    "DIREITA": "#1f77b4", "DESCONHECIDO": "#cccccc"}

    # Painel 1: custo mediano por voto, cargo × ano (heatmap)
    ax = axes[0, 0]
    cargos_ord = ["Vereador", "Prefeito", "Deputado Estadual",
                   "Deputado Federal", "Senador", "Governador"]
    pivot = pivot.reindex(cargos_ord).astype(float)
    im = ax.imshow(pivot.values, cmap="YlOrRd", aspect="auto")
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            v = pivot.iat[i, j]
            if not np.isnan(v):
                ax.text(j, i, f"{v:.0f}", ha="center", va="center",
                        fontsize=9, fontweight="bold",
                        color="white" if v > 50 else "black")
    ax.set_xticks(range(pivot.shape[1]))
    ax.set_xticklabels(pivot.columns)
    ax.set_yticks(range(pivot.shape[0]))
    ax.set_yticklabels(pivot.index)
    fig.colorbar(im, ax=ax, label="R$/voto (mediana)")
    ax.set_title("Custo mediano por voto (R$ 2024)\npor cargo × ano",
                  fontsize=11, fontweight="bold")

    # Painel 2: receita média por eleito (R$M)
    ax = axes[0, 1]
    pivot_r = pivot_r.reindex(cargos_ord).astype(float)
    im = ax.imshow(pivot_r.values, cmap="Blues", aspect="auto")
    for i in range(pivot_r.shape[0]):
        for j in range(pivot_r.shape[1]):
            v = pivot_r.iat[i, j]
            if not np.isnan(v):
                ax.text(j, i, f"{v:.1f}", ha="center", va="center",
                        fontsize=9, fontweight="bold",
                        color="white" if v > pivot_r.max().max()/2 else "black")
    ax.set_xticks(range(pivot_r.shape[1]))
    ax.set_xticklabels(pivot_r.columns)
    ax.set_yticks(range(pivot_r.shape[0]))
    ax.set_yticklabels(pivot_r.index)
    fig.colorbar(im, ax=ax, label="R$ milhões 2024")
    ax.set_title("Receita média por eleito\npor cargo × ano",
                  fontsize=11, fontweight="bold")

    # Painel 3: barras custo mediano por bloco × cargo (todos anos)
    ax = axes[1, 0]
    pb = pb.reindex(cargos_ord)
    x = np.arange(len(pb.index))
    w = 0.27
    for i, b in enumerate(["ESQUERDA", "CENTRO", "DIREITA"]):
        if b in pb.columns:
            valores = pb[b].values
            ax.bar(x + (i - 1) * w, valores, w, color=cores_bloco[b],
                    alpha=0.85, edgecolor="black", linewidth=0.4, label=b)
    ax.set_xticks(x)
    ax.set_xticklabels(pb.index, rotation=15, ha="right")
    ax.set_ylabel("Custo mediano por voto (R$ 2024)")
    ax.set_title("Custo por voto, por cargo × bloco",
                  fontsize=11, fontweight="bold")
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.3)

    # Painel 4: scatter votos × receita, log-log, todos os cargos juntos
    ax = axes[1, 1]
    cores_cargo = {
        "Vereador": "#1f77b4", "Prefeito": "#ff7f0e",
        "Deputado Estadual": "#2ca02c", "Deputado Federal": "#d62728",
        "Senador": "#9467bd", "Governador": "#8c564b",
    }
    for c in cargos_ord:
        sub = big[big["cargo"] == c]
        if sub.empty: continue
        ax.scatter(sub["receita_2024"]/1000, sub["votos"],
                   c=cores_cargo[c], s=40, alpha=0.5,
                   edgecolor="black", linewidth=0.2, label=c)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("Receita declarada (R$ mil 2024)")
    ax.set_ylabel("Votos do eleito")
    ax.set_title("Votos × receita — todos os cargos\n(log-log)",
                  fontsize=11, fontweight="bold")
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(alpha=0.3, which="both")

    fig.suptitle(
        "Votos × Financiamento — Eleitos em SP, todos os cargos\n"
        f"N total: {len(big)} eleitos | R$ corrigidos para 2024",
        fontsize=13, fontweight="bold",
    )
    fig.tight_layout()
    fig.savefig(SAIDA_FIG, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"\nFigura salva: {SAIDA_FIG}")


if __name__ == "__main__":
    main()
