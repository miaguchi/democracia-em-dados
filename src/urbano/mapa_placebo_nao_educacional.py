"""Mapa exploratório: locais de votação não-educacionais em São Paulo.

Plota os locais não-educacionais (candidatos a placebo) sobre o polígono
de SP, coloridos por subgrupo funcional. Destaca as 8 zonas-alvo do
projeto para avaliar cobertura espacial.

Uso interativo (Spyder): execute o script, o mapa abre com plt.show().
Uso batch: gera PNG em outputs/mapa_placebo_nao_educacional.png.
"""

from pathlib import Path

import geobr
import geopandas as gpd
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt


_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.dominio.local_votacao import carregar_cem, filtrar_locais_cem

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

CODIGO_IBGE_SP = 3550308
SAIDA = _ROOT / "outputs/mapa_placebo_nao_educacional.png"

# Subgrupos funcionais para coloração
_SUBGRUPO: dict[str, str] = {
    "CDP": "Prisional",
    "PENIT": "Prisional",
    "FUND CASA": "Prisional",
    "CPP": "Prisional",
    "POSTO SAUDE": "Saúde",
    "UBS": "Saúde",
    "ASSOC": "Associação",
    "ASSOC CULT": "Associação",
    "COOP": "Associação",
    "ASSIST SOC": "Associação",
    "IGREJA": "Religioso",
    "PASTORAL": "Religioso",
    "CLUBE": "Esportivo",
    "CLUBE ATL": "Esportivo",
    "CDC": "Esportivo",
    "CREAS": "Assist. social",
    "CCA": "Assist. social",
    "AUTARQUIA": "Administrativo",
    "SECRETARIA": "Administrativo",
    "ESP CULT": "Cultural",
    "BIBLI": "Cultural",
    "GURI": "Cultural",
    "EQUIP PUB": "Equip. público",
    "CEU": "CEU (multiuso)",
    "BAIRRO": "Comunidade",
    "ASSENT": "Comunidade",
    "NUCLEO": "Outro",
    "FUND": "Outro",
}

_CORES: dict[str, str] = {
    "Prisional": "#d62728",
    "Saúde": "#2ca02c",
    "Associação": "#ff7f0e",
    "Religioso": "#9467bd",
    "Esportivo": "#17becf",
    "Assist. social": "#e377c2",
    "Administrativo": "#7f7f7f",
    "Cultural": "#bcbd22",
    "Equip. público": "#1f77b4",
    "CEU (multiuso)": "#8c564b",
    "Comunidade": "#aec7e8",
    "Outro": "#c7c7c7",
}


def _atribuir_subgrupo(lv_tipo: str) -> str:
    return _SUBGRUPO.get(lv_tipo, "Outro")


def gerar_mapa(interativo: bool = False) -> None:
    """Gera mapa dos locais não-educacionais.

    Parameters
    ----------
    interativo : bool
        Se True, abre janela interativa (plt.show()) em vez de salvar PNG.
    """
    # Polígono SP
    print("Baixando polígono IBGE de SP...")
    sp_poly = geobr.read_municipality(code_muni=CODIGO_IBGE_SP, year=2020)

    # Classificar locais
    print("Carregando e classificando base CEM...")
    gdf = carregar_cem()
    _, nao_educ = filtrar_locais_cem(gdf)

    # Filtrar SP
    sp_nao_educ = nao_educ[nao_educ["MUN_NOME"] == "SAO PAULO"].copy()
    sp_nao_educ["NR_ZONA"] = sp_nao_educ["ZE_NUM"].astype(int)
    sp_nao_educ["subgrupo"] = sp_nao_educ["LV_TIPO"].apply(_atribuir_subgrupo)

    # Todos os não-educacionais do estado (para stats)
    total_estado = len(nao_educ)
    total_sp = len(sp_nao_educ)
    em_zonas_alvo = sp_nao_educ[sp_nao_educ["NR_ZONA"].isin(ZONAS_ALVO.keys())]

    print(f"Não-educacionais no estado: {total_estado}")
    print(f"Não-educacionais em SP capital: {total_sp}")
    print(f"Não-educacionais nas zonas-alvo: {len(em_zonas_alvo)}")

    if len(em_zonas_alvo) > 0:
        print("\nNas zonas-alvo:")
        for _, row in em_zonas_alvo.iterrows():
            zona = row["NR_ZONA"]
            nome_zona = ZONAS_ALVO.get(zona, "?")
            print(f"  Z{zona} ({nome_zona}): {row['LV_TIPO']} — {row['NOME_LV']}")

    # --- Plot ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))

    # Painel esquerdo: SP inteiro
    sp_poly.boundary.plot(ax=ax1, color="#555555", linewidth=0.8)
    sp_poly.plot(ax=ax1, color="#f0f0f0", alpha=0.5)

    for subgrupo, cor in _CORES.items():
        subset = sp_nao_educ[sp_nao_educ["subgrupo"] == subgrupo]
        if subset.empty:
            continue
        subset.plot(
            ax=ax1,
            color=cor,
            markersize=30,
            edgecolor="black",
            linewidth=0.3,
            alpha=0.85,
            label=f"{subgrupo} ({len(subset)})",
        )

    # Retângulo das zonas-alvo
    if not em_zonas_alvo.empty:
        bbox = em_zonas_alvo.total_bounds
    else:
        # Usar bbox aproximado do centro de SP
        all_sp = gdf[gdf["MUN_NOME"] == "SAO PAULO"]
        zonas_pts = all_sp[all_sp["ZE_NUM"].isin(ZONAS_ALVO.keys())]
        bbox = zonas_pts.total_bounds

    padding = 0.015
    rect = mpatches.Rectangle(
        (bbox[0] - padding, bbox[1] - padding),
        (bbox[2] - bbox[0]) + 2 * padding,
        (bbox[3] - bbox[1]) + 2 * padding,
        linewidth=2,
        edgecolor="red",
        facecolor="none",
        linestyle="--",
    )
    ax1.add_patch(rect)

    ax1.set_title(
        f"Locais não-educacionais — SP capital ({total_sp} locais)",
        fontsize=12,
    )
    ax1.legend(loc="lower left", fontsize=8, framealpha=0.9)
    ax1.set_axis_off()

    # Painel direito: zoom nas zonas-alvo
    sp_poly.boundary.plot(ax=ax2, color="#555555", linewidth=0.8)
    sp_poly.plot(ax=ax2, color="#f0f0f0", alpha=0.5)

    # Plotar educacionais como fundo cinza nas zonas-alvo
    educ_all, _ = filtrar_locais_cem(gdf)
    sp_educ = educ_all[educ_all["MUN_NOME"] == "SAO PAULO"].copy()
    sp_educ["NR_ZONA"] = sp_educ["ZE_NUM"].astype(int)
    sp_educ_zonas = sp_educ[sp_educ["NR_ZONA"].isin(ZONAS_ALVO.keys())]
    sp_educ_zonas.plot(
        ax=ax2,
        color="#cccccc",
        markersize=20,
        edgecolor="#999999",
        linewidth=0.2,
        alpha=0.5,
        label=f"Educacionais ({len(sp_educ_zonas)})",
    )

    # Não-educacionais nas zonas-alvo
    for subgrupo, cor in _CORES.items():
        subset = em_zonas_alvo[em_zonas_alvo["subgrupo"] == subgrupo]
        if subset.empty:
            continue
        subset.plot(
            ax=ax2,
            color=cor,
            markersize=60,
            edgecolor="black",
            linewidth=0.5,
            alpha=0.9,
            label=f"{subgrupo} ({len(subset)})",
        )

    # Rótulos das zonas
    all_sp = gdf[gdf["MUN_NOME"] == "SAO PAULO"].copy()
    all_sp["NR_ZONA"] = all_sp["ZE_NUM"].astype(int)
    for zona, nome in ZONAS_ALVO.items():
        pontos = all_sp[all_sp["NR_ZONA"] == zona]
        if pontos.empty:
            continue
        cx, cy = pontos.geometry.x.mean(), pontos.geometry.y.mean()
        ax2.annotate(
            f"Z{zona}\n{nome}",
            xy=(cx, cy),
            fontsize=8,
            ha="center",
            va="center",
            fontweight="bold",
            bbox=dict(
                boxstyle="round,pad=0.2",
                facecolor="white",
                edgecolor="black",
                alpha=0.85,
            ),
        )

    xlim = (bbox[0] - padding, bbox[2] + padding)
    ylim = (bbox[1] - padding, bbox[3] + padding)
    ax2.set_xlim(xlim)
    ax2.set_ylim(ylim)
    ax2.set_title(
        f"Zoom zonas-alvo — não-educacionais: {len(em_zonas_alvo)}",
        fontsize=12,
    )
    ax2.legend(loc="lower left", fontsize=8, framealpha=0.9)
    ax2.set_axis_off()

    fig.suptitle(
        "Inventário espacial: locais de votação não-educacionais\n"
        "Base CEM/USP EL2022 — candidatos a grupo placebo",
        fontsize=14,
        fontweight="bold",
    )

    plt.tight_layout()

    if interativo:
        plt.show()
    else:
        SAIDA.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(SAIDA, dpi=300, bbox_inches="tight")
        print(f"\nMapa salvo: {SAIDA}")
        plt.close()


if __name__ == "__main__":
    import sys

    interativo = "--interativo" in sys.argv
    gerar_mapa(interativo=interativo)
