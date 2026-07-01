"""Montagem da página HTML final com abas (deploy via GitHub Pages)."""

import re

import plotly.graph_objects as go
from plotly.io import to_html

_PLOTLY_CDN_RE = re.compile(
    r'<script[^>]*src="https://cdn\.plot\.ly/[^"]*"[^>]*>\s*</script>', re.I
)


def _plotly_cdn_tag() -> str:
    """Tag <script> da CDN do Plotly, na versão que o plotly.py gera (evita mismatch)."""
    html = to_html(go.Figure(), include_plotlyjs="cdn", full_html=False)
    m = _PLOTLY_CDN_RE.search(html)
    return m.group(0) if m else '<script src="https://cdn.plot.ly/plotly.min.js"></script>'


def _charts_html(items) -> str:
    """Blocos de gráficos de uma aba.

    Cada item é uma go.Figure ou uma tupla (título, html) já pronta (ex.: o mapa
    de cobertura, com seus próprios controles). O Plotly vem uma única vez no
    <head> da página, então nenhuma figura embute a biblioteca.
    """
    blocks = []
    for i, item in enumerate(items):
        if isinstance(item, tuple):
            title, graph_html = item
        else:
            graph_html = to_html(item, include_plotlyjs=False, full_html=False)
            title = item.layout.title.text or f"Gráfico {i + 1}"
        blocks.append(f'<div class="chart"><h2>{title}</h2>{graph_html}</div>')
    return "\n".join(blocks)


_CSS = """
    body { font-family: Arial, sans-serif; margin: 0; padding: 0; }
    h1 { text-align: center; margin: 20px 0 0; }
    .tabs {
        position: sticky; top: 0; z-index: 10;
        display: flex; justify-content: center; gap: 8px;
        background: #fff; padding: 14px; border-bottom: 1px solid #ddd;
    }
    .tab-btn {
        font-size: 16px; padding: 10px 22px; cursor: pointer;
        border: 1px solid #ccc; border-radius: 6px; background: #f5f5f5;
    }
    .tab-btn.active { background: #0078c8; color: #fff; border-color: #0078c8; }
    .tab-panel { display: none; max-width: 1400px; margin: auto; padding: 20px; }
    .tab-panel.active { display: block; }
    .chart { margin-top: 50px; margin-bottom: 50px; }
"""

_JS = """
    document.querySelectorAll('.tab-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
            btn.classList.add('active');
            var panel = document.getElementById(btn.dataset.tab);
            panel.classList.add('active');
            // gráficos renderizados escondidos ficam com largura 0: força o redimensionamento
            panel.querySelectorAll('.js-plotly-plot').forEach(function (gd) {
                if (window.Plotly) window.Plotly.Plots.resize(gd);
            });
        });
    });
"""


def build_tabbed_page(tabs, output_file, page_title="WCA Brasil — Análise") -> str:
    """Gera uma única página HTML com abas.

    tabs: list[tuple[str, list]] -> [(rótulo_da_aba, [figuras/fragmentos]), ...]
    Escreve `output_file` e o retorna. Nenhum arquivo intermediário é criado.
    """
    nav, panels = [], []
    for i, (label, items) in enumerate(tabs):
        active = " active" if i == 0 else ""
        nav.append(f'<button class="tab-btn{active}" data-tab="tab{i}">{label}</button>')
        panels.append(
            f'<section id="tab{i}" class="tab-panel{active}">{_charts_html(items)}</section>'
        )

    html = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{page_title}</title>
    {_plotly_cdn_tag()}
    <style>{_CSS}</style>
</head>
<body>
    <h1>{page_title}</h1>
    <nav class="tabs">{"".join(nav)}</nav>
    {"".join(panels)}
    <script>{_JS}</script>
</body>
</html>"""

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)
    return str(output_file)
