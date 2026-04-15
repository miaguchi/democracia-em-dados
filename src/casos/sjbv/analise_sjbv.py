"""Análise de volatilidade ideológica — São João da Boa Vista, 2020→2024.

Cidade pequena (1 zona eleitoral, ~45k votos válidos), só faz sentido
análise temporal e decomposição ideológica. Espacial é inaplicável.
"""

from pathlib import Path

import pandas as pd

from src.partidario.analise_volatilidade import normalizar_partido, pedersen
from src.partidario.ideologia import (
    ESCORE_BOLOGNESI,
    usar_quintipartite,
    usar_tripartite,
    volatilidade_decomposta,
    votos_por_bloco,
)

CD_TSE_SJBV = 70831


def carregar(ano: int, cargo: str) -> pd.DataFrame:
    df = pd.read_parquet(
        f"data/processed/votacao_partido_munzona_{ano}_SP.parquet"
    )
    filtro = (
        (df["CD_MUNICIPIO"] == CD_TSE_SJBV)
        & (df["DS_CARGO"].str.upper() == cargo.upper())
        & (df["NR_TURNO"] == 1)
    )
    sub = df.loc[
        filtro,
        ["SG_PARTIDO", "QT_VOTOS_NOMINAIS_VALIDOS", "QT_VOTOS_LEGENDA_VALIDOS"],
    ].copy()
    sub["VOTOS"] = sub["QT_VOTOS_NOMINAIS_VALIDOS"] + sub["QT_VOTOS_LEGENDA_VALIDOS"]
    sub["PARTIDO"] = sub["SG_PARTIDO"].map(normalizar_partido)
    return sub


def tabela_votos(df: pd.DataFrame) -> pd.Series:
    return df.groupby("PARTIDO")["VOTOS"].sum().sort_values(ascending=False)


def escore_ponderado(votos: pd.Series) -> float:
    escores = votos.index.map(ESCORE_BOLOGNESI.get)
    tab = pd.DataFrame({"votos": votos.values, "escore": escores})
    tab = tab.dropna()
    return (tab["escore"] * tab["votos"]).sum() / tab["votos"].sum()


def relatorio(cargo: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  SÃO JOÃO DA BOA VISTA — {cargo}")
    print(f"{'=' * 60}")

    df_2020 = carregar(2020, cargo)
    df_2024 = carregar(2024, cargo)
    v_2020 = tabela_votos(df_2020)
    v_2024 = tabela_votos(df_2024)

    def linha_partidos(ano, v):
        total = v.sum()
        print(f"\n  {ano} (total {total:,} votos):")
        for p, n in v.items():
            escore = ESCORE_BOLOGNESI.get(p)
            es = f"escore {escore:.2f}" if escore is not None else "sem escore"
            print(f"    {p:<22} {n:>7,}  {n/total*100:>5.1f}%   {es}")

    linha_partidos(2020, v_2020)
    linha_partidos(2024, v_2024)

    # Pedersen bruto
    vt = pedersen(v_2020, v_2024)
    print(f"\n  Pedersen bruto: {vt:.4f}")

    # Decomposição em 3 blocos
    usar_tripartite()
    t3, e3, d3 = volatilidade_decomposta(v_2020, v_2024)
    print(f"\n  3 blocos: V_entre={e3:.4f} ({e3/t3*100:.1f}%)  V_dentro={d3:.4f}")
    b3_2020 = votos_por_bloco(v_2020) / v_2020.sum() * 100
    b3_2024 = votos_por_bloco(v_2024) / v_2024.sum() * 100
    print("    Distribuição (%):")
    tab3 = pd.DataFrame({"2020": b3_2020, "2024": b3_2024}).fillna(0).round(2)
    print(tab3.to_string().replace("\n", "\n    "))

    # Decomposição em 5 blocos
    usar_quintipartite()
    t5, e5, d5 = volatilidade_decomposta(v_2020, v_2024)
    print(f"\n  5 blocos: V_entre={e5:.4f} ({e5/t5*100:.1f}%)  V_dentro={d5:.4f}")
    b5_2020 = votos_por_bloco(v_2020) / v_2020.sum() * 100
    b5_2024 = votos_por_bloco(v_2024) / v_2024.sum() * 100
    print("    Distribuição (%):")
    tab5 = pd.DataFrame({"2020": b5_2020, "2024": b5_2024}).fillna(0).round(2)
    ordem = ["ESQUERDA", "CENTRO-ESQUERDA", "CENTRO", "CENTRO-DIREITA", "DIREITA", "DESCONHECIDO"]
    tab5 = tab5.reindex([x for x in ordem if x in tab5.index])
    print(tab5.to_string().replace("\n", "\n    "))

    # Escore médio
    e_2020 = escore_ponderado(v_2020)
    e_2024 = escore_ponderado(v_2024)
    print(f"\n  Escore médio ponderado (0=extrema-esq, 10=extrema-dir):")
    print(f"    2020: {e_2020:.3f}")
    print(f"    2024: {e_2024:.3f}")
    print(f"    Δ   : {e_2024 - e_2020:+.3f}")


relatorio("PREFEITO")
relatorio("VEREADOR")
