"""Geração do relatório HTML de análise da WCA (World Cube Association).

Pipeline: `db` (conexão DuckDB) -> `queries` (SQL -> DataFrames) ->
`charts`/`coverage` (figuras Plotly) -> `report` (página HTML com abas).

Ponto de entrada: `main.py` na raiz do projeto.
"""
