"""Gera o relatório HTML da WCA (index.html) a partir dos TSVs oficiais.

Uso:
    python main.py

Reexecute sempre que atualizar os arquivos em tsv/. Só o index.html gerado
precisa ir para o git (deploy automático via GitHub Pages).
"""

from wca_report import charts, config, coverage, queries
from wca_report.db import connect
from wca_report.report import build_tabbed_page


def build_competicoes_tab(con):
    """Aba 'Competições': modalidades no mundo, Brasil, SP, rounds e cobertura."""
    world = queries.event_presence(con, config.WORLD_START_YEAR, config.SCOPE_WORLD)
    brazil = queries.event_presence(con, config.BRAZIL_START_YEAR, config.SCOPE_BRAZIL)
    sp = queries.event_presence(con, config.BRAZIL_START_YEAR, config.SCOPE_SP)
    rounds = queries.rounds_sp(con, config.BRAZIL_START_YEAR)
    rounds = rounds.rename(columns={"competitive_units": "num_competitions"})

    return [
        charts.plot_events_over_time(world, "Quantidade de Competições por Modalidade no Mundo"),
        charts.plot_event_presence_pct(world, "Presença das Modalidades nas Competições Mundiais"),
        charts.plot_events_over_time(brazil, "Quantidade de Competições por Modalidade no Brasil"),
        charts.plot_event_presence_pct(brazil, "Presença das Modalidades nas Competições Brasileiras"),
        charts.plot_events_over_time(sp, "Quantidade de Competições por Modalidade Em São Paulo"),
        charts.plot_event_presence_pct(sp, "Presença das Modalidades nas Competições Paulistas"),
        charts.plot_events_over_time(rounds, "Quantidade de rounds por Modalidade Em São Paulo"),
        ("Mapa de Cobertura de Competições no Brasil", coverage.build_coverage_block(con)),
    ]


def build_competidores_tab(con):
    """Aba 'Competidores': ativos, presença, estreias e renovação."""
    active = queries.active_competitors(con)
    active_plot = active.rename(columns={
        "num_active_competitors": "num_competitions",
        "total_active_competitors": "total_competitions",
    })

    return [
        charts.plot_events_over_time(active_plot, "Competidores Ativos por Modalidade no Mundo"),
        charts.plot_event_presence_pct(active, "Competidores Ativos por Modalidade no Mundo (percentual)"),
        charts.plot_new_competitors(queries.new_competitors(con)),
        charts.plot_renovation(queries.renovation(con)),
    ]


def main():
    con = connect()
    tabs = [
        ("Competições", build_competicoes_tab(con)),
        ("Competidores", build_competidores_tab(con)),
    ]
    build_tabbed_page(tabs, config.OUTPUT_HTML, page_title="WCA Brasil — Análise")
    print(f"Relatório gerado em: {config.OUTPUT_HTML}")


if __name__ == "__main__":
    main()
