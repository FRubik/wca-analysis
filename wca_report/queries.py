"""Consultas SQL (DuckDB) que devolvem DataFrames prontos para os gráficos."""

import pandas as pd

from . import config


def _and(*clauses: str) -> str:
    """Junta cláusulas WHERE não vazias com AND (ou TRUE se nenhuma)."""
    parts = [c for c in clauses if c]
    return " AND ".join(parts) if parts else "TRUE"


# ----------------------------------------------------------------------
# Competições
# ----------------------------------------------------------------------
def competitions_per_year(con, scope_where: str = "") -> pd.DataFrame:
    """Total de competições (não canceladas) por ano, dentro do recorte."""
    where = _and(scope_where, "c.cancelled = 0")
    return con.execute(f"""
        SELECT c.year, COUNT(DISTINCT c.id) AS total_competitions
        FROM competitions c
        JOIN results r ON r.competition_id = c.id
        WHERE {where}
        GROUP BY c.year
        ORDER BY c.year
    """).df()


def event_presence(con, start_year: int, scope_where: str = "") -> pd.DataFrame:
    """Nº de competições por modalidade/ano e sua presença (%) no recorte."""
    totals = competitions_per_year(con, scope_where)
    where = _and(scope_where, f"c.year BETWEEN {start_year} AND {config.MAX_YEAR}")
    per_event = con.execute(f"""
        SELECT
            c.year,
            e.id   AS event_id,
            e.name AS event_name,
            COUNT(DISTINCT c.id) AS num_competitions
        FROM competitions c
        JOIN results r ON r.competition_id = c.id
        JOIN events   e ON e.id = r.event_id
        WHERE {where}
        GROUP BY c.year, e.id, e.name
    """).df()

    df = per_event.merge(totals, on="year", how="left")
    df["presence_pct"] = df["num_competitions"] / df["total_competitions"]
    df = df[~df["event_name"].isin(config.EXCLUDED_EVENTS)]
    return df.sort_values("event_name")


def rounds_sp(con, start_year: int) -> pd.DataFrame:
    """Unidades competitivas (rounds, com peso extra para 333fm/333mbf) em SP."""
    totals = competitions_per_year(con, config.SCOPE_SP)
    df = con.execute(f"""
        WITH rounds AS (
            SELECT DISTINCT competition_id, event_id, round_type_id, format_id
            FROM results
        )
        SELECT
            c.year,
            e.id   AS event_id,
            e.name AS event_name,
            SUM(
                CASE
                    WHEN e.id IN ('333fm', '333mbf')
                    THEN CASE rounds.format_id
                            WHEN '1' THEN 1
                            WHEN '2' THEN 2
                            WHEN '3' THEN 3
                            ELSE 1
                         END
                    ELSE 1
                END
            ) AS competitive_units
        FROM rounds
        JOIN competitions c ON c.id = rounds.competition_id
        JOIN events       e ON e.id = rounds.event_id
        WHERE {config.SCOPE_SP}
          AND c.year BETWEEN {start_year} AND {config.MAX_YEAR}
        GROUP BY c.year, e.id, e.name
    """).df()

    df = df.merge(totals, on="year", how="left")
    df = df[~df["event_name"].isin(config.EXCLUDED_EVENTS)]
    return df.sort_values("event_name")


# ----------------------------------------------------------------------
# Competidores
# ----------------------------------------------------------------------
def active_competitors(con) -> pd.DataFrame:
    """Competidores ativos (best > 0) por modalidade/ano e presença (%)."""
    df = con.execute("""
        SELECT
            c.year,
            e.id   AS event_id,
            e.name AS event_name,
            COUNT(DISTINCT r.person_id) AS num_active_competitors
        FROM results r
        JOIN competitions c ON c.id = r.competition_id
        JOIN events       e ON e.id = r.event_id
        WHERE r.best > 0 AND c.year > 2000
        GROUP BY c.year, e.id, e.name
    """).df()

    totals = con.execute("""
        SELECT c.year, COUNT(DISTINCT r.person_id) AS total_active_competitors
        FROM results r
        JOIN competitions c ON c.id = r.competition_id
        WHERE r.best > 0 AND c.year > 2000
        GROUP BY c.year
    """).df()

    df = df.merge(totals, on="year", how="left")
    df = df[~df["event_name"].isin(config.EXCLUDED_EVENTS)].sort_values("event_name")
    df["presence_pct"] = df["num_active_competitors"] / df["total_active_competitors"]
    return df


def new_competitors(con) -> pd.DataFrame:
    """Estreias por modalidade/ano (1º ano de cada pessoa em cada modalidade)."""
    return con.execute("""
        WITH first_year AS (
            SELECT r.person_id, r.event_id, MIN(c.year) AS estreia
            FROM results r
            JOIN competitions c ON r.competition_id = c.id
            WHERE c.cancelled = 0
            GROUP BY r.person_id, r.event_id
        )
        SELECT
            e.name     AS event_name,
            fy.estreia AS year,
            COUNT(*)   AS new_competitors
        FROM first_year fy
        JOIN events e ON e.id = fy.event_id
        WHERE fy.estreia > 2000
        GROUP BY e.name, fy.estreia
        ORDER BY year, event_name
    """).df()


def renovation(con) -> pd.DataFrame:
    """% dos ativos de cada ano/modalidade que são estreantes (renovação)."""
    return con.execute("""
        WITH res AS (
            SELECT r.person_id, r.event_id, c.year
            FROM results r
            JOIN competitions c ON r.competition_id = c.id
            WHERE c.cancelled = 0
        ),
        ativos AS (
            SELECT event_id, year, COUNT(DISTINCT person_id) AS ativos
            FROM res GROUP BY event_id, year
        ),
        estreia AS (
            SELECT person_id, event_id, MIN(year) AS year
            FROM res GROUP BY person_id, event_id
        ),
        novos AS (
            SELECT event_id, year, COUNT(*) AS novos
            FROM estreia GROUP BY event_id, year
        )
        SELECT
            e.name AS event_name,
            a.year,
            a.ativos,
            COALESCE(n.novos, 0) AS novos,
            100.0 * COALESCE(n.novos, 0) / a.ativos AS pct_renovacao
        FROM ativos a
        LEFT JOIN novos n ON n.event_id = a.event_id AND n.year = a.year
        JOIN events e ON e.id = a.event_id
        WHERE a.year > 2000
        ORDER BY a.year, event_name
    """).df()


def coverage_competitions(con) -> pd.DataFrame:
    """Competições no Brasil que JÁ ACONTECERAM (fim <= hoje), de 2022 em diante."""
    return con.execute(f"""
        SELECT
            c.cell_name              AS name,
            c.year,
            c.latitude_microdegrees  / 1e6 AS lat,
            c.longitude_microdegrees / 1e6 AS lon
        FROM competitions c
        WHERE c.country_id = 'Brazil'
          AND c.cancelled = 0
          AND c.year >= {config.COVERAGE_START_YEAR}
          AND make_date(c.end_year, c.end_month, c.end_day) <= current_date
    """).df()
