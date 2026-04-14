"""Trajetória temporal 2016-2024 das zonas ricas de SP.

Computa escore ideológico médio, NEP (Laakso-Taagepera), % esquerda e %
direita por ano para cada zona do corredor universitário. Gera gráfico
de séries temporais para cada métrica.

Anos disponíveis:
- 2016: municipal (prefeito + vereador)
- 2018: geral (deputados; não tem prefeito/vereador)
- 2020: municipal
- 2022: geral (deputados)
- 2024: municipal

Para a trajetória de vereador/prefeito, usamos 2016/2020/2024.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from analise_volatilidade import CODIGO_TSE_SAO_PAULO, normalizar_partido
from ideologia import ESCORE_BOLOGNESI, bloco_quintipartite

ZONAS_ALVO = {
    1: "Bela Vista",
    2: "Perdizes",
    3: "Santa Ifigênia",
    5: "Jardim Paulista",
    6: "Vila Mariana",
    251: "Pinheiros",
    258: "Indianópolis",
    346: "Butantã",
}

ANOS_MUNICIPAIS = [2016, 2020, 2024]
SAIDA_PNG = Path("outputs/trajetoria_zonas_ricas_2016_2024.png")
SAIDA_CSV = Path("outputs/trajetoria_zonas_ricas.csv")


def carregar(ano: int, cargo: str) -> pd.DataFrame:
    parquet = Path(f"data/processed/votacao_partido_munzona_{ano}_SP.parquet")
    df = pd.read_parquet(parquet)
    filtro = (
        (df["CD_MUNICIPIO"] == CODIGO_TSE_SAO_PAULO)
        & (df["DS_CARGO"].str.upper() == cargo.upper())
        & (df["NR_TURNO"] == 1)
        & (df["NR_ZONA"].isin(ZONAS_ALVO.keys()))
    )
    sub = df.loc[
        filtro,
        ["NR_ZONA", "SG_PARTIDO", "QT_VOTOS_NOMINAIS_VALIDOS", "QT_VOTOS_LEGENDA_VALIDOS"],
    ].copy()
    sub["VOTOS"] = sub["QT_VOTOS_NOMINAIS_VALIDOS"] + sub["QT_VOTOS_LEGENDA_VALIDOS"]
    sub["PARTIDO"] = sub["SG_PARTIDO"].map(normalizar_partido)
    return sub


def metricas(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for zona, nome in ZONAS_ALVO.items():
        votos = df[df["NR_ZONA"] == zona].groupby("PARTIDO")["VOTOS"].sum()
        if votos.empty or votos.sum() == 0:
            continue
        total = votos.sum()
        props = votos / total
        nep_val = 1.0 / (props ** 2).sum()

        escores = votos.index.map(ESCORE_BOLOGNESI.get)
        tab_esc = pd.DataFrame({"v": votos.values, "e": escores}).dropna()
        escore_medio = (
            (tab_esc["v"] * tab_esc["e"]).sum() / tab_esc["v"].sum()
            if tab_esc["v"].sum() > 0
            else float("nan")
        )

        blocos = votos.index.map(
            lambda p: bloco_quintipartite(ESCORE_BOLOGNESI[p])
            if p in ESCORE_BOLOGNESI
            else "DESCONHECIDO"
        )
        por_bloco = votos.groupby(blocos).sum() / total * 100
        pct_esq = por_bloco.get("ESQUERDA", 0) + por_bloco.get("CENTRO-ESQUERDA", 0)
        pct_dir = por_bloco.get("DIREITA", 0) + por_bloco.get("CENTRO-DIREITA", 0)

        rows.append(
            {
                "zona": zona,
                "nome": nome,
                "nep": nep_val,
                "escore_medio": escore_medio,
                "pct_esq": pct_esq,
                "pct_dir": pct_dir,
            }
        )
    return pd.DataFrame(rows)


# Coleta
linhas = []
for cargo in ["VEREADOR", "PREFEITO"]:
    for ano in ANOS_MUNICIPAIS:
        try:
            df = carregar(ano, cargo)
            tab = metricas(df)
            tab["ano"] = ano
            tab["cargo"] = cargo
            linhas.append(tab)
            print(f"{cargo} {ano}: {len(tab)} zonas")
        except FileNotFoundError as e:
            print(f"{cargo} {ano}: {e}")

todos = pd.concat(linhas, ignore_index=True)
todos.to_csv(SAIDA_CSV, index=False)
print(f"\nCSV salvo: {SAIDA_CSV}")

# Gráfico — 4 painéis (NEP, escore, %esq, %dir) × cargo
fig, axes = plt.subplots(2, 2, figsize=(16, 11))

cores = plt.cm.tab10(range(len(ZONAS_ALVO)))
zona_cor = dict(zip(ZONAS_ALVO.keys(), cores))

for col, cargo in enumerate(["VEREADOR", "PREFEITO"]):
    sub = todos[todos["cargo"] == cargo]
    ax_esc = axes[0, col]
    ax_pct = axes[1, col]
    for zona, nome in ZONAS_ALVO.items():
        z = sub[sub["zona"] == zona].sort_values("ano")
        if len(z) < 2:
            continue
        cor = zona_cor[zona]
        ax_esc.plot(z["ano"], z["escore_medio"], "o-", color=cor, label=f"Z{zona} {nome}")
        ax_pct.plot(z["ano"], z["pct_esq"], "o-", color=cor, label=f"Z{zona}")

    ax_esc.axhline(y=5.0, color="gray", linestyle="--", linewidth=0.8)
    ax_esc.set_title(f"{cargo} — Escore ideológico médio (2016–2024)")
    ax_esc.set_ylabel("Escore (0=extrema-esq, 10=extrema-dir)")
    ax_esc.set_xticks(ANOS_MUNICIPAIS)
    ax_esc.grid(alpha=0.3)
    if col == 1:
        ax_esc.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=8)

    ax_pct.set_title(f"{cargo} — % votos esquerda+centro-esquerda (2016–2024)")
    ax_pct.set_ylabel("% votos")
    ax_pct.set_xlabel("Ano")
    ax_pct.set_xticks(ANOS_MUNICIPAIS)
    ax_pct.grid(alpha=0.3)

fig.suptitle(
    "Trajetória das zonas ricas de SP — corredor universitário (2016 → 2024)",
    fontsize=14,
)
plt.tight_layout()
SAIDA_PNG.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(SAIDA_PNG, dpi=150, bbox_inches="tight")
print(f"Gráfico salvo: {SAIDA_PNG}")

# Resumo textual
print("\n\n" + "=" * 80)
print(" RESUMO ESCORE IDEOLÓGICO — ZONAS RICAS (2016 → 2024)")
print("=" * 80)
for cargo in ["VEREADOR", "PREFEITO"]:
    print(f"\n{cargo}:")
    piv = todos[todos["cargo"] == cargo].pivot(
        index=["zona", "nome"], columns="ano", values="escore_medio"
    )
    piv.columns = [str(c) for c in piv.columns]
    if "2016" in piv.columns and "2024" in piv.columns:
        piv["Δ 2016→2024"] = piv["2024"] - piv["2016"]
    print(piv.round(3).to_string())
