"""Chart factory: every chart of the interface is built here (docs/umsetzungsplan.md, 7.1).

Standard for every chart: time range buttons 1 M / 6 M / 1 J / 5 J / Max (no range slider),
zoom and pan (no scroll zoom), PNG export with a dated file name, title, source, observation
date and retrieval time as an annotation inside the chart, a fixed uirevision so the 5-minute
refresh keeps the zoom, connectgaps=False, decimal comma and numeric dates. Titles, annotations
and hover texts carry only configuration texts and self-formatted values (Plotly interprets an
HTML subset). Colours: validated reference palette (dataviz skill), light and dark steps.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

import plotly.graph_objects as go
import plotly.io as pio

from fever.web import format as fmt

# Reference palette (validated 26.09.2026 with the dataviz validator, light and dark surface).
PALETTE = {
    "light": {
        "surface": "#fcfcfb", "ink": "#0b0b0b", "secondary": "#52514e", "muted": "#898781",
        "grid": "#e1e0d9", "axis": "#c3c2b7", "series": ["#2a78d6", "#eb6834"],
    },
    "dark": {
        "surface": "#1a1a19", "ink": "#ffffff", "secondary": "#c3c2b7", "muted": "#898781",
        "grid": "#2c2c2a", "axis": "#383835", "series": ["#3987e5", "#d95926"],
    },
}
FONT = 'system-ui, -apple-system, "Segoe UI", sans-serif'
RANGE_BUTTONS = [
    {"count": 1, "label": "1 M", "step": "month", "stepmode": "backward"},
    {"count": 6, "label": "6 M", "step": "month", "stepmode": "backward"},
    {"count": 1, "label": "1 J", "step": "year", "stepmode": "backward"},
    {"count": 5, "label": "5 J", "step": "year", "stepmode": "backward"},
    {"label": "Max", "step": "all"},
]
DATE_FORMATS = [
    {"dtickrange": [None, "M1"], "value": "%d.%m.%Y"},
    {"dtickrange": ["M1", "M11"], "value": "%m.%Y"},
    {"dtickrange": ["M12", None], "value": "%Y"},
]
INITIAL_YEARS = 5


def _template(mode: str) -> go.layout.Template:
    p = PALETTE[mode]
    axis = {"gridcolor": p["grid"], "linecolor": p["axis"], "zerolinecolor": p["axis"], "tickcolor": p["axis"],
            "tickfont": {"color": p["muted"]}, "title": {"font": {"color": p["secondary"]}}}
    return go.layout.Template(layout={
        "paper_bgcolor": p["surface"], "plot_bgcolor": p["surface"], "colorway": p["series"],
        "font": {"family": FONT, "color": p["ink"], "size": 13},
        "xaxis": axis, "yaxis": axis,
        "hoverlabel": {"bgcolor": p["surface"], "bordercolor": p["axis"], "font": {"color": p["ink"], "family": FONT}},
        "legend": {"font": {"color": p["secondary"]}},
    })


for _mode in PALETTE:
    pio.templates[f"fever_{_mode}"] = _template(_mode)


@dataclass(frozen=True)
class Line:
    """One series of a chart; None values stay gaps (stale or missing), never interpolated."""

    name: str
    x: list[date]
    y: list[float | None]
    hover_decimals: int = 1
    shape: str = "linear"  # "hv" for levels that hold until the next change


@dataclass(frozen=True)
class Chart:
    kennzahl_id: str
    title: str
    source: str
    lines: list[Line]
    y_title: str
    observed: date | None = None  # newest observation date shown
    retrieved: datetime | None = None  # newest retrieval behind the chart
    y_range: tuple[float, float] | None = None
    y_ticks: dict[float, str] = field(default_factory=dict)  # fixed tick labels, e.g. traffic light levels


def time_series(chart: Chart, theme: str, today: date | None = None) -> tuple[go.Figure, dict]:
    """Figure and dcc.Graph config of a time series chart in the project standard."""
    mode = theme if theme in PALETTE else "light"
    palette = PALETTE[mode]
    figure = go.Figure()
    for index, line in enumerate(chart.lines):
        figure.add_trace(go.Scatter(
            x=line.x, y=line.y, name=line.name, mode="lines", connectgaps=False,
            line={"width": 2, "shape": line.shape, "color": palette["series"][index % len(palette["series"])]},
            hovertemplate=f"%{{y:,.{line.hover_decimals}f}}<extra>{line.name}</extra>",
        ))
    last = max((max(line.x) for line in chart.lines if line.x), default=None)
    xaxis = {
        "type": "date", "rangeselector": {"buttons": RANGE_BUTTONS, "x": 0, "y": 1.02, "yanchor": "bottom",
                                          "bgcolor": palette["surface"], "activecolor": palette["grid"],
                                          "bordercolor": palette["axis"], "borderwidth": 1,
                                          "font": {"color": palette["secondary"]}},
        "rangeslider": {"visible": False}, "tickformatstops": DATE_FORMATS, "hoverformat": "%d.%m.%Y",
        "tickangle": 0,  # rotated labels would run into the dating lines on a narrow screen
    }
    if last is not None:
        first = min(min(line.x) for line in chart.lines if line.x)
        xaxis["range"] = [max(first, _years_before(last, INITIAL_YEARS)), last]
    yaxis = {"title": {"text": chart.y_title}, "fixedrange": False}
    if chart.y_range is not None:
        yaxis["range"] = list(chart.y_range)
    if chart.y_ticks:
        yaxis.update(tickmode="array", tickvals=list(chart.y_ticks), ticktext=list(chart.y_ticks.values()))
    figure.update_layout(
        template=f"fever_{mode}", separators=",.", uirevision=chart.kennzahl_id,
        title={"text": chart.title, "x": 0, "xanchor": "left", "font": {"size": 15}},
        margin={"l": 56, "r": 16, "t": 124 if len(chart.lines) > 1 else 84, "b": 104}, hovermode="x unified",
        showlegend=len(chart.lines) > 1,
        # own row between title and range buttons, so it never covers them on a narrow screen
        legend={"orientation": "h", "x": 0, "xanchor": "left", "y": 1.15, "yanchor": "bottom"},
        xaxis=xaxis, yaxis=yaxis,
        annotations=[{
            "text": stamp(chart.source, chart.observed, chart.retrieved), "showarrow": False,
            "xref": "paper", "yref": "paper", "x": 0, "y": -0.14, "xanchor": "left", "yanchor": "top", "align": "left",
            "font": {"size": 11, "color": palette["muted"]},
        }],
    )
    config = {
        "displaylogo": False, "scrollZoom": False, "responsive": True,
        "modeBarButtonsToRemove": ["select2d", "lasso2d", "autoScale2d"],
        "toImageButtonOptions": {"format": "png", "scale": 2,
                                 "filename": f"{chart.kennzahl_id}_{(today or date.today()):%d-%m-%Y}"},
    }
    return figure, config


def stamp(source: str, observed: date | None, retrieved: datetime | None) -> str:
    """The dating lines inside every chart: an exported or printed image is never timeless.

    Three short lines (<br> is the only markup, set here) so the stamp fits a 390 px screen.
    """
    return f"Quelle: {source}<br>Stand: {fmt.day(observed)}<br>Abruf: {fmt.berlin(retrieved)}"


def _years_before(day: date, years: int) -> date:
    try:
        return day.replace(year=day.year - years)
    except ValueError:
        return day - timedelta(days=1)
