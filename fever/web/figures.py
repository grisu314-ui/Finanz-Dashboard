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
        "grid": "#e1e0d9", "axis": "#c3c2b7",
        # categorical slots in the validated order (blue, orange, aqua, yellow, magenta, green, violet, red)
        "series": ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"],
        "recession": "rgba(137, 135, 129, 0.18)",
        "shaded": "rgba(74, 58, 167, 0.14)",  # violet slot: phases like backwardation or inversion
    },
    "dark": {
        "surface": "#1a1a19", "ink": "#ffffff", "secondary": "#c3c2b7", "muted": "#898781",
        "grid": "#2c2c2a", "axis": "#383835",
        "series": ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#008300", "#9085e9", "#e66767"],
        "recession": "rgba(195, 194, 183, 0.14)",
        "shaded": "rgba(144, 133, 233, 0.20)",
    },
}
FONT = 'system-ui, -apple-system, "Segoe UI", sans-serif'
# Sequential blue ramp of the reference palette, light -> dark (E-1: percentile colours).
PERCENTILE_RAMP = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5",
                   "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b"]
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
    hover_decimals: int | None = 1  # None: four significant digits (small changes stay readable)
    shape: str = "linear"  # "hv" for levels that hold until the next change


@dataclass(frozen=True)
class Band:
    """Percentile band of an indicator (E-64): 10th to 90th percentile of its window, with the median."""

    x: list[date]
    low: list[float | None]
    mid: list[float | None]
    high: list[float | None]


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
    recessions: tuple[tuple[date, date], ...] = ()  # grey bars behind the lines (E-56)
    full_history: bool = False  # start with the whole history instead of the last INITIAL_YEARS (E-61)
    shaded: tuple[tuple[date, date], ...] = ()  # violet phases, e.g. backwardation or inversion (M7)
    shaded_label: str = ""  # what the violet phases mean, one line under the dating lines
    zero_line: bool = False
    end_labels: bool = False  # name at the end of each line (relief rule for more than two series)
    episodes: tuple[tuple[date, date, str], ...] = ()  # crisis marks as a strip on top (E-63)
    band: Band | None = None


def time_series(chart: Chart, theme: str, today: date | None = None) -> tuple[go.Figure, dict]:
    """Figure and dcc.Graph config of a time series chart in the project standard."""
    mode = theme if theme in PALETTE else "light"
    palette = PALETTE[mode]
    figure = go.Figure()
    if chart.band is not None:
        band, colour = chart.band, palette["series"][0]
        figure.add_trace(go.Scatter(x=band.x, y=band.low, mode="lines", line={"width": 0}, connectgaps=False,
                                    showlegend=False, hoverinfo="skip"))
        figure.add_trace(go.Scatter(x=band.x, y=band.high, mode="lines", line={"width": 0}, connectgaps=False,
                                    fill="tonexty", fillcolor=_tint(colour, palette["surface"], 0.25),
                                    name="10–90 % des Fensters", hovertemplate="%{y:,.4~g}<extra>90 %</extra>"))
        figure.add_trace(go.Scatter(x=band.x, y=band.mid, mode="lines", connectgaps=False, name="Median des Fensters",
                                    line={"width": 1, "dash": "dash", "color": palette["secondary"]},
                                    hovertemplate="%{y:,.4~g}<extra>Median</extra>"))
    for index, line in enumerate(chart.lines):
        figure.add_trace(go.Scatter(
            x=line.x, y=line.y, name=line.name, mode="lines", connectgaps=False,
            line={"width": 2, "shape": line.shape, "color": palette["series"][index % len(palette["series"])]},
            hovertemplate=(f"%{{y:,.{line.hover_decimals}f}}" if line.hover_decimals is not None else "%{y:,.4~g}")
            + f"<extra>{line.name}</extra>",
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
    shapes, labels = [], []
    if last is not None:
        # the first day with a value: score days before an indicator existed would only show empty space
        firsts = [next((x for x, y in zip(line.x, line.y) if y is not None), None) for line in chart.lines]
        first = min((x for x in firsts if x is not None), default=min(min(line.x) for line in chart.lines if line.x))
        xaxis["range"] = [first if chart.full_history else max(first, _years_before(last, INITIAL_YEARS)), last]
        shapes = [
            {"type": "rect", "xref": "x", "yref": "paper", "x0": start, "x1": end, "y0": 0, "y1": 1,
             "fillcolor": palette[kind], "line": {"width": 0}, "layer": "below"}
            for kind, periods in (("recession", chart.recessions), ("shaded", chart.shaded))
            for start, end in periods if end >= first and start <= last
        ]
    for start, end, label in chart.episodes:
        shapes.append({"type": "rect", "xref": "x", "yref": "paper", "x0": start, "x1": end, "y0": 0.94, "y1": 1,
                       "fillcolor": palette["secondary"], "opacity": 0.55, "line": {"width": 0}})
    if chart.episodes:  # hover over the strip names the episode
        figure.add_trace(go.Scatter(
            x=[start + (end - start) / 2 for start, end, _ in chart.episodes], y=[1.0] * len(chart.episodes), yaxis="y2",
            mode="markers", marker={"size": 14, "opacity": 0}, showlegend=False,
            text=[f"{label}: {fmt.day(start)} bis {fmt.day(end)}" for start, end, label in chart.episodes],
            hovertemplate="%{text}<extra>Krise</extra>"))
    if chart.zero_line:
        shapes.append({"type": "line", "xref": "paper", "yref": "y", "x0": 0, "x1": 1, "y0": 0, "y1": 0,
                       "line": {"width": 1, "color": palette["axis"]}, "layer": "below"})
    if chart.end_labels:
        for index, line in enumerate(chart.lines):
            points = [(x, y) for x, y in zip(line.x, line.y) if y is not None]
            if points:
                labels.append({"x": points[-1][0], "y": points[-1][1], "text": line.name, "showarrow": False,
                               "xanchor": "right", "yanchor": "bottom", "yshift": 2,
                               "font": {"size": 11, "color": palette["secondary"]}})
    yaxis = {"title": {"text": chart.y_title}, "fixedrange": False}
    if chart.y_range is not None:
        yaxis["range"] = list(chart.y_range)
    if chart.y_ticks:
        yaxis.update(tickmode="array", tickvals=list(chart.y_ticks), ticktext=list(chart.y_ticks.values()))
    figure.update_layout(
        template=f"fever_{mode}", separators=",.", uirevision=chart.kennzahl_id,
        title={"text": chart.title, "x": 0, "xanchor": "left", "font": {"size": 15}},
        margin={"l": 56, "r": 16, "t": 124 if len(chart.lines) > 1 or chart.band is not None else 84,
                "b": 62 + 14 * (3 + bool(chart.recessions) + bool(chart.shaded_label) + bool(chart.episodes))},
        hovermode="x unified",
        showlegend=len(chart.lines) > 1 or chart.band is not None,
        # own row between title and range buttons, so it never covers them on a narrow screen
        legend={"orientation": "h", "x": 0, "xanchor": "left", "y": 1.15, "yanchor": "bottom"},
        xaxis=xaxis, yaxis=yaxis, shapes=shapes,
        **({"yaxis2": {"overlaying": "y", "range": [0, 1.03], "visible": False, "fixedrange": True}} if chart.episodes else {}),
        annotations=[*labels, stamp_annotation(
            stamp(chart.source, chart.observed, chart.retrieved, recessions=bool(chart.recessions))
            + (f"<br>{chart.shaded_label}" if chart.shaded_label else "")
            + ("<br>Balken oben: Krisen, S&P 500 vom Hoch bis zum Tief" if chart.episodes else ""), mode)],
    )
    return figure, graph_config(chart.kennzahl_id, today)


def graph_config(chart_id: str, today: date | None = None) -> dict:
    """dcc.Graph config shared by every chart: PNG export with a dated name, no scroll zoom, no cloud."""
    return {
        "displaylogo": False, "scrollZoom": False, "responsive": True,
        # plotly.js 4 shows "Share chart..." by default, which uploads the chart with its data to
        # Plotly Cloud: no licensed data leaves the house, the browser talks only to this server
        "showSendToCloud": False,
        "modeBarButtonsToRemove": ["select2d", "lasso2d", "autoScale2d"],
        "toImageButtonOptions": {"format": "png", "scale": 2, "filename": f"{chart_id}_{(today or date.today()):%d-%m-%Y}"},
    }


def stamp_annotation(text: str, mode: str, yshift: int = -28) -> dict:
    # fixed pixel offset below the axis: a paper fraction grows with the plot and pushed the
    # lines out of the full-screen view
    return {"text": text, "showarrow": False, "xref": "paper", "yref": "paper", "x": 0, "y": 0, "yshift": yshift,
            "xanchor": "left", "yanchor": "top", "align": "left", "font": {"size": 11, "color": PALETTE[mode]["muted"]}}


# Status colours of the traffic light (reference palette, reserved for it; always with the level name).
STATUS = ("#0ca30c", "#fab219", "#ec835a", "#d03b3b")


@dataclass(frozen=True)
class Region:
    """A rectangle of the traffic light matrix in score units; regions are drawn in order, later on top."""

    level: int  # index into STATUS and the level names
    label: str  # shown in the region; empty for a second rectangle of the same level
    x0: float
    x1: float
    y0: float
    y1: float


@dataclass(frozen=True)
class Matrix:
    """Traffic light matrix (report 6.3, view 1): stress on x, vulnerability on y, with a trace of recent days."""

    chart_id: str
    title: str
    source: str
    days: list[date]  # oldest first; the last one is today's point
    stress: list[float | None]
    vulnerability: list[float | None]
    regions: tuple[Region, ...]
    observed: date | None = None
    retrieved: datetime | None = None
    note: str = ""  # extra line under the dating lines


def matrix(chart: Matrix, theme: str, today: date | None = None) -> tuple[go.Figure, dict]:
    mode = theme if theme in PALETTE else "light"
    palette = PALETTE[mode]
    # opaque tints: later regions cover earlier ones completely instead of mixing their colours
    shapes = [{"type": "rect", "xref": "x", "yref": "y", "x0": r.x0, "x1": r.x1, "y0": r.y0, "y1": r.y1,
               "fillcolor": _tint(STATUS[r.level], palette["surface"], 0.3), "line": {"width": 0}, "layer": "below"}
              for r in chart.regions]
    # labels of full-height stress bands stand upright: side by side they would collide on a phone
    labels = [{"text": r.label, "x": r.x0, "y": r.y0, "xref": "x", "yref": "y", "xanchor": "left", "yanchor": "bottom",
               "xshift": 4, "yshift": 4, "showarrow": False, "font": {"size": 12, "color": palette["ink"]},
               "textangle": -90 if (r.x0 > 0 and r.y0 == 0 and r.y1 == 100) else 0}
              for r in chart.regions if r.label]
    points = [(d, x, y) for d, x, y in zip(chart.days, chart.stress, chart.vulnerability) if x is not None and y is not None]
    hover = "%{customdata}<br>Stress %{x:,.1f} · Fallhöhe %{y:,.1f}<extra></extra>"
    figure = go.Figure()
    if points:
        days, xs, ys = zip(*points)
        figure.add_trace(go.Scatter(
            x=xs, y=ys, mode="lines+markers", name="Spur", customdata=[fmt.day(d) for d in days], hovertemplate=hover,
            line={"width": 2, "color": palette["series"][0]}, marker={"size": 6, "color": palette["series"][0]},
        ))
        figure.add_trace(go.Scatter(
            x=[xs[-1]], y=[ys[-1]], mode="markers+text", name="Heute", customdata=[fmt.day(days[-1])], hovertemplate=hover,
            text=[f"Stand {fmt.day(days[-1])}"], textposition="top center", textfont={"color": palette["ink"]},
            marker={"size": 14, "color": palette["series"][0], "line": {"width": 2, "color": palette["surface"]}},
        ))
    axis = {"range": [0, 100], "dtick": 20, "zeroline": False}
    text = stamp(chart.source, chart.observed, chart.retrieved) + (f"<br>{chart.note}" if chart.note else "")
    figure.update_layout(
        template=f"fever_{mode}", separators=",.", uirevision=chart.chart_id, showlegend=False,
        title={"text": chart.title, "x": 0, "xanchor": "left", "font": {"size": 15}},
        margin={"l": 56, "r": 16, "t": 56, "b": 150 + 14 * chart.note.count("<br>") if chart.note else 150},
        xaxis={**axis, "title": {"text": "Stress (geglättet)"}}, yaxis={**axis, "title": {"text": "Fallhöhe (geglättet)"}},
        shapes=shapes, annotations=[*labels, stamp_annotation(text, mode, yshift=-58)],
    )
    return figure, graph_config(chart.chart_id, today)


@dataclass(frozen=True)
class CurvePoint:
    label: str  # e.g. "VIX3M" or "VX2"
    days: float  # nominal horizon of an index, days to expiry of a future
    value: float
    group: str  # one line per group


@dataclass(frozen=True)
class Curve:
    """Term structure on one day: x = days, y = level (report 6.3, view 2)."""

    chart_id: str
    title: str
    source: str
    points: list[CurvePoint]
    x_title: str
    y_title: str
    observed: date | None = None
    retrieved: datetime | None = None
    note: str = ""


def curve(chart: Curve, theme: str, today: date | None = None) -> tuple[go.Figure, dict]:
    mode = theme if theme in PALETTE else "light"
    palette = PALETTE[mode]
    figure = go.Figure()
    groups = list(dict.fromkeys(point.group for point in chart.points))
    for index, group in enumerate(groups):
        points = sorted((p for p in chart.points if p.group == group), key=lambda p: p.days)
        figure.add_trace(go.Scatter(
            x=[p.days for p in points], y=[p.value for p in points], name=group, mode="lines+markers+text",
            text=[p.label for p in points], textposition="top center", textfont={"size": 10, "color": palette["secondary"]},
            line={"width": 2, "color": palette["series"][index]}, marker={"size": 8, "color": palette["series"][index]},
            hovertemplate="%{text}: %{y:,.2f} (%{x} Tage)<extra></extra>",
        ))
    text = stamp(chart.source, chart.observed, chart.retrieved) + (f"<br>{chart.note}" if chart.note else "")
    figure.update_layout(
        template=f"fever_{mode}", separators=",.", uirevision=chart.chart_id, showlegend=len(groups) > 1,
        title={"text": chart.title, "x": 0, "xanchor": "left", "font": {"size": 15}},
        legend={"orientation": "h", "x": 0, "xanchor": "left", "y": 1.02, "yanchor": "bottom"},
        margin={"l": 56, "r": 16, "t": 96, "b": 62 + 14 * (3 + chart.note.count("<br>") + bool(chart.note)) + 26},
        xaxis={"title": {"text": chart.x_title}, "rangemode": "tozero"}, yaxis={"title": {"text": chart.y_title}},
        annotations=[stamp_annotation(text, mode, yshift=-54)],
    )
    return figure, graph_config(chart.chart_id, today)


@dataclass(frozen=True)
class Heatmap:
    """Indicators x time in the percentile colours (E-1, E-66); None stays blank (not valid that day)."""

    chart_id: str
    title: str
    source: str
    rows: list[str]  # names, top to bottom
    x: list[date]
    z: list[list[float | None]]  # one list per row
    observed: date | None = None
    retrieved: datetime | None = None
    note: str = ""


def heatmap(chart: Heatmap, theme: str, today: date | None = None) -> tuple[go.Figure, dict]:
    mode = theme if theme in PALETTE else "light"
    steps = len(PERCENTILE_RAMP) - 1
    scale = [[i / steps, colour] for i, colour in enumerate(PERCENTILE_RAMP)]
    figure = go.Figure(go.Heatmap(
        x=chart.x, y=chart.rows, z=chart.z, zmin=0, zmax=100, colorscale=scale, hoverongaps=False,
        colorbar={"title": {"text": "Perzentil"}, "thickness": 10, "len": 0.8},
        hovertemplate="%{y}<br>%{x|%d.%m.%Y}: Perzentil %{z:.0f}<extra></extra>",
    ))
    text = stamp(chart.source, chart.observed, chart.retrieved) + (f"<br>{chart.note}" if chart.note else "")
    figure.update_layout(
        template=f"fever_{mode}", separators=",.", uirevision=chart.chart_id,
        title={"text": chart.title, "x": 0, "xanchor": "left", "font": {"size": 15}},
        margin={"l": 8, "r": 8, "t": 56, "b": 62 + 14 * (4 + chart.note.count("<br>"))},
        xaxis={"type": "date", "tickformatstops": DATE_FORMATS, "tickangle": 0},
        yaxis={"autorange": "reversed", "automargin": True, "tickfont": {"size": 11}},
        annotations=[stamp_annotation(text, mode)],
    )
    return figure, graph_config(chart.chart_id, today)


@dataclass(frozen=True)
class Regime:
    """Traffic light level per score day as one coloured strip (report 6.3, view 7)."""

    chart_id: str
    title: str
    source: str
    x: list[date]
    levels: list[int | None]
    names: tuple[str, ...]  # level names, index = level
    observed: date | None = None
    retrieved: datetime | None = None


def regime(chart: Regime, theme: str, today: date | None = None) -> tuple[go.Figure, dict]:
    mode = theme if theme in PALETTE else "light"
    n = len(STATUS)
    scale = [item for level, colour in enumerate(STATUS) for item in ([level / n, colour], [(level + 1) / n, colour])]
    figure = go.Figure(go.Heatmap(
        x=chart.x, y=["Ampel"], z=[chart.levels], zmin=-0.5, zmax=n - 0.5, colorscale=scale, showscale=False,
        customdata=[[chart.names[v] if v is not None else "–" for v in chart.levels]], hoverongaps=False,
        hovertemplate="%{x|%d.%m.%Y}: %{customdata}<extra></extra>",
    ))
    text = stamp(chart.source, chart.observed, chart.retrieved) + "<br>Farben: " + ", ".join(chart.names)
    figure.update_layout(
        template=f"fever_{mode}", separators=",.", uirevision=chart.chart_id,
        title={"text": chart.title, "x": 0, "xanchor": "left", "font": {"size": 15}},
        margin={"l": 56, "r": 16, "t": 84, "b": 62 + 14 * 4},
        xaxis={"type": "date", "tickformatstops": DATE_FORMATS, "tickangle": 0,
               "rangeselector": {"buttons": RANGE_BUTTONS, "x": 0, "y": 1.02, "yanchor": "bottom"}},
        yaxis={"visible": False, "fixedrange": True},
        annotations=[stamp_annotation(text, mode)],
    )
    return figure, graph_config(chart.chart_id, today)


def sparkline(x: list[date], y: list[float | None], theme: str) -> tuple[go.Figure, dict]:
    """Small line without axes; its date and value stand as text next to it (view 7)."""
    mode = theme if theme in PALETTE else "light"
    figure = go.Figure(go.Scatter(x=x, y=y, mode="lines", connectgaps=False, hoverinfo="skip",
                                  line={"width": 1.5, "color": PALETTE[mode]["series"][0]}))
    figure.update_layout(template=f"fever_{mode}", margin={"l": 0, "r": 0, "t": 2, "b": 2}, showlegend=False,
                         xaxis={"visible": False}, yaxis={"visible": False})
    return figure, {"staticPlot": True, "displayModeBar": False, "responsive": True}


def stamp(source: str, observed: date | None, retrieved: datetime | None, *, recessions: bool = False) -> str:
    """The dating lines inside every chart: an exported or printed image is never timeless.

    Short lines (<br> is the only markup, set here) so the stamp fits a 390 px screen.
    """
    text = f"Quelle: {source}<br>Stand: {fmt.day(observed)}<br>Abruf: {fmt.berlin(retrieved)}"
    return text + ("<br>Grau: US-Rezessionen nach NBER (über FRED)" if recessions else "")


def _tint(color: str, surface: str, share: float) -> str:
    """`share` of the colour on the surface, as an opaque hex colour (works in light and dark mode)."""
    a, b = (tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in (color, surface))
    return "#" + "".join(f"{round(share * x + (1 - share) * y):02x}" for x, y in zip(a, b))


def _years_before(day: date, years: int) -> date:
    try:
        return day.replace(year=day.year - years)
    except ValueError:
        return day - timedelta(days=1)
