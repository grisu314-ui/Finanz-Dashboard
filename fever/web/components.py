"""Shared building blocks: Kennzahl head with tooltip, freshness line, traffic light, chart card.

Every value is plain text (Dash escapes it); nothing is rendered as HTML.
"""

from datetime import date, datetime

from dash import dcc, html

from fever.web import format as fmt
from fever.web import texts
from fever.web.figures import Chart, time_series

LEVEL_CLASSES = ("level-green", "level-yellow", "level-orange", "level-red")
# Sequential blue ramp of the reference palette, light -> dark (E-1: percentile colours).
PERCENTILE_RAMP = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5",
                   "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b"]


def kennzahl_head(kennzahl_id: str, *, tag=html.H2) -> html.Div:
    """Name as link to /kennzahl/<id> plus info symbol with the short info as a CSS tooltip.

    Raises TextError without a text file: a Kennzahl without text is never displayed.
    """
    text = texts.text(kennzahl_id)
    return html.Div(className="k-head", children=[
        tag(dcc.Link(text.title, href=f"/kennzahl/{kennzahl_id}", className="k-name")),
        html.Span("ⓘ", className="tip", tabIndex=0, role="note", **{"data-tip": text.short, "aria-label": text.short}),
    ])


def freshness(observed: date | None, retrieved: datetime | None, *, stale: bool, now: datetime,
              retrieved_label: str = "Abruf") -> html.Div:
    parts = [f"Stand {fmt.day(observed)}", f"{retrieved_label} {fmt.berlin(retrieved)} ({fmt.age(retrieved, now)})"]
    children = [html.Span(" · ".join(parts))]
    if stale:
        children.append(html.Span("veraltet", className="badge badge-stale"))
    return html.Div(className="freshness" + (" is-stale" if stale else ""), children=children)


def level_badge(level: int | None) -> html.Span:
    if level is None:
        return html.Span("unbekannt", className="level level-unknown")
    return html.Span(texts.LEVEL_NAMES[level], className=f"level {LEVEL_CLASSES[level]}")


def percentile_chip(percentile: float | None, elevated_above: float) -> html.Span:
    """Neutral blue scale; "erhöht" as text plus border above the diffusion threshold (E-1)."""
    if percentile is None:
        return html.Span("kein Perzentil", className="pct pct-none")
    step = PERCENTILE_RAMP[min(len(PERCENTILE_RAMP) - 1, int(percentile / 100 * len(PERCENTILE_RAMP)))]
    dark = PERCENTILE_RAMP.index(step) >= 7
    elevated = percentile > elevated_above
    label = f"Perzentil {fmt.number(percentile, 0)}" + (" · erhöht" if elevated else "")
    return html.Span(label, className="pct" + (" pct-elevated" if elevated else ""),
                     style={"backgroundColor": step, "color": "#ffffff" if dark else "#0b0b0b"})


def chart_card(graph_id: str, chart: Chart, theme: str) -> html.Div:
    figure, config = time_series(chart, theme)
    return html.Div(className="card chart-card", children=[
        html.Button("Vollbild", className="fullscreen-toggle", type="button", **{"aria-label": "Chart im Vollbild zeigen"}),
        dcc.Graph(id=graph_id, figure=figure, config=config, responsive=True, className="chart"),
    ])


def note(text: str) -> html.P:
    return html.P(text, className="note")


def facts_table(rows: list[tuple[str, str]]) -> html.Table:
    return html.Table(className="facts", children=[html.Tbody([html.Tr([html.Th(label), html.Td(value)]) for label, value in rows])])
