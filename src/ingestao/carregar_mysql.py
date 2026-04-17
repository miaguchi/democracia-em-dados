"""Carrega dados eleitorais do TSE (parquet) no MySQL.

Cria o banco democracia_em_dados, executa o schema e insere dados
das tabelas de dimensão e fato a partir dos parquets processados.
"""

from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import glob

import mysql.connector
import pandas as pd

SCHEMA_SQL = _ROOT / "scripts/sql/schema_tse.sql"
DATA_DIR = _ROOT / "data/processed"

MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Miaguchi123!",
}

DATABASE = "democracia_em_dados"


def conectar(database: str | None = None) -> mysql.connector.MySQLConnection:
    """Conecta ao MySQL, opcionalmente a um banco específico."""
    config = dict(MYSQL_CONFIG)
    if database:
        config["database"] = database
    return mysql.connector.connect(**config)


def criar_banco() -> None:
    """Cria o banco de dados se não existir."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE} "
                   "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    conn.commit()
    print(f"Banco '{DATABASE}' criado/verificado.")
    cursor.close()
    conn.close()


def executar_schema() -> None:
    """Executa o schema SQL (CREATE TABLEs)."""
    conn = conectar(DATABASE)
    cursor = conn.cursor()

    sql = SCHEMA_SQL.read_text()
    # Remover comentários de linha
    import re
    sql_clean = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
    for statement in sql_clean.split(";"):
        stmt = statement.strip()
        if not stmt:
            continue
        try:
            cursor.execute(stmt)
        except mysql.connector.Error as e:
            if e.errno not in (1061, 1050):  # duplicate key/table
                print(f"  AVISO: {e.msg}")

    conn.commit()
    print("Schema executado.")
    cursor.close()
    conn.close()


def carregar_parquets() -> pd.DataFrame:
    """Lê e concatena todos os parquets de votacao_partido_munzona."""
    files = sorted(glob.glob(str(DATA_DIR / "votacao_partido_munzona_*_SP.parquet")))
    print(f"Parquets encontrados: {len(files)}")

    dfs = []
    for f in files:
        df = pd.read_parquet(f)
        # Harmonizar colunas entre anos
        # 2012-2016: QT_VOTOS_NOMINAIS / QT_VOTOS_LEGENDA
        # 2018+: QT_VOTOS_NOMINAIS_VALIDOS / QT_VOTOS_LEGENDA_VALIDOS
        if "QT_VOTOS_NOMINAIS" not in df.columns and "QT_VOTOS_NOMINAIS_VALIDOS" in df.columns:
            df["QT_VOTOS_NOMINAIS"] = df["QT_VOTOS_NOMINAIS_VALIDOS"]
            df["QT_VOTOS_LEGENDA"] = df["QT_VOTOS_LEGENDA_VALIDOS"]

        dfs.append(df)
        print(f"  {Path(f).name}: {len(df)} linhas")

    all_df = pd.concat(dfs, ignore_index=True)
    print(f"Total: {len(all_df)} linhas")
    return all_df


def inserir_dimensoes(df: pd.DataFrame, conn: mysql.connector.MySQLConnection) -> None:
    """Popula tabelas de dimensão."""
    cursor = conn.cursor()

    # Municípios
    munis = df[["CD_MUNICIPIO", "NM_MUNICIPIO", "SG_UF"]].drop_duplicates()
    cursor.executemany(
        "INSERT IGNORE INTO municipio (cd_municipio, nm_municipio, sg_uf) VALUES (%s, %s, %s)",
        munis.values.tolist(),
    )
    print(f"  municipio: {cursor.rowcount} inseridos (de {len(munis)} únicos)")

    # Zonas eleitorais
    zonas = df[["NR_ZONA", "CD_MUNICIPIO"]].drop_duplicates()
    cursor.executemany(
        "INSERT IGNORE INTO zona_eleitoral (nr_zona, cd_municipio) VALUES (%s, %s)",
        zonas.values.tolist(),
    )
    print(f"  zona_eleitoral: {cursor.rowcount} inseridos (de {len(zonas)} únicos)")

    # Partidos
    partidos = df[["NR_PARTIDO", "SG_PARTIDO", "NM_PARTIDO"]].drop_duplicates(subset=["NR_PARTIDO"])
    # Pegar o nome mais recente de cada partido
    partidos = (
        df.sort_values("ANO_ELEICAO", ascending=False)
        .drop_duplicates(subset=["NR_PARTIDO"])[["NR_PARTIDO", "SG_PARTIDO", "NM_PARTIDO"]]
    )
    cursor.executemany(
        "INSERT IGNORE INTO partido (nr_partido, sg_partido, nm_partido) VALUES (%s, %s, %s)",
        partidos.values.tolist(),
    )
    print(f"  partido: {cursor.rowcount} inseridos (de {len(partidos)} únicos)")

    # Cargos
    cargos = df[["CD_CARGO", "DS_CARGO"]].drop_duplicates()
    cursor.executemany(
        "INSERT IGNORE INTO cargo (cd_cargo, ds_cargo) VALUES (%s, %s)",
        cargos.values.tolist(),
    )
    print(f"  cargo: {cursor.rowcount} inseridos (de {len(cargos)} únicos)")

    # Eleições
    eleicoes = df[["CD_ELEICAO", "ANO_ELEICAO", "NR_TURNO", "CD_TIPO_ELEICAO",
                   "NM_TIPO_ELEICAO", "DS_ELEICAO", "DT_ELEICAO", "TP_ABRANGENCIA"]].drop_duplicates(
        subset=["CD_ELEICAO", "NR_TURNO"]
    )
    # Converter DT_ELEICAO de DD/MM/YYYY para YYYY-MM-DD
    eleicoes = eleicoes.copy()
    eleicoes["DT_ELEICAO"] = pd.to_datetime(
        eleicoes["DT_ELEICAO"], format="%d/%m/%Y"
    ).dt.strftime("%Y-%m-%d")
    cursor.executemany(
        "INSERT IGNORE INTO eleicao (cd_eleicao, ano_eleicao, nr_turno, "
        "cd_tipo_eleicao, nm_tipo_eleicao, ds_eleicao, dt_eleicao, tp_abrangencia) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        eleicoes.values.tolist(),
    )
    print(f"  eleicao: {cursor.rowcount} inseridos (de {len(eleicoes)} únicos)")

    conn.commit()
    cursor.close()


def inserir_fato(df: pd.DataFrame, conn: mysql.connector.MySQLConnection) -> None:
    """Popula tabela fato votacao_partido_munzona."""
    cursor = conn.cursor()

    # Preparar dados
    fato = df[[
        "CD_ELEICAO", "NR_TURNO", "CD_MUNICIPIO", "NR_ZONA",
        "CD_CARGO", "NR_PARTIDO", "QT_VOTOS_NOMINAIS", "QT_VOTOS_LEGENDA",
        "ST_VOTO_EM_TRANSITO", "SQ_COLIGACAO", "NM_COLIGACAO",
        "DS_COMPOSICAO_COLIGACAO", "TP_AGREMIACAO",
    ]].copy()

    # Tratar NaN em campos nullable
    fato = fato.where(fato.notna(), None)

    # Inserir em batches
    sql = (
        "INSERT INTO votacao_partido_munzona "
        "(cd_eleicao, nr_turno, cd_municipio, nr_zona, cd_cargo, nr_partido, "
        "qt_votos_nominais, qt_votos_legenda, st_voto_em_transito, "
        "sq_coligacao, nm_coligacao, ds_composicao_coligacao, tp_agremiacao) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    )

    batch_size = 5000
    total = len(fato)
    inserted = 0

    for i in range(0, total, batch_size):
        batch = fato.iloc[i:i + batch_size]
        rows = [tuple(None if pd.isna(v) else v for v in row) for row in batch.itertuples(index=False)]
        cursor.executemany(sql, rows)
        conn.commit()
        inserted += len(rows)
        if (i // batch_size) % 10 == 0:
            print(f"  votacao_partido_munzona: {inserted}/{total}...")

    print(f"  votacao_partido_munzona: {inserted} inseridos")
    cursor.close()


def main() -> None:
    """Pipeline completo de carga."""
    print("=" * 60)
    print("CARGA DOS DADOS TSE NO MYSQL")
    print("=" * 60)

    criar_banco()
    executar_schema()

    print("\nCarregando parquets...")
    df = carregar_parquets()

    print("\nInserindo dimensões...")
    conn = conectar(DATABASE)
    inserir_dimensoes(df, conn)

    print("\nInserindo fato...")
    inserir_fato(df, conn)

    # Verificação final
    print("\n" + "=" * 60)
    print("VERIFICAÇÃO")
    print("=" * 60)
    cursor = conn.cursor()
    for tabela in ["municipio", "zona_eleitoral", "partido", "cargo", "eleicao", "votacao_partido_munzona"]:
        cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
        count = cursor.fetchone()[0]
        print(f"  {tabela:<30} {count:>10} linhas")
    cursor.close()
    conn.close()

    print("\nCarga concluída.")


if __name__ == "__main__":
    main()
