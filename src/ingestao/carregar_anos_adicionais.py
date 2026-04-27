"""Carrega anos eleitorais adicionais no MySQL.

Reusa o esquema e funções de carregar_mysql.py, mas insere apenas os
parquets dos anos especificados, sem duplicar o que já está no banco.

Uso:
    python -m src.ingestao.carregar_anos_adicionais 2010 2014
    python -m src.ingestao.carregar_anos_adicionais  # default: 2010, 2014
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

DATA_DIR = _ROOT / "data/processed"


def carregar_parquets_anos(anos: list[int]) -> pd.DataFrame:
    """Lê e concatena parquets dos anos especificados."""
    dfs = []
    for ano in anos:
        f = DATA_DIR / f"votacao_partido_munzona_{ano}_SP.parquet"
        if not f.exists():
            print(f"  AVISO: {f.name} não existe — pule")
            continue
        df = pd.read_parquet(f)
        # Harmonizar nomes de colunas (igual ao script principal)
        if "QT_VOTOS_NOMINAIS" not in df.columns and "QT_VOTOS_NOMINAIS_VALIDOS" in df.columns:
            df["QT_VOTOS_NOMINAIS"] = df["QT_VOTOS_NOMINAIS_VALIDOS"]
            df["QT_VOTOS_LEGENDA"] = df["QT_VOTOS_LEGENDA_VALIDOS"]
        dfs.append(df)
        print(f"  {f.name}: {len(df)} linhas")

    return pd.concat(dfs, ignore_index=True)


def main(anos: list[int] | None = None) -> None:
    if anos is None:
        anos = [2010, 2014]
    print("=" * 60)
    print(f"CARGA DE ANOS ADICIONAIS: {anos}")
    print("=" * 60)

    print("\nCarregando parquets...")
    df = carregar_parquets_anos(anos)
    print(f"Total: {len(df)} linhas")

    conn = conectar(DATABASE)
    cursor = conn.cursor()

    # Verificar quais eleições já existem
    cursor.execute("SELECT DISTINCT ano_eleicao FROM eleicao ORDER BY ano_eleicao")
    anos_existentes = [r[0] for r in cursor.fetchall()]
    print(f"\nAnos já no banco: {anos_existentes}")

    # Filtrar só os anos novos
    anos_novos = [a for a in anos if a not in anos_existentes]
    if not anos_novos:
        print("Todos os anos já estão no banco. Nada a fazer.")
        cursor.close()
        conn.close()
        return

    print(f"Anos a inserir: {anos_novos}")
    df_novo = df[df["ANO_ELEICAO"].isin(anos_novos)]
    print(f"Linhas a inserir: {len(df_novo)}")

    # Contagem antes
    cursor.execute("SELECT COUNT(*) FROM votacao_partido_munzona")
    fato_antes = cursor.fetchone()[0]

    print("\nInserindo dimensões (INSERT IGNORE — não duplica)...")
    inserir_dimensoes(df_novo, conn)

    print("\nInserindo fato...")
    inserir_fato(df_novo, conn)

    # Verificação
    print("\n" + "=" * 60)
    print("VERIFICAÇÃO")
    print("=" * 60)
    cursor.execute("SELECT COUNT(*) FROM votacao_partido_munzona")
    fato_depois = cursor.fetchone()[0]
    print(f"  votacao_partido_munzona: {fato_antes} -> {fato_depois} "
          f"(+{fato_depois - fato_antes})")

    cursor.execute("SELECT DISTINCT ano_eleicao FROM eleicao ORDER BY ano_eleicao")
    anos_final = [r[0] for r in cursor.fetchall()]
    print(f"  anos no banco: {anos_final}")

    cursor.close()
    conn.close()
    print("\nCarga concluída.")


if __name__ == "__main__":
    args_anos = [int(a) for a in sys.argv[1:]] if len(sys.argv) > 1 else None
    main(args_anos)
