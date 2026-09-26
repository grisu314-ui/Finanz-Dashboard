"""Page contents as plain functions (tested without a browser); the modules in pages/ call them.

Everything shown comes from the database (read-only) and the configuration; nothing is
computed here that the scoring computes. Database errors turn into a visible notice.
"""

from datetime import date, datetime

from dash import dcc, html
from sqlalchemy.exc import SQLAlchemyError

from fever.config import indicator_catalog, scoring_config, series_catalog
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
    )
    return [html.Div(cards, className="grid"), ui.chart_card("overview-history", chart, theme)]


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
        parts += [state, *charts]
    elif kennzahl_id in texts.SCORES:
        parts += _score_state(kennzahl_id, theme, now)
    for heading, body in text.sections:
        parts.append(html.Section(className="card card-wide text", children=[html.H2(heading), dcc.Markdown(body, link_target="_blank")]))
    facts = texts.steckbrief(kennzahl_id, history_from)
    if facts:
        parts.append(html.Section(className="card card-wide", children=[html.H2("Steckbrief"), ui.facts_table(facts)]))
    parts.append(html.Section(className="card card-wide", children=[
        html.H2("Schwellen und Farben"), html.Ul([html.Li(line) for line in texts.thresholds(kennzahl_id)])]))
    return parts


def _indicator_state(kennzahl_id, theme, now):
    indicator = indicator_catalog()[kennzahl_id]
    latest = db.latest_composite()
    row = db.indicator_scores_on(latest["score_date"]).get(kennzahl_id) if latest else None
    fresh = db.series_freshness()
    retrieved = max((fresh[s.id]["retrieved_at"] for s in indicator.series if s.id in fresh), default=None)
    config = scoring_config()
    if row is None:
        state = html.Div(className="card", children=[html.H2("Aktueller Stand"), ui.note("Noch kein Wert berechnet.")])
        return state, [], None
    stale = row["status"] == "stale"
    state = html.Div(className="card card-wide", children=[
        html.H2("Aktueller Stand"),
        html.Div(_value(row["value"]), className="big number"),
        ui.percentile_chip(row["percentile"], config.yellow_diffusion_percentile),
        *([html.P(f"Perzentil über {config.display_window_years} Jahre: {fmt.number(row['percentile_display'], 0)}")]
          if row["percentile_display"] is not None else []),
        html.P(f"Status: {STATUS_NAMES[row['status']]}", className="detail"),
        ui.freshness(row["obs_date"], retrieved, stale=stale, now=now),
    ])
    history = db.indicator_history(kennzahl_id)
    shown = {"ok", "history"}
    days = [r["score_date"] for r in history]
    source = ", ".join(sorted({SOURCE_NAMES.get(s.source, s.source) for s in indicator.series}))
    charts = [
        ui.chart_card(f"chart-{kennzahl_id}-value", Chart(
            kennzahl_id, f"{texts.text(kennzahl_id).title}: Wert", source,
            [Line("Wert", days, [r["value"] if r["status"] in shown else None for r in history], hover_decimals=2, shape="hv")],
            "Wert", observed=row["obs_date"], retrieved=retrieved), theme),
        ui.chart_card(f"chart-{kennzahl_id}-percentile", Chart(
            f"{kennzahl_id}-percentile", f"{texts.text(kennzahl_id).title}: Perzentil", source,
            [Line("Perzentil", days, [r["percentile"] if r["status"] == "ok" else None for r in history], hover_decimals=0, shape="hv")],
            "Perzentil (0–100)", observed=row["obs_date"], retrieved=retrieved, y_range=(0, 100)), theme),
    ]
    return state, charts, db.first_observation([s.id for s in indicator.series])


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
                  y_range=(-0.5, 3.5) if ticks else (0, 100), y_ticks=ticks)
    return [state, ui.chart_card(f"chart-{kennzahl_id}", chart, theme)]
