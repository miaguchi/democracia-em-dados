"""Carrega dados de votação para Presidente (1998-2022) no MySQL.

Os dados de Presidente estão nos CSVs nacionais (BR ou BRASIL) do TSE,
não nos por UF que usamos para os outros cargos. Filtra SG_UF='SP',
DS_CARGO='Presidente', NR_TURNO=1.
"""

from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import pandas as pd

from src.ingestao.carregar_mysql import (
    DATABASE,
    conectar,
    inserir_dimensoes,
    inserir_fato,
)

ANOS = [1998, 2002, 2006, 2010, 2014, 2018, 2022]
RAW_DIR = _ROOT / "data/raw"


def localizar_csv_nacional(ano: int) -> Path:
    """Encontra o CSV nacional que tem os dados de Presidente."""
    pasta = RAW_DIR / f"votacao_partido_munzona_{ano}"
    # Tentar BR.csv primeiro (formato moderno), depois BRASIL.csv (1998)
    for nome in [
        f"votacao_partido_munzona_{ano}_BR.csv",
        f"votacao_partido_munzona_{ano}_BRASIL.csv",
    ]:
        f = pasta / nome
        if f.exists():
            return f
    raise FileNotFoundError(f"Nenhum CSV nacional para {ano} em {pasta}")


def carregar_presidente_sp(ano: int) -> pd.DataFrame:
    """Lê o CSV nacional, filtra SP/Presidente/1º turno."""
    f = localizar_csv_nacional(ano)
    df = pd.read_csv(f, sep=";", encoding="latin-1", low_memory=False)
    sub = df[
        (df["SG_UF"] == "SP")
        & (df["DS_CARGO"] == "Presidente")
        & (df["NR_TURNO"] == 1)
    ].copy()

    # Harmonizar nomes de votos (igual aos outros loaders)
    if "QT_VOTOS_NOMINAIS" not in sub.columns and "QT_VOTOS_NOMINAIS_VALIDOS" in sub.columns:
        sub["QT_VOTOS_NOMINAIS"] = sub["QT_VOTOS_NOMINAIS_VALIDOS"]
        sub["QT_VOTOS_LEGENDA"] = sub["QT_VOTOS_LEGENDA_VALIDOS"]

    print(f"  {ano}: {len(sub)} linhas (Pres SP 1T)")
    return sub


def main() -> None:
    print("=" * 60)
    print("CARGA DE DADOS DE PRESIDENTE (1998-2022, SP, 1º turno)")
    print("=" * 60)

    print("\nLendo CSVs nacionais...")
    dfs = [carregar_presidente_sp(ano) for ano in ANOS]
    df = pd.concat(dfs, ignore_index=True)
    print(f"\nTotal: {len(df)} linhas")

    conn = conectar(DATABASE)
    cursor = conn.cursor()

    # Verificar quantas linhas de Presidente já existem
    cursor.execute(
        "SELECT COUNT(*) FROM votacao_partido_munzona "
        "WHERE cd_cargo = 1"
    )
    pres_antes = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM votacao_partido_munzona")
    fato_antes = cursor.fetchone()[0]
    print(f"\nLinhas de Presidente já no banco: {pres_antes}")

    if pres_antes > 0:
        print("Já existem dados de Presidente — abortando para evitar duplicação.")
        cursor.close()
        conn.close()
        return

    print("\nInserindo dimensões (INSERT IGNORE — não duplica)...")
    inserir_dimensoes(df, conn)

    print("\nInserindo fato...")
    inserir_fato(df, conn)

    # Verificação
    print("\n" + "=" * 60)
    print("VERIFICAÇÃO")
    print("=" * 60)
    cursor.execute("SELECT COUNT(*) FROM votacao_partido_munzona")
    fato_depois = cursor.fetchone()[0]
    print(f"  votacao_partido_munzona: {fato_antes} -> {fato_depois} "
          f"(+{fato_depois - fato_antes})")

    cursor.execute(
        "SELECT e.ano_eleicao, COUNT(*) FROM votacao_partido_munzona v "
        "JOIN eleicao e ON v.cd_eleicao = e.cd_eleicao AND v.nr_turno = e.nr_turno "
        "WHERE v.cd_cargo = 1 GROUP BY e.ano_eleicao ORDER BY e.ano_eleicao"
    )
    print("\nPresidente por ano:")
    for ano, n in cursor.fetchall():
        print(f"  {ano}: {n} linhas")

    cursor.close()
    conn.close()
    print("\nCarga concluída.")


if __name__ == "__main__":
    main()
