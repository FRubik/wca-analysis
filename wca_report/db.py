"""Conexão DuckDB com os TSVs oficiais da WCA materializados em tabelas.

Os arquivos são lidos uma única vez (evita reparsear o results.tsv, ~600 MB,
a cada consulta). De `results` mantemos só as colunas usadas nas análises.
"""

import duckdb

from . import config

# colunas de results realmente usadas (mantém a tabela enxuta em memória)
_RESULTS_COLUMNS = [
    "competition_id",
    "event_id",
    "person_id",
    "best",
    "round_type_id",
    "format_id",
]


def _read_tsv(name: str) -> str:
    path = config.TSV_DIR / f"WCA_export_{name}.tsv"
    return f"read_csv_auto('{path}', delim='\t')"


def connect() -> duckdb.DuckDBPyConnection:
    """Abre a conexão e materializa `competitions`, `results` e `events`."""
    con = duckdb.connect()
    con.execute(f"CREATE TABLE competitions AS SELECT * FROM {_read_tsv('competitions')}")
    con.execute(f"CREATE TABLE events       AS SELECT * FROM {_read_tsv('events')}")
    con.execute(
        f"CREATE TABLE results AS "
        f"SELECT {', '.join(_RESULTS_COLUMNS)} FROM {_read_tsv('results')}"
    )
    return con
