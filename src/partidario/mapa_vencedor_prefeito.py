"""Mapa do partido/candidato vencedor por zona — prefeito 1T, SP, 2020 e 2024.

Em prefeito de 1º turno há um candidato por partido/coligação, então a
plurality do SG_PARTIDO por zona equivale à plurality do candidato.
Usamos a coluna SG_PARTIDO original (sem normalizar federações) para
preservar a identidade do candidato.
"""

from pathlib import Path

import geopandas as gpd
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pandas as pd

SHAPEFILE = Path("data/raw/shapes/EL2022_LV_ESP_CEM_V2/EL2022_LV_ESP_CEM_V2.shp")
SAIDA = Path("outputs/mapa_vencedor_prefeito_2020_2024.png")
CODIGO_TSE_SAO_PAULO = 71072

# Mapa partido → (candidato, cor). Cores livres, com consistência
# esquerda-vermelho / direita-azul para facilitar leitura.
CANDIDATOS = {
    2020: {
        "PSDB": ("Covas (PSDB)", "#4daf4a"),
        "PSOL": ("Boulos (PSOL)", "#a50f15"),
        "PSB": ("Márcio France (PSB)", "#f768a1"),
        "REPUBLICANOS": ("Russomanno (Republicanos)", "#08519c"),
        "PATRIOTA": ("Arthur do Val (Patriota)", "#6baed6"),
        "PT": ("Jilmar Tatto (PT)", "#cb181d"),
        "NOVO": ("Filipe Sabará (Novo)", "#fdae6b"),
        "PMB": ("Antônio Carlos (PMB)", "#c6dbef"),
        "PDT": ("Marina Helou (PDT)", "#fcae91"),
        "PV": ("Orlando Silva (PV)", "#74c476"),
        "PCO": ("PCO", "#525252"),
        "PSTU": ("PSTU", "#525252"),
    },
    2024: {
        "MDB": ("Nunes (MDB)", "#08519c"),
        "PSOL": ("Boulos (PSOL)", "#a50f15"),
        "PRTB": ("Marçal (PRTB)", "#ff7f00"),
        "PSB": ("Tabata Amaral (PSB)", "#f768a1"),
        "PSDB": ("Datena (PSDB)", "#4daf4a"),
        "NOVO": ("Marina Helou (Novo)", "#fdae6b"),
        "UP": ("Bebeto Haddad (UP)", "#525252"),
        "PCO": ("PCO", "#525252"),
        "PSTU": ("PSTU", "#525252"),
    },
}


def vencedor_por_zona(ano: int) -> pd.Series:
    parquet = Path(f"data/processed/votacao_partido_munzona_{ano}_SP.parquet")
    df = pd.read_parquet(parquet)
    filtro = (
        (df["CD_MUNICIPIO"] == CODIGO_TSE_SAO_PAULO)
        & (df["DS_CARGO"].str.upper() == "PREFEITO")
        & (df["NR_TURNO"] == 1)
    )
    sub = df.loc[filtro, ["NR_ZONA", "SG_PARTIDO", "QT_VOTOS_NOMINAIS_VALIDOS", "QT_VOTOS_LEGENDA_VALIDOS"]].copy()
    sub["VOTOS"] = sub["QT_VOTOS_NOMINAIS_VALIDOS"] + sub["QT_VOTOS_LEGENDA_VALIDOS"]
    return (
        sub.groupby(["NR_ZONA", "SG_PARTIDO"])["VOTOS"]
        .sum()
        .groupby("NR_ZONA")
        .idxmax()
        .apply(lambda t: t[1])
    )


venc_2020 = vencedor_por_zona(2020)
venc_2024 = vencedor_por_zona(2024)

print("=== Zonas vencidas por partido ===")
print("2020:")
print(venc_2020.value_counts())
print("\n2024:")
print(venc_2024.value_counts())

gdf = gpd.read_file(SHAPEFILE)
sp = gdf[gdf["MUN_NOME"] == "SAO PAULO"].copy()
sp["NR_ZONA"] = sp["ZE_NUM"].astype(int)
sp["lon"] = sp.geometry.x
sp["lat"] = sp.geometry.y

# Centroide e nome por zona (para rotular)
CENTROIDES = sp.groupby("NR_ZONA").agg(
    lon=("lon", "mean"),
    lat=("lat", "mean"),
    nome=("ZE_NOME", "first"),
)


def plot_painel(ax, dom: pd.Series, ano: int, titulo: str):
    sp_merged = sp.merge(dom.rename("partido"), left_on="NR_ZONA", right_index=True, how="inner")
    mapa_ano = CANDIDATOS[ano]
    presentes = sorted(
        dom.unique(),
        key=lambda p: (dom == p).sum(),
        reverse=True,
    )
    for partido in presentes:
        info = mapa_ano.get(partido, (partido, "#999999"))
        cor = info[1]
        sub = sp_merged[sp_merged["partido"] == partido]
        sub.plot(ax=ax, color=cor, markersize=11, alpha=0.9)
    # Rótulos com nome da zona no centroide
    for zona, row in CENTROIDES.iterrows():
        if zona not in dom.index:
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
    legenda = []
    for partido in presentes:
        info = mapa_ano.get(partido, (partido, "#999999"))
        n_zonas = int((dom == partido).sum())
        legenda.append(mpatches.Patch(color=info[1], label=f"{info[0]} — {n_zonas} zonas"))
    ax.legend(handles=legenda, loc="lower left", fontsize=8, framealpha=0.9)


fig, axes = plt.subplots(1, 2, figsize=(18, 10))
plot_painel(axes[0], venc_2020, 2020, "Prefeito 1T")
plot_painel(axes[1], venc_2024, 2024, "Prefeito 1T")
fig.suptitle(
    "Candidato mais votado por zona eleitoral — Prefeito 1T, São Paulo\n"
    "Plurality do SG_PARTIDO (um candidato por partido no 1º turno)",
    fontsize=13,
)
SAIDA.parent.mkdir(parents=True, exist_ok=True)
plt.tight_layout()
plt.savefig(SAIDA, dpi=150, bbox_inches="tight")
print(f"\nMapa salvo: {SAIDA}")
