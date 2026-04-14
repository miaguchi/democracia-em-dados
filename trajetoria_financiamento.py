"""Trajetória do financiamento eleitoral nas zonas ricas de SP 2012-2024.

Carrega os CSVs/TXTs de prestação de contas dos 4 anos com loaders
específicos por layout, padroniza em estrutura comum e gera análise
de trajetória das receitas de vereadores com voto concentrado nas
zonas-alvo.

Três eras de regra de financiamento:
- 2012: ainda permitia doação PJ (empresarial)
- 2016: após reforma de 2015 — PJ proibida; Fundo Partidário ainda
  era a principal fonte pública; crowdfunding inexistente
- 2020/2024: FEFC (Fundo Especial) dominante; crowdfunding disponível
"""

from pathlib import Path
import pandas as pd

PASTA = Path("data/raw/prestacao_contas")
OUT = Path("outputs")


def _num(s):
    return pd.to_numeric(s.astype(str).str.replace(",", "."), errors="coerce")


def carregar_2012() -> pd.DataFrame:
    f = PASTA / "2012_SP/receitas_candidatos_2012_SP.txt"
    df = pd.read_csv(f, sep=";", encoding="latin-1", low_memory=False, quotechar='"')
    df = df[(df["Municipio"] == "SÃO PAULO") & (df["Cargo"] == "Vereador")].copy()
    df["valor"] = _num(df["Valor receita"])
    df = df.rename(
        columns={
            "Sequencial Candidato": "sq_candidato",
            "Nome candidato": "nome",
            "Sigla  Partido": "partido",
            "Tipo receita": "tipo_receita",
            "CPF/CNPJ do doador": "doador_id",
        }
    )
    df["ano"] = 2012
    return df[["ano", "sq_candidato", "nome", "partido", "tipo_receita", "doador_id", "valor"]]


def carregar_2016() -> pd.DataFrame:
    f = PASTA / "2016_SP/receitas_candidatos_prestacao_contas_final_2016_SP.txt"
    df = pd.read_csv(f, sep=";", encoding="latin-1", low_memory=False, quotechar='"')
    df = df[(df["Nome da UE"] == "SÃO PAULO") & (df["Cargo"] == "Vereador")].copy()
    df["valor"] = _num(df["Valor receita"])
    df = df.rename(
        columns={
            "Sequencial Candidato": "sq_candidato",
            "Nome candidato": "nome",
            "Sigla  Partido": "partido",
            "Tipo receita": "tipo_receita",
            "CPF/CNPJ do doador": "doador_id",
        }
    )
    df["ano"] = 2016
    return df[["ano", "sq_candidato", "nome", "partido", "tipo_receita", "doador_id", "valor"]]


def carregar_novo(ano: int) -> pd.DataFrame:
    f = PASTA / f"{ano}_SP/receitas_candidatos_{ano}_SP.csv"
    df = pd.read_csv(
        f,
        sep=";",
        encoding="latin-1",
        low_memory=False,
        usecols=[
            "SQ_CANDIDATO",
            "NM_CANDIDATO",
            "SG_PARTIDO",
            "NM_UE",
            "DS_CARGO",
            "DS_ORIGEM_RECEITA",
            "VR_RECEITA",
            "NR_CPF_CNPJ_DOADOR",
        ],
    )
    df = df[(df["NM_UE"].str.upper() == "SÃO PAULO") & (df["DS_CARGO"].str.upper() == "VEREADOR")].copy()
    df["valor"] = _num(df["VR_RECEITA"])
    df = df.rename(
        columns={
            "SQ_CANDIDATO": "sq_candidato",
            "NM_CANDIDATO": "nome",
            "SG_PARTIDO": "partido",
            "DS_ORIGEM_RECEITA": "tipo_receita",
            "NR_CPF_CNPJ_DOADOR": "doador_id",
        }
    )
    df["ano"] = ano
    return df[["ano", "sq_candidato", "nome", "partido", "tipo_receita", "doador_id", "valor"]]


# Categorização comum das fontes. Cada string possível é mapeada para uma categoria.
MAPA_CATEGORIA = {
    # 2012
    "Recursos de partido político": "partido",
    "Recursos de pessoas jurídicas": "pj",
    "Recursos de pessoas físicas": "pf",
    "Recursos próprios": "proprio",
    "Recursos de outros candidatos/comitês": "outros_cand",
    "Recursos de outros candidatos": "outros_cand",
    "Rendimentos de aplicações financeiras": "outros",
    "Recursos de origens não identificadas": "outros",
    "Recursos de Financiamento Coletivo": "crowdfund",
    # Fallback 2016 - similar 2012
}


def categorizar(s: str) -> str:
    if not isinstance(s, str):
        return "outros"
    s2 = s.strip()
    if s2 in MAPA_CATEGORIA:
        return MAPA_CATEGORIA[s2]
    sl = s2.lower()
    if "jurídica" in sl or "juridica" in sl:
        return "pj"
    if "física" in sl or "fisica" in sl:
        return "pf"
    if "partid" in sl:
        return "partido"
    if "próprio" in sl or "proprio" in sl:
        return "proprio"
    if "coletivo" in sl or "crowdfund" in sl:
        return "crowdfund"
    if "outros candidat" in sl:
        return "outros_cand"
    return "outros"


def carregar_todos() -> pd.DataFrame:
    dfs = []
    print("Carregando 2012...")
    dfs.append(carregar_2012())
    print("Carregando 2016...")
    dfs.append(carregar_2016())
    print("Carregando 2020...")
    dfs.append(carregar_novo(2020))
    print("Carregando 2024...")
    dfs.append(carregar_novo(2024))
    df = pd.concat(dfs, ignore_index=True)
    df["categoria"] = df["tipo_receita"].map(categorizar)
    # Força tipo texto para evitar erro de schema no parquet
    df["doador_id"] = df["doador_id"].astype(str)
    df["sq_candidato"] = df["sq_candidato"].astype(str)
    df["partido"] = df["partido"].astype(str)
    return df


def resumo_por_ano(df: pd.DataFrame):
    """Quadro agregado: fontes de receita por ano em SP vereador."""
    tot = df.groupby("ano")["valor"].sum() / 1e6
    por_cat = df.groupby(["ano", "categoria"])["valor"].sum().unstack(fill_value=0) / 1e6
    pct = por_cat.div(por_cat.sum(axis=1), axis=0) * 100
    n_cand = df.groupby("ano")["sq_candidato"].nunique()
    return tot, por_cat, pct, n_cand


if __name__ == "__main__":
    df = carregar_todos()
    print(f"\nTotal linhas: {len(df):,}")

    tot, por_cat, pct, n_cand = resumo_por_ano(df)

    print("\n=== RECEITAS DE VEREADORES EM SP (2012-2024, R$ milhões) ===")
    print(por_cat.round(1).to_string())

    print("\n=== PARTICIPAÇÃO PERCENTUAL POR CATEGORIA ===")
    print(pct.round(1).to_string())

    print(f"\n=== TOTAIS ===")
    resumo = pd.DataFrame({
        "receita_total_mi": tot.round(1),
        "n_candidatos": n_cand,
    })
    print(resumo.to_string())

    # Salva
    OUT.mkdir(parents=True, exist_ok=True)
    pct.to_csv(OUT / "financiamento_trajetoria_pct.csv")
    por_cat.to_csv(OUT / "financiamento_trajetoria_valores_mi.csv")
    df.to_parquet("data/processed/receitas_vereador_sp_2012_2024.parquet", index=False)
    print(f"\nCSV: {OUT/'financiamento_trajetoria_pct.csv'}")
    print(f"Parquet: data/processed/receitas_vereador_sp_2012_2024.parquet")
