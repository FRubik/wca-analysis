"""Mapa de cobertura: silhueta da união de círculos em torno das competições.

Em vez de empilhar um círculo por competição (o que satura regiões densas),
monta-se um campo de "distância até a competição mais próxima" numa grade e
extrai-se o contorno no nível do raio — a borda da união, com opacidade uniforme.

Gera um fragmento HTML com dois seletores (ano-início e raio) que compõem via JS.
"""

import json

import matplotlib
matplotlib.use("Agg")            # só usamos o contour para o cálculo, sem exibir
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.io import to_html
from scipy.spatial import cKDTree

from . import config
from .queries import coverage_competitions


def _latlon_to_xyz(lat, lon, R=config.EARTH_RADIUS_KM):
    """Projeta lat/lon em coordenadas cartesianas na esfera (para distância real)."""
    la, lo = np.radians(lat), np.radians(lon)
    return np.column_stack([
        R * np.cos(la) * np.cos(lo),
        R * np.cos(la) * np.sin(lo),
        R * np.sin(la),
    ])


def _make_grid(comps):
    """Grade lon/lat que cobre todos os recortes, e seus pontos em xyz."""
    pad = max(config.RADIUS_OPTIONS_KM) / 111.0 + 1.0
    lons = np.arange(comps.lon.min() - pad, comps.lon.max() + pad, config.GRID_STEP_DEG)
    lats = np.arange(comps.lat.min() - pad, comps.lat.max() + pad, config.GRID_STEP_DEG)
    lon_grid, lat_grid = np.meshgrid(lons, lats)
    return lon_grid, lat_grid, _latlon_to_xyz(lat_grid.ravel(), lon_grid.ravel())


def _distance_field(df, grid_xyz, shape):
    """Distância (km) de cada ponto da grade até a competição mais próxima."""
    tree = cKDTree(_latlon_to_xyz(df["lat"].values, df["lon"].values))
    chord, _ = tree.query(grid_xyz, k=1)
    R = config.EARTH_RADIUS_KM
    arc = 2 * R * np.arcsin(np.clip(chord / (2 * R), 0, 1))
    return arc.reshape(shape)


def _union_segments(field, level_km, lon_grid, lat_grid):
    """Anéis do contorno da união dos círculos de raio `level_km`."""
    fig_tmp, ax = plt.subplots()
    cs = ax.contour(lon_grid, lat_grid, field, levels=[level_km])
    segs = [np.asarray(s) for s in cs.allsegs[0]]
    plt.close(fig_tmp)
    return segs


def _build_figure(comps, lon_grid, lat_grid, grid_xyz):
    """Uma trace por (ano-início x raio) + marcadores por ano-início."""
    fig = go.Figure()
    meta = []

    for ys in config.COVERAGE_YEAR_OPTIONS:
        field = _distance_field(comps[comps["year"] >= ys], grid_xyz, lat_grid.shape)
        for r in config.RADIUS_OPTIONS_KM:
            lat_all, lon_all = [], []
            for seg in _union_segments(field, r, lon_grid, lat_grid):
                lon_all.extend(seg[:, 0].tolist() + [None])
                lat_all.extend(seg[:, 1].tolist() + [None])
            fig.add_trace(go.Scattermap(
                lat=lat_all, lon=lon_all, mode="lines", fill="toself",
                fillcolor="rgba(0, 120, 200, 0.25)",
                line=dict(width=1.2, color="rgba(0, 90, 160, 0.9)"),
                name=f"União {ys}+ / {r} km", hoverinfo="skip",
                visible=(ys == config.COVERAGE_DEFAULT_YEAR and r == config.DEFAULT_RADIUS_KM),
            ))
            meta.append({"kind": "union", "year": ys, "radius": r})

    for ys in config.COVERAGE_YEAR_OPTIONS:
        sub = comps[comps["year"] >= ys]
        fig.add_trace(go.Scattermap(
            lat=sub["lat"], lon=sub["lon"], mode="markers",
            marker=dict(size=6, color="rgb(200, 30, 30)"),
            name=f"Competições {ys}+",
            text=sub["name"] + " (" + sub["year"].astype(str) + ")",
            hovertemplate="%{text}<extra></extra>",
            visible=(ys == config.COVERAGE_DEFAULT_YEAR),
        ))
        meta.append({"kind": "markers", "year": ys, "radius": None})

    fig.update_layout(
        map=dict(style="open-street-map", center=dict(lat=-14.5, lon=-51.5), zoom=3.2),
        height=800, margin=dict(l=0, r=0, t=10, b=0), showlegend=False,
    )
    return fig, meta


def _fragment(fig, meta, div_id="coverage-map"):
    """Dois seletores (ano e raio) + mapa + JS que compõe a visibilidade."""
    plot_div = to_html(fig, include_plotlyjs=False, full_html=False, div_id=div_id)
    year_opts = "".join(
        f'<option value="{y}"{" selected" if y == config.COVERAGE_DEFAULT_YEAR else ""}>{y}+</option>'
        for y in config.COVERAGE_YEAR_OPTIONS
    )
    rad_opts = "".join(
        f'<option value="{r}"{" selected" if r == config.DEFAULT_RADIUS_KM else ""}>{r} km</option>'
        for r in config.RADIUS_OPTIONS_KM
    )
    return f"""
<div class="coverage-controls" style="display:flex;gap:24px;align-items:center;margin:0 0 12px;">
  <label>Competições desde: <select id="cov-year">{year_opts}</select></label>
  <label>Raio de cobertura: <select id="cov-radius">{rad_opts}</select></label>
</div>
{plot_div}
<script>
(function () {{
  var META = {json.dumps(meta)};
  function covUpdate() {{
    var ys  = parseInt(document.getElementById('cov-year').value, 10);
    var rad = parseInt(document.getElementById('cov-radius').value, 10);
    var vis = META.map(function (m) {{
      return m.kind === 'markers' ? (m.year === ys) : (m.year === ys && m.radius === rad);
    }});
    Plotly.restyle('{div_id}', {{visible: vis}});
  }}
  document.getElementById('cov-year').addEventListener('change', covUpdate);
  document.getElementById('cov-radius').addEventListener('change', covUpdate);
}})();
</script>
"""


def build_coverage_block(con) -> str:
    """Fragmento HTML completo (controles + mapa + JS) pronto para a página."""
    comps = coverage_competitions(con)
    lon_grid, lat_grid, grid_xyz = _make_grid(comps)
    fig, meta = _build_figure(comps, lon_grid, lat_grid, grid_xyz)
    return _fragment(fig, meta)
