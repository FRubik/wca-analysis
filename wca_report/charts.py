"""Figuras Plotly a partir dos DataFrames das consultas."""

import plotly.graph_objects as go

_LEGEND = dict(itemclick="toggle", itemdoubleclick="toggleothers")


def plot_events_over_time(df, title=""):
    """Linha por modalidade (num_competitions) + linha de total, ao longo dos anos."""
    fig = go.Figure()

    for event_name in df["event_name"].unique():
        temp = df[df["event_name"] == event_name].sort_values("year")
        fig.add_trace(go.Scatter(
            x=temp["year"], y=temp["num_competitions"],
            mode="lines+markers", name=event_name,
            line=dict(width=3), marker=dict(size=8),
            hovertemplate=(
                "<b>%{fullData.name}</b><br>"
                "Ano: %{x}<br>Competições: %{y}<extra></extra>"
            ),
        ))

    total_df = df[["year", "total_competitions"]].drop_duplicates().sort_values("year")
    fig.add_trace(go.Scatter(
        x=total_df["year"], y=total_df["total_competitions"],
        mode="lines+markers", name="Total de Competições",
        line=dict(width=6), marker=dict(size=10),
        hovertemplate=(
            "<b>Total de Competições</b><br>"
            "Ano: %{x}<br>Total: %{y}<extra></extra>"
        ),
    ))

    fig.update_layout(
        title=title, xaxis_title="Ano", yaxis_title="Número de Competições",
        hovermode="closest", template="plotly_white",
        legend_title="Modalidade", height=700, legend=_LEGEND,
    )
    return fig


def plot_event_presence_pct(df, title=""):
    """Presença (%) de cada modalidade ao longo dos anos."""
    fig = go.Figure()

    for event_name in df["event_name"].unique():
        temp = df[df["event_name"] == event_name].sort_values("year")
        fig.add_trace(go.Scatter(
            x=temp["year"], y=temp["presence_pct"] * 100,
            mode="lines+markers", name=event_name,
            line=dict(width=3), marker=dict(size=8),
            hovertemplate=(
                "<b>%{fullData.name}</b><br>"
                "Ano: %{x}<br>Presença: %{y:.1f}%<extra></extra>"
            ),
        ))

    fig.update_layout(
        title=title, xaxis_title="Ano", yaxis_title="% das Competições",
        hovermode="closest", template="plotly_white",
        legend_title="Modalidade", height=700, legend=_LEGEND,
    )
    return fig


def plot_new_competitors(df_new, title="Novos competidores por ano, por modalidade"):
    """Estreias por ano, uma linha por modalidade."""
    fig = go.Figure()
    for event_name in sorted(df_new["event_name"].unique()):
        temp = df_new[df_new["event_name"] == event_name].sort_values("year")
        fig.add_trace(go.Scatter(
            x=temp["year"], y=temp["new_competitors"],
            mode="lines+markers", name=event_name,
        ))
    fig.update_layout(
        title=title, xaxis_title="Ano",
        yaxis_title="Novos competidores (estreias)", height=700,
    )
    return fig


def plot_renovation(df_renov, title="Renovação por modalidade (% dos ativos que são novos)"):
    """% de competidores novos entre os ativos, por ano e modalidade."""
    fig = go.Figure()
    for event_name in sorted(df_renov["event_name"].unique()):
        temp = df_renov[df_renov["event_name"] == event_name].sort_values("year")
        fig.add_trace(go.Scatter(
            x=temp["year"], y=temp["pct_renovacao"],
            mode="lines+markers", name=event_name,
            hovertemplate=(
                "%{x}: %{y:.1f}% novos<br>"
                "ativos=%{customdata[0]}, novos=%{customdata[1]}"
                "<extra>" + event_name + "</extra>"
            ),
            customdata=temp[["ativos", "novos"]].values,
        ))
    fig.update_layout(
        title=title, xaxis_title="Ano", yaxis_title="% de competidores novos",
        yaxis_ticksuffix="%", height=700,
    )
    return fig
