"""Page contents as plain functions (tested without a browser); the modules in pages/ call them.

Everything shown comes from the database (read-only) and the configuration; nothing is
computed here that the scoring computes. Database errors turn into a visible notice.
"""

from datetime import date, datetime

from dash import dcc, html
from sqlalchemy.exc import SQLAlchemyError

from fever.config import VULNERABILITY, indicator_catalog, scoring_config, series_catalog
from fever.release import NEW_YORK, is_stale
from fever.store.db import DataDirError
from fever.web import components as ui
from fever.web import db, texts
from fever.web import format as fmt
from fever.web.figures import Chart, Line
from fever.worker import HEARTBEAT_MAX_AGE  # same limit as the container healthcheck (E-33)

SOURCE_NAMES = {
    "cboe": "Cboe (Indizes)", "cfe": "Cboe Futures Exchange (VX-Futures)", "fred": "FRED (St. Louis Fed)",
    "ecb": "EZB", "ofr": "Office of Financial Research", "fed": "Federal Reserve Board", "cftc": "CFTC",
    "shiller": "Robert J. Shiller", "scoring": "Scoring (Berechnung im Worker)",
}
STATUS_NAMES = {
    "ok": "gültig", "stale": "veraltet", "history": "unter Mindesthistorie: angezeigt, nicht im Score",
    "missing": "noch kein veröffentlichter Wert",
}
# Phase-1 exception to the look-ahead rule; every history view says so (CLAUDE.md, fachliche Korrektheit).
HISTORY_NOTE = ("Verläufe: Je Beobachtung zählt der neueste veröffentlichte Stand. Revidierte Reihen sahen am "
                "jeweiligen Tag teils anders aus; die revisionsgenaue Rückrechnung folgt in Phase 2.")
PLACEHOLDERS = [
    "Nicht enthalten: Block Breite/Internals (keine Kursquelle, O-1) und Block Positionierung/Sentiment (erst Phase 2).",
    "Rot-Regel über den Anstieg des HY-OAS: inaktiv, bis O-5 entschieden ist.",
]


def guarded(render):
    """Show a notice instead of an error page when the database cannot be read."""
    def wrapper(*args, **kwargs):
        try:
            return render(*args, **kwargs)
        except (DataDirError, SQLAlchemyError) as exc:
            return [html.Div(f"Datenbank nicht lesbar: {exc}", className="banner banner-alert", role="alert")]
    return wrapper


def _today_new_york(now: datetime) -> date:
    return now.astimezone(NEW_YORK).date()


def _scores_stale(latest: dict, now: datetime) -> bool:
    # The score calendar is daily (Cboe trading days): same tolerance as a daily series (E-10).
    return is_stale(latest["score_date"], 0, "daily", 3, _today_new_york(now))


def _value(value: float | None) -> str:
    if value is None:
        return fmt.DASH
    return fmt.number(value, 0 if abs(value) >= 1000 else 2)


# --- overview --------------------------------------------------------------------------------------


@guarded
def overview(theme: str, now: datetime) -> list:
    latest = db.latest_composite()
    if latest is None:
        return [ui.note("Noch keine Scores berechnet. Der Worker rechnet nach dem nächsten Abruf; "
                        "sofort mit python -m fever.score (docs/einrichtung.md).")]
    stale = _scores_stale(latest, now)
    stamp = ui.freshness(latest["score_date"], latest["computed_at"], stale=stale, now=now, retrieved_label="berechnet")
    rules = [rule for rule in latest["active_rules"].split(",") if rule]
    traffic = html.Div(className="card card-traffic", children=[
        ui.kennzahl_head("traffic_light"),
        html.Div(ui.level_badge(latest["level"]), className="big"),
        html.Ul([html.Li(texts.rule_text(rule)) for rule in rules] or [html.Li("Keine Regel trifft zu.")], className="rules"),
        *([ui.note("Der Stress-Composite fehlt (weniger Blöcke als nötig); die Ampel stützt sich auf die übrigen Regeln.")]
          if latest["stress"] is None else []),
        stamp,
    ])
    cards = [
        traffic,
        _number_card("stress", latest["stress"], f"ungeglättet {fmt.number(latest['stress_raw'])}", stamp, PLACEHOLDERS),
        _number_card("vulnerability", latest["vulnerability"], f"ungeglättet {fmt.number(latest['vulnerability_raw'])}", stamp),
        _number_card("confidence", latest["confidence"], "Anteil aktueller Daten, gewichtet nach Vorlauf", stamp, unit=" %"),
    ]
    history = db.composite_history("stress", "vulnerability")
    chart = Chart(
        "stress", "Stress und Fallhöhe (geglättet)", "eigene Berechnung (Scoring)",
        [Line("Stress", [r["score_date"] for r in history], [r["stress"] for r in history]),
         Line("Fallhöhe", [r["score_date"] for r in history], [r["vulnerability"] for r in history])],
        "Wert (0–100)", observed=latest["score_date"], retrieved=latest["computed_at"], y_range=(0, 100),
        recessions=db.recessions(),
    )
    return [html.Div(cards, className="grid"), ui.chart_card("overview-history", chart, theme), ui.note(HISTORY_NOTE)]


def _number_card(kennzahl_id, value, detail, stamp, notes=(), unit=""):
    return html.Div(className="card", children=[
        ui.kennzahl_head(kennzahl_id),
        html.Div(fmt.number(value) + (unit if value is not None else ""), className="big number"),
        html.P(detail, className="detail"),
        *[ui.note(text) for text in notes],
        stamp,
    ])


# --- data status -----------------------------------------------------------------------------------


@guarded
def data_status(now: datetime) -> list:
    beat = db.heartbeat()
    alive = beat is not None and now - beat <= HEARTBEAT_MAX_AGE
    worker = html.Div(className="card", children=[
        html.H2("Worker"),
        html.P(f"Letztes Lebenszeichen {fmt.berlin(beat)} ({fmt.age(beat, now)})"),
        html.P("aktiv" if alive else "ohne Lebenszeichen: Werte werden nicht aktualisiert",
               className="badge" + ("" if alive else " badge-stale")),
    ])
    source_rows = [
        html.Tr([
            html.Td(SOURCE_NAMES.get(row["source"], row["source"])),
            html.Td(fmt.berlin(row["last_success_at"])),
            html.Td(fmt.berlin(row["last_attempt_at"])),
            html.Td([html.Div(fmt.berlin(row["last_error_at"])), html.Div(row["last_error_message"] or "", className="error-text")]),
        ])
        for row in db.sources()
    ]
    sources = html.Div(className="card card-wide", children=[
        html.H2("Quellen"),
        html.Div(className="table-scroll", children=html.Table(className="table", children=[
            html.Thead(html.Tr([html.Th("Quelle"), html.Th("Letzter Erfolg"), html.Th("Letzter Versuch"), html.Th("Letzter Fehler")])),
            html.Tbody(source_rows),
        ])),
    ])
    catalog = series_catalog()
    fresh = db.series_freshness()
    today = _today_new_york(now)
    rows = []
    for series in catalog.values():
        info = fresh.get(series.id)
        observed = info["obs_date"] if info else None
        stale = observed is None or is_stale(observed, series.lag_days, series.frequency, series.tolerance_days, today)
        rows.append((not stale, series.source, series.id, [
            html.Td(series.id), html.Td(series.name), html.Td(SOURCE_NAMES.get(series.source, series.source)),
            html.Td(fmt.day(observed)),
            html.Td(f"{fmt.berlin(info['retrieved_at'])} ({fmt.age(info['retrieved_at'], now)})" if info else fmt.DASH),
            html.Td("veraltet" if stale else "aktuell", className="badge badge-stale" if stale else "badge"),
        ]))
    rows.sort(key=lambda row: row[:3])  # stale first, then by source and id
    series_table = html.Div(className="card card-wide", children=[
        html.H2("Reihen"),
        ui.note("Veraltet: mehr Tage seit der erwarteten Veröffentlichung als Frequenz plus Toleranz der Reihe "
                "(Erklärung unter „Veraltung“)."),
        html.Div(className="table-scroll", children=html.Table(className="table", children=[
            html.Thead(html.Tr([html.Th("Reihe"), html.Th("Name"), html.Th("Quelle"), html.Th("Letzte Beobachtung"),
                                html.Th("Letzter neuer Wert abgerufen"), html.Th("Status")])),
            html.Tbody([html.Tr(cells, className="is-stale" if not ok else "") for ok, _, _, cells in rows]),
        ])),
    ])
    return [html.Div([worker], className="grid"), sources, series_table]


# --- explanations ----------------------------------------------------------------------------------


def explanations() -> list:
    groups: dict[str, list] = {}
    for kennzahl_id in texts.all_ids():
        if texts.has_text(kennzahl_id):
            groups.setdefault(texts.group_of(kennzahl_id), []).append(kennzahl_id)
    order = ["scores", "volatility", "credit", "macro", "breadth", "positioning", "vulnerability", "concepts"]
    sections = []
    for group in order:
        if group not in groups:
            continue
        items = [html.Li([dcc.Link(texts.text(k).title, href=f"/kennzahl/{k}"), html.Span(f" – {texts.text(k).short}")])
                 for k in groups[group]]
        sections.append(html.Div(className="card card-wide", children=[html.H2(texts.GROUPS[group]), html.Ul(items)]))
    missing = [k for k in texts.all_ids() if not texts.has_text(k) and k not in texts.CONCEPTS]
    if missing:
        sections.append(ui.note(f"Noch ohne Erklärtext und deshalb nicht angezeigt: {len(missing)} Kennzahlen (Texte folgen in M8)."))
    return sections


# --- Kennzahl page ---------------------------------------------------------------------------------


@guarded
def kennzahl(kennzahl_id: str | None, theme: str, now: datetime) -> list:
    if kennzahl_id not in texts.all_ids() or not texts.has_text(kennzahl_id):
        return [html.H1("Kennzahl nicht gefunden"), ui.note("Zu dieser Adresse gibt es keine Erklärseite."),
                dcc.Link("Alle Erklärungen", href="/erklaerungen")]
    text = texts.text(kennzahl_id)
    parts = [html.H1(text.title), html.P(text.short, className="lead")]
    history_from = None
    if kennzahl_id in indicator_catalog():
        state, charts, history_from = _indicator_state(kennzahl_id, theme, now)
        parts += [state, *charts, ui.note(HISTORY_NOTE)]
    elif kennzahl_id in texts.SCORES:
        parts += [*_score_state(kennzahl_id, theme, now), ui.note(HISTORY_NOTE)]
    for heading, body in text.sections:
        parts.append(html.Section(className="card card-wide text", children=[html.H2(heading), dcc.Markdown(body, link_target="_blank")]))
    if kennzahl_id in indicator_catalog():
        parts.append(_contribution_card(kennzahl_id))
    if kennzahl_id == "recessions":
        history_from = db.first_observation([db.RECESSION_SERIES])
    facts = texts.steckbrief(kennzahl_id, history_from)
    if facts:
        parts.append(html.Section(className="card card-wide", children=[html.H2("Steckbrief"), ui.facts_table(facts)]))
    parts.append(html.Section(className="card card-wide", children=[
        html.H2("Schwellen und Farben"), html.Ul([html.Li(line) for line in texts.thresholds(kennzahl_id)])]))
    return parts


def _indicator_state(kennzahl_id, theme, now):
    latest = db.latest_composite()
    row = db.indicator_scores_on(latest["score_date"]).get(kennzahl_id) if latest else None
    series_ids = [s.id for s in indicator_catalog()[kennzahl_id].series]
    if row is None:
        state = html.Div(className="card", children=[html.H2("Aktueller Stand"), ui.note("Noch kein Wert berechnet.")])
        return state, [], db.history_start(series_ids)
    config = scoring_config()
    retrieved = _retrieved(kennzahl_id, db.series_freshness())
    state = html.Div(className="card card-wide", children=[
        html.H2("Aktueller Stand"),
        html.Div(_value(row["value"]), className="big number"),
        ui.percentile_chip(row["percentile"], config.yellow_diffusion_percentile),
        *([html.P(f"Perzentil über {config.display_window_years} Jahre: {fmt.number(row['percentile_display'], 0)}")]
          if row["percentile_display"] is not None else []),
        html.P(f"Status: {STATUS_NAMES[row['status']]}", className="detail"),
        ui.freshness(row["obs_date"], retrieved, stale=row["status"] == "stale", now=now),
    ])
    return state, _indicator_charts(kennzahl_id, theme, row, retrieved, "chart"), db.history_start(series_ids)


def _retrieved(indicator_id: str, fresh: dict) -> datetime | None:
    return max((fresh[s.id]["retrieved_at"] for s in indicator_catalog()[indicator_id].series if s.id in fresh), default=None)


def _indicator_charts(kennzahl_id, theme, row, retrieved, prefix) -> list:
    """Value and percentile over time, both with the recession bars (E-56, E-59)."""
    indicator = indicator_catalog()[kennzahl_id]
    history = db.indicator_history(kennzahl_id)
    shown = {"ok", "history"}
    days = [r["score_date"] for r in history]
    source = ", ".join(sorted({SOURCE_NAMES.get(s.source, s.source) for s in indicator.series}))
    title = texts.text(kennzahl_id).title
    recessions = db.recessions()
    return [
        ui.chart_card(f"{prefix}-{kennzahl_id}-value", Chart(
            kennzahl_id, f"{title}: Wert", source,
            [Line("Wert", days, [r["value"] if r["status"] in shown else None for r in history], hover_decimals=2, shape="hv")],
            "Wert", observed=row["obs_date"], retrieved=retrieved, recessions=recessions), theme),
        ui.chart_card(f"{prefix}-{kennzahl_id}-percentile", Chart(
            f"{kennzahl_id}-percentile", f"{title}: Perzentil", source,
            [Line("Perzentil", days, [r["percentile"] if r["status"] == "ok" else None for r in history], hover_decimals=0, shape="hv")],
            "Perzentil (0–100)", observed=row["obs_date"], retrieved=retrieved, y_range=(0, 100),
            recessions=recessions), theme),
    ]


def _contribution_card(indicator_id: str, latest: dict | None = None, rows: dict | None = None) -> html.Section:
    """Generated section "So fließt der Wert in den Bereich ein": today's role, then the steps (E-57)."""
    if latest is None:
        latest = db.latest_composite()
        rows = db.indicator_scores_on(latest["score_date"]) if latest else {}
    return html.Section(className="card card-wide", children=[
        html.H2("So fließt der Wert in den Bereich ein"),
        html.P(_role_today(indicator_id, latest, rows), className="detail"),
        html.Ol([html.Li(line) for line in texts.contribution(indicator_id)], className="steps"),
    ])


def _role_today(indicator_id: str, latest: dict | None, rows: dict) -> str:
    """The indicator's part in today's area value, from the stored scores (nothing is computed here)."""
    if latest is None or indicator_id not in rows:
        return "Noch kein berechneter Wert."
    catalog = indicator_catalog()
    block = catalog[indicator_id].block
    row = rows[indicator_id]
    day = f"Stand {fmt.day(latest['score_date'])}"
    if row["status"] != "ok":
        reason = {"stale": "veraltet", "history": "unter der Mindesthistorie", "missing": "noch kein veröffentlichter Wert"}
        return f"{day}: {reason[row['status']]}; zählt heute nicht, der Bereich rechnet ohne ihn."
    peers = sum(1 for i, r in rows.items() if i in catalog and catalog[i].block == block and r["status"] == "ok")
    if block == VULNERABILITY:
        return (f"{day}: gültig mit Perzentil {fmt.number(row['percentile'], 0)}, eine von {peers} gültigen "
                f"Komponenten; Fallhöhe ungeglättet {fmt.number(latest['vulnerability_raw'])}.")
    return (f"{day}: gültig mit Perzentil {fmt.number(row['percentile'], 0)}, einer von {peers} gültigen Indikatoren "
            f"im Bereich; Bereichswert (Median) {fmt.number(latest[f'block_{block}'])}.")


# --- areas on the overview (E-57 to E-60) ---------------------------------------------------------

AREA_NOTE = ("Nicht als Bereich enthalten: Breite/Internals (keine Kursquelle, O-1) und Positionierung/Sentiment "
             "(erst Phase 2).")
AREA_LINES = {  # (column in composite_score, name) per area: lines of the chart and values in the head
    "volatility": (("block_volatility", "Median"), ("fast_block_smoothed", "geglättet")),
    "credit": (("block_credit", "Median"),),
    "macro": (("block_macro", "Median"),),
    VULNERABILITY: (("vulnerability_raw", "ungeglättet"), ("vulnerability", "geglättet")),
}


def is_open(clicks: int | None) -> bool:
    return (clicks or 0) % 2 == 1


def area_indicators(area: str) -> list[str]:
    """Indicators of an area in catalogue order; one without text is never shown (7.2)."""
    return [i for i, indicator in indicator_catalog().items() if indicator.block == area and texts.has_text(i)]


def areas() -> list:
    """Static frame of the areas below the overview: values and charts come from callbacks, charts only when open."""
    sections = []
    for area, head in texts.AREAS.items():
        if not texts.has_text(head):
            continue
        indicators = area_indicators(area)
        sections.append(html.Section(className="card card-wide area", children=[
            ui.kennzahl_head(head),
            html.Div(id={"type": "area-summary", "area": area}, className="area-summary"),
            ui.toggle({"type": "area-toggle", "area": area}, f"Verlauf und {len(indicators)} Einzelreihen"),
            html.Div(id={"type": "area-body", "area": area}, hidden=True, className="area-body", children=[
                html.Div(id={"type": "area-chart", "area": area}),
                html.Div([_indicator_row(i) for i in indicators], className="indicator-list"),
            ]),
        ]))
    return [
        html.H2("Bereiche und Einzelreihen", className="section-title"),
        ui.note("Jeder Bereich zeigt seinen Wert und die Indikatoren, aus denen er entsteht. Charts laden erst beim Aufklappen."),
        ui.note(HISTORY_NOTE),
        *sections,
        ui.note(AREA_NOTE),
    ]


def _indicator_row(indicator_id: str) -> html.Div:
    return html.Div(className="indicator-row", children=[
        html.Div(className="indicator-head", children=[
            ui.kennzahl_head(indicator_id, tag=html.H3),
            html.Div(id={"type": "indicator-summary", "id": indicator_id}, className="indicator-summary"),
            ui.toggle({"type": "indicator-toggle", "id": indicator_id}, "Charts und Berechnung"),
        ]),
        html.Div(id={"type": "indicator-body", "id": indicator_id}, hidden=True, className="indicator-body"),
    ])


def summaries(area_ids: list[str], indicator_ids: list[str], now: datetime) -> tuple[list, list]:
    """Current values of the areas and indicators, in the order Dash asks for them; one database read."""
    try:
        latest = db.latest_composite()
        rows = db.indicator_scores_on(latest["score_date"]) if latest else {}
        fresh = db.series_freshness()
    except (DataDirError, SQLAlchemyError) as exc:
        notice = ui.note(f"Datenbank nicht lesbar: {exc}")
        return [notice for _ in area_ids], [notice for _ in indicator_ids]
    if latest is None:
        empty = ui.note("Noch keine Scores berechnet.")
        return [empty for _ in area_ids], [empty for _ in indicator_ids]
    stamp = ui.freshness(latest["score_date"], latest["computed_at"], stale=_scores_stale(latest, now), now=now,
                         retrieved_label="berechnet")
    return ([_area_summary(a, latest, rows, stamp) for a in area_ids],
            [_indicator_summary(i, rows.get(i), fresh, now) for i in indicator_ids])


def _area_summary(area: str, latest: dict, rows: dict, stamp) -> list:
    indicators = [i for i, indicator in indicator_catalog().items() if indicator.block == area]
    valid = sum(1 for i in indicators if rows.get(i, {}).get("status") == "ok")
    values = [f"{name} {fmt.number(latest[column])}" for column, name in AREA_LINES[area]]
    if all(latest[column] is None for column, _ in AREA_LINES[area]):
        values = ["Bereichswert fehlt: kein gültiger Indikator" if area != VULNERABILITY else "Fallhöhe fehlt: zu wenige Komponenten"]
    return [html.Span(" · ".join(values), className="number"),
            html.Span(f"{valid} von {len(indicators)} gültig", className="detail"), stamp]


def _indicator_summary(indicator_id: str, row: dict | None, fresh: dict, now: datetime) -> list:
    if row is None:
        return [html.Span("noch kein Wert", className="detail")]
    config = scoring_config()
    return [
        html.Span(_value(row["value"]), className="number"),
        ui.percentile_chip(row["percentile"], config.yellow_diffusion_percentile),
        html.Span(STATUS_NAMES[row["status"]], className="detail"),
        ui.freshness(row["obs_date"], _retrieved(indicator_id, fresh), stale=row["status"] == "stale", now=now),
    ]


@guarded
def area_chart(area: str, theme: str, now: datetime) -> list:
    latest = db.latest_composite()
    if latest is None:
        return [ui.note("Noch keine Scores berechnet.")]
    columns = AREA_LINES[area]
    history = db.composite_history(*(column for column, _ in columns))
    days = [r["score_date"] for r in history]
    head = texts.text(texts.AREAS[area]).title
    chart = Chart(f"area-{area}", f"{head}: Verlauf", "eigene Berechnung (Scoring)",
                  [Line(name, days, [r[column] for r in history]) for column, name in columns],
                  "Wert (0–100)", observed=latest["score_date"], retrieved=latest["computed_at"], y_range=(0, 100),
                  recessions=db.recessions())
    return [ui.chart_card(f"area-{area}-history", chart, theme)]


@guarded
def indicator_detail(indicator_id: str, theme: str, now: datetime) -> list:
    latest = db.latest_composite()
    rows = db.indicator_scores_on(latest["score_date"]) if latest else {}
    row = rows.get(indicator_id)
    if row is None:
        return [ui.note("Noch kein berechneter Wert.")]
    retrieved = _retrieved(indicator_id, db.series_freshness())
    return [*_indicator_charts(indicator_id, theme, row, retrieved, "area"), _contribution_card(indicator_id, latest, rows)]


_SCORE_COLUMNS = {"stress": ("stress", "Stress (geglättet)"), "vulnerability": ("vulnerability", "Fallhöhe (geglättet)"),
                  "confidence": ("confidence", "Konfidenz in %"), "diffusion": ("diffusion", "Diffusionsindex in %"),
                  "traffic_light": ("level", "Ampelstufe")}


def _score_state(kennzahl_id, theme, now):
    latest = db.latest_composite()
    if latest is None:
        return [ui.note("Noch keine Scores berechnet.")]
    column, label = _SCORE_COLUMNS.get(kennzahl_id, (kennzahl_id, texts.text(kennzahl_id).title))
    value = latest[column]
    shown = ui.level_badge(value) if kennzahl_id == "traffic_light" else fmt.number(value)
    state = html.Div(className="card card-wide", children=[
        html.H2("Aktueller Stand"), html.Div(shown, className="big number"),
        ui.freshness(latest["score_date"], latest["computed_at"], stale=_scores_stale(latest, now), now=now, retrieved_label="berechnet"),
    ])
    history = db.composite_history(column)
    ticks = {i: name for i, name in enumerate(texts.LEVEL_NAMES)} if kennzahl_id == "traffic_light" else {}
    chart = Chart(kennzahl_id, label, "eigene Berechnung (Scoring)",
                  [Line(label, [r["score_date"] for r in history], [r[column] for r in history],
                        hover_decimals=0 if ticks else 1, shape="hv" if ticks else "linear")],
                  label, observed=latest["score_date"], retrieved=latest["computed_at"],
                  y_range=(-0.5, 3.5) if ticks else (0, 100), y_ticks=ticks, recessions=db.recessions())
    return [state, ui.chart_card(f"chart-{kennzahl_id}", chart, theme)]
