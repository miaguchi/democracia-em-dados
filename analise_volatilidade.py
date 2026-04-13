"""Volatilidade eleitoral (Pedersen) — São Paulo, vereador, 2020 vs 2024."""

from pathlib import Path

import pandas as pd

from src.ingestao.tse_downloader import TSEDownloader

CODIGO_TSE_SAO_PAULO = 71072
CARGO_VEREADOR = "VEREADOR"
CARGO_PREFEITO = "PREFEITO"

# Federações ativas em 2024 (obtidas do próprio parquet, coluna SG_FEDERACAO).
# Cada membro da federação é agrupado sob o rótulo da federação, e o mesmo
# agrupamento é aplicado retroativamente em 2020 para tornar a comparação justa.
FEDERACOES_2024 = {
    "PT": "FED_PT_PCDOB_PV",
    "PC do B": "FED_PT_PCDOB_PV",
    "PV": "FED_PT_PCDOB_PV",
    "PSDB": "FED_PSDB_CIDADANIA",
    "CIDADANIA": "FED_PSDB_CIDADANIA",
    "PSOL": "FED_PSOL_REDE",
    "REDE": "FED_PSOL_REDE",
}

# Fusões e renomeações partidárias entre 2020 e 2024 (partidos que deixaram de
# existir e foram absorvidos por outro). Lista conservadora — expandir conforme
# for validando com fontes oficiais.
FUSOES_2020_PARA_2024 = {
    "DEM": "UNIÃO",
    "PSL": "UNIÃO",
    "PROS": "SOLIDARIEDADE",
    "PATRIOTA": "PRD",
    "PTB": "PRD",
    "PTC": "AGIR",
    "PSC": "PODE",
}


def normalizar_partido(sigla: str) -> str:
    sigla = FUSOES_2020_PARA_2024.get(sigla, sigla)
    return FEDERACOES_2024.get(sigla, sigla)


def garantir_dados() -> None:
    d = TSEDownloader(
        raw_dir=Path("data/raw"), processed_dir=Path("data/processed")
    )
    d.ingerir("votacao_partido_munzona", 2020, uf="SP")
    d.ingerir("votacao_partido_munzona", 2024, uf="SP")


def carregar_sp(ano: int, cargo: str = CARGO_VEREADOR) -> pd.DataFrame:
    parquet = Path(f"data/processed/votacao_partido_munzona_{ano}_SP.parquet")
    df = pd.read_parquet(parquet)
    filtro = (
        (df["CD_MUNICIPIO"] == CODIGO_TSE_SAO_PAULO)
        & (df["DS_CARGO"].str.upper() == cargo.upper())
        & (df["NR_TURNO"] == 1)
    )
    sub = df.loc[filtro, ["NR_ZONA", "SG_PARTIDO", "QT_VOTOS_NOMINAIS_VALIDOS", "QT_VOTOS_LEGENDA_VALIDOS"]].copy()
    sub["VOTOS"] = sub["QT_VOTOS_NOMINAIS_VALIDOS"] + sub["QT_VOTOS_LEGENDA_VALIDOS"]
    sub["PARTIDO"] = sub["SG_PARTIDO"].map(normalizar_partido)
    return sub


def carregar_sp_vereador(ano: int) -> pd.DataFrame:
    return carregar_sp(ano, CARGO_VEREADOR)


def carregar_sp_prefeito(ano: int) -> pd.DataFrame:
    return carregar_sp(ano, CARGO_PREFEITO)


def votos_por_partido(df: pd.DataFrame) -> pd.Series:
    return df.groupby("PARTIDO")["VOTOS"].sum().sort_values(ascending=False)


def votos_por_zona_partido(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(["NR_ZONA", "PARTIDO"])["VOTOS"].sum().unstack(fill_value=0)


def pedersen(anterior: pd.Series, atual: pd.Series) -> float:
    p_ant = anterior / anterior.sum()
    p_atu = atual / atual.sum()
    partidos = p_ant.index.union(p_atu.index)
    return 0.5 * (
        p_ant.reindex(partidos, fill_value=0) - p_atu.reindex(partidos, fill_value=0)
    ).abs().sum()


def pedersen_por_zona(matriz_ant: pd.DataFrame, matriz_atu: pd.DataFrame) -> pd.Series:
    partidos = matriz_ant.columns.union(matriz_atu.columns)
    m_ant = matriz_ant.reindex(columns=partidos, fill_value=0)
    m_atu = matriz_atu.reindex(columns=partidos, fill_value=0)
    # Mantém apenas zonas presentes nas duas eleições (exclui extintas/criadas).
    zonas = m_ant.index.intersection(m_atu.index)
    m_ant = m_ant.loc[zonas]
    m_atu = m_atu.loc[zonas]
    p_ant = m_ant.div(m_ant.sum(axis=1), axis=0).fillna(0)
    p_atu = m_atu.div(m_atu.sum(axis=1), axis=0).fillna(0)
    return 0.5 * (p_ant - p_atu).abs().sum(axis=1)


def main() -> None:
    garantir_dados()
    df_2020 = carregar_sp_vereador(2020)
    df_2024 = carregar_sp_vereador(2024)

    volatilidade_cidade = pedersen(
        votos_por_partido(df_2020), votos_por_partido(df_2024)
    )
    print(
        f"Volatilidade (Pedersen) SP vereador 2020→2024 — cidade: "
        f"{volatilidade_cidade:.4f}"
    )

    vol_zona = pedersen_por_zona(
        votos_por_zona_partido(df_2020), votos_por_zona_partido(df_2024)
    ).sort_values(ascending=False)

    print(f"\nZonas analisadas: {len(vol_zona)}")
    print(
        f"Média: {vol_zona.mean():.4f} | mediana: {vol_zona.median():.4f} | "
        f"dp: {vol_zona.std():.4f}"
    )
    print(
        f"Mín: {vol_zona.min():.4f} (zona {vol_zona.idxmin()}) | "
        f"Máx: {vol_zona.max():.4f} (zona {vol_zona.idxmax()})"
    )
    print("\nTop 10 zonas mais voláteis:")
    print(vol_zona.head(10))
    print("\nTop 10 zonas mais estáveis:")
    print(vol_zona.tail(10))


if __name__ == "__main__":
    main()
