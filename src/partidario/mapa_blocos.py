"""Mapa do bloco ideológico dominante por zona eleitoral — SP vereador.

Para cada zona, calcula a proporção de votos por bloco ideológico
(classificação quintipartite de Bolognesi et al. 2023) e classifica a
zona pelo bloco de plurality. Dois painéis lado a lado: 2020 e 2024.
"""

from pathlib import Path

import geopandas as gpd
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

from src.partidario.analise_volatilidade import carregar_sp_vereador, carregar_sp_prefeito
from src.partidario.ideologia import classificar, usar_quintipartite

usar_quintipartite()

SHAPEFILE = Path("data/raw/shapes/EL2022_LV_ESP_CEM_V2/EL2022_LV_ESP_CEM_V2.shp")
SAIDA_VEREADOR = Path("outputs/mapa_blocos_vereador_2020_2024.png")
SAIDA_PREFEITO = Path("outputs/mapa_blocos_prefeito_2020_2024.png")

# Paleta: vermelho = esquerda, azul = direita; intensidade = distância ao centro
CORES = {
    "ESQUERDA": "#b2182b",
    "CENTRO-ESQUERDA": "#ef8a62",
    "CENTRO": "#f7f7f7",
    "CENTRO-DIREITA": "#67a9cf",
    "DIREITA": "#2166ac",
    "DESCONHECIDO": "#cccccc",
}
ORDEM = ["ESQUERDA", "CENTRO-ESQUERDA", "CENTRO", "CENTRO-DIREITA", "DIREITA", "DESCONHECIDO"]


def bloco_dominante_por_zona(df):
    df = df.copy()
    df["BLOCO"] = df["PARTIDO"].map(classificar)
    pivot = df.groupby(["NR_ZONA", "BLOCO"])["VOTOS"].sum().unstack(fill_value=0)
    return pivot.idxmax(axis=1)


def plot_painel(ax, pontos_gdf, ano, titulo, centroides, zonas_presentes):
    for bloco in ORDEM:
        sub = pontos_gdf[pontos_gdf["bloco"] == bloco]
        if sub.empty:
            continue
        sub.plot(ax=ax, color=CORES[bloco], markersize=10, alpha=0.85)
    for zona, row in centroides.iterrows():
        if zona not in zonas_presentes:
            continue
        ax.annotate(
            str(row["nome"]).title(),
            xy=(row["lon"], row["lat"]),
            fontsize=5.5,
            ha="center",
            va="center",
            color="black",
            bbox=dict(
                boxstyle="round,pad=0.15",
                facecolor="white",
                edgecolor="none",
                alpha=0.7,
            ),
        )
    ax.set_title(f"{titulo} — {ano}", fontsize=12)
    ax.set_axis_off()


def gerar_mapa(carregar_fn, saida, cargo_label):
    dom_2020 = bloco_dominante_por_zona(carregar_fn(2020))
    dom_2024 = bloco_dominante_por_zona(carregar_fn(2024))

    gdf = gpd.read_file(SHAPEFILE)
    sp = gdf[gdf["MUN_NOME"] == "SAO PAULO"].copy()
    sp["NR_ZONA"] = sp["ZE_NUM"].astype(int)
    sp["lon"] = sp.geometry.x
    sp["lat"] = sp.geometry.y
    centroides = sp.groupby("NR_ZONA").agg(
        lon=("lon", "mean"), lat=("lat", "mean"), nome=("ZE_NOME", "first")
    )

    sp_2020 = sp.merge(dom_2020.rename("bloco"), left_on="NR_ZONA", right_index=True, how="inner")
    sp_2024 = sp.merge(dom_2024.rename("bloco"), left_on="NR_ZONA", right_index=True, how="inner")

    fig, axes = plt.subplots(1, 2, figsize=(18, 10))
    plot_painel(axes[0], sp_2020, 2020, cargo_label, centroides, set(dom_2020.index))
    plot_painel(axes[1], sp_2024, 2024, cargo_label, centroides, set(dom_2024.index))

    presentes = sorted(
        set(dom_2020.unique()) | set(dom_2024.unique()),
        key=lambda b: ORDEM.index(b) if b in ORDEM else 99,
    )
    legenda = [mpatches.Patch(color=CORES[b], label=b.title().replace("-", "-")) for b in presentes]
    fig.legend(
        handles=legenda,
        loc="lower center",
        ncol=len(legenda),
        frameon=False,
        fontsize=10,
        bbox_to_anchor=(0.5, 0.02),
    )
    fig.suptitle(
        f"Bloco ideológico dominante por zona eleitoral — {cargo_label}, São Paulo\n"
        "Classificação quintipartite (Bolognesi, Ribeiro & Codato 2023)",
        fontsize=13,
    )
    saida.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(saida, dpi=150, bbox_inches="tight")
    plt.close(fig)

    # Estatísticas: quantas zonas em cada bloco, por ano
    print(f"\n=== {cargo_label} ===")
    for ano, dom in [(2020, dom_2020), (2024, dom_2024)]:
        contagem = dom.value_counts().reindex(ORDEM, fill_value=0)
        print(f"  {ano}: " + ", ".join(f"{b}={n}" for b, n in contagem.items() if n > 0))
    print(f"  Mapa salvo: {saida}")


gerar_mapa(carregar_sp_vereador, SAIDA_VEREADOR, "Vereador")
gerar_mapa(carregar_sp_prefeito, SAIDA_PREFEITO, "Prefeito 1T")
