"""Financiamento eleitoral dos vereadores por zona — SP 2024.

Cruza a prestação de contas eleitorais do TSE (receitas_candidatos_2024_SP)
com a votação por seção (votacao_secao_2024_SP), para cada uma das 8 zonas
do corredor universitário + 4 zonas de comparação (Vila Maria, Perus,
Cidade Tiradentes, Vila Sabrina).

Para cada zona, lista os 6 candidatos a vereador mais votados naquela
zona com a composição percentual das suas receitas (pessoa física,
recursos de partido, financiamento coletivo, recursos próprios).

Pergunta: o perfil de doador dos vereadores com alta performance em
Pinheiros/Bela Vista/Perdizes (redutos de esquerda nas zonas ricas)
difere do perfil de doador dos vereadores com alta performance em
Indianópolis/Vila Maria (redutos de direita)?

Achado central: sim.
- Zonas ricas progressistas: 16-28% das receitas vêm de PF, +
  financiamento coletivo (crowdfunding) visível (até 8%)
- Zonas ricas conservadoras: pessoa física residual (0-4%), zero
  crowdfunding, 96-100% FEFC via partido
- Periferia popular: ~100% partido independentemente do campo; a
  infraestrutura de doadores PF simplesmente não existe fora do
  corredor cultural-universitário

Entra como evidência para H3 (a recomposição da direita pós-2020
envolveu desconexão do eleitor-doador local) e H4 (o voto de esquerda
nos bairros ricos tem infraestrutura material distinta, não só
posicionamento ideológico).
"""

from pathlib import Path

import pandas as pd

ZONAS_ALVO = {
    # Zonas ricas / corredor universitário
    1: "Bela Vista",
    2: "Perdizes",
    3: "Santa Ifigênia",
    5: "Jardim Paulista",
    6: "Vila Mariana",
    251: "Pinheiros",
    258: "Indianópolis",
    346: "Butantã",
    # Zonas de comparação (redutos de direita periférica e esquerda periférica)
    254: "Vila Maria",
    389: "Perus",
    404: "Cidade Tiradentes",
    420: "Vila Sabrina",
}

CSV_RECEITAS = Path(
    "data/raw/prestacao_contas/2024_SP/receitas_candidatos_2024_SP.csv"
)
PARQUET_VOTOS = Path("data/processed/votacao_secao_2024_SP.parquet")
PARQUET_REC = Path("data/processed/receitas_vereador_sp_2024.parquet")
SAIDA_CSV = Path("outputs/financiamento_zonas_ricas.csv")


def processar_receitas_sp() -> pd.DataFrame:
    """Filtra e salva as receitas de vereador SP como parquet (reutilizável)."""
    if PARQUET_REC.exists():
        return pd.read_parquet(PARQUET_REC)

    print(f"Lendo {CSV_RECEITAS}...")
    rec = pd.read_csv(
        CSV_RECEITAS,
        sep=";",
        encoding="latin-1",
        low_memory=False,
        usecols=[
            "SQ_CANDIDATO",
            "NM_CANDIDATO",
            "SG_PARTIDO",
            "DS_CARGO",
            "NM_UE",
            "DS_FONTE_RECEITA",
            "DS_ORIGEM_RECEITA",
            "NM_DOADOR",
            "NR_CPF_CNPJ_DOADOR",
            "VR_RECEITA",
        ],
    )
    ver = rec[
        (rec["NM_UE"].str.upper() == "SÃO PAULO")
        & (rec["DS_CARGO"].str.upper() == "VEREADOR")
    ].copy()
    ver["VR_RECEITA"] = pd.to_numeric(
        ver["VR_RECEITA"].astype(str).str.replace(",", "."), errors="coerce"
    )
    PARQUET_REC.parent.mkdir(parents=True, exist_ok=True)
    ver.to_parquet(PARQUET_REC, index=False)
    return ver


def candidatos_vereador_sp() -> pd.DataFrame:
    """Votos por (candidato, zona) para vereador SP 2024 — só candidatos reais."""
    df = pd.read_parquet(PARQUET_VOTOS)
    df = df[
        (df["NM_MUNICIPIO"] == "SÃO PAULO")
        & (df["DS_CARGO"].str.upper() == "VEREADOR")
        & (df["NR_TURNO"] == 1)
    ]
    df = df.dropna(subset=["SQ_CANDIDATO"])
    df = df[df["SQ_CANDIDATO"] > 0]
    df["NR_VOTAVEL"] = pd.to_numeric(df["NR_VOTAVEL"], errors="coerce")
    # Votos em candidato (5 dígitos) — descarta votos em legenda, brancos, nulos
    df = df[df["NR_VOTAVEL"] >= 10000]
    return (
        df.groupby(["SQ_CANDIDATO", "NM_VOTAVEL", "NR_ZONA"])["QT_VOTOS"]
        .sum()
        .reset_index()
    )


def montar_tabela() -> pd.DataFrame:
    rec = processar_receitas_sp()
    rec["FONTE"] = rec["DS_ORIGEM_RECEITA"].str.strip()
    rec_fonte = (
        rec.groupby(["SQ_CANDIDATO", "FONTE"])["VR_RECEITA"].sum().unstack(fill_value=0)
    )
    rec_total = rec.groupby("SQ_CANDIDATO")["VR_RECEITA"].sum().rename("receita_total")
    partido = rec.drop_duplicates("SQ_CANDIDATO").set_index("SQ_CANDIDATO")["SG_PARTIDO"]

    votos_cz = candidatos_vereador_sp()
    tot_cand = (
        votos_cz.groupby(["SQ_CANDIDATO", "NM_VOTAVEL"])["QT_VOTOS"]
        .sum()
        .reset_index()
        .rename(columns={"QT_VOTOS": "total_votos"})
    )
    cand = tot_cand.merge(rec_total, on="SQ_CANDIDATO", how="left").fillna(
        {"receita_total": 0}
    )
    cand = cand.merge(rec_fonte, left_on="SQ_CANDIDATO", right_index=True, how="left").fillna(
        0
    )
    cand["partido"] = cand["SQ_CANDIDATO"].map(partido).fillna("-")
    return cand, votos_cz


def ranking_por_zona(cand: pd.DataFrame, votos_cz: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for zona, nome in ZONAS_ALVO.items():
        na_zona = (
            votos_cz[votos_cz["NR_ZONA"] == zona]
            .sort_values("QT_VOTOS", ascending=False)
            .head(6)
        )
        top = na_zona.merge(
            cand[
                [
                    "SQ_CANDIDATO",
                    "total_votos",
                    "receita_total",
                    "partido",
                    "Recursos de partido político",
                    "Recursos de pessoas físicas",
                    "Recursos próprios",
                    "Recursos de Financiamento Coletivo",
                ]
            ],
            on="SQ_CANDIDATO",
            how="left",
        )
        top["zona"] = zona
        top["zona_nome"] = nome
        top["pct_partido"] = (
            top["Recursos de partido político"] / top["receita_total"].replace(0, 1) * 100
        )
        top["pct_pf"] = (
            top["Recursos de pessoas físicas"] / top["receita_total"].replace(0, 1) * 100
        )
        top["pct_proprio"] = (
            top["Recursos próprios"] / top["receita_total"].replace(0, 1) * 100
        )
        top["pct_crowdfund"] = (
            top["Recursos de Financiamento Coletivo"]
            / top["receita_total"].replace(0, 1)
            * 100
        )
        linhas.append(top)
    return pd.concat(linhas, ignore_index=True)


def imprimir(ranking: pd.DataFrame) -> None:
    for zona, nome in ZONAS_ALVO.items():
        sub = ranking[ranking["zona"] == zona]
        print(f"\n{'=' * 115}")
        print(f"  Z{zona} {nome.upper()} — top 6 candidatos a vereador 2024 (por votos na zona)")
        print(f"{'=' * 115}")
        for _, r in sub.iterrows():
            nome_c = str(r["NM_VOTAVEL"])[:30]
            rec_k = r["receita_total"] / 1000
            print(
                f"  {int(r['QT_VOTOS']):>5}v  {nome_c:<32} "
                f"{r['partido']:<12} R${rec_k:>6.0f}k  "
                f"PF:{r['pct_pf']:4.0f}% Partido:{r['pct_partido']:4.0f}% "
                f"Próprio:{r['pct_proprio']:3.0f}% FinColet:{r['pct_crowdfund']:4.0f}%"
            )


if __name__ == "__main__":
    cand, votos_cz = montar_tabela()
    ranking = ranking_por_zona(cand, votos_cz)
    imprimir(ranking)

    SAIDA_CSV.parent.mkdir(parents=True, exist_ok=True)
    ranking.to_csv(SAIDA_CSV, index=False)
    print(f"\nCSV salvo: {SAIDA_CSV}")

    # Síntese: médias por "tipo de zona"
    grupos = {
        "ricas progressistas (1, 2, 251)": [1, 2, 251],
        "ricas conservadoras (5, 258)": [5, 258],
        "outras ricas (3, 6, 346)": [3, 6, 346],
        "periferia direita (254, 420)": [254, 420],
        "periferia esquerda (389, 404)": [389, 404],
    }
    print(f"\n{'=' * 85}")
    print("  Perfil médio de financiamento por tipo de zona (top 6 candidatos)")
    print(f"{'=' * 85}")
    linhas = []
    for grupo, zonas in grupos.items():
        sub = ranking[ranking["zona"].isin(zonas)]
        linha = {
            "grupo": grupo,
            "pct_pf_medio": sub["pct_pf"].mean(),
            "pct_partido_medio": sub["pct_partido"].mean(),
            "pct_crowdfund_medio": sub["pct_crowdfund"].mean(),
            "pct_proprio_medio": sub["pct_proprio"].mean(),
        }
        linhas.append(linha)
        print(
            f"  {grupo:<35} PF:{linha['pct_pf_medio']:4.1f}% "
            f"Partido:{linha['pct_partido_medio']:5.1f}% "
            f"FC:{linha['pct_crowdfund_medio']:4.2f}% "
            f"Próp:{linha['pct_proprio_medio']:4.1f}%"
        )
    pd.DataFrame(linhas).to_csv("outputs/financiamento_grupos.csv", index=False)
