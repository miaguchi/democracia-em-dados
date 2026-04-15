"""Mapas de bloco dominante por SEÇÃO eleitoral — SP 2024.

Para cada seção, classifica o bloco ideológico vencedor usando plurality
bipartite (ESQ vs DIR, cortes em 4.49 e 5.50 de Bolognesi 2023). Agrega
seções por local de votação (centroide) e plota pontos coloridos.

Dois painéis: vereador e prefeito 1T.
Também gera uma versão focada no corredor das universidades.
"""

from pathlib import Path

import geobr
import geopandas as gpd
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pandas as pd

from src.partidario.analise_volatilidade import normalizar_partido
from src.partidario.ideologia import ESCORE_BOLOGNESI, bloco_quintipartite

SHAPEFILE_LV = Path("data/raw/shapes/EL2022_LV_ESP_CEM_V2/EL2022_LV_ESP_CEM_V2.shp")
CODIGO_IBGE_SP = 3550308

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

# Bipartite: colapsa em 3 categorias — ESQ (esq+c-esq), CENTRO, DIR (c-dir+dir)
MAPA_BIPARTITE = {
    "ESQUERDA": "ESQ",
    "CENTRO-ESQUERDA": "ESQ",
    "CENTRO": "CENTRO",
    "CENTRO-DIREITA": "DIR",
    "DIREITA": "DIR",
}
CORES_BIPARTITE = {
    "ESQ": "#b2182b",
    "CENTRO": "#f7f7f7",
    "DIR": "#2166ac",
    "DESCONHECIDO": "#cccccc",
}
ROTULOS_BIPARTITE = {
    "ESQ": "Esquerda + Centro-Esquerda (escore ≤ 4.49)",
    "CENTRO": "Centro (escore 4.5–5.5)",
    "DIR": "Centro-Direita + Direita (escore > 5.5)",
}

# Mapa NR_PARTIDO → sigla
MAPA_PARTIDO: dict[int, str] = {}
for ano in [2020, 2024]:
    df_ref = pd.read_parquet(f"data/processed/votacao_partido_munzona_{ano}_SP.parquet")
    for _, row in df_ref[["NR_PARTIDO", "SG_PARTIDO"]].drop_duplicates().iterrows():
        MAPA_PARTIDO[int(row["NR_PARTIDO"])] = row["SG_PARTIDO"]


def carregar_secao(ano: int) -> pd.DataFrame:
    df = pd.read_parquet(f"data/processed/votacao_secao_{ano}_SP.parquet")
    df = df[df["NM_MUNICIPIO"] == "SÃO PAULO"].copy()
    df = df[df["NR_TURNO"] == 1].copy()
    df["NR_VOTAVEL"] = pd.to_numeric(df["NR_VOTAVEL"], errors="coerce")
    df = df.dropna(subset=["NR_VOTAVEL"])
    df["NR_PARTIDO"] = (df["NR_VOTAVEL"].astype(int) // 1000).replace(0, None)
    cargo_pref = df["DS_CARGO"].str.upper() == "PREFEITO"
    df.loc[cargo_pref, "NR_PARTIDO"] = df.loc[cargo_pref, "NR_VOTAVEL"].astype(int)
    df["NR_PARTIDO"] = df["NR_PARTIDO"].astype("Int64")
    df["SG_PARTIDO"] = df["NR_PARTIDO"].map(MAPA_PARTIDO)
    df = df.dropna(subset=["SG_PARTIDO"])
    df["PARTIDO"] = df["SG_PARTIDO"].map(normalizar_partido)
    df["BLOCO"] = df["PARTIDO"].map(
        lambda p: bloco_quintipartite(ESCORE_BOLOGNESI[p])
        if p in ESCORE_BOLOGNESI
        else "DESCONHECIDO"
    )
    df["LADO"] = df["BLOCO"].map(MAPA_BIPARTITE).fillna("DESCONHECIDO")
    return df


def bloco_dominante_por_local(df: pd.DataFrame, cargo: str) -> pd.DataFrame:
    """Agrega seções por (NR_ZONA, NR_LOCAL_VOTACAO) — NR_LOCAL_VOTACAO repete entre zonas."""
    sub = df[df["DS_CARGO"].str.upper() == cargo.upper()]
    tab = (
        sub.groupby(["NR_ZONA", "NR_LOCAL_VOTACAO", "LADO"])["QT_VOTOS"]
        .sum()
        .unstack(fill_value=0)
    )
    for c in ["ESQ", "DIR", "CENTRO", "DESCONHECIDO"]:
        if c not in tab.columns:
            tab[c] = 0
    tab["total"] = tab[["ESQ", "DIR", "CENTRO"]].sum(axis=1)
    tab["pct_esq"] = tab["ESQ"] / tab["total"] * 100
    tab["pct_dir"] = tab["DIR"] / tab["total"] * 100
    tab["pct_centro"] = tab["CENTRO"] / tab["total"] * 100
    tab["dominante"] = tab[["ESQ", "DIR", "CENTRO"]].idxmax(axis=1)
    return tab.reset_index()


print("Carregando dados secao 2024 (SP)...")
df_2024 = carregar_secao(2024)
print(f"Linhas: {len(df_2024):,}")

print("\nCarregando geometria (CEM + IBGE)...")
gdf = gpd.read_file(SHAPEFILE_LV)
sp_lv = gdf[gdf["MUN_NOME"] == "SAO PAULO"].copy()
sp_lv["NR_ZONA"] = sp_lv["ZE_NUM"].astype(int)

# Matching: pelo nome do local (CEM não usa o mesmo código do TSE)
import re
import unicodedata


def normalizar_nome(s):
    if not isinstance(s, str):
        return ""
    s = unicodedata.normalize("NFKD", s).encode("ASCII", "ignore").decode()
    s = re.sub(r"[^A-Z ]", " ", s.upper())
    return re.sub(r"\s+", " ", s).strip()


# Cria mapa NR_LOCAL_VOTACAO + NR_ZONA → coordenadas via fuzzy por nome + zona
nomes_votacao = (
    df_2024[["NR_LOCAL_VOTACAO", "NR_ZONA", "NM_LOCAL_VOTACAO"]]
    .drop_duplicates()
    .copy()
)
nomes_votacao["nome_norm"] = nomes_votacao["NM_LOCAL_VOTACAO"].map(normalizar_nome)
sp_lv["nome_norm"] = sp_lv["NOME_LV"].map(normalizar_nome)

# Para casamento eficiente por zona: indexar por NR_ZONA
from collections import defaultdict

zona_to_shape: dict[int, list] = defaultdict(list)
for idx, row in sp_lv.iterrows():
    zona_to_shape[int(row["NR_ZONA"])].append((idx, row["nome_norm"]))


def casar_por_zona(nr_zona: int, nome_norm: str):
    if nr_zona not in zona_to_shape:
        return None
    tokens = set(nome_norm.split())
    melhor_idx, melhor_score = None, 0
    for idx, nome_shape in zona_to_shape[nr_zona]:
        score = len(tokens & set(nome_shape.split()))
        if score > melhor_score:
            melhor_score = score
            melhor_idx = idx
    return melhor_idx if melhor_score >= 1 else None


print("Casando locais por nome (dentro da mesma zona)...")
nomes_votacao["shape_idx"] = nomes_votacao.apply(
    lambda r: casar_por_zona(int(r["NR_ZONA"]), r["nome_norm"]), axis=1
)
ok = nomes_votacao["shape_idx"].notna().sum()
print(f"Casados: {ok}/{len(nomes_votacao)}")

mapa_local_coord = {}
for _, row in nomes_votacao.dropna(subset=["shape_idx"]).iterrows():
    shape_row = sp_lv.loc[row["shape_idx"]]
    chave = (int(row["NR_ZONA"]), int(row["NR_LOCAL_VOTACAO"]))
    mapa_local_coord[chave] = (shape_row.geometry.x, shape_row.geometry.y)


mapa_local_nome = {
    (int(r["NR_ZONA"]), int(r["NR_LOCAL_VOTACAO"])): r["NM_LOCAL_VOTACAO"]
    for _, r in nomes_votacao.dropna(subset=["shape_idx"]).iterrows()
}


def gerar_mapa(cargo: str, focado: bool, saida: Path, rotular: bool = False):
    dom = bloco_dominante_por_local(df_2024, cargo)
    dom["coord"] = dom.apply(
        lambda r: mapa_local_coord.get((int(r["NR_ZONA"]), int(r["NR_LOCAL_VOTACAO"]))),
        axis=1,
    )
    dom = dom.dropna(subset=["coord"]).copy()
    dom["x"] = dom["coord"].map(lambda c: c[0])
    dom["y"] = dom["coord"].map(lambda c: c[1])
    dom["nome_local"] = dom.apply(
        lambda r: mapa_local_nome.get((int(r["NR_ZONA"]), int(r["NR_LOCAL_VOTACAO"])), ""),
        axis=1,
    )
    dom_gdf = gpd.GeoDataFrame(
        dom, geometry=gpd.points_from_xy(dom["x"], dom["y"]), crs="EPSG:4326"
    )

    if focado:
        dom_gdf = dom_gdf[dom_gdf["NR_ZONA"].isin(ZONAS_ALVO.keys())].copy()
        bbox = dom_gdf.total_bounds
        padding = 0.012
        xlim = (bbox[0] - padding, bbox[2] + padding)
        ylim = (bbox[1] - padding, bbox[3] + padding)
    else:
        xlim = ylim = None

    sp_poly = geobr.read_municipality(code_muni=CODIGO_IBGE_SP, year=2020)

    fig, ax = plt.subplots(figsize=(13, 13))
    sp_poly.boundary.plot(ax=ax, color="#555555", linewidth=0.8)
    sp_poly.plot(ax=ax, color="#f8f8f8", alpha=0.5)

    for lado in ["DIR", "CENTRO", "ESQ"]:
        sub = dom_gdf[dom_gdf["dominante"] == lado]
        if sub.empty:
            continue
        sub.plot(
            ax=ax,
            color=CORES_BIPARTITE[lado],
            markersize=18 if focado else 8,
            edgecolor="black" if focado else "none",
            linewidth=0.2,
            alpha=0.85,
            label=f"{ROTULOS_BIPARTITE[lado]} ({len(sub)} locais)",
        )
    if xlim:
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

    if focado:
        if rotular:
            # Rotula cada local (escola/colégio) individualmente
            import re as _re
            for _, row in dom_gdf.iterrows():
                nome = row["nome_local"]
                if not isinstance(nome, str) or not nome.strip():
                    continue
                # Encurta: remove prefixos comuns e limita tamanho
                limpo = _re.sub(
                    r"^(E\.?\s*E\.?|EMEIF|EMEF|EMEB|EMEI|COL[ÉE]GIO|ESCOLA|CEU|EE\.?)\s*",
                    "",
                    nome,
                    flags=_re.IGNORECASE,
                ).strip()
                ax.annotate(
                    limpo[:26],
                    xy=(row["x"], row["y"]),
                    xytext=(3, 3),
                    textcoords="offset points",
                    fontsize=4.5,
                    color="black",
                    bbox=dict(
                        boxstyle="round,pad=0.1",
                        facecolor="white",
                        edgecolor="none",
                        alpha=0.75,
                    ),
                )
        # Rotula as 8 zonas-alvo
        for zona, nome in ZONAS_ALVO.items():
            pontos = sp_lv[sp_lv["NR_ZONA"] == zona]
            if pontos.empty:
                continue
            cx, cy = pontos.geometry.x.mean(), pontos.geometry.y.mean()
            ax.annotate(
                f"Z{zona}\n{nome}",
                xy=(cx, cy),
                fontsize=11,
                ha="center",
                va="center",
                fontweight="bold",
                bbox=dict(
                    boxstyle="round,pad=0.3",
                    facecolor="#ffff99",
                    edgecolor="black",
                    alpha=0.95,
                ),
            )

    total = len(dom_gdf)
    contagem = dom_gdf["dominante"].value_counts()
    titulo = (
        f"Bloco dominante por local de votação — {cargo}, SP 2024\n"
        f"Agregação bipartite ESQ / CENTRO / DIR (Bolognesi 2023)"
    )
    if focado:
        titulo = "Corredor das universidades — " + titulo
    ax.set_title(
        titulo
        + f"\n{contagem.get('ESQ', 0)} locais ESQ | "
        f"{contagem.get('CENTRO', 0)} CENTRO | "
        f"{contagem.get('DIR', 0)} DIR  (de {total})",
        fontsize=12,
    )
    ax.set_axis_off()
    ax.legend(loc="lower left", fontsize=9, framealpha=0.92)
    saida.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(saida, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Mapa salvo: {saida}")
    print(f"  Distribuição: {contagem.to_dict()}")


print("\n--- Vereador (cidade toda) ---")
gerar_mapa("VEREADOR", focado=False, saida=Path("outputs/mapa_blocos_secao_sp_vereador_2024.png"))

print("\n--- Prefeito (cidade toda) ---")
gerar_mapa("PREFEITO", focado=False, saida=Path("outputs/mapa_blocos_secao_sp_prefeito_2024.png"))

print("\n--- Vereador (corredor, com rótulos) ---")
gerar_mapa(
    "VEREADOR",
    focado=True,
    saida=Path("outputs/mapa_blocos_secao_corredor_vereador_2024.png"),
    rotular=True,
)

print("\n--- Prefeito (corredor, com rótulos) ---")
gerar_mapa(
    "PREFEITO",
    focado=True,
    saida=Path("outputs/mapa_blocos_secao_corredor_prefeito_2024.png"),
    rotular=True,
)
