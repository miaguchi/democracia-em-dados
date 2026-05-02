"""Comparação espacial Bolsonaro × Tarcísio em SP capital, 2022 (1º turno).

Analisa padrões espaciais e correlação entre votos por zona eleitoral.
- Bolsonaro: Presidente, PL (nr_partido=22)
- Tarcísio: Governador, Republicanos (nr_partido=10)

Identifica zonas onde:
- Tarcísio supera Bolsonaro (vantagem do governador)
- Bolsonaro supera Tarcísio (vantagem do presidente)
- Padrão geográfico (centro/periferia, zonas progressistas vs populares)
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
import geopandas as gpd
from scipy import stats

from src.ingestao.carregar_mysql import MYSQL_CONFIG, DATABASE

SHAPEFILE_LV = _ROOT / "data/raw/shapes/EL2022_LV_ESP_CEM_V2/EL2022_LV_ESP_CEM_V2.shp"
CSV_INDICE = _ROOT / "outputs/indice_institucional_por_zona.csv"
SAIDA_CSV = _ROOT / "outputs/tables/comparacao_bolsonaro_tarcisio_2022.csv"
SAIDA_FIG_SCATTER = _ROOT / "outputs/figures/scatter_bolsonaro_tarcisio_2022.png"
SAIDA_FIG_MAPA = _ROOT / "outputs/figures/mapa_bolsonaro_tarcisio_2022.png"

CD_MUNICIPIO_SP = 71072


def carregar_votos_2022() -> pd.DataFrame:
    """Votos de Bolsonaro (Pres) e Tarcísio (Gov) por zona em SP capital."""
    conn = mysql.connector.connect(database=DATABASE, **MYSQL_CONFIG)
    sql = f"""
    SELECT
        v.nr_zona,
        SUM(CASE WHEN v.cd_cargo = 1 AND v.nr_partido = 22 THEN v.qt_votos_nominais ELSE 0 END) AS votos_bolsonaro,
        SUM(CASE WHEN v.cd_cargo = 3 AND v.nr_partido = 10 THEN v.qt_votos_nominais ELSE 0 END) AS votos_tarcisio
    FROM votacao_partido_munzona v
    JOIN eleicao e ON v.cd_eleicao = e.cd_eleicao AND v.nr_turno = e.nr_turno
    WHERE v.cd_municipio = {CD_MUNICIPIO_SP}
      AND e.ano_eleicao = 2022
      AND e.nr_turno = 1
      AND ((v.cd_cargo = 1 AND v.nr_partido = 22)
        OR (v.cd_cargo = 3 AND v.nr_partido = 10))
    GROUP BY v.nr_zona
    """
    df = pd.read_sql(sql, conn)
    conn.close()
    return df


def main() -> None:
    print("=" * 65)
    print("COMPARAÇÃO ESPACIAL — Bolsonaro × Tarcísio em SP capital (2022 1T)")
    print("=" * 65)

    df = carregar_votos_2022()
    print(f"\nZonas: {len(df)}")
    print(f"Total Bolsonaro: {df['votos_bolsonaro'].sum():>10,.0f}")
    print(f"Total Tarcísio:  {df['votos_tarcisio'].sum():>10,.0f}")
    print(f"Ratio Tarc/Bolso: {df['votos_tarcisio'].sum()/df['votos_bolsonaro'].sum():.3f}")

    # Razão e diferença por zona
    df["ratio_tarc_bolso"] = df["votos_tarcisio"] / df["votos_bolsonaro"]
    df["diff_tarc_bolso"] = df["votos_tarcisio"] - df["votos_bolsonaro"]
    df["pct_tarc_relativo_bolso"] = (df["ratio_tarc_bolso"] - 1) * 100

    # Trazer índice institucional + nome
    idx = pd.read_csv(CSV_INDICE)[["NR_ZONA", "nome_ze", "indice_cultural"]]
    idx.columns = ["nr_zona", "nome_ze", "indice_cultural"]
    df = df.merge(idx, on="nr_zona", how="left")

    # Correlação
    r, p = stats.pearsonr(df["votos_bolsonaro"], df["votos_tarcisio"])
    print(f"\nCorrelação Bolsonaro × Tarcísio (zonas): r = {r:+.3f} (p = {p:.2g})")

    # Top 10 zonas onde Tarcísio mais supera Bolsonaro
    top_tarc = df.sort_values("pct_tarc_relativo_bolso", ascending=False).head(10)
    print(f"\nTop 10 zonas onde Tarcísio mais supera Bolsonaro (ratio):")
    print(top_tarc[["nr_zona", "nome_ze", "votos_bolsonaro", "votos_tarcisio",
                    "pct_tarc_relativo_bolso", "indice_cultural"]].to_string(
        index=False, float_format=lambda x: f"{x:.1f}"))

    bottom_tarc = df.sort_values("pct_tarc_relativo_bolso").head(10)
    print(f"\nTop 10 zonas onde Bolsonaro mais supera Tarcísio:")
    print(bottom_tarc[["nr_zona", "nome_ze", "votos_bolsonaro", "votos_tarcisio",
                       "pct_tarc_relativo_bolso", "indice_cultural"]].to_string(
        index=False, float_format=lambda x: f"{x:.1f}"))

    # Salvar
    SAIDA_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.sort_values("votos_bolsonaro", ascending=False).to_csv(SAIDA_CSV, index=False)
    print(f"\nCSV salvo: {SAIDA_CSV}")

    # ===== Plot 1: scatter Bolsonaro × Tarcísio =====
    fig, ax = plt.subplots(figsize=(9, 8), dpi=120)
    sc = ax.scatter(df["votos_bolsonaro"], df["votos_tarcisio"],
                    s=80, alpha=0.7, c=df["indice_cultural"],
                    cmap="viridis", edgecolor="black", linewidth=0.4)
    cb = fig.colorbar(sc, ax=ax)
    cb.set_label("Índice institucional (%)", fontsize=10)

    # Linha diagonal Tarc = Bolso
    lim = max(df["votos_bolsonaro"].max(), df["votos_tarcisio"].max())
    ax.plot([0, lim], [0, lim], "k--", alpha=0.4, label="Tarc = Bolso")

    # Linha de regressão
    res = stats.linregress(df["votos_bolsonaro"], df["votos_tarcisio"])
    x_l = np.linspace(0, lim, 100)
    ax.plot(x_l, res.slope * x_l + res.intercept, "r-",
            linewidth=2, alpha=0.7,
            label=f"OLS: y={res.slope:.2f}x+{res.intercept:.0f}, R²={res.rvalue**2:.3f}")

    # Anotar zonas-alvo
    zonas_destaque = {1: "Bela Vista", 2: "Perdizes", 5: "Jd Paulista",
                      6: "V. Mariana", 251: "Pinheiros", 258: "Indianópolis",
                      346: "Butantã", 3: "Sta Ifigênia", 348: "Itaim Pta",
                      403: "Brasilândia", 326: "Capão Redondo"}
    for z, nome in zonas_destaque.items():
        row = df[df["nr_zona"] == z]
        if row.empty:
            continue
        ax.annotate(
            f"Z{z}\n{nome}",
            xy=(row["votos_bolsonaro"].iloc[0], row["votos_tarcisio"].iloc[0]),
            fontsize=7, ha="center", va="bottom",
            xytext=(0, 6), textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                      edgecolor="gray", alpha=0.9),
        )

    ax.set_xlabel("Votos Bolsonaro (Presidente, 1T 2022)", fontsize=11)
    ax.set_ylabel("Votos Tarcísio (Governador, 1T 2022)", fontsize=11)
    ax.set_title(
        f"Bolsonaro × Tarcísio por zona — SP capital (2022, 1T)\n"
        f"r = {r:+.3f}   N = {len(df)}   color = índice institucional",
        fontsize=12, fontweight="bold",
    )
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(SAIDA_FIG_SCATTER, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Figura salva: {SAIDA_FIG_SCATTER}")

    # ===== Plot 2: mapa espacial — diff Tarc - Bolso por zona =====
    print("\nCarregando shapefile para mapa...")
    gdf = gpd.read_file(SHAPEFILE_LV)
    sp = gdf[gdf["MUN_NOME"] == "SAO PAULO"].copy()
    sp["NR_ZONA"] = sp["ZE_NUM"].astype(int)

    # Agregar local de votação por zona (centróide)
    centroides = sp.dissolve(by="NR_ZONA").geometry.centroid
    centroides = gpd.GeoDataFrame({"nr_zona": centroides.index, "geometry": centroides.values},
                                   geometry="geometry", crs=sp.crs)
    df_geo = centroides.merge(df, on="nr_zona", how="left")

    fig, axes = plt.subplots(1, 2, figsize=(18, 9), dpi=120)

    # Painel 1: votos Bolsonaro
    df_geo.plot(
        ax=axes[0], column="votos_bolsonaro", cmap="Reds",
        markersize=df_geo["votos_bolsonaro"] / 200,
        legend=True, alpha=0.8, edgecolor="black", linewidth=0.3,
        legend_kwds={"label": "Votos", "shrink": 0.6},
    )
    axes[0].set_title(f"Bolsonaro (Pres. 1T)\nTotal SP capital: "
                      f"{df['votos_bolsonaro'].sum():,.0f}",
                      fontsize=12, fontweight="bold")
    axes[0].set_axis_off()

    # Painel 2: diferença Tarc - Bolso (vantagem de Tarc onde positivo)
    df_geo.plot(
        ax=axes[1], column="pct_tarc_relativo_bolso", cmap="RdBu",
        vmin=-30, vmax=30,
        markersize=80, legend=True, alpha=0.85,
        edgecolor="black", linewidth=0.3,
        legend_kwds={"label": "% Tarcísio relativo a Bolsonaro",
                     "shrink": 0.6},
    )
    axes[1].set_title("Diferença % Tarcísio vs Bolsonaro\n"
                      "(azul = Tarc supera; vermelho = Bolso supera)",
                      fontsize=12, fontweight="bold")
    axes[1].set_axis_off()

    fig.suptitle(
        "Padrão espacial — Bolsonaro × Tarcísio em SP capital (2022, 1º turno)",
        fontsize=14, fontweight="bold",
    )
    fig.tight_layout()
    fig.savefig(SAIDA_FIG_MAPA, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Figura salva: {SAIDA_FIG_MAPA}")

    # ===== Análise complementar =====
    # Correlação com índice institucional
    print("\n--- Correlação com índice institucional ---")
    r_b, p_b = stats.pearsonr(df["indice_cultural"].fillna(0), df["votos_bolsonaro"])
    r_t, p_t = stats.pearsonr(df["indice_cultural"].fillna(0), df["votos_tarcisio"])
    r_d, p_d = stats.pearsonr(df["indice_cultural"].fillna(0), df["pct_tarc_relativo_bolso"])
    print(f"  índice × Bolsonaro:                 r = {r_b:+.3f} (p = {p_b:.2g})")
    print(f"  índice × Tarcísio:                  r = {r_t:+.3f} (p = {p_t:.2g})")
    print(f"  índice × diff% (Tarc rel a Bolso):  r = {r_d:+.3f} (p = {p_d:.2g})")


if __name__ == "__main__":
    main()
