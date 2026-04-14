"""Trajetória individual de candidatos a vereador nas zonas ricas de SP 2012-2024.

Para cada par (ano, zona), identifica o top 6 candidatos por votos naquela
zona e cruza com a prestação de contas daquele ano para mostrar a
composição percentual de receita (PF, partido, PJ quando existia,
próprio, crowdfund quando existia).

Objetivo: testar se os candidatos PSDB que dominavam Pinheiros e
Indianópolis em 2012 captavam PF em percentual mais alto que os
candidatos PL/PP que ocuparam o mesmo espaço em 2024.
"""

from pathlib import Path

import pandas as pd

from trajetoria_financiamento import carregar_todos as carregar_receitas

ZONAS_ALVO = {
    1: "Bela Vista",
    2: "Perdizes",
    5: "Jardim Paulista",
    6: "Vila Mariana",
    251: "Pinheiros",
    258: "Indianópolis",
    346: "Butantã",
}

CODIGO_TSE_SP = 71072
ANOS = [2012, 2016, 2020, 2024]

OUT = Path("outputs")


def carregar_votos_candidato(ano: int) -> pd.DataFrame:
    """Votos por candidato-zona para vereador em SP em um ano."""
    df = pd.read_parquet(f"data/processed/votacao_candidato_munzona_{ano}_SP.parquet")
    df = df[
        (df["CD_MUNICIPIO"] == CODIGO_TSE_SP)
        & (df["DS_CARGO"].str.upper() == "VEREADOR")
        & (df["NR_TURNO"] == 1)
    ].copy()
    # Coluna de votos — nome pode variar por ano
    candidatas = [
        "QT_VOTOS_NOMINAIS_VALIDOS",
        "QT_VOTOS_NOMINAIS",
        "QT_VOTOS",
    ]
    for col in candidatas:
        if col in df.columns:
            df["VOTOS"] = df[col]
            return df[["NR_ZONA", "SQ_CANDIDATO", "NM_CANDIDATO", "SG_PARTIDO", "VOTOS"]]
    raise KeyError(f"{ano}: nenhuma coluna de votos encontrada")


def top_candidatos_zona(df_votos: pd.DataFrame, zona: int, n: int = 6) -> pd.DataFrame:
    sub = df_votos[df_votos["NR_ZONA"] == zona]
    return (
        sub.groupby(["SQ_CANDIDATO", "NM_CANDIDATO", "SG_PARTIDO"])["VOTOS"]
        .sum()
        .reset_index()
        .sort_values("VOTOS", ascending=False)
        .head(n)
    )


def composicao_receitas(rec: pd.DataFrame, sq_candidato: str) -> dict:
    """Retorna dicionário com % por categoria para um candidato."""
    sub = rec[rec["sq_candidato"] == str(sq_candidato)]
    tot = sub["valor"].sum()
    if tot <= 0:
        return {"total": 0, "pf": 0, "partido": 0, "pj": 0, "proprio": 0, "crowdfund": 0}
    por_cat = sub.groupby("categoria")["valor"].sum()
    return {
        "total": tot,
        "pf": por_cat.get("pf", 0) / tot * 100,
        "partido": por_cat.get("partido", 0) / tot * 100,
        "pj": por_cat.get("pj", 0) / tot * 100,
        "proprio": por_cat.get("proprio", 0) / tot * 100,
        "crowdfund": por_cat.get("crowdfund", 0) / tot * 100,
        "outros_cand": por_cat.get("outros_cand", 0) / tot * 100,
    }


def construir_tabela() -> pd.DataFrame:
    print("Carregando receitas 2012-2024...")
    rec = carregar_receitas()
    print(f"Receitas: {len(rec):,} linhas")

    linhas = []
    for ano in ANOS:
        rec_ano = rec[rec["ano"] == ano]
        votos = carregar_votos_candidato(ano)
        for zona, nome_bairro in ZONAS_ALVO.items():
            tops = top_candidatos_zona(votos, zona, n=6)
            for _, r in tops.iterrows():
                comp = composicao_receitas(rec_ano, r["SQ_CANDIDATO"])
                linhas.append(
                    {
                        "ano": ano,
                        "zona": zona,
                        "bairro": nome_bairro,
                        "sq_candidato": r["SQ_CANDIDATO"],
                        "nome": r["NM_CANDIDATO"],
                        "partido": r["SG_PARTIDO"],
                        "votos_zona": int(r["VOTOS"]),
                        "receita_k": comp["total"] / 1000,
                        "pct_partido": comp["partido"],
                        "pct_pf": comp["pf"],
                        "pct_pj": comp["pj"],
                        "pct_proprio": comp["proprio"],
                        "pct_crowdfund": comp["crowdfund"],
                        "pct_outros_cand": comp["outros_cand"],
                    }
                )
    return pd.DataFrame(linhas)


def imprimir(tab: pd.DataFrame) -> None:
    for ano in ANOS:
        for zona, bairro in ZONAS_ALVO.items():
            sub = tab[(tab["ano"] == ano) & (tab["zona"] == zona)].head(4)
            if sub.empty:
                continue
            print(f"\n--- {ano} · Z{zona} {bairro} ---")
            for _, r in sub.iterrows():
                nome = str(r["nome"])[:28]
                print(
                    f"  {int(r['votos_zona']):>5}v  {nome:<30} "
                    f"{r['partido']:<10} R${r['receita_k']:>6.0f}k  "
                    f"PF:{r['pct_pf']:4.0f}% Partido:{r['pct_partido']:4.0f}% "
                    f"PJ:{r['pct_pj']:4.0f}% Próp:{r['pct_proprio']:4.0f}% "
                    f"FC:{r['pct_crowdfund']:4.0f}%"
                )


def resumo_por_partido_zona(tab: pd.DataFrame) -> pd.DataFrame:
    """Média de % PF e % PJ dos top candidatos por (ano, partido, zona)."""
    agg = (
        tab.groupby(["ano", "zona", "partido"])
        .agg(
            n_cand=("sq_candidato", "count"),
            votos_tot=("votos_zona", "sum"),
            pct_pf_medio=("pct_pf", "mean"),
            pct_pj_medio=("pct_pj", "mean"),
            pct_partido_medio=("pct_partido", "mean"),
            receita_k_mediana=("receita_k", "median"),
        )
        .reset_index()
    )
    return agg


if __name__ == "__main__":
    tab = construir_tabela()
    imprimir(tab)
    OUT.mkdir(parents=True, exist_ok=True)
    tab.to_csv(OUT / "trajetoria_candidatos_zonas_ricas.csv", index=False)
    print(f"\nCSV: {OUT/'trajetoria_candidatos_zonas_ricas.csv'}")

    # Resumo focado em Pinheiros e Indianópolis
    print("\n\n" + "=" * 100)
    print("  TRAJETÓRIA: % MÉDIO DE PF/PJ/PARTIDO DO PSDB E SUCESSORES EM Z251/Z258")
    print("=" * 100)
    resumo = tab[tab["zona"].isin([251, 258])].copy()
    for zona in [251, 258]:
        print(f"\n  Zona {zona}:")
        for ano in ANOS:
            sub = resumo[(resumo["zona"] == zona) & (resumo["ano"] == ano)]
            if sub.empty:
                continue
            # Média ponderada por votos
            pf_medio = (sub["pct_pf"] * sub["votos_zona"]).sum() / sub["votos_zona"].sum()
            pj_medio = (sub["pct_pj"] * sub["votos_zona"]).sum() / sub["votos_zona"].sum()
            partido_medio = (sub["pct_partido"] * sub["votos_zona"]).sum() / sub["votos_zona"].sum()
            partidos = ", ".join(sub["partido"].unique()[:6])
            print(
                f"    {ano}: PF={pf_medio:5.1f}% Partido={partido_medio:5.1f}% "
                f"PJ={pj_medio:5.1f}%  ({partidos})"
            )
