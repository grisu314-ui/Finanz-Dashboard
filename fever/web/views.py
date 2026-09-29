"""Page contents as plain functions (tested without a browser); the modules in pages/ call them.

Everything shown comes from the database (read-only) and the configuration; nothing is
computed here that the scoring computes. Database errors turn into a visible notice.
"""

import math
from datetime import date, datetime, timedelta

from dash import dcc, html
from sqlalchemy.exc import SQLAlchemyError

from fever.config import RULE_ONLY, VULNERABILITY, crisis_episodes, indicator_catalog, scoring_config, series_catalog
from fever.release import NEW_YORK, is_stale
from fever.scoring.composite import RULE_INDICATORS, SAHM_INDICATOR, SOS_INDICATOR
from fever.store.db import DataDirError
from fever.store.status import HEARTBEAT_MAX_AGE
from fever.web import components as ui
from fever.web import db, texts
from fever.web import format as fmt
from fever.web.figures import (
    Band, Chart, Curve, CurvePoint, Heatmap, Line, Matrix, Regime, Region, curve, heatmap, matrix, regime, sparkline,
)

SOURCE_NAMES = {
    "cboe": "Cboe (Indizes)", "cfe": "Cboe Futures Exchange (VX-Futures)", "fred": "FRED (St. Louis Fed)",
    "ecb": "EZB", "ofr": "Office of Financial Research", "fed": "Federal Reserve Board", "cftc": "CFTC",
    "shiller": "Robert J. Shiller", "sec": "SEC EDGAR (N-PORT)", "scoring": "Scoring (Berechnung im Worker)",
}
STATUS_NAMES = {
    "ok": "gültig", "stale": "veraltet", "history": "unter Mindesthistorie: angezeigt, nicht im Score",
    "missing": "noch kein veröffentlichter Wert",
}
# Phase-1 exception to the look-ahead rule; every history view says so (CLAUDE.md, fachliche Korrektheit).
HISTORY_NOTE = ("Verläufe: Je Beobachtung zählt der neueste veröffentlichte Stand. Revidierte Reihen sahen am "
                "jeweiligen Tag teils anders aus; die revisionsgenaue Rückrechnung folgt in Phase 2.")
PLACEHOLDERS = [
    "Nicht enthalten: Block Positionierung/Sentiment (erst Phase 2) und im Block Breite der Anteil der Aktien über "
    "ihrer 50- bzw. 200-Tage-Linie (keine freie Quelle, E-72).",
    "HY-OAS zählt im Bereich Kredit, gemessen vorerst nur an der kurzen Historie seit 2023 (FRED liefert drei Jahre); "
    "Anstieg, Rot-Regel und Fallhöhe nutzen den Kreditspread Baa von Moody's (E-75, E-85, E-90).",
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
    """Two decimals, at least two significant digits for small values (a 5-day change of 0.0042 is not 0,00)."""
    if value is None:
        return fmt.DASH
    if abs(value) >= 1000:
        return fmt.number(value, 0)
    if 0 < abs(value) < 0.1:
        return fmt.number(value, min(6, 1 - math.floor(math.log10(abs(value)))))
    return fmt.number(value, 2)


# --- overview --------------------------------------------------------------------------------------


def _score_stamp(latest: dict, now: datetime):
    return ui.freshness(latest["score_date"], latest["computed_at"], stale=_scores_stale(latest, now), now=now,
                        retrieved_label="berechnet")


def _traffic_card(latest: dict, stamp) -> html.Div:
    rules = [rule for rule in latest["active_rules"].split(",") if rule]
    return html.Div(className="card card-traffic", children=[
        ui.kennzahl_head("traffic_light"),
        html.Div(ui.level_badge(latest["level"]), className="big"),
        html.Ul([html.Li(texts.rule_text(rule)) for rule in rules] or [html.Li("Keine Regel trifft zu.")], className="rules"),
        *([ui.note("Der Stress-Composite fehlt (weniger Blöcke als nötig); die Ampel stützt sich auf die übrigen Regeln.")]
          if latest["stress"] is None else []),
        stamp,
    ])


# --- overview (report 6.3 view 1; start page since E-67) ------------------------------------------------------------

TRACE_DAYS = 60  # report 6.3: current point with a 60-day trace
MATRIX_NOTE = ("Nicht in den Flächen: Rot über VIX/VIX3M und<br>Kreditspread-Anstieg, Orange über die Sahm-Regel,<br>"
               "Gelb über SOS-Indikator und Diffusionsindex,<br>Hysterese; die Ampel kann höher stehen als die Fläche.")


def matrix_regions() -> tuple[Region, ...]:
    """Areas of the traffic light rules on stress and vulnerability from scoring.toml, low to high (4.3, step 5)."""
    c = scoring_config()
    return (
        Region(0, "Grün", 0, 100, 0, 100),
        Region(1, "Gelb", 0, 100, c.yellow_vulnerability, 100),
        Region(2, "Orange", c.orange_stress_with_vulnerability, 100, c.orange_vulnerability, 100),
        Region(2, "Orange", c.orange_stress, 100, 0, 100),
        Region(3, "Rot", c.red_stress, 100, 0, 100),
    )


@guarded
def overview(theme: str, now: datetime) -> list:
    """Start page (E-67): cards, traffic light matrix with trace, last update per source."""
    latest = db.latest_composite()
    if latest is None:
        return [ui.note("Noch keine Scores berechnet. Der Worker rechnet nach dem nächsten Abruf; "
                        "sofort mit python -m fever.score (docs/einrichtung.md).")]
    stamp = _score_stamp(latest, now)
    cards = [
        _traffic_card(latest, stamp),
        _number_card("stress", latest["stress"], f"ungeglättet {fmt.number(latest['stress_raw'])}", stamp, PLACEHOLDERS),
        _number_card("vulnerability", latest["vulnerability"], f"ungeglättet {fmt.number(latest['vulnerability_raw'])}", stamp),
        _number_card("confidence", latest["confidence"], "Anteil aktueller Daten, gewichtet nach Vorlauf", stamp, unit=" %"),
        _number_card("diffusion", latest["diffusion"], "Anteil der gültigen Stress-Indikatoren über „erhöht“", stamp, unit=" %"),
    ]
    history = db.composite_history("stress", "vulnerability")[-TRACE_DAYS:]
    chart = Matrix(
        "matrix", "Ampelmatrix", "eigene Berechnung (Scoring)",
        [r["score_date"] for r in history], [r["stress"] for r in history], [r["vulnerability"] for r in history],
        matrix_regions(), observed=latest["score_date"], retrieved=latest["computed_at"],
        note=f"Linie: Spur der letzten {len(history)} Handelstage<br>{MATRIX_NOTE}",
    )
    return [
        html.Div(cards, className="grid grid-3"),
        ui.figure_card("matrix", *matrix(chart, theme)),
        ui.note(HISTORY_NOTE),
        _sources_card(now),
    ]


def _sources_card(now: datetime) -> html.Div:
    rows = [
        html.Tr([
            html.Td(SOURCE_NAMES.get(row["source"], row["source"])),
            html.Td(f"{fmt.berlin(row['last_success_at'])} ({fmt.age(row['last_success_at'], now)})"),
            html.Td(fmt.berlin(row["last_error_at"]) if row["last_error_at"] else "–"),
        ])
        for row in db.sources()
    ]
    return html.Div(className="card card-wide", children=[
        html.H2("Letzte Aktualisierung je Quelle"),
        html.Div(className="table-scroll", children=html.Table(className="table", children=[
            html.Thead(html.Tr([html.Th("Quelle"), html.Th("Letzter Erfolg"), html.Th("Letzter Fehler")])),
            html.Tbody(rows),
        ])),
        dcc.Link("Einzelheiten je Reihe im Datenstand", href="/datenstand"),
    ])


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
    order = ["scores", "volatility", "credit", "macro", "breadth", "positioning", "vulnerability", RULE_ONLY, "display", "concepts"]
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
    if texts.roles(kennzahl_id):
        parts.insert(1, html.Div(ui.role_marks(kennzahl_id), className="roles"))
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
    if kennzahl_id in texts.DISPLAYS:
        history_from = db.first_observation(list(texts.DISPLAYS[kennzahl_id]))
        view_name = DISPLAY_VIEWS[kennzahl_id]
        parts.insert(3, html.P(["Verlauf: Ansicht ", dcc.Link(VIEW_TITLES[view_name], href=f"/ansicht/{view_name}")],
                               className="detail"))
        if kennzahl_id == "yield_curve":
            parts.insert(4, ui.note(resteepening(db.series_history("t10y3m"))))
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
    retrieved = db.newest_retrieval(series_ids)
    state = html.Div(className="card card-wide", children=[
        html.H2("Aktueller Stand"),
        html.Div(_value(row["value"]), className="big number"),
        ui.percentile_chip(row["percentile"], config.yellow_diffusion_percentile),
        *([html.P(f"Perzentil über {config.display_window_years} Jahre: {fmt.number(row['percentile_display'], 0)}")]
          if row["percentile_display"] is not None else []),
        html.P(f"Status: {STATUS_NAMES[row['status']]}", className="detail"),
        ui.freshness(row["obs_date"], retrieved, stale=row["status"] == "stale", now=now),
    ])
    return state, _indicator_charts(kennzahl_id, theme, row, retrieved), db.history_start(series_ids)


def _retrieved(indicator_id: str, fresh: dict) -> datetime | None:
    return max((fresh[s.id]["retrieved_at"] for s in indicator_catalog()[indicator_id].series if s.id in fresh), default=None)


def _indicator_charts(kennzahl_id, theme, row, retrieved) -> list:
    """Value and percentile over time on the Kennzahl page, both with the recession bars (E-56)."""
    indicator = indicator_catalog()[kennzahl_id]
    history = db.indicator_history(kennzahl_id, "status", "value", "percentile")
    shown = {"ok", "history"}
    days = [r["score_date"] for r in history]
    source = ", ".join(sorted({SOURCE_NAMES.get(s.source, s.source) for s in indicator.series}))
    title = texts.text(kennzahl_id).title
    recessions = db.recessions()
    shaded, shaded_label = rule_periods(kennzahl_id)
    return [
        ui.chart_card(f"chart-{kennzahl_id}-value", Chart(
            kennzahl_id, f"{title}: Wert", source,
            [Line("Wert", days, [r["value"] if r["status"] in shown else None for r in history], hover_decimals=2, shape="hv")],
            "Wert", observed=row["obs_date"], retrieved=retrieved, recessions=recessions, shaded=shaded,
            shaded_label=shaded_label), theme),
        ui.chart_card(f"chart-{kennzahl_id}-percentile", Chart(
            f"{kennzahl_id}-percentile", f"{title}: Perzentil", source,
            [Line("Perzentil", days, [r["percentile"] if r["status"] == "ok" else None for r in history], hover_decimals=0, shape="hv")],
            "Perzentil (0–100)", observed=row["obs_date"], retrieved=retrieved, y_range=(0, 100),
            recessions=recessions), theme),
    ]


def rule_periods(indicator_id: str) -> tuple[tuple[tuple[date, date], ...], str]:
    """Score days on which the Sahm or SOS rule was active (E-80), from the stored traffic light; violet in the charts."""
    if indicator_id not in (SAHM_INDICATOR, SOS_INDICATOR):
        return (), ""
    rules = set(RULE_INDICATORS[indicator_id])
    history = db.composite_history("active_rules")
    flags = [bool(rules & set((r["active_rules"] or "").split(","))) for r in history]
    label = "; ".join(texts.rule_text(rule) for rule in RULE_INDICATORS[indicator_id])
    return runs([r["score_date"] for r in history], flags), f"Violett: Ampelregel aktiv ({label})"


def resteepening(points: list[tuple[date, float]]) -> str:
    """Last end of an inversion of 10Y - 3M (E-84): display only, no score and no rule."""
    below = [day for day, value in points if value < 0]
    if not below:
        return "10J − 3M war in der gespeicherten Historie nie invertiert."
    after = next((day for day, _ in points if day > below[-1]), None)
    if after is None:
        start = below[-1]
        for day, value in reversed(points):
            if value >= 0:
                break
            start = day
        return f"10J − 3M ist invertiert seit {fmt.day(start)}; noch kein Re-Steepening."
    return (f"Letztes Re-Steepening: {fmt.day(after)} (erster Wert ab null nach dem letzten Tag der Inversion am "
            f"{fmt.day(below[-1])}). Keine Wirkung auf die Ampel (E-84).")


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
    rule = ""
    if indicator_id in RULE_INDICATORS:
        active = set((latest.get("active_rules") or "").split(",")) & set(RULE_INDICATORS[indicator_id])
        rule = " Die Ampelregel greift heute." if active else " Die Ampelregel greift heute nicht."
    if row["status"] != "ok":
        reason = {"stale": "veraltet", "history": "unter der Mindesthistorie", "missing": "noch kein veröffentlichter Wert"}
        return f"{day}: {reason[row['status']]}; zählt heute nicht, der Bereich rechnet ohne ihn." + rule
    if block == RULE_ONLY:
        return f"{day}: gültig mit Wert {_value(row['value'])}; zählt nur in seiner Ampelregel." + rule
    peers = sum(1 for i, r in rows.items() if i in catalog and catalog[i].block == block and r["status"] == "ok")
    if block == VULNERABILITY:
        return (f"{day}: gültig mit Perzentil {fmt.number(row['percentile'], 0)}, eine von {peers} gültigen "
                f"Komponenten; Fallhöhe ungeglättet {fmt.number(latest['vulnerability_raw'])}." + rule)
    return (f"{day}: gültig mit Perzentil {fmt.number(row['percentile'], 0)}, einer von {peers} gültigen Indikatoren "
            f"im Bereich; Bereichswert (Median) {fmt.number(latest[f'block_{block}'])}." + rule)


# --- indicator rows shared by the views -----------------------------------------------------------


def area_indicators(area: str) -> list[str]:
    """Indicators of an area in catalogue order; one without text is never shown (7.2)."""
    return [i for i, indicator in indicator_catalog().items() if indicator.block == area and texts.has_text(i)]


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


# --- views 2 to 6 of report 6.3 (M7, E-62) ---------------------------------------------------------

VIEW_TITLES = {
    "signale": "Schnelle Marktsignale", "breite": "Marktbreite", "positionierung": "Sentiment und Positionierung",
    "makro": "Makro und Liquidität", "fallhoehe": "Fallhöhe", "visualisierung": "Visualisierung",
}
DISPLAY_VIEWS = {"vix_term": "signale", "skew": "signale", "ccc_bb": "makro", "anfci": "makro",
                 "ofr_fsi": "makro", "yield_curve": "makro", "cape": "fallhoehe", "money_market": "fallhoehe"}
INDEX_HORIZONS = {"vix9d": ("VIX9D", 9), "vix": ("VIX", 30), "vix3m": ("VIX3M", 91), "vix6m": ("VIX6M", 182)}  # nominal
OFR_CATEGORIES = {"ofr_fsi_credit": "Kredit", "ofr_fsi_equity_valuation": "Aktienbewertung", "ofr_fsi_funding": "Refinanzierung",
                  "ofr_fsi_safe_assets": "Sichere Anlagen", "ofr_fsi_volatility": "Volatilität"}
OFR_REGIONS = {"ofr_fsi_united_states": "USA", "ofr_fsi_other_advanced": "Andere Industrieländer",
               "ofr_fsi_emerging_markets": "Schwellenländer"}


def runs(days: list[date], flags: list[bool]) -> tuple[tuple[date, date], ...]:
    """Consecutive days with a true flag as (first day, day after the last), so single days stay visible."""
    periods, start, previous = [], None, None
    for day, flag in zip(days, flags):
        if flag and start is None:
            start = day
        elif not flag and start is not None:
            periods.append((start, previous + timedelta(days=1)))
            start = None
        previous = day
    if start is not None:
        periods.append((start, previous + timedelta(days=1)))
    return tuple(periods)


@guarded
def view(name: str | None, theme: str, now: datetime) -> list:
    builders = {"signale": _view_signals, "breite": _view_breadth, "positionierung": _view_positioning,
                "makro": _view_macro, "fallhoehe": _view_vulnerability}
    if name not in VIEW_TITLES:
        return [html.H1("Ansicht nicht gefunden"), dcc.Link("Zur Übersicht", href="/")]
    if name == "visualisierung":
        return visualisation_frame()
    context = _Context(theme, now)
    return [html.H1(VIEW_TITLES[name]), *builders[name](context), ui.note(HISTORY_NOTE)]


class _Context:
    """What every item of a view needs, read once per page."""

    def __init__(self, theme: str, now: datetime):
        self.theme, self.now = theme, now
        self.latest = db.latest_composite()
        self.rows = db.indicator_scores_on(self.latest["score_date"]) if self.latest else {}
        self.fresh = db.series_freshness()
        self.recessions = db.recessions()
        self.config = scoring_config()


def _item(kennzahl_id: str, summary: list, charts: list, notes=()) -> html.Section:
    return html.Section(className="card card-wide view-item", children=[
        ui.kennzahl_head(kennzahl_id), html.Div(summary, className="indicator-summary"), *[ui.note(n) for n in notes], *charts,
    ])


ITEM_COLUMNS = ("status", "value", "percentile", "percentile_display")  # what an indicator item draws


def _indicator_item(ctx: _Context, indicator_id: str, *, shaded=(), shaded_label="", percentile=False,
                    history: list[dict] | None = None, notes=()) -> html.Section:
    row = ctx.rows.get(indicator_id)
    summary = _indicator_summary(indicator_id, row, ctx.fresh, ctx.now)
    if row is None:
        return _item(indicator_id, summary, [], notes)
    indicator = indicator_catalog()[indicator_id]
    history = db.indicator_history(indicator_id, *ITEM_COLUMNS) if history is None else history
    days = [r["score_date"] for r in history]
    source = ", ".join(sorted({SOURCE_NAMES.get(s.source, s.source) for s in indicator.series}))
    title = texts.text(indicator_id).title
    retrieved = _retrieved(indicator_id, ctx.fresh)
    value = [r["value"] if r["status"] in ("ok", "history") else None for r in history]
    charts = [ui.chart_card(f"view-{indicator_id}-value", Chart(
        indicator_id, f"{title}: Wert", source, [Line("Wert", days, value, hover_decimals=None, shape="hv")], "Wert",
        observed=row["obs_date"], retrieved=retrieved, recessions=ctx.recessions, shaded=shaded,
        shaded_label=shaded_label, full_history=True), ctx.theme)]
    if percentile:
        lines = [Line(f"{ctx.config.window_years} Jahre (Score)", days,
                      [r["percentile"] if r["status"] == "ok" else None for r in history], hover_decimals=0, shape="hv")]
        if indicator.display_window:
            lines.append(Line(f"{ctx.config.display_window_years} Jahre (Anzeige)", days,
                              [r["percentile_display"] for r in history], hover_decimals=0, shape="hv"))
        charts.append(ui.chart_card(f"view-{indicator_id}-percentile", Chart(
            f"{indicator_id}-percentile", f"{title}: Perzentil", source, lines, "Perzentil (0–100)",
            observed=row["obs_date"], retrieved=retrieved, y_range=(0, 100), recessions=ctx.recessions,
            full_history=True), ctx.theme))
    return _item(indicator_id, summary, charts, notes)


def _series_line(series_id: str, name: str) -> Line:
    history = db.series_history(series_id)
    return Line(name, [d for d, _ in history], [v for _, v in history], hover_decimals=None)


def _display_summary(ctx: _Context, series_ids) -> list:
    """Stand, retrieval and stale mark of display-only series (E-10 per series)."""
    catalog = series_catalog()
    today = _today_new_york(ctx.now)
    infos = [(catalog[s], ctx.fresh.get(s)) for s in series_ids]
    observed = min((i["obs_date"] for _, i in infos if i), default=None)
    retrieved = max((i["retrieved_at"] for _, i in infos if i), default=None)
    stale = any(i is None or is_stale(i["obs_date"], s.lag_days, s.frequency, s.tolerance_days, today) for s, i in infos)
    return [ui.freshness(observed, retrieved, stale=stale, now=ctx.now)]  # "nur Anzeige" stands as a role mark (E-81)


def _display_item(ctx: _Context, display_id: str, lines: list[Line], y_title: str, *, source: str, notes=(),
                  shaded=(), shaded_label="", zero_line=False, extra_charts=()) -> html.Section:
    series_ids = texts.DISPLAYS[display_id]
    summary = _display_summary(ctx, series_ids)
    observed = max((max(line.x) for line in lines if line.x), default=None)
    retrieved = max((ctx.fresh[s]["retrieved_at"] for s in series_ids if s in ctx.fresh), default=None)
    chart = Chart(display_id, texts.text(display_id).title, source, lines, y_title, observed=observed, retrieved=retrieved,
                  recessions=ctx.recessions, shaded=shaded, shaded_label=shaded_label, zero_line=zero_line,
                  end_labels=len(lines) > 2, full_history=True)
    return _item(display_id, summary, [ui.chart_card(f"view-{display_id}", chart, ctx.theme), *extra_charts], notes)


def _view_signals(ctx: _Context) -> list:
    ratio = db.indicator_history("vix_vix3m", *ITEM_COLUMNS)
    backwardation = runs([r["score_date"] for r in ratio], [r["value"] is not None and r["value"] > 1 for r in ratio])
    return [
        _term_structure_item(ctx),
        _indicator_item(ctx, "vix_vix3m", shaded=backwardation, shaded_label="Violett: Backwardation (VIX über VIX3M)",
                        history=ratio),
        _indicator_item(ctx, "vix"),
        _indicator_item(ctx, "vrp"),
        _indicator_item(ctx, "vvix"),
        _display_item(ctx, "skew", [_series_line("skew", "SKEW")], "Punkte", source="Cboe (Indizes)"),
        _indicator_item(ctx, "usdjpy_change"),
        _indicator_item(ctx, "usdjpy_vol"),
        ui.note("MOVE (Volatilität am Anleihemarkt) fehlt in Phase 1: Lizenz von ICE (W-6)."),
    ]


def _term_structure_item(ctx: _Context) -> html.Section:
    """Today's curve: the VIX indices at their nominal horizon, VX futures at their days to expiry."""
    points, observed = [], []
    for series_id, (label, horizon) in INDEX_HORIZONS.items():
        newest = db.newest_observation(series_id)
        if newest:
            points.append(CurvePoint(label, horizon, newest[1], "VIX-Indizes"))
            observed.append(newest[0])
    futures_day = None
    for rank in range(1, 9):
        price = db.newest_observation(f"cfe_vx{rank}")
        days = db.value_on(f"cfe_vx{rank}_days", price[0]) if price else None
        if days is not None:
            futures_day = futures_day or price[0]
            if price[0] == futures_day:
                points.append(CurvePoint(f"VX{rank}", days, price[1], "VX-Futures (Settlement)"))
    retrieved = max((ctx.fresh[s]["retrieved_at"] for s in texts.DISPLAYS["vix_term"] if s in ctx.fresh), default=None)
    note = (f"Indizes Stand {fmt.day(max(observed)) if observed else '–'}, Futures Stand {fmt.day(futures_day)};"
            "<br>Indizes auf ihrer nominalen Frist")
    chart = Curve("vix_term", "VIX-Termstruktur", "Cboe (Indizes), Cboe Futures Exchange", points,
                  "Tage (Frist bzw. Restlaufzeit)", "Punkte", observed=max(observed) if observed else None,
                  retrieved=retrieved, note=note)
    return _item("vix_term", _display_summary(ctx, texts.DISPLAYS["vix_term"][:4]), [ui.figure_card("view-vix_term", *curve(chart, ctx.theme))])


def _view_breadth(ctx: _Context) -> list:
    nasdaq = "Lizenz Nasdaq, Inc.: nur für dich selbst, nicht veröffentlichen oder weitergeben."
    return [
        ui.note("Statt der ETFs des Berichts (RSP/SPY, IWM, SMH, KRE, XLY/XLP) stehen hier Nasdaq-Indizes über FRED "
                "(Entscheidungen E-68 und E-73). " + nasdaq),
        *[_indicator_item(ctx, i, percentile=True) for i in area_indicators("breadth")],
        ui.note("Nicht enthalten: der Anteil der Aktien über ihrer 50- bzw. 200-Tage-Linie. Dafür bräuchte es die Kurse "
                "aller Indexmitglieder mit historischen Mitgliederlisten; eine freie Quelle, die gespeichert werden darf, "
                "gibt es nicht (E-72)."),
    ]


def _view_positioning(ctx: _Context) -> list:
    return [
        _indicator_item(ctx, "vx_cot_short", percentile=True),
        _indicator_item(ctx, "margin_yoy"),
        ui.note("Die AAII-Umfrage (Bull-Bear-Spread) folgt in Phase 2; der Block Positionierung/Sentiment hat bis dahin "
                "keinen Indikator im Stress."),
    ]


def _view_macro(ctx: _Context) -> list:
    t10y3m = db.series_history("t10y3m")
    inversion = runs([d for d, _ in t10y3m], [v < 0 for _, v in t10y3m])
    hy = dict(db.series_history("bamlh0a3hyc"))
    bb = db.series_history("bamlh0a1hybb")
    ccc_bb = [(d, hy[d] - v) for d, v in bb if d in hy]
    ofr_source = "Office of Financial Research"
    ofr_charts = [
        ui.chart_card("view-ofr_fsi-categories", Chart(
            "ofr_fsi-categories", "OFR FSI: Beiträge der Kategorien", ofr_source,
            [_series_line(s, n) for s, n in OFR_CATEGORIES.items()], "Beitrag", recessions=ctx.recessions, zero_line=True,
            full_history=True,
            end_labels=True, observed=_newest(ctx, OFR_CATEGORIES), retrieved=_retrieved_of(ctx, OFR_CATEGORIES)), ctx.theme),
        ui.chart_card("view-ofr_fsi-regions", Chart(
            "ofr_fsi-regions", "OFR FSI: Beiträge der Regionen", ofr_source,
            [_series_line(s, n) for s, n in OFR_REGIONS.items()], "Beitrag", recessions=ctx.recessions, zero_line=True,
            full_history=True,
            end_labels=True, observed=_newest(ctx, OFR_REGIONS), retrieved=_retrieved_of(ctx, OFR_REGIONS)), ctx.theme),
    ]
    ice = "Lizenz ICE Data Indices: nur für dich selbst, nicht veröffentlichen oder weitergeben."
    return [
        _indicator_item(ctx, "nfci"),
        _display_item(ctx, "anfci", [_series_line("anfci", "ANFCI"), _series_line("nfci", "NFCI")], "Index",
                      source="Chicago Fed (über FRED)", zero_line=True),
        _indicator_item(ctx, "stlfsi4"),
        _display_item(ctx, "ofr_fsi", [_series_line("ofr_fsi", "OFR FSI")], "Index", source=ofr_source, zero_line=True,
                      extra_charts=ofr_charts),
        _indicator_item(ctx, "ciss"),
        _indicator_item(ctx, "credit_spread_level"),
        _indicator_item(ctx, "credit_spread_change", percentile=True),
        _indicator_item(ctx, "hy_oas", percentile=True, notes=[ice]),
        _display_item(ctx, "ccc_bb", [Line("CCC − BB", [d for d, _ in ccc_bb], [v for _, v in ccc_bb], hover_decimals=None)],
                      "Prozentpunkte", source="ICE Data Indices (über FRED)", notes=[ice]),
        _indicator_item(ctx, "ebp"),
        _indicator_item(ctx, "sofr_iorb"),
        _display_item(ctx, "yield_curve", [Line("10J − 3M", [d for d, _ in t10y3m], [v for _, v in t10y3m], hover_decimals=None),
                                           _series_line("t10y2y", "10J − 2J")], "Prozentpunkte",
                      source="FRED (US-Finanzministerium)", shaded=inversion,
                      shaded_label="Violett: Inversion (10J − 3M unter null)", zero_line=True, notes=[resteepening(t10y3m)]),
        _rule_item(ctx, SAHM_INDICATOR),
        _rule_item(ctx, SOS_INDICATOR),
        _indicator_item(ctx, "claims"),
    ]


def _rule_item(ctx: _Context, indicator_id: str) -> html.Section:
    """Sahm rule and SOS indicator with the days their traffic light rule was active (E-80)."""
    shaded, label = rule_periods(indicator_id)
    return _indicator_item(ctx, indicator_id, shaded=shaded, shaded_label=label)


def _newest(ctx: _Context, series) -> date | None:
    return max((ctx.fresh[s]["obs_date"] for s in series if s in ctx.fresh), default=None)


def _retrieved_of(ctx: _Context, series) -> datetime | None:
    return max((ctx.fresh[s]["retrieved_at"] for s in series if s in ctx.fresh), default=None)


def money_market_share(funds, nonfinancial, financial) -> list[tuple[date, float]]:
    """Money market fund assets in percent of the market value of all corporate equities (E-86), on common quarters."""
    equities = {day: value for day, value in nonfinancial}
    for day, value in financial:
        equities[day] = equities[day] + value if day in equities else None
    return [(day, 100 * value / equities[day]) for day, value in funds if equities.get(day)]


def _view_vulnerability(ctx: _Context) -> list:
    share = money_market_share(*(db.series_history(s) for s in texts.DISPLAYS["money_market"]))
    return [
        _display_item(ctx, "cape", [_series_line("shiller_cape", "CAPE")], "Verhältnis", source="Robert J. Shiller (Online Data)"),
        _indicator_item(ctx, "ecy"),
        _indicator_item(ctx, "equity_allocation"),
        _display_item(ctx, "money_market", [Line("Geldmarktfonds in % der Aktien", [d for d, _ in share], [v for _, v in share],
                                                 hover_decimals=None, shape="hv")],
                      "Prozent", source="Federal Reserve Board, Z.1 (über FRED)"),
        _indicator_item(ctx, "credit_spread_tight"),
        _indicator_item(ctx, "margin_yoy"),
        _indicator_item(ctx, "top10_concentration", percentile=True),
        ui.note("Nicht enthalten: Margin Debt relativ zur Marktkapitalisierung (die Fallhöhe nutzt die Veränderung "
                "ggü. Vorjahr, Entscheidung E-49)."),
    ]


# --- view 7: visualisation (M7, E-63, E-64, E-66) -------------------------------------------------

HEATMAP_GRAINS = {"weekly": "Wöchentlich, ganze Historie", "daily": "Täglich, letzte 2 Jahre"}
SPARK_DAYS = 365


def _ordered_indicators() -> list[str]:
    return [i for area in texts.AREAS for i in area_indicators(area)]


def visualisation_frame() -> list:
    """Static frame of view 7; callbacks fill each part, so switch and selection survive the refresh."""
    episodes = crisis_episodes()
    table = html.Div(className="table-scroll", children=html.Table(className="table", children=[
        html.Thead(html.Tr([html.Th("Krise"), html.Th("Hoch"), html.Th("Tief"), html.Th("Quelle")])),
        html.Tbody([html.Tr([html.Td(e.label), html.Td(fmt.day(e.start)), html.Td(fmt.day(e.end)), html.Td(e.source)])
                    for e in episodes]),
    ]))
    options = [{"label": texts.text(i).title, "value": i} for i in _ordered_indicators()]
    return [
        html.H1("Visualisierung"),
        html.Section(className="card card-wide", children=[
            html.H2("Stress-Historie mit Krisen"), html.Div(id="vis-stress"),
            html.Details([html.Summary("Krisen: Daten und Quellen"), table]),
        ]),
        html.Section(className="card card-wide", children=[html.H2("Regime-Zeitleiste"), html.Div(id="vis-regime")]),
        html.Section(className="card card-wide", children=[
            html.H2("Heatmap der Perzentile"),
            dcc.RadioItems(id="heatmap-grain", options=[{"label": v, "value": k} for k, v in HEATMAP_GRAINS.items()],
                           value="weekly", inline=True, persistence=True, persistence_type="session", className="switch"),
            html.Div(id="vis-heatmap"),
        ]),
        html.Section(className="card card-wide", children=[
            html.H2("Perzentilbänder"),
            ui.note("Wert des Indikators mit dem Bereich zwischen dem 10. und 90. Perzentil seines Fensters und dem Median."),
            dcc.Dropdown(id="bands-indicator", options=options, value=options[0]["value"] if options else None,
                         clearable=False, persistence=True, persistence_type="session", className="select"),
            html.Div(id="vis-bands"),
        ]),
        html.Section(className="card card-wide", children=[
            html.H2("Sparklines"), ui.note("Letzte 12 Monate je Indikator; Stand und Abruf stehen darunter."),
            html.Div(id="vis-sparklines", className="spark-grid"),
        ]),
        ui.note(HISTORY_NOTE),
    ]


@guarded
def vis_stress(theme: str, now: datetime) -> list:
    latest = db.latest_composite()
    if latest is None:
        return [ui.note("Noch keine Scores berechnet.")]
    history = db.composite_history("stress")
    chart = Chart("stress-crises", "Stress (geglättet) mit Krisen", "eigene Berechnung (Scoring)",
                  [Line("Stress", [r["score_date"] for r in history], [r["stress"] for r in history])], "Wert (0–100)",
                  observed=latest["score_date"], retrieved=latest["computed_at"], y_range=(0, 100),
                  recessions=db.recessions(), episodes=tuple((e.start, e.end, e.label) for e in crisis_episodes()),
                  full_history=True)
    return [ui.chart_card("vis-stress-chart", chart, theme)]


@guarded
def vis_regime(theme: str, now: datetime) -> list:
    latest = db.latest_composite()
    if latest is None:
        return [ui.note("Noch keine Scores berechnet.")]
    history = db.composite_history("level")
    chart = Regime("regime", "Ampelstufe je Handelstag", "eigene Berechnung (Scoring)", [r["score_date"] for r in history],
                   [r["level"] for r in history], texts.LEVEL_NAMES, observed=latest["score_date"],
                   retrieved=latest["computed_at"])
    return [ui.figure_card("vis-regime-chart", *regime(chart, theme), box="chart-box chart-box-short")]


@guarded
def vis_heatmap(grain: str, theme: str, now: datetime) -> list:
    latest = db.latest_composite()
    if latest is None:
        return [ui.note("Noch keine Scores berechnet.")]
    days = db.score_days()
    if grain == "daily":
        start = days[-1] - timedelta(days=730)
        columns = [d for d in days if d > start]
    else:  # last score day of every ISO week: shows the stored daily percentile, nothing is averaged
        last_of_week = {}
        for d in days:
            last_of_week[d.isocalendar()[:2]] = d
        columns = sorted(last_of_week.values())
    values = db.valid_percentiles(tuple(columns))
    indicators = _ordered_indicators()
    chart = Heatmap("heatmap", "Perzentile der Indikatoren", "eigene Berechnung (Scoring)",
                    [texts.text(i).title for i in indicators], columns,
                    [[values.get((i, d)) for d in columns] for i in indicators],
                    observed=latest["score_date"], retrieved=latest["computed_at"],
                    note=f"{HEATMAP_GRAINS.get(grain, HEATMAP_GRAINS['weekly'])}; leer = nicht gültig (veraltet, zu kurze Historie)",
                    roles=[tuple(texts.roles(i)) for i in indicators])
    return [ui.figure_card("vis-heatmap-chart", *heatmap(chart, theme), box="chart-box chart-box-tall")]


@guarded
def vis_bands(indicator_id: str | None, theme: str, now: datetime) -> list:
    if indicator_id not in indicator_catalog():
        return [ui.note("Bitte einen Indikator wählen.")]
    latest = db.latest_composite()
    row = db.indicator_scores_on(latest["score_date"]).get(indicator_id) if latest else None
    if row is None:
        return [ui.note("Noch kein berechneter Wert.")]
    history = db.indicator_history(indicator_id, "status", "value", "band_p10", "band_p50", "band_p90")
    days = [r["score_date"] for r in history]
    indicator = indicator_catalog()[indicator_id]
    source = ", ".join(sorted({SOURCE_NAMES.get(s.source, s.source) for s in indicator.series}))
    band = Band(days, [r["band_p10"] for r in history], [r["band_p50"] for r in history], [r["band_p90"] for r in history])
    chart = Chart(f"bands-{indicator_id}", f"{texts.text(indicator_id).title}: Wert und Perzentilband", source,
                  [Line("Wert", days, [r["value"] if r["status"] in ("ok", "history") else None for r in history],
                        hover_decimals=None, shape="hv")],
                  "Wert", observed=row["obs_date"], retrieved=db.newest_retrieval([s.id for s in indicator.series]),
                  recessions=db.recessions(), band=band, full_history=True)
    return [ui.chart_card("vis-bands-chart", chart, theme)]


@guarded
def vis_sparklines(theme: str, now: datetime) -> list:
    latest = db.latest_composite()
    if latest is None:
        return [ui.note("Noch keine Scores berechnet.")]
    rows = db.indicator_scores_on(latest["score_date"])
    fresh = db.series_freshness()
    config = scoring_config()
    histories = db.indicator_values_since(latest["score_date"] - timedelta(days=SPARK_DAYS))
    cards = []
    for indicator_id in _ordered_indicators():
        history = histories.get(indicator_id, [])
        row = rows.get(indicator_id)
        figure, graph = sparkline([r["score_date"] for r in history],
                                  [r["value"] if r["status"] in ("ok", "history") else None for r in history], theme)
        cards.append(html.Div(className="spark", children=[
            ui.kennzahl_head(indicator_id, tag=html.H3),
            html.Div([html.Span(_value(row["value"] if row else None), className="number"),
                      ui.percentile_chip(row["percentile"] if row else None, config.yellow_diffusion_percentile)],
                     className="indicator-summary"),
            html.Div(className="spark-box", children=dcc.Graph(figure=figure, config=graph, className="chart",
                                                               style={"height": "100%"})),
            ui.freshness(row["obs_date"] if row else None, _retrieved(indicator_id, fresh),
                         stale=bool(row and row["status"] == "stale"), now=now),
        ]))
    return cards
