"""Perfil dos candidatos a vereador por tipo de zona em SP 2024.

Análise da composição sociodemográfica e ocupacional dos candidatos
cujo voto se concentra nas zonas do corredor universitário vs outras
zonas. Testa se há um "perfil vencedor" distinto entre bairros com
alto índice institucional vs baixo.

Dados:
- consulta_cand_2024_SP.parquet (metadados de candidatos)
- votacao_candidato_munzona_2024_SP.parquet (votos por zona)
- indice_institucional_por_zona.csv (índice institucional)
"""

from pathlib import Path

import pandas as pd

from src.ingestao.tse_downloader import TSEDownloader


def carregar_cand():
    """consulta_cand com metadados (baixa se não tiver)."""
    p = Path("data/processed/consulta_cand_2024_SP.parquet")
    if not p.exists():
        d = TSEDownloader(raw_dir=Path("data/raw"), processed_dir=Path("data/processed"))
        d.ingerir("consulta_cand", 2024, uf="SP")
    df = pd.read_parquet(p)
    df = df[
        (df["NM_UE"] == "SÃO PAULO")
        & (df["DS_CARGO"].str.upper() == "VEREADOR")
        & (df["NR_TURNO"] == 1)
    ].copy()
    # Garante uma linha por candidato (o arquivo pode repetir por turno)
    df = df.drop_duplicates("SQ_CANDIDATO")
    return df[
        [
            "SQ_CANDIDATO",
            "NM_URNA_CANDIDATO",
            "NM_CANDIDATO",
            "SG_PARTIDO",
            "DS_GENERO",
            "DS_GRAU_INSTRUCAO",
            "DS_OCUPACAO",
            "DS_COR_RACA",
            "DS_ESTADO_CIVIL",
            "DT_NASCIMENTO",
        ]
    ]


def carregar_votos_zona():
    df = pd.read_parquet("data/processed/votacao_candidato_munzona_2024_SP.parquet")
    df = df[
        (df["CD_MUNICIPIO"] == 71072)
        & (df["DS_CARGO"].str.upper() == "VEREADOR")
        & (df["NR_TURNO"] == 1)
    ].copy()
    col = "QT_VOTOS_NOMINAIS_VALIDOS" if "QT_VOTOS_NOMINAIS_VALIDOS" in df.columns else "QT_VOTOS"
    df["VOTOS"] = df[col]
    return df.groupby(["SQ_CANDIDATO", "NR_ZONA"])["VOTOS"].sum().reset_index()


CATEGORIAS_OCUPACAO = {
    "academia_cultura": [
        "PROFESSOR", "PROFESSORA", "PESQUISADOR", "ECONOMISTA", "CIENTISTA",
        "HISTORIADOR", "SOCIÓLOGO", "FILOSOFO", "ARTISTA", "ESCRITOR",
        "JORNALISTA", "PSICÓLOGO", "ANTROPOLOGO", "LINGUISTA", "MUSICO",
        "ATOR", "ATRIZ", "DIRETOR TEATRO", "CINEASTA", "POETA",
    ],
    "profissional_liberal": [
        "ADVOGADO", "ADVOGADA", "ENGENHEIRO", "ENGENHEIRA", "MÉDICO",
        "MEDICA", "DENTISTA", "ARQUITETO", "ARQUITETA", "CONTADOR",
        "VETERINÁRIO", "FISIOTERAPEUTA", "FARMACÊUTICO",
    ],
    "empresario": [
        "EMPRESÁRIO", "EMPRESARIA", "EMPREENDEDOR", "COMERCIANTE",
        "INDUSTRIAL", "ADMINISTRADOR DE EMPRESAS",
    ],
    "servidor_publico": [
        "SERVIDOR", "FUNCIONÁRIO PÚBLICO", "AGENTE PÚBLICO",
        "ANALISTA", "FISCAL", "AUDITOR",
    ],
    "religioso": [
        "PASTOR", "PADRE", "BISPO", "MISSIONARIO", "SACERDOTE", "RABINO",
        "EVANGELISTA",
    ],
    "saude": [
        "ENFERMEIRO", "ENFERMEIRA", "TÉCNICO EM ENFERMAGEM",
    ],
    "politico": [
        "VEREADOR", "PREFEITO", "DEPUTADO", "POLÍTICO", "ADMINISTRADOR",
    ],
    "outros_tecnicos": [
        "TÉCNICO", "ANALISTA DE SISTEMAS", "PROGRAMADOR",
    ],
}


def categorizar_ocupacao(ocup: str) -> str:
    if not isinstance(ocup, str):
        return "outros"
    up = ocup.upper()
    for cat, termos in CATEGORIAS_OCUPACAO.items():
        for t in termos:
            if t in up:
                return cat
    return "outros"


if __name__ == "__main__":
    cand = carregar_cand()
    print(f"Candidatos a vereador SP 2024: {len(cand):,}")
    cand["SQ_CANDIDATO"] = cand["SQ_CANDIDATO"].astype(int)
    cand["categoria_ocup"] = cand["DS_OCUPACAO"].map(categorizar_ocupacao)

    print("\nDistribuição de categoria de ocupação (todos os candidatos):")
    print(cand["categoria_ocup"].value_counts())

    votos = carregar_votos_zona()
    votos["SQ_CANDIDATO"] = votos["SQ_CANDIDATO"].astype(int)

    # Índice institucional por zona
    idx = pd.read_csv("outputs/indice_institucional_por_zona.csv").set_index("NR_ZONA")
    # Classifica zonas em 3 categorias pelo índice
    idx["tipo_zona"] = pd.cut(
        idx["indice_cultural"],
        bins=[-0.01, 5, 15, 100],
        labels=["baixa_densidade", "média_densidade", "alta_densidade"],
    )
    zona_tipo = idx["tipo_zona"]

    # Para cada candidato, calcular em que tipo de zona se concentra o voto
    votos = votos.merge(zona_tipo.rename("tipo_zona"), left_on="NR_ZONA", right_index=True, how="left")
    perfil_votos = (
        votos.groupby(["SQ_CANDIDATO", "tipo_zona"], observed=True)["VOTOS"]
        .sum()
        .unstack(fill_value=0)
    )
    perfil_votos["total"] = perfil_votos.sum(axis=1)
    perfil_votos["pct_alta_dens"] = perfil_votos.get("alta_densidade", 0) / perfil_votos["total"] * 100

    # Junta com metadados do candidato
    cand_com_perfil = cand.merge(perfil_votos.reset_index(), on="SQ_CANDIDATO", how="inner")
    # Filtra candidatos com pelo menos 500 votos
    cand_com_perfil = cand_com_perfil[cand_com_perfil["total"] >= 500].copy()
    print(f"\nCandidatos com ≥500 votos: {len(cand_com_perfil)}")

    # Top 15 candidatos com MAIOR % de votos em zonas de alta densidade
    print("\n=== TOP 15: candidatos cuja voto se concentra em ZONAS DE ALTA DENSIDADE INSTITUCIONAL ===")
    top_alta = cand_com_perfil.sort_values("pct_alta_dens", ascending=False).head(15)
    for _, r in top_alta.iterrows():
        print(
            f"  {r['pct_alta_dens']:5.1f}%  {str(r['NM_URNA_CANDIDATO'])[:28]:<30} "
            f"{r['SG_PARTIDO']:<10} {str(r['DS_OCUPACAO'])[:35]:<37} "
            f"({int(r['total'])}v)"
        )

    print("\n=== TOP 15: candidatos com voto em ZONAS DE BAIXA DENSIDADE INSTITUCIONAL ===")
    top_baixa = cand_com_perfil.sort_values("pct_alta_dens").head(15)
    for _, r in top_baixa.iterrows():
        print(
            f"  {100-r['pct_alta_dens']:5.1f}% bx {str(r['NM_URNA_CANDIDATO'])[:28]:<30} "
            f"{r['SG_PARTIDO']:<10} {str(r['DS_OCUPACAO'])[:35]:<37} "
            f"({int(r['total'])}v)"
        )

    # Comparação de perfis por tipo de zona
    print("\n=== DISTRIBUIÇÃO DE OCUPAÇÕES POR TIPO DE CONCENTRAÇÃO DE VOTO ===")
    cand_com_perfil["perfil_zona"] = pd.cut(
        cand_com_perfil["pct_alta_dens"],
        bins=[-0.01, 15, 40, 101],
        labels=["baixa (<15%)", "mista (15-40%)", "alta (>40%)"],
    )
    dist = pd.crosstab(
        cand_com_perfil["categoria_ocup"],
        cand_com_perfil["perfil_zona"],
        normalize="columns",
    ) * 100
    print(dist.round(1).to_string())

    cand_com_perfil.to_csv("outputs/perfil_candidatos_zonas.csv", index=False)
    print(f"\nCSV: outputs/perfil_candidatos_zonas.csv")
