"""Análise seção-a-seção dentro das zonas ricas do corredor universitário.

Para cada seção das 8 zonas-alvo (Bela Vista, Perdizes, Santa Ifigênia,
Jd Paulista, Vila Mariana, Pinheiros, Indianópolis, Butantã), computa o
escore ideológico médio ponderado e identifica:
- seções onde a esquerda (bloco ESQUERDA+CENTRO-ESQUERDA) tem maioria
- seções mais à esquerda e mais à direita dentro de cada zona
- comparação 2020 vs 2024 por seção (para quantas mudaram de lado)
"""

from pathlib import Path

import pandas as pd

from src.partidario.analise_volatilidade import normalizar_partido
from src.partidario.ideologia import bloco_quintipartite, ESCORE_BOLOGNESI

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

# Mapa NR_PARTIDO → sigla
MAPA_PARTIDO: dict[int, str] = {}
for ano in [2020, 2024]:
    df_ref = pd.read_parquet(f"data/processed/votacao_partido_munzona_{ano}_SP.parquet")
    for _, row in df_ref[["NR_PARTIDO", "SG_PARTIDO"]].drop_duplicates().iterrows():
        MAPA_PARTIDO[int(row["NR_PARTIDO"])] = row["SG_PARTIDO"]


def carregar_secao_sp(ano: int) -> pd.DataFrame:
    df = pd.read_parquet(f"data/processed/votacao_secao_{ano}_SP.parquet")
    df = df[df["NM_MUNICIPIO"] == "SÃO PAULO"].copy()
    df = df[df["NR_TURNO"] == 1].copy()
    df["NR_VOTAVEL"] = pd.to_numeric(df["NR_VOTAVEL"], errors="coerce")
    df = df.dropna(subset=["NR_VOTAVEL"])
    # Vereador: 2 primeiros dígitos = partido. Prefeito: NR_VOTAVEL já é partido.
    df["NR_PARTIDO"] = (df["NR_VOTAVEL"].astype(int) // 1000).replace(0, None)
    cargo_pref = df["DS_CARGO"].str.upper() == "PREFEITO"
    df.loc[cargo_pref, "NR_PARTIDO"] = df.loc[cargo_pref, "NR_VOTAVEL"].astype(int)
    df["NR_PARTIDO"] = df["NR_PARTIDO"].astype("Int64")
    df["SG_PARTIDO"] = df["NR_PARTIDO"].map(MAPA_PARTIDO)
    df = df.dropna(subset=["SG_PARTIDO"])
    df["PARTIDO"] = df["SG_PARTIDO"].map(normalizar_partido)
    df["ESCORE"] = df["PARTIDO"].map(ESCORE_BOLOGNESI)
    df["BLOCO"] = df["PARTIDO"].map(
        lambda p: bloco_quintipartite(ESCORE_BOLOGNESI[p])
        if p in ESCORE_BOLOGNESI
        else "DESCONHECIDO"
    )
    return df[df["NR_ZONA"].isin(ZONAS_ALVO.keys())].copy()


def escore_e_dominio_por_secao(df: pd.DataFrame, cargo: str) -> pd.DataFrame:
    sub = df[df["DS_CARGO"].str.upper() == cargo.upper()].copy()
    sub = sub.dropna(subset=["ESCORE"])

    # Escore médio ponderado por seção
    escore = sub.groupby(["NR_ZONA", "NR_SECAO"]).apply(
        lambda g: (g["ESCORE"] * g["QT_VOTOS"]).sum() / g["QT_VOTOS"].sum()
        if g["QT_VOTOS"].sum() > 0
        else float("nan"),
        include_groups=False,
    ).rename("escore")

    # % votos esquerda e direita por seção
    mapa_bipartite = {
        "ESQUERDA": "ESQ",
        "CENTRO-ESQUERDA": "ESQ",
        "CENTRO": "C",
        "CENTRO-DIREITA": "DIR",
        "DIREITA": "DIR",
    }
    sub["LADO"] = sub["BLOCO"].map(mapa_bipartite)
    lados = (
        sub.groupby(["NR_ZONA", "NR_SECAO", "LADO"])["QT_VOTOS"]
        .sum()
        .unstack(fill_value=0)
    )
    for c in ["ESQ", "DIR", "C"]:
        if c not in lados.columns:
            lados[c] = 0
    lados["total"] = lados[["ESQ", "DIR", "C"]].sum(axis=1)
    lados["pct_esq"] = lados["ESQ"] / lados["total"] * 100
    lados["pct_dir"] = lados["DIR"] / lados["total"] * 100
    lados["esq_maior"] = lados["pct_esq"] > lados["pct_dir"]

    out = pd.concat([escore, lados[["pct_esq", "pct_dir", "esq_maior", "total"]]], axis=1)
    out = out.reset_index()
    out["zona_nome"] = out["NR_ZONA"].map(ZONAS_ALVO)
    return out


df_2020 = carregar_secao_sp(2020)
df_2024 = carregar_secao_sp(2024)

for cargo in ["PREFEITO", "VEREADOR"]:
    print(f"\n{'=' * 85}")
    print(f"  {cargo} — seções das zonas ricas")
    print(f"{'=' * 85}")

    sec_2020 = escore_e_dominio_por_secao(df_2020, cargo)
    sec_2024 = escore_e_dominio_por_secao(df_2024, cargo)

    print(f"\nTotal de seções analisadas 2020: {len(sec_2020)} | 2024: {len(sec_2024)}")

    # Por zona: quantas seções tem esquerda majoritária
    tab_zona = sec_2024.groupby(["NR_ZONA", "zona_nome"]).agg(
        n_secoes=("NR_SECAO", "count"),
        escore_medio=("escore", "mean"),
        escore_min=("escore", "min"),
        escore_max=("escore", "max"),
        n_esq_maior=("esq_maior", "sum"),
    ).round(3)
    tab_zona["%_esq_maior"] = (tab_zona["n_esq_maior"] / tab_zona["n_secoes"] * 100).round(1)
    print(f"\nResumo por zona (2024):")
    print(tab_zona.to_string())

    # Top 10 seções mais à esquerda e mais à direita (2024)
    print(f"\nTop 10 seções MAIS À ESQUERDA em 2024:")
    mais_esq = sec_2024.nsmallest(10, "escore")[
        ["zona_nome", "NR_SECAO", "escore", "pct_esq", "pct_dir", "total"]
    ]
    print(mais_esq.to_string(index=False, float_format=lambda x: f"{x:7.2f}"))

    print(f"\nTop 10 seções MAIS À DIREITA em 2024:")
    mais_dir = sec_2024.nlargest(10, "escore")[
        ["zona_nome", "NR_SECAO", "escore", "pct_esq", "pct_dir", "total"]
    ]
    print(mais_dir.to_string(index=False, float_format=lambda x: f"{x:7.2f}"))

    # Seções que mudaram de lado 2020 → 2024
    merged = sec_2020.merge(
        sec_2024, on=["NR_ZONA", "NR_SECAO"], suffixes=("_2020", "_2024")
    )
    mudaram_para_dir = merged[
        merged["esq_maior_2020"] & ~merged["esq_maior_2024"]
    ]
    mudaram_para_esq = merged[
        ~merged["esq_maior_2020"] & merged["esq_maior_2024"]
    ]
    print(f"\nSeções que mudaram:")
    print(f"  ESQ → DIR: {len(mudaram_para_dir)}")
    print(f"  DIR → ESQ: {len(mudaram_para_esq)}")
    print(f"  Estáveis ESQ: {(merged['esq_maior_2020'] & merged['esq_maior_2024']).sum()}")
    print(f"  Estáveis DIR: {(~merged['esq_maior_2020'] & ~merged['esq_maior_2024']).sum()}")
    print(f"  Total seções comuns: {len(merged)}")

    # Salva CSV
    sec_2024.to_csv(f"outputs/secoes_zonas_ricas_{cargo.lower()}_2024.csv", index=False)
    merged.to_csv(f"outputs/secoes_zonas_ricas_{cargo.lower()}_trajetoria.csv", index=False)
    print(f"\nCSVs: outputs/secoes_zonas_ricas_{cargo.lower()}_2024.csv + _trajetoria.csv")
