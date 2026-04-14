"""SJBV — bloco dominante por seção eleitoral, 2020 vs 2024.

Usa votacao_secao (granular por seção). Deriva partido a partir dos
2 primeiros dígitos de NR_VOTAVEL e aplica a classificação quintipartite
de Bolognesi et al. (2023).
"""

from pathlib import Path

import geopandas as gpd
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pandas as pd

from analise_volatilidade import normalizar_partido
from ideologia import bloco_quintipartite, ESCORE_BOLOGNESI

# Mapa NR_PARTIDO → sigla (construído em runtime)
MAPA_PARTIDO: dict[int, str] = {}
for ano in [2020, 2024]:
    df_ref = pd.read_parquet(f"data/processed/votacao_partido_munzona_{ano}_SP.parquet")
    for _, row in df_ref[["NR_PARTIDO", "SG_PARTIDO"]].drop_duplicates().iterrows():
        MAPA_PARTIDO[int(row["NR_PARTIDO"])] = row["SG_PARTIDO"]

SHAPEFILE = Path("data/raw/shapes/EL2022_LV_ESP_CEM_V2/EL2022_LV_ESP_CEM_V2.shp")
SAIDA = Path("outputs/mapa_blocos_sjbv_secao_2020_2024.png")

ORDEM = ["ESQUERDA", "CENTRO-ESQUERDA", "CENTRO", "CENTRO-DIREITA", "DIREITA", "DESCONHECIDO"]
CORES = {
    "ESQUERDA": "#b2182b",
    "CENTRO-ESQUERDA": "#ef8a62",
    "CENTRO": "#f7f7f7",
    "CENTRO-DIREITA": "#67a9cf",
    "DIREITA": "#2166ac",
    "DESCONHECIDO": "#cccccc",
}


def carregar_sjbv_secao(ano: int) -> pd.DataFrame:
    if ano == 2020:
        df = pd.read_parquet("data/processed/votacao_secao_2020_SP.parquet")
        df = df[df["NM_MUNICIPIO"] == "SÃO JOÃO DA BOA VISTA"].copy()
    else:
        df = pd.read_parquet("data/processed/votacao_secao_2024_SJBV.parquet")
    df = df[df["NR_TURNO"] == 1].copy()
    # Deriva NR_PARTIDO dos 2 primeiros dígitos de NR_VOTAVEL.
    # Votos 95/96/97 e similares são brancos/nulos — descartar.
    df["NR_VOTAVEL"] = pd.to_numeric(df["NR_VOTAVEL"], errors="coerce")
    df = df.dropna(subset=["NR_VOTAVEL"])
    df["NR_PARTIDO"] = (df["NR_VOTAVEL"].astype(int) // 1000).replace(0, None)
    # Para prefeito, NR_VOTAVEL já é o número do partido (dois dígitos)
    cargo_prefeito = df["DS_CARGO"].str.upper() == "PREFEITO"
    df.loc[cargo_prefeito, "NR_PARTIDO"] = df.loc[cargo_prefeito, "NR_VOTAVEL"].astype(int)
    df["NR_PARTIDO"] = df["NR_PARTIDO"].astype("Int64")
    df["SG_PARTIDO"] = df["NR_PARTIDO"].map(MAPA_PARTIDO)
    df = df.dropna(subset=["SG_PARTIDO"])
    df["PARTIDO"] = df["SG_PARTIDO"].map(normalizar_partido)
    df["BLOCO"] = df["PARTIDO"].map(
        lambda p: bloco_quintipartite(ESCORE_BOLOGNESI[p]) if p in ESCORE_BOLOGNESI else "DESCONHECIDO"
    )
    return df


def bloco_dominante_por_secao(df: pd.DataFrame, cargo: str) -> pd.Series:
    sub = df[df["DS_CARGO"].str.upper() == cargo.upper()]
    votos = sub.groupby(["NR_SECAO", "BLOCO"])["QT_VOTOS"].sum().unstack(fill_value=0)
    return votos.idxmax(axis=1)


def resumo(dom_2020: pd.Series, dom_2024: pd.Series, cargo: str):
    print(f"\n== {cargo} ==")
    print(f"  Seções 2020: {len(dom_2020)} | 2024: {len(dom_2024)}")
    for ano, dom in [(2020, dom_2020), (2024, dom_2024)]:
        cont = dom.value_counts().reindex(ORDEM, fill_value=0)
        print(f"  {ano}: " + ", ".join(f"{b}={n}" for b, n in cont.items() if n > 0))

    secoes_comuns = dom_2020.index.intersection(dom_2024.index)
    tab = pd.DataFrame({"2020": dom_2020.loc[secoes_comuns], "2024": dom_2024.loc[secoes_comuns]})
    print(f"\n  Seções presentes nos dois anos: {len(secoes_comuns)}")
    mudou = (tab["2020"] != tab["2024"]).sum()
    print(f"  Mudaram de bloco: {mudou} ({mudou/len(secoes_comuns)*100:.1f}%)")
    cruzada = pd.crosstab(tab["2020"], tab["2024"])
    print("\n  Transição 2020 (linhas) → 2024 (colunas):")
    print(cruzada.to_string())


df_2020 = carregar_sjbv_secao(2020)
df_2024 = carregar_sjbv_secao(2024)
print(f"SJBV: {df_2020.NR_SECAO.nunique()} seções em 2020, {df_2024.NR_SECAO.nunique()} em 2024")

for cargo in ["PREFEITO", "VEREADOR"]:
    dom_2020 = bloco_dominante_por_secao(df_2020, cargo)
    dom_2024 = bloco_dominante_por_secao(df_2024, cargo)
    resumo(dom_2020, dom_2024, cargo)

# Mapa por local de votação (agregando seções) — prefeito
def bloco_por_local(df: pd.DataFrame, cargo: str) -> pd.Series:
    sub = df[df["DS_CARGO"].str.upper() == cargo.upper()]
    votos = sub.groupby(["NR_LOCAL_VOTACAO", "BLOCO"])["QT_VOTOS"].sum().unstack(fill_value=0)
    return votos.idxmax(axis=1)


local_2020_pref = bloco_por_local(df_2020, "PREFEITO")
local_2024_pref = bloco_por_local(df_2024, "PREFEITO")
local_2020_ver = bloco_por_local(df_2020, "VEREADOR")
local_2024_ver = bloco_por_local(df_2024, "VEREADOR")

gdf = gpd.read_file(SHAPEFILE)
sj = gdf[gdf["MUN_NOME"] == "SAO JOAO DA BOA VISTA"].copy()
print(f"\nLocais no shapefile: {len(sj)}")

# Fuzzy match de NOME_LV (shapefile) ↔ NR_LOCAL_VOTACAO (via NM_LOCAL_VOTACAO)
import unicodedata
import re


def normalizar_nome(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = unicodedata.normalize("NFKD", s).encode("ASCII", "ignore").decode()
    s = re.sub(r"[^A-Z ]", " ", s.upper())
    return re.sub(r"\s+", " ", s).strip()


nomes_votacao = df_2020[["NR_LOCAL_VOTACAO", "NM_LOCAL_VOTACAO"]].drop_duplicates()
nomes_votacao["nome_norm"] = nomes_votacao["NM_LOCAL_VOTACAO"].map(normalizar_nome)
sj["nome_norm"] = sj["NOME_LV"].map(normalizar_nome)


def casa_local(nome_shape: str) -> int | None:
    tokens = set(nome_shape.split())
    melhor = None
    melhor_score = 0
    for _, row in nomes_votacao.iterrows():
        score = len(tokens & set(row["nome_norm"].split()))
        if score > melhor_score:
            melhor_score = score
            melhor = int(row["NR_LOCAL_VOTACAO"])
    return melhor if melhor_score >= 1 else None


sj["NR_LOCAL_VOTACAO"] = sj["nome_norm"].map(casa_local)
casados = sj["NR_LOCAL_VOTACAO"].notna().sum()
print(f"Locais casados por nome: {casados}/{len(sj)}")


def plot_painel(ax, dom: pd.Series, ano: int, titulo: str):
    sj_merged = sj.merge(dom.rename("bloco"), left_on="NR_LOCAL_VOTACAO", right_index=True, how="left")
    sj_merged["bloco"] = sj_merged["bloco"].fillna("DESCONHECIDO")
    for bloco in ORDEM:
        sub = sj_merged[sj_merged["bloco"] == bloco]
        if sub.empty:
            continue
        sub.plot(ax=ax, color=CORES[bloco], markersize=60, alpha=0.9, edgecolor="black", linewidth=0.3)
    for _, row in sj_merged.iterrows():
        ax.annotate(
            str(row["NOME_LV"])[:20],
            xy=(row.geometry.x, row.geometry.y),
            xytext=(4, 2),
            textcoords="offset points",
            fontsize=5,
            color="black",
            bbox=dict(boxstyle="round,pad=0.15", facecolor="white", edgecolor="none", alpha=0.7),
        )
    ax.set_title(f"{titulo} — {ano}", fontsize=11)
    ax.set_axis_off()


fig, axes = plt.subplots(2, 2, figsize=(16, 14))
plot_painel(axes[0, 0], local_2020_pref, 2020, "Prefeito — bloco dominante por local")
plot_painel(axes[0, 1], local_2024_pref, 2024, "Prefeito — bloco dominante por local")
plot_painel(axes[1, 0], local_2020_ver, 2020, "Vereador — bloco dominante por local")
plot_painel(axes[1, 1], local_2024_ver, 2024, "Vereador — bloco dominante por local")
presentes = set()
for d in [local_2020_pref, local_2024_pref, local_2020_ver, local_2024_ver]:
    presentes.update(d.unique())
legenda = [mpatches.Patch(color=CORES[b], label=b) for b in ORDEM if b in presentes]
fig.legend(handles=legenda, loc="lower center", ncol=len(legenda), frameon=False, bbox_to_anchor=(0.5, 0.02))
fig.suptitle(
    "São João da Boa Vista — bloco ideológico dominante por local de votação\n"
    "Classificação quintipartite (Bolognesi, Ribeiro & Codato 2023)",
    fontsize=13,
)
SAIDA.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(SAIDA, dpi=150, bbox_inches="tight")
print(f"\nMapa salvo: {SAIDA}")
