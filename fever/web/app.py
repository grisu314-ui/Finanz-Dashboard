"""Dash app (M6): page frame, freshness line, banners, health endpoint.

gunicorn serves `fever.web.app:server` (compose.dockge.yaml). Only local resources: Dash
serves plotly.js and its own scripts from the Python packages (serve_locally=True), the CSS and
JS of the project come from assets/. The web process only reads (PRAGMA query_only).
"""

from pathlib import Path

import dash
from dash import Input, Output, State, clientside_callback, dcc, html
from sqlalchemy.exc import SQLAlchemyError

from fever.store.db import DataDirError
from fever.web import db
from fever.web import format as fmt
from fever.worker import HEARTBEAT_MAX_AGE

ASSETS = Path(__file__).resolve().parents[2] / "assets"
REFRESH_MS = 5 * 60 * 1000  # E-7
WATCHDOG_MS = 30 * 1000
NAVIGATION = [("/", "Übersicht"), ("/datenstand", "Datenstand"), ("/erklaerungen", "Erklärungen")]
NOTICES = [
    "This product uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis.",
    "Source: ECB statistics.",
    "Quellen: Cboe Global Markets (nur private, nicht kommerzielle Nutzung), Board of Governors of the Federal Reserve "
    "System, Office of Financial Research, CFTC Commitments of Traders, Robert J. Shiller (Online Data); über FRED "
    "auch ICE Data Indices und S&P Dow Jones Indices (nur private Nutzung, keine Weitergabe).",
    "Regime- und Risikoanzeige, keine Prognose und keine Handelsempfehlung.",
]

app = dash.Dash(
    __name__,
    use_pages=True,
    pages_folder=str(Path(__file__).resolve().parent / "pages"),
    assets_folder=str(ASSETS),
    serve_locally=True,
    title="Fieberthermometer",
    update_title=None,
    suppress_callback_exceptions=True,
)
server = app.server

app.layout = html.Div(className="page", children=[
    dcc.Location(id="url"),
    dcc.Store(id="theme", data="light"),
    dcc.Store(id="last-ok"),
    dcc.Interval(id="refresh", interval=REFRESH_MS),
    dcc.Interval(id="watchdog", interval=WATCHDOG_MS),
    html.Header(className="top", children=[
        dcc.Link("Fieberthermometer", href="/", className="brand"),
        html.Nav(className="nav", children=[dcc.Link(label, href=path, className="nav-link") for path, label in NAVIGATION]),
        html.Div(id="status-line", className="status-line"),
    ]),
    html.Div(id="banner-worker"),
    html.Div(id="banner-connection", className="banner banner-connection is-hidden", role="alert"),
    html.Main(dash.page_container, className="main"),
    html.Footer(className="footer", children=[html.P(text) for text in NOTICES]),
])


@app.callback(
    Output("status-line", "children"),
    Output("banner-worker", "children"),
    Input("refresh", "n_intervals"),
    Input("url", "pathname"),
)
def status(_n, _path):
    """Header line and worker banner; runs on every page load and every refresh."""
    now = fmt.utcnow()
    try:
        beat = db.heartbeat()
        scoring = next((row for row in db.sources() if row["source"] == "scoring"), None)
    except (DataDirError, SQLAlchemyError) as exc:
        message = f"Datenbank nicht lesbar: {exc}"
        return [html.Span(f"Seite aktualisiert {fmt.berlin(now)}")], html.Div(message, className="banner banner-alert", role="alert")
    scored = scoring["last_success_at"] if scoring else None
    line = [
        html.Span(f"Worker zuletzt aktiv {fmt.age(beat, now)}"),
        html.Span(f"Scores berechnet {fmt.berlin(scored)}"),
        html.Span(f"Seite aktualisiert {fmt.berlin(now)}"),
    ]
    banner = None
    if beat is None or now - beat > HEARTBEAT_MAX_AGE:
        since = "nie" if beat is None else fmt.berlin(beat)
        banner = html.Div(f"Worker ohne Lebenszeichen seit {since}, Werte werden nicht aktualisiert.",
                          className="banner banner-alert", role="alert")
    return line, banner


@server.route("/health")
def health():
    """200 if the database can be read, 503 otherwise (container healthcheck)."""
    try:
        db.heartbeat()
    except (DataDirError, SQLAlchemyError) as exc:
        return {"status": "error", "message": str(exc)}, 503
    return {"status": "ok"}, 200


# Colour scheme follows the system (E-5); assets/theme.js reports later changes.
clientside_callback(
    "function(_path) { return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'; }",
    Output("theme", "data"),
    Input("url", "pathname"),
)

# Connection watchdog (7.3): remember the browser time of the last server answer ...
clientside_callback(
    "function(_children) { return Date.now(); }",
    Output("last-ok", "data"),
    Input("status-line", "children"),
)

# ... and show a banner after more than two refresh intervals without one (browser clock only).
clientside_callback(
    f"""function(_n, last) {{
        if (!last || Date.now() - last <= 2 * {REFRESH_MS}) {{
            return ['', 'banner banner-connection is-hidden'];
        }}
        const when = new Date(last).toLocaleString('de-DE', {{dateStyle: 'medium', timeStyle: 'short'}});
        return ['Keine Verbindung zum Server – angezeigte Werte vom ' + when + '.', 'banner banner-connection'];
    }}""",
    Output("banner-connection", "children"),
    Output("banner-connection", "className"),
    Input("watchdog", "n_intervals"),
    State("last-ok", "data"),
)
