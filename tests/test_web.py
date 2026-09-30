"""Web interface (M6): smoke test, local resources only, chart standard, texts, formats."""

import json
from dataclasses import replace
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import plotly.graph_objects as go
import pytest
from plotly.utils import PlotlyJSONEncoder

from fever.store.db import make_engine
from fever.store.observations import NewObservation, append_observations
from fever.store.status import record_heartbeat, record_success
from fever.web import db as web_db
from fever.web import format as fmt
from fever.web import texts, views
from fever.web.figures import Chart, Line, time_series

REPO = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 9, 26, 12, 0, tzinfo=timezone.utc)


def rendered(components) -> str:
    """Components as the JSON Dash sends to the browser."""
    return json.dumps(components, cls=PlotlyJSONEncoder, ensure_ascii=False)


def validated(figure: dict) -> go.Figure:
    """The chart factory builds plain dicts; plotly.graph_objects checks every property (a typo fails here)."""
    return go.Figure(figure)


@pytest.fixture
def data(migrated_dir, monkeypatch):
    """Database with a few VIX closes, scores and status rows; the web engine points at it."""
    engine = make_engine(migrated_dir)
    days = [date(2014, 1, 1 + i) for i in range(20)] + [date(2026, 9, 21 + i) for i in range(5)]
    with engine.begin() as conn:
        append_observations(conn, "vix", [NewObservation(d, 15.0 + i % 7, NOW, True) for i, d in enumerate(days)], retrieved_at=NOW)
        record_heartbeat(conn, "worker", NOW)
        record_success(conn, "cboe", NOW)
    from fever import score
    score.run(engine, clock=lambda: NOW)
    monkeypatch.setenv("FEVER_DATA", str(migrated_dir))
    web_db.engine.cache_clear()
    yield migrated_dir
    web_db.engine.cache_clear()


@pytest.fixture
def client(data):
    from fever.web.app import server
    return server.test_client()


def test_smoke_pages_layout_and_health(client):
    for path in ("/", "/datenstand", "/erklaerungen", "/kennzahl/stress", "/_dash-layout", "/_dash-dependencies", "/health"):
        assert client.get(path).status_code == 200, path


def test_json_answers_are_gzipped_when_the_browser_accepts_it(client):
    import gzip
    plain = client.get("/_dash-layout")
    assert "Content-Encoding" not in plain.headers and len(plain.data) > 2048
    packed = client.get("/_dash-layout", headers={"Accept-Encoding": "gzip, deflate, br"})
    assert packed.headers["Content-Encoding"] == "gzip" and "Accept-Encoding" in packed.headers["Vary"]
    assert gzip.decompress(packed.data) == plain.data and len(packed.data) < len(plain.data) / 2
    refused = client.get("/_dash-layout", headers={"Accept-Encoding": "gzip;q=0, br"})
    assert "Content-Encoding" not in refused.headers
    assert "Content-Encoding" not in client.get("/health", headers={"Accept-Encoding": "gzip"}).headers  # small


def test_health_fails_without_database(tmp_path, monkeypatch):
    monkeypatch.setenv("FEVER_DATA", str(tmp_path))
    web_db.engine.cache_clear()
    from fever.web.app import server
    response = server.test_client().get("/health")
    assert response.status_code == 503 and response.get_json()["status"] == "error"
    web_db.engine.cache_clear()


def test_served_html_and_scripts_use_no_external_url(client):
    html = client.get("/").get_data(as_text=True)
    urls = re.findall(r'(?:src|href)="([^"]+)"', html)
    assert urls and all(not re.match(r"(?i)(https?:)?//", url) for url in urls), urls
    assert "cdn" not in html.lower()


def test_web_connections_are_read_only(data):
    with web_db.engine().connect() as conn:
        assert conn.exec_driver_sql("PRAGMA query_only").scalar() == 1


def test_no_dangerously_allow_html_anywhere():
    for path in list((REPO / "fever").rglob("*.py")) + list((REPO / "assets").rglob("*.js")):
        assert "dangerously_allow_html" not in path.read_text(encoding="utf-8"), path


# --- chart standard (7.1) ----------------------------------------------------------------------------


def test_chart_factory_sets_the_standard():
    chart = Chart("vix", "VIX", "Cboe", [Line("VIX", [date(2020, 1, 1), date(2026, 9, 25)], [15.0, None])], "Punkte",
                  observed=date(2026, 9, 25), retrieved=datetime(2026, 9, 26, 12, 47, tzinfo=timezone.utc))
    figure, config = time_series(chart, "dark", today=date(2026, 9, 26))
    figure = validated(figure)
    layout = figure.layout
    assert config["displaylogo"] is False and config["scrollZoom"] is False
    assert config["showSendToCloud"] is False  # no upload of chart data to Plotly Cloud
    assert config["toImageButtonOptions"] == {"format": "png", "scale": 2, "filename": "vix_26-09-2026"}
    assert [b.label for b in layout.xaxis.rangeselector.buttons] == ["1 M", "6 M", "1 J", "5 J", "Max"]
    assert layout.xaxis.rangeslider.visible is False
    assert layout.uirevision == "vix" and layout.separators == ",." and layout.template.layout.paper_bgcolor == "#1a1a19"
    assert figure.data[0].connectgaps is False
    assert layout.annotations[0].text == "Quelle: Cboe<br>Stand: 25.09.2026<br>Abruf: 26.09.2026, 14:47 MESZ"
    # pixel offset, not a paper fraction: stays inside the margin at any chart height (full screen)
    assert layout.annotations[0].y == 0 and layout.annotations[0].yshift == -28
    assert layout.xaxis.hoverformat == "%d.%m.%Y"
    assert figure.data[0].x == ("2020-01-01", "2026-09-25") and layout.xaxis.range == ("2021-09-25", "2026-09-25")


# --- texts (docs/leitfaden-erklaertexte.md) ---------------------------------------------------------


def test_every_text_file_follows_the_guideline():
    files = sorted(texts.TEXT_DIR.glob("*.md"))
    assert files
    for path in files:
        assert path.stem in texts.all_ids(), f"{path.name}: keine bekannte Kennzahl"
        text = texts.text(path.stem)  # raises TextError on any rule violation
        assert len(text.short) <= texts.MAX_SHORT


@pytest.mark.parametrize(
    "change, message",
    [
        (lambda s: s.replace("## Quellen", "## Literatur"), "Überschriften"),
        (lambda s: s.replace("## Kurzinfo\n", "## Kurzinfo\n" + "x" * 201 + " "), "Kurzinfo"),
        (lambda s: s.replace("## So liest du sie\n", "## So liest du sie\nAb dem 90. Perzentil rot.\n"), "Schwellenzahl"),
        (lambda s: s.replace("## So liest du sie\n", "## So liest du sie\n<b>fett</b>\n"), "HTML"),
    ],
)
def test_text_rules_are_enforced(change, message):
    content = (texts.TEXT_DIR / "stress.md").read_text(encoding="utf-8")
    with pytest.raises(texts.TextError, match=message):
        texts.parse("stress", change(content))


def test_every_displayed_kennzahl_has_a_text(data):
    """Render every page; a Kennzahl without text raises in kennzahl_head (rule of 7.2)."""
    pages = [views.overview("light", NOW), views.data_status(NOW), views.explanations()]
    pages += [views.kennzahl(k, "light", NOW) for k in texts.all_ids() if texts.has_text(k)]
    shown = set(re.findall(r"/kennzahl/([a-z0-9_]+)", rendered(pages)))
    assert shown and all(texts.has_text(k) for k in shown)


def test_generated_sections_come_from_the_configuration():
    lines = texts.thresholds("traffic_light")
    assert any(line.startswith("Rot: Stress mindestens 90") for line in lines)
    assert any("Kreditspreads Baa" in line and "mindestens 95" in line for line in lines)  # E-75: the credit rule is active
    facts = dict(texts.steckbrief("vix_vix3m"))
    assert facts["Orientierung"] == "hoch = mehr Stress" and facts["Frequenz"] == "täglich"


def test_unknown_kennzahl_page(data):
    assert "nicht gefunden" in rendered(views.kennzahl("gibt_es_nicht", "light", NOW))


def test_data_status_marks_stale_series(data):
    page = rendered(views.data_status(NOW))
    assert "veraltet" in page and "aktuell" in page and "Cboe (Indizes)" in page


def test_data_status_shows_what_the_alerts_reported(data):
    page = rendered(views.data_status(NOW))
    assert "Alerts (ntfy.sh)" in page and "Noch keine Alerts gesendet" in page
    from fever.store.alerts import write_alert_state
    engine = make_engine(data)
    with engine.begin() as conn:
        write_alert_state(conn, "traffic_light", {"level": 2, "score_date": "2026-09-25"}, NOW)
        write_alert_state(conn, "stale", {"indicators": ["ebp"]}, NOW)
        write_alert_state(conn, "errors", {"pending": {"ecb": NOW.isoformat()}, "reported": []}, NOW)
        record_success(conn, "alerts", NOW)
    engine.dispose()
    page = rendered(views.data_status(NOW))
    assert "Ampel: Orange, Stand 25.09.2026 (aktualisiert" in page and "Veraltete Indikatoren: Excess Bond Premium" in page
    assert "Anhaltende Fehler: keine" in page and "Alerts (Versand an ntfy.sh, M12)" in page
    assert page.index("Ampel: Orange") < page.index("Veraltete Indikatoren") < page.index("Anhaltende Fehler")


# --- formats ------------------------------------------------------------------------------------------


def test_german_formats():
    assert fmt.number(1234.56) == "1.234,6" and fmt.number(None) == "–" and fmt.number(0.5, 2) == "0,50"
    assert fmt.day(date(2026, 9, 5)) == "05.09.2026"
    assert fmt.berlin(datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)) == "15.01.2026, 13:00 MEZ"
    assert fmt.berlin(datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)) == "15.07.2026, 14:00 MESZ"
    now = datetime(2026, 9, 26, 12, 0, tzinfo=timezone.utc)
    assert fmt.age(now, now) == "gerade eben"
    assert fmt.age(datetime(2026, 9, 26, 9, 0, tzinfo=timezone.utc), now) == "vor 3 Std."
    assert fmt.age(datetime(2026, 9, 23, 12, 0, tzinfo=timezone.utc), now) == "vor 3 Tagen"


# --- recession bars (E-56) ------------------------------------------------------------------------------


def test_recession_periods_from_usrec(migrated_dir, monkeypatch):
    engine = make_engine(migrated_dir)
    months = [date(2007, 11, 1), date(2007, 12, 1), date(2008, 1, 1), date(2008, 2, 1), date(2020, 2, 1),
              date(2020, 3, 1), date(2020, 4, 1), date(2020, 5, 1), date(2026, 7, 1), date(2026, 8, 1)]
    values = [0, 1, 1, 0, 0, 1, 1, 0, 0, 1]
    with engine.begin() as conn:
        append_observations(conn, "usrec", [NewObservation(m, float(v), NOW, True) for m, v in zip(months, values)], retrieved_at=NOW)
    monkeypatch.setenv("FEVER_DATA", str(migrated_dir))
    web_db.engine.cache_clear()
    try:
        assert web_db.recessions() == (
            (date(2007, 12, 1), date(2008, 1, 31)),
            (date(2020, 3, 1), date(2020, 4, 30)),
            (date(2026, 8, 1), date(2026, 8, 31)),  # still running at the end of the series
        )
    finally:
        web_db.engine.cache_clear()


def test_charts_draw_grey_bars_behind_the_lines_and_say_so():
    periods = ((date(2008, 1, 1), date(2009, 6, 30)), (date(2020, 3, 1), date(2020, 4, 30)), (date(1990, 8, 1), date(1991, 3, 31)))
    chart = Chart("vix", "VIX", "Cboe", [Line("VIX", [date(2005, 1, 3), date(2026, 9, 25)], [12.0, 15.0])], "Punkte",
                  recessions=periods)
    figure = validated(time_series(chart, "light", today=date(2026, 9, 26))[0])
    shapes = figure.layout.shapes
    iso = [tuple(day.isoformat() for day in period) for period in periods]
    assert [(s.x0, s.x1) for s in shapes] == iso[:2]  # 1990 lies before the data
    assert all(s.layer == "below" and s.yref == "paper" for s in shapes)
    assert figure.layout.annotations[0].text.endswith("Grau: US-Rezessionen nach NBER (über FRED)")
    plain = validated(time_series(replace(chart, recessions=()), "light")[0])
    assert not plain.layout.shapes and "Rezession" not in plain.layout.annotations[0].text


def test_chart_card_gives_the_responsive_graph_a_box_with_a_height():
    """Regression: without a sized box the graph collapsed to 0 px after a range button click."""
    from fever.web.components import chart_card
    card = chart_card("g", Chart("vix", "VIX", "Cboe", [Line("VIX", [date(2026, 9, 25)], [15.0])], "Punkte"), "light")
    box = card.children[1]
    assert box.className == "chart-box" and box.children.responsive is True and box.children.style == {"height": "100%"}
    css = (REPO / "assets" / "base.css").read_text(encoding="utf-8")
    assert re.search(r"\.chart-box \{ height: \d+px; \}", css)


# --- areas with their indicators (M7a, E-57 to E-60) --------------------------------------------------


def component_ids(component) -> list:
    """Ids of all components below `component`, in document order."""
    found = []

    def walk(node):
        if isinstance(node, (list, tuple)):
            for child in node:
                walk(child)
        elif hasattr(node, "to_plotly_json"):
            if getattr(node, "id", None) is not None:
                found.append(node.id)
            walk(getattr(node, "children", None))

    walk(component)
    return found


def _walk_components(node):
    if isinstance(node, (list, tuple)):
        for child in node:
            yield from _walk_components(child)
    elif hasattr(node, "to_plotly_json"):
        yield node
        yield from _walk_components(getattr(node, "children", None))


def test_contribution_steps_come_from_the_configuration(monkeypatch):
    from fever.config import scoring_config
    config = scoring_config()
    ratio = " ".join(texts.contribution("vix_vix3m"))
    assert f"letzten {config.window_years} Jahre" in ratio and f"mindestens {config.min_history_years} Jahren" in ratio
    assert "Median der Perzentile" in ratio and "Diffusionsindex" in ratio and "Eigene Ampelregel: Rot" in ratio
    assert "(mehr als 4 Tage" in ratio  # daily: frequency 1 day + tolerance 3
    vix = " ".join(texts.contribution("vix"))
    assert "Ampelregel" not in vix and "hoch = mehr Stress" in vix
    ecy = " ".join(texts.contribution("ecy"))
    assert "umgedreht, weil ein niedriger Wert mehr Fallhöhe bedeutet" in ecy and "Diffusionsindex" not in ecy
    assert f"mindestens {config.min_vulnerability}" in ecy and "Mittel der Perzentile" in ecy
    assert "nur zur Anzeige" in " ".join(texts.contribution("vx_cot_short"))
    changed = replace(config, window_years=7, min_history_years=4, fast_block_half_life=4, red_vix_ratio_days=6)
    monkeypatch.setattr(texts, "scoring_config", lambda: changed)
    ratio = " ".join(texts.contribution("vix_vix3m"))
    assert "letzten 7 Jahre" in ratio and "mindestens 4 Jahren" in ratio
    assert "Halbwertszeit 4 Handelstage), bevor" in ratio and "an 6 Handelstagen" in ratio


def test_role_today_names_the_share_in_the_area():
    latest = {"score_date": date(2026, 9, 25), "block_volatility": 28.2, "vulnerability_raw": 82.2}
    rows = {"vix": {"status": "ok", "percentile": 33.0}, "vvix": {"status": "ok", "percentile": 24.0},
            "vrp": {"status": "stale", "percentile": None}, "ecy": {"status": "ok", "percentile": 99.6}}
    assert views._role_today("vix", latest, rows) == (
        "Stand 25.09.2026: gültig mit Perzentil 33, einer von 2 gültigen Indikatoren im Bereich; Bereichswert (Median) 28,2.")
    assert views._role_today("vrp", latest, rows) == "Stand 25.09.2026: veraltet; zählt heute nicht, der Bereich rechnet ohne ihn."
    assert "eine von 1 gültigen Komponenten; Fallhöhe ungeglättet 82,2" in views._role_today("ecy", latest, rows)
    assert views._role_today("nfci", latest, rows) == "Noch kein berechneter Wert."


def test_history_start_needs_every_input(migrated_dir, monkeypatch):
    engine = make_engine(migrated_dir)
    with engine.begin() as conn:
        append_observations(conn, "sofr", [NewObservation(date(2018, 4, 3), 1.8, NOW, True)], retrieved_at=NOW)
        append_observations(conn, "iorb", [NewObservation(date(2021, 7, 29), 0.15, NOW, True)], retrieved_at=NOW)
    monkeypatch.setenv("FEVER_DATA", str(migrated_dir))
    web_db.engine.cache_clear()
    assert web_db.history_start(["sofr", "iorb"]) == date(2021, 7, 29)
    assert web_db.history_start(["sofr", "vix"]) is None
    web_db.engine.cache_clear()


def test_indicator_page_explains_its_contribution(data):
    page = rendered(views.kennzahl("vix", "light", NOW))
    assert "So fließt der Wert in den Bereich ein" in page and "Steckbrief" in page


def test_every_history_view_names_the_latest_vintage_rule(data):
    """CLAUDE.md: in phase 1 the newest vintage counts per observation, and the history view says so."""
    for page in (views.overview("light", NOW), views.view("makro", "light", NOW), views.kennzahl("vix", "light", NOW),
                 views.kennzahl("stress", "light", NOW)):
        assert views.HISTORY_NOTE in rendered(page)


# --- overview (report 6.3 view 1; start page since E-67) -----------------------------------------------------


def test_matrix_regions_follow_the_rules_in_scoring_toml(monkeypatch):
    from fever.config import scoring_config
    c = scoring_config()
    regions = views.matrix_regions()
    # drawn low to high: the highest level covers the rest; no yellow area, the vulnerability alone is no rule (E-95)
    assert [r.level for r in regions] == [0, 2, 2, 3]
    assert (regions[3].x0, regions[2].x0) == (c.red_stress, c.orange_stress)
    assert (regions[1].x0, regions[1].y0) == (c.orange_stress_with_vulnerability, c.orange_vulnerability)
    monkeypatch.setattr(views, "scoring_config", lambda: replace(c, red_stress=95, orange_vulnerability=70))
    assert (views.matrix_regions()[3].x0, views.matrix_regions()[1].y0) == (95, 70)


def test_matrix_chart_standard_and_labels():
    from fever.web.figures import Matrix, matrix
    days = [date(2026, 9, 24), date(2026, 9, 25)]
    chart = Matrix("matrix", "Ampelmatrix", "eigene Berechnung", days, [30.0, 35.0], [70.0, 80.0], views.matrix_regions(),
                   observed=days[-1], retrieved=NOW, note="Hinweis")
    figure, config = matrix(chart, "dark", today=date(2026, 9, 26))
    figure = validated(figure)
    assert config["showSendToCloud"] is False and config["toImageButtonOptions"]["filename"] == "matrix_26-09-2026"
    assert len(figure.layout.shapes) == 4 and figure.layout.xaxis.range == (0, 100)  # four areas, no yellow one (E-95)
    labels = [(a.text, a.textangle) for a in figure.layout.annotations if a.text in ("Grün", "Gelb", "Orange", "Rot")]
    assert labels == [("Grün", 0), ("Orange", 0), ("Orange", -90), ("Rot", -90)]  # full-height bands upright
    assert figure.data[1].text == ("Stand 25.09.2026",) and "Hinweis" in figure.layout.annotations[-1].text


def test_overview_shows_cards_matrix_and_sources(data):
    page = views.overview("light", NOW)
    text = rendered(page)
    for kennzahl in ("traffic_light", "stress", "vulnerability", "confidence", "diffusion"):
        assert f"/kennzahl/{kennzahl}" in text
    graph = next(c for c in _walk_components(page) if type(c).__name__ == "Graph")
    assert graph.id == "matrix" and len(validated(graph.figure).layout.shapes) == 4
    assert "Letzte Aktualisierung je Quelle" in text and "Cboe (Indizes)" in text


def test_overview_trace_covers_the_last_60_score_days(data, monkeypatch):
    rows = [{"score_date": date(2026, 1, 1) + timedelta(days=i), "stress": 30.0 + i / 10, "vulnerability": 70.0} for i in range(100)]
    monkeypatch.setattr(web_db, "composite_history", lambda *columns: rows)
    graph = next(c for c in _walk_components(views.overview("light", NOW)) if type(c).__name__ == "Graph")
    trace, today = validated(graph.figure).data
    assert len(trace.x) == views.TRACE_DAYS == 60 and trace.x[0] == rows[40]["stress"]
    assert today.x == (rows[-1]["stress"],) and today.text == ("Stand 10.04.2026",)


def test_one_navigation_row_and_the_old_overview_b_address(client):
    from fever.web.app import NAVIGATION
    assert [path for path, _ in NAVIGATION][:2] == ["/", "/ansicht/signale"] and len(NAVIGATION) == 10
    layout = json.dumps(client.get("/_dash-layout").get_json(), ensure_ascii=False)
    assert all(path in layout for path, _ in NAVIGATION) and "Übersicht B" not in layout
    moved = client.get("/uebersicht-b")  # old address of the overview (E-67)
    assert moved.status_code == 301 and moved.headers["Location"].endswith("/")


# --- views 2 to 6 (M7) ----------------------------------------------------------------------------------


def test_every_view_renders_and_every_display_kennzahl_is_shown(data):
    shown = set()
    for name in views.VIEW_TITLES:
        page = rendered(views.view(name, "light", NOW))
        assert "Datenbank nicht lesbar" not in page, name
        shown |= set(re.findall(r"/kennzahl/([a-z0-9_]+)", page))
    assert set(texts.DISPLAYS) <= shown and set(texts.DISPLAY_VIEWS) == set(texts.DISPLAYS)
    assert "nicht gefunden" in rendered(views.view("gibt_es_nicht", "light", NOW))
    breadth = rendered(views.view("breite", "light", NOW))
    assert "E-72" in breadth  # the 50/200-day line is named as missing
    assert all(f"/kennzahl/{i}" in breadth for i in views.area_indicators("breadth"))
    assert len(views.area_indicators("breadth")) == 5
    assert "/kennzahl/top10_concentration" in rendered(views.view("fallhoehe", "light", NOW))


def test_view_pages_answer(client):
    for name in views.VIEW_TITLES:
        assert client.get(f"/ansicht/{name}").status_code == 200


def test_runs_mark_consecutive_days_and_keep_single_days_visible():
    days = [date(2026, 9, d) for d in range(1, 8)]
    assert views.runs(days, [False, True, True, False, True, False, False]) == (
        (date(2026, 9, 2), date(2026, 9, 4)), (date(2026, 9, 5), date(2026, 9, 6)))
    assert views.runs(days[:2], [True, True]) == ((date(2026, 9, 1), date(2026, 9, 3)),)


def test_ccc_bb_uses_only_common_days_and_the_curve_shading(data, monkeypatch):
    series = {"bamlh0a3hyc": [(date(2026, 9, 1), 9.0), (date(2026, 9, 2), 9.5)], "bamlh0a1hybb": [(date(2026, 9, 2), 2.0)],
              "t10y3m": [(date(2026, 9, 1), -0.1), (date(2026, 9, 2), 0.2)]}
    monkeypatch.setattr(web_db, "series_history", lambda sid: series.get(sid, []))
    charts = []
    real = views.ui.chart_card
    monkeypatch.setattr(views.ui, "chart_card", lambda graph_id, chart, theme: charts.append(chart) or real(graph_id, chart, theme))
    views.view("makro", "light", NOW)
    by_id = {c.kennzahl_id: c for c in charts}
    assert by_id["ccc_bb"].lines[0].x == [date(2026, 9, 2)] and by_id["ccc_bb"].lines[0].y == [7.5]
    assert by_id["yield_curve"].shaded == ((date(2026, 9, 1), date(2026, 9, 2)),)
    assert all(c.full_history for c in charts)


def test_small_values_keep_two_significant_digits():
    assert views._value(0.0042) == "0,0042" and views._value(0.045) == "0,045" and views._value(-0.0042) == "-0,0042"
    assert views._value(0.83) == "0,83" and views._value(14.87) == "14,87" and views._value(0.0) == "0,00"


def test_display_pages_link_their_view(data):
    page = rendered(views.kennzahl("ccc_bb", "light", NOW))
    assert "/ansicht/makro" in page and "nur Anzeige" in page


# --- decisions of 29.09.2026 (E-80 to E-90) ----------------------------------------------------------------


def test_role_marks_name_every_role_of_a_value():
    """E-81: blue stress with its area, purple vulnerability, grey display, outlined rule; both roles of one value."""
    both = [("Stress · Kredit", "stress"), ("Fallhöhe", "vulnerability")]
    assert texts.roles("credit_spread_level") == both and texts.roles("credit_spread_tight") == both  # E-85
    assert texts.roles("credit_spread_change") == [("Stress · Kredit", "stress"), ("Ampelregel", "rule")]
    assert texts.roles("sahm") == [("Stress · Makro", "stress"), ("Ampelregel", "rule")]
    assert texts.roles("sos") == [("Ampelregel", "rule")]
    assert texts.roles("ecy") == [("Fallhöhe", "vulnerability")] and texts.roles("vix") == [("Stress · Volatilität", "stress")]
    assert texts.roles("money_market") == [("nur Anzeige", "display")] and texts.roles("stress") == []
    from fever.web.components import kennzahl_head
    head = rendered(kennzahl_head("credit_spread_tight"))
    assert '"role role-stress"' in head and '"role role-vulnerability"' in head and "Fallhöhe" in head


def test_views_show_the_new_kennzahlen(data):
    macro = rendered(views.view("makro", "light", NOW))
    for kennzahl in ("sahm", "sos", "spx_trend", "hy_oas"):
        assert f"/kennzahl/{kennzahl}" in macro
    assert "Lizenz ICE Data Indices" in macro and "Re-Steepening" not in macro  # no curve data in the fixture
    vulnerability = rendered(views.view("fallhoehe", "light", NOW))
    for kennzahl in ("equity_allocation", "credit_spread_tight", "money_market"):
        assert f"/kennzahl/{kennzahl}" in vulnerability
    assert not any("fünf Jahre" in text for text in views.PLACEHOLDERS)


def test_rule_periods_come_from_the_stored_traffic_light(monkeypatch):
    """The violet days are the days the scoring stored the rule as active; the web recomputes nothing."""
    days = [date(2026, 1, d) for d in range(1, 6)]
    stored = ["", "yellow_sahm", "orange_sahm_trend,yellow_sos", "yellow_diffusion", "yellow_sahm"]
    monkeypatch.setattr(web_db, "composite_history", lambda *columns: [
        {"score_date": d, "active_rules": rules} for d, rules in zip(days, stored)])
    periods, label = views.rule_periods("sahm")
    assert periods == ((days[1], days[3]), (days[4], days[4] + timedelta(days=1)))
    assert label == "Violett: Ampelregel aktiv (Sahm-Regel mindestens 0,50: Gelb, mit S&P 500 unter der 200-Tage-Linie Orange)"
    assert views.rule_periods("spx_trend")[0] == ((days[2], days[3]),)
    periods, label = views.rule_periods("sos")
    assert periods == ((days[2], days[3]),) and "SOS-Indikator über 0,20" in label
    assert views.rule_periods("vix") == ((), "")


def test_resteepening_note():
    d = [date(2025, 10, 15), date(2025, 10, 16), date(2025, 10, 17), date(2025, 10, 20)]
    assert views.resteepening(list(zip(d, [0.1, -0.05, 0.0, 0.2]))) == (
        "Letztes Re-Steepening: 17.10.2025 (erster Wert ab null nach dem letzten Tag der Inversion am 16.10.2025). "
        "Keine Wirkung auf die Ampel (E-84).")
    assert "invertiert seit 16.10.2025" in views.resteepening(list(zip(d, [0.1, -0.05, -0.1, -0.2])))
    assert "nie invertiert" in views.resteepening(list(zip(d, [0.1, 0.0, 0.3, 0.2])))


def test_money_market_share_uses_common_quarters():
    q = [date(2026, 1, 1), date(2026, 4, 1), date(2026, 7, 1)]
    funds = list(zip(q, [10.0, 20.0, 30.0]))
    nonfinancial = list(zip(q, [80.0, 0.0, 100.0]))
    financial = list(zip(q[::2], [20.0, 50.0]))
    assert views.money_market_share(funds, nonfinancial, financial) == [(q[0], 10.0), (q[2], 20.0)]


def test_generated_texts_name_the_recession_rules():
    lines = " ".join(texts.thresholds("traffic_light"))
    assert "Sahm-Regel mindestens 0,50, während der S&P 500 unter seiner 200-Tage-Linie liegt (ohne Hysterese)" in lines
    assert "Sahm-Regel mindestens 0,50 ohne diesen Abwärtstrend, oder der SOS-Indikator über 0,20" in lines
    assert texts.rule_text("orange_sahm_trend") == "Orange: Sahm-Regel mindestens 0,50 und S&P 500 unter seiner 200-Tage-Linie"
    assert texts.rule_text("yellow_sahm") == "Gelb: Sahm-Regel mindestens 0,50"
    assert texts.rule_text("yellow_sos") == "Gelb: SOS-Indikator über 0,20"
    assert texts.roles("spx_trend") == [("Ampelregel", "rule")]
    sos = " ".join(texts.contribution("sos"))
    assert "nicht in Stress, Fallhöhe, Konfidenz oder Diffusionsindex" in sos and "mindestens Gelb" in sos
    assert dict(texts.steckbrief("sos"))["Gewicht in der Konfidenz"].startswith("keins")
    assert any("mindestens Gelb" in line and "Orange, solange zugleich" in line for line in texts.contribution("sahm"))
    assert any("Derselbe Wert zählt zusätzlich im Bereich Fallhöhe" in line for line in texts.contribution("credit_spread_level"))
    assert "Nur Ampelregel" in rendered(views.explanations())


def test_time_series_fit_the_y_axis_to_the_visible_part():
    """E-88: first view fitted on the server; the browser script keeps it so after zoom and refresh."""
    from fever.web import figures
    days = [date(2020, 1, 1), date(2021, 6, 1), date(2024, 1, 1), date(2026, 9, 25)]
    chart = Chart("vix", "VIX", "Cboe", [Line("VIX", days, [80.0, 20.0, 10.0, 30.0])], "Punkte")
    layout = validated(time_series(chart, "light")[0]).layout
    # window from 25.09.2021: 20 (last before), 10, 30 -> span 20, padding 1 each side
    assert layout.xaxis.range == ("2021-09-25", "2026-09-25") and layout.yaxis.range == (9.0, 31.0)
    assert layout.meta == {"autoY": True}
    fixed = validated(time_series(replace(chart, y_range=(0, 100)), "light")[0]).layout
    assert fixed.yaxis.range == (0, 100) and fixed.meta is None
    whole = validated(time_series(replace(chart, full_history=True), "light")[0]).layout
    assert whole.yaxis.range == (6.5, 83.5)
    assert figures.fitted_range([(days, [5.0, None, 5.0, 5.0])], "2021-01-01", "2026-12-31") == [4.75, 5.25]
    assert figures.fitted_range([(days, [None] * 4)], "2021-01-01", "2026-12-31") is None
    script = (REPO / "assets" / "autoscale.js").read_text(encoding="utf-8")
    assert f"const PADDING = {figures.Y_PADDING};" in script and "meta.autoY" in script


def test_the_vulnerability_is_purple_everywhere():
    """E-98: lines, band, sparkline, percentile chip, heatmap part, names and titles of the vulnerability in purple,
    from the Kennzahl's own block (the Baa level stays blue, its reversal in the vulnerability is purple)."""
    from fever.web import components as ui
    from fever.web.figures import (
        PALETTE, VULNERABILITY_RAMP, Band, Chart, Heatmap, Line, curve_style, heatmap, line_colours, sparkline, time_series,
    )
    assert [texts.accent(k) for k in ("vulnerability", "credit_spread_tight", "credit_spread_level", "vix", "stress")] == [
        "vulnerability", "vulnerability", "", "", ""]
    assert [texts.accent(k) for k in ("cape", "money_market", "skew")] == ["vulnerability", "vulnerability", ""]
    assert "Farbskala Lila" in texts.thresholds("ecy")[0] and "Farbskala Blau" in texts.thresholds("vix")[0]
    cards = [c for c in views.explanations() if isinstance(getattr(c, "children", None), list)]
    assert [c.children[0].children for c in cards if getattr(c.children[0], "className", None)] == ["Fallhöhe"]
    links = {li.children[0].href: getattr(li, "className", None) for c in cards for li in c.children[1].children}
    assert [links[f"/kennzahl/{k}"] for k in ("vulnerability", "ecy", "cape", "stress", "vix")] == [
        "k-vulnerability", "k-vulnerability", "k-vulnerability", None, None]
    light = line_colours("light", "vulnerability")
    assert light[0] == "#7b3f93" and PALETTE["light"]["series"][0] not in light and "#4a3aa7" not in light
    assert line_colours("dark") == PALETTE["dark"]["series"] and line_colours("dark", "vulnerability")[0] == "#9c56ba"
    days = [date(2026, 9, 24), date(2026, 9, 25)]
    chart = Chart("x", "T", "s", [Line("Wert", days, [1.0, 2.0])], "Wert", band=Band(days, [0.0, 0.0], [1.0, 1.0], [2.0, 2.0]),
                  accent="vulnerability")
    figure = validated(time_series(chart, "light")[0])
    assert figure.data[-1].line.color == "#7b3f93" and figure.data[2].line.color == PALETTE["light"]["secondary"]
    assert figure.data[1].fillcolor != figure.data[1].line.color  # the band is a purple tint
    assert validated(sparkline(days, [1.0, 2.0], "dark", "vulnerability")[0]).data[0].line.color == "#9c56ba"
    chip = ui.percentile_chip(95.0, 80.0, "vulnerability")
    assert chip.style["backgroundColor"] == VULNERABILITY_RAMP[-1] and ui.percentile_chip(95.0, 80.0).style["backgroundColor"] == "#0d366b"
    # the heatmap: the vulnerability rows as a purple lower part on their own y-axis, the dates under it
    chart = Heatmap("heatmap", "H", "x", ["VIX", "VRP", "CAPE"], days, [[10.0, 20.0], [30.0, None], [90.0, 95.0]],
                    accents=["", "", "vulnerability"])
    figure = validated(heatmap(chart, "light")[0])
    top, bottom = figure.data
    assert top.y == ("VIX", "VRP") and bottom.y == ("CAPE",) and bottom.yaxis == "y2"
    assert top.colorscale[0][1] == "#cde2fb" and bottom.colorscale[-1][1] == VULNERABILITY_RAMP[-1]
    assert figure.layout.xaxis.anchor == "y2" and figure.layout.yaxis2.domain[1] < figure.layout.yaxis.domain[0]
    assert "lila Fallhöhe" in figure.layout.annotations[-1].text
    assert len(validated(heatmap(Heatmap("h", "H", "x", ["VIX"], days, [[1.0, 2.0]]), "light")[0]).data) == 1
    # curves of the validation: purple dashed, blue solid
    assert curve_style("dark", "vulnerability") == ("#9c56ba", "dash") and curve_style("light", "stress") == ("#2a78d6", "solid")
    assert "k-vulnerability" in ui.kennzahl_head("credit_spread_tight").className
    assert "k-vulnerability" not in ui.kennzahl_head("credit_spread_level").className


def test_heatmap_rows_carry_their_roles():
    from fever.web.figures import Heatmap, heatmap
    days = [date(2026, 9, 24), date(2026, 9, 25)]
    chart = Heatmap("heatmap", "H", "x", ["Kreditspread Baa (Niveau)"], days, [[10.0, 20.0]],
                    roles=[(("Stress · Kredit", "stress"), ("Fallhöhe", "vulnerability"))])
    figure = validated(heatmap(chart, "light")[0])
    assert figure.data[0].y == ("Kreditspread Baa (Niveau) · Stress · Kredit · Fallhöhe",)  # shown in the hover
    tick = figure.layout.yaxis.ticktext[0]
    assert tick.count("■") == 2 and tick.endswith(" Kreditspread Baa (Niveau)") and "#7b3f93" in tick  # purple (E-98)
    stamp = figure.layout.annotations[-1].text
    assert "■</span> Stress · " in stamp and "■</span> Fallhöhe (Bereich im Hover)" in stamp and "Ampelregel" not in stamp


# --- load time (28.09.2026): lean queries and plain figures -----------------------------------------------


def test_every_chart_of_every_page_is_a_valid_plotly_figure(data):
    """Figures are plain dicts (speed); here plotly.graph_objects checks every property of every chart."""
    pages = [views.overview("light", NOW), views.kennzahl("vix", "dark", NOW), views.kennzahl("stress", "light", NOW)]
    pages += [views.view(name, "light", NOW) for name in views.VIEW_TITLES if name != "visualisierung"]
    pages += [views.vis_stress("light", NOW), views.vis_regime("light", NOW), views.vis_heatmap("weekly", "light", NOW),
              views.vis_bands("vix", "light", NOW), views.vis_sparklines("dark", NOW)]
    graphs = [c for c in _walk_components(pages) if type(c).__name__ == "Graph"]
    assert len(graphs) > 20
    for graph in graphs:
        validated(graph.figure)
        json.dumps(graph.figure, allow_nan=False)  # plain JSON: ISO dates, no objects left for the encoder


def test_long_reads_are_kept_until_the_worker_stores_new_data(data):
    """E-78: kept per data version; a new observation or a new scoring run makes every page read afresh."""
    from fever import score
    engine = make_engine(data)
    first = web_db.series_history("vix")
    assert web_db.series_history("vix") is first  # same data version: kept, not read again
    scores = web_db.composite_history("stress")
    with engine.begin() as conn:
        append_observations(conn, "vix", [NewObservation(date(2026, 9, 28), 30.0, NOW, False)], retrieved_at=NOW)
    again = web_db.series_history("vix")
    assert again is not first and again[-1] == (date(2026, 9, 28), 30.0)
    assert web_db.composite_history("stress") is not scores  # every kept read is dropped together
    kept = web_db.composite_history("stress")
    score.run(engine, clock=lambda: NOW + timedelta(hours=1))  # new scoring run: new computed_at
    assert web_db.composite_history("stress") is not kept
    assert web_db.series_history("vix") is not again


def test_kept_reads_render_the_same_page(data):
    for name in ("makro", "signale"):
        assert rendered(views.view(name, "light", NOW)) == rendered(views.view(name, "light", NOW))
    assert rendered(views.vis_sparklines("dark", NOW)) == rendered(views.vis_sparklines("dark", NOW))


def test_lean_score_queries(migrated_dir, monkeypatch):
    from fever.store.tables import indicator_score
    engine = make_engine(migrated_dir)
    d1, d2, d3 = date(2026, 9, 23), date(2026, 9, 24), date(2026, 9, 25)
    rows = [(d1, "vix", "ok", 10.0, 50.0), (d1, "vvix", "stale", 90.0, 70.0), (d2, "vix", "ok", 11.0, 60.0),
            (d3, "vix", "history", 12.0, None), (d3, "vvix", "ok", 95.0, 80.0)]
    with engine.begin() as conn:
        conn.execute(indicator_score.insert(), [
            {"score_date": d, "indicator_id": i, "status": st, "value": v, "percentile": p, "band_p10": 1.0}
            for d, i, st, v, p in rows])
    monkeypatch.setenv("FEVER_DATA", str(migrated_dir))
    web_db.engine.cache_clear()
    try:
        assert web_db.score_days() == [d1, d2, d3]
        assert web_db.valid_percentiles((d1, d3)) == {("vix", d1): 50.0, ("vvix", d3): 80.0}  # stale and other days left out
        assert web_db.indicator_values_since(d1) == {
            "vix": [{"score_date": d2, "status": "ok", "value": 11.0}, {"score_date": d3, "status": "history", "value": 12.0}],
            "vvix": [{"score_date": d3, "status": "ok", "value": 95.0}]}
        assert web_db.indicator_history("vix", "value", "band_p10") == [
            {"score_date": d, "value": v, "band_p10": 1.0} for d, v in ((d1, 10.0), (d2, 11.0), (d3, 12.0))]
    finally:
        web_db.engine.cache_clear()


def test_lean_observation_queries(migrated_dir, monkeypatch):
    engine = make_engine(migrated_dir)
    later = NOW + timedelta(days=1)
    with engine.begin() as conn:
        append_observations(conn, "cfe_vx1", [NewObservation(date(2026, 9, 24), 17.0, NOW, True),
                                              NewObservation(date(2026, 9, 25), 18.0, NOW, True)], retrieved_at=NOW)
        append_observations(conn, "cfe_vx1", [NewObservation(date(2026, 9, 25), 18.5, later, False)], retrieved_at=later)
        append_observations(conn, "cfe_vx1_days", [NewObservation(date(2026, 9, 25), 21.0, NOW, True)], retrieved_at=NOW)
    monkeypatch.setenv("FEVER_DATA", str(migrated_dir))
    web_db.engine.cache_clear()
    try:
        assert web_db.newest_observation("cfe_vx1") == (date(2026, 9, 25), 18.5)  # newest vintage of the newest date
        assert web_db.newest_observation("cfe_vx2") is None
        assert web_db.value_on("cfe_vx1_days", date(2026, 9, 25)) == 21.0
        assert web_db.value_on("cfe_vx1_days", date(2026, 9, 24)) is None
        assert web_db.newest_retrieval(["cfe_vx1", "cfe_vx1_days"]) == later
        assert web_db.newest_retrieval(["cfe_vx2"]) is None
    finally:
        web_db.engine.cache_clear()


# --- view 7 (M7, E-63, E-64, E-66) ------------------------------------------------------------------------


def test_crisis_episodes_are_sorted_dated_and_sourced(tmp_path):
    from fever.config import ConfigError, crisis_episodes
    episodes = crisis_episodes()
    assert len(episodes) == 13 and [e.start for e in episodes] == sorted(e.start for e in episodes)
    assert all(e.start <= e.end and e.source and e.label for e in episodes)
    assert (episodes[0].start, episodes[0].end) == (date(1998, 7, 17), date(1998, 8, 31))
    (tmp_path / "episodes.toml").write_text('[episode.x]\nlabel = "X"\nstart = 2020-03-23\nend = 2020-02-19\nsource = "Q"\n')
    with pytest.raises(ConfigError, match="start <= end"):
        crisis_episodes(tmp_path)


def test_stress_history_carries_the_crisis_strip():
    days = [date(2020, 1, 2), date(2020, 6, 1)]
    chart = Chart("stress-crises", "Stress", "eigene Berechnung", [Line("Stress", days, [40.0, 60.0])], "Wert",
                  episodes=((date(2020, 2, 19), date(2020, 3, 23), "März 2020"),))
    figure = validated(time_series(chart, "light")[0])
    strips = [s for s in figure.layout.shapes if s.y0 == 0.94]
    assert len(strips) == 1 and "Krisen" in figure.layout.annotations[-1].text
    assert figure.data[-1].text == ("März 2020: 19.02.2020 bis 23.03.2020",)


def test_view_7_parts_render(data):
    for part in (views.vis_stress("light", NOW), views.vis_regime("light", NOW), views.vis_heatmap("weekly", "light", NOW),
                 views.vis_heatmap("daily", "dark", NOW), views.vis_bands("vix", "light", NOW), views.vis_sparklines("light", NOW)):
        assert "Datenbank nicht lesbar" not in rendered(part)
    assert "Bitte einen Indikator" in rendered(views.vis_bands("gibt_es_nicht", "light", NOW))


def test_heatmap_grains_pick_stored_days_and_leave_invalid_blank(data, monkeypatch):
    days = [date(2024, 1, 1) + timedelta(days=i) for i in range(1000)]
    valid = {("vix", d): float(i % 100) for i, d in enumerate(days) if i % 10}  # every tenth day stale
    asked = []
    monkeypatch.setattr(web_db, "score_days", lambda: days)
    monkeypatch.setattr(web_db, "valid_percentiles",
                        lambda wanted: asked.append(list(wanted)) or {k: v for k, v in valid.items() if k[1] in set(wanted)})
    weekly = next(c for c in _walk_components(views.vis_heatmap("weekly", "light", NOW)) if type(c).__name__ == "Graph")
    x = [date.fromisoformat(d) for d in validated(weekly.figure).data[0].x]
    assert all(a.isocalendar()[:2] != b.isocalendar()[:2] for a, b in zip(x, x[1:]))  # one column per week
    assert x[-1] == days[-1] and x[0] == date(2024, 1, 7)  # the last day of each week
    assert asked[-1] == x  # only the shown columns are read
    daily = validated(next(c for c in _walk_components(views.vis_heatmap("daily", "light", NOW))
                           if type(c).__name__ == "Graph").figure)
    assert len(daily.data[0].x) == 730 and daily.data[0].x[-1] == days[-1].isoformat()
    row = views._ordered_indicators().index("vix")
    z = daily.data[0].z[row]
    assert z[list(daily.data[0].x).index("2026-09-17")] is None  # day 990: stale stays blank


def test_bands_chart_draws_the_stored_band(data, monkeypatch):
    history = [{"score_date": date(2026, 9, 21 + i), "status": "ok", "value": 15.0 + i, "band_p10": 12.0, "band_p50": 16.0,
                "band_p90": 27.0, "obs_date": date(2026, 9, 21 + i), "percentile": 50.0} for i in range(5)]
    monkeypatch.setattr(web_db, "indicator_history", lambda indicator_id, *columns: history)
    graph = next(c for c in _walk_components(views.vis_bands("vix", "light", NOW)) if type(c).__name__ == "Graph")
    low, high, mid, value = validated(graph.figure).data
    assert low.y == (12.0,) * 5 and high.y == (27.0,) * 5 and high.fill == "tonexty" and mid.y == (16.0,) * 5
    assert value.y == tuple(15.0 + i for i in range(5))


def test_regime_heatmap_and_sparkline_follow_the_standard():
    from fever.web.figures import Heatmap, Regime, heatmap, regime, sparkline
    days = [date(2026, 9, 24), date(2026, 9, 25)]
    figure, config = regime(Regime("regime", "Ampel", "x", days, [0, 3], texts.LEVEL_NAMES), "dark")
    figure = validated(figure)
    assert config["showSendToCloud"] is False and [list(row) for row in figure.data[0].customdata] == [["Grün", "Rot"]]
    assert len(figure.data) == 1 and figure.layout.yaxis.visible is False
    # E-96: the vulnerability as a second strip below, in its purple percentile colours (E-98), gaps stay empty
    figure, _ = regime(Regime("regime", "Ampel", "x", days, [0, 3], texts.LEVEL_NAMES, vulnerability=[85.0, None]), "light")
    figure = validated(figure)
    strip = figure.data[1]
    assert strip.y == ("Fallhöhe",) and [list(row) for row in strip.z] == [[85.0, None]] and (strip.zmin, strip.zmax) == (0, 100)
    assert strip.colorscale[0][1] == "#ead8f3" and strip.colorscale[-1][1] == "#4b235b" and "Fallhöhe" in strip.hovertemplate
    assert strip.yaxis == "y2" and figure.layout.yaxis2.domain == (0, 0.48) and figure.layout.yaxis.domain == (0.52, 1)
    figure, config = heatmap(Heatmap("heatmap", "H", "x", ["VIX"], days, [[10.0, None]]), "light")
    figure = validated(figure)
    assert config["showSendToCloud"] is False and figure.data[0].zmax == 100 and figure.data[0].colorscale[0][1] == "#cde2fb"
    figure, config = sparkline(days, [1.0, 2.0], "light")
    assert config["staticPlot"] is True and validated(figure).data[0].x == ("2026-09-24", "2026-09-25")


def test_visualisation_frame_keeps_switch_and_selection(client):
    from fever.web.pages import ansicht
    frame = ansicht.layout(name="visualisierung")
    components = {c.id: c for c in _walk_components(frame) if isinstance(getattr(c, "id", None), str)}
    assert components["heatmap-grain"].value == "weekly" and components["heatmap-grain"].persistence is True
    assert components["bands-indicator"].persistence is True and "vis-heatmap" in components
    assert "Yardeni" in rendered(frame) and client.get("/ansicht/visualisierung").status_code == 200


# --- view 8: validation (M10, E-93) --------------------------------------------------------------------


def store_constructed_report(directory, computed_at, score_computed_at=None):
    """A report from the constructed history of tests/test_validation.py, stored as the worker does."""
    from dataclasses import replace as replace_config
    from fever.config import validation_config
    from fever.store.validation import replace_report
    from fever.validation import validate
    from tests.test_validation import constructed
    spx, vix, scores, vix_percentile, _ = constructed()
    config = replace_config(validation_config(), walk_forward_start=1997, bootstrap_samples=50)
    report = validate(spx, vix, scores, vix_percentile, config, 80.0)
    with make_engine(directory).begin() as conn:
        replace_report(conn, report, computed_at=computed_at, score_computed_at=score_computed_at or computed_at, config_hash="x")
    return report


def test_validation_view_without_and_with_a_report(data):
    from fever.web import validation_view
    assert "Noch keine Validierung berechnet" in rendered(validation_view.content("drawdown", "light", NOW))
    store_constructed_report(data, NOW)
    for event in ("drawdown", "vix", "bear", None):
        page = validation_view.content(event, "dark", NOW)
        text = rendered(page)
        assert "Datenbank nicht lesbar" not in text and "berechnet" in text
        for graph in (c for c in _walk_components(page) if type(c).__name__ == "Graph"):
            validated(graph.figure)
            json.dumps(graph.figure, allow_nan=False)
    drawdown = rendered(validation_view.content("drawdown", "light", NOW))
    for part in ("Kurzfazit", "Trennschärfe", "ROC-Kurve", "Treffer und Fehlalarme", "Vorlauf", "Fehlalarme", "Stabilität",
                 "Grenzen", "Ampel mindestens Orange", "VIX-Filter wie Orange", "besser", "Prozentpunkte (Intervall",
                 "davon 2 mit ganzem Vorlauf", "höchstens 63 Tage"):
        assert part in drawdown, part
    assert "Beruht auf älteren Scores" not in drawdown  # the fixture scored at NOW, the report is on those scores
    store_constructed_report(data, NOW, score_computed_at=NOW - timedelta(hours=1))
    assert "Beruht auf älteren Scores" in rendered(validation_view.content("drawdown", "light", NOW))
    assert "Zu wenige Ereignisse" in rendered(validation_view.content("bear", "light", NOW))  # 14 % is no bear market


def test_validation_view_shows_the_estimated_weights(data):
    """M11 (E-94): the section with the walk-forward logit, the decision rules and the weights per year."""
    from dataclasses import replace as replace_config
    from fever.config import validation_config
    from fever.store.validation import replace_report
    from fever.validation import validate
    from fever.web import validation_view
    from tests.test_validation import constructed, features_of
    store_constructed_report(data, NOW)  # an older report without the M11 part
    assert "Noch nicht berechnet" in rendered(validation_view.content("drawdown", "light", NOW))
    spx, vix, scores, vix_percentile, days = constructed()
    config = replace_config(validation_config(), walk_forward_start=1997, bootstrap_samples=30)
    report = validate(spx, vix, scores, vix_percentile, config, 80.0, features_of(scores, days))
    with make_engine(data).begin() as conn:
        replace_report(conn, report, computed_at=NOW, score_computed_at=NOW, config_hash="x")
    page = validation_view.content("drawdown", "dark", NOW)
    text = rendered(page)
    for part in ("Geschätzte Gewichte (Walk-forward)", "Volatilität, Kredit, Makro", "Geschätzte gegen gleiche Gewichte",
                 "Mit Fallhöhe gegen ohne", "Regel 1", "Regel 2 (E-95)", "Geschätzt, Alarmanteil wie Orange",
                 "Gewichte je Jahr", "Precision gegen Ampel"):
        assert part in text, part
    graphs = {c.id: c for c in _walk_components(page) if type(c).__name__ == "Graph"}
    validated(graphs["validation-roc-fitted"].figure)
    assert len(graphs["validation-roc-fitted"].figure["data"]) == 6  # the diagonal and five signals
    # bear markets: the constructed history has none (the view stops before); the section itself says why
    bear = validation_view._fitted_section(report, "bear", ("B", "B"), date(2001, 7, 3), NOW, "light")
    assert "zu wenige Ereignisse für eine Schätzung" in rendered(bear)
    rules = validation_view.fitted_rules(report)
    assert rules[0].startswith("Regel 1") and rules[1].startswith("Regel 2")


def test_validation_view_names_missing_closes(data):
    """Before the first retrieval of spx (Cboe) the declines have no day to evaluate: say so, not "too few"."""
    from dataclasses import replace as replace_config
    import pandas as pd
    from fever.config import validation_config
    from fever.store.validation import replace_report
    from fever.validation import validate
    from fever.web import validation_view
    from tests.test_validation import constructed
    _, vix, scores, vix_percentile, _ = constructed()
    config = replace_config(validation_config(), walk_forward_start=1997, bootstrap_samples=20)
    report = validate(pd.Series([], index=[], dtype=float), vix, scores, vix_percentile, config, 80.0)
    with make_engine(data).begin() as conn:
        replace_report(conn, report, computed_at=NOW, score_computed_at=NOW, config_hash="x")
    text = rendered(validation_view.content("drawdown", "light", NOW))
    assert "Keine auswertbaren Tage" in text and "Zu wenige Ereignisse" not in text
    assert "ROC-Kurve" in rendered(validation_view.content("vix", "light", NOW))  # VIX spikes need no S&P 500


def test_validation_frame_page_and_explanation(client, data):
    from fever.web import validation_view
    frame = validation_view.frame()
    components = {c.id: c for c in _walk_components(frame) if isinstance(getattr(c, "id", None), str)}
    radio = components["validation-event"]
    assert radio.persistence is True and [o["value"] for o in radio.options] == ["drawdown", "vix", "bear"]
    assert radio.options[0]["label"] == "Rückgang ab 10 % (Beginn in 63 Handelstagen)"
    assert client.get("/ansicht/validierung").status_code == 200
    page = rendered(views.kennzahl("validation", "light", NOW))
    assert "Block-Bootstrap mit Blöcken von 126 Handelstagen und 1.000 Ziehungen" in page
    assert "/kennzahl/validation" in rendered(views.explanations())
    assert texts.SOURCE_NAMES["validation"] == "Validierung (Berechnung im Worker)"


def test_lead_bins_cover_the_horizon():
    from fever.web.validation_view import lead_bins
    assert lead_bins(63) == [(1, 21), (22, 42), (43, 62), (63, 63)]  # the horizon alone: alarm on from the start
    assert lead_bins(21) == [(1, 7), (8, 14), (15, 20), (21, 21)]
    assert lead_bins(3) == [(1, 1), (2, 2), (3, 3)] and lead_bins(1) == [(1, 1)]


def test_the_overall_verdict_names_who_is_better():
    from fever.web.validation_view import overall
    assert overall(["same", "better", "same", "same"]).startswith("Ampel und Stress sind in mindestens einem Vergleich")
    assert overall(["worse", "same"]).startswith("Der VIX-Filter ist")
    assert overall(["better", "worse"]).startswith("Gemischt")
    assert overall(["same", "same"]).startswith("Kein belastbarer Unterschied")


def test_roc_and_bars_follow_the_standard():
    from fever.web.figures import Bars, Roc, bars, roc
    figure, config = roc(Roc("r", "ROC", "x", [("Stress (AUC 0,70)", [0, 0.5, 1], [0, 0.8, 1])]), "dark", today=date(2026, 9, 29))
    figure = validated(figure)
    assert config["showSendToCloud"] is False and config["toImageButtonOptions"]["filename"] == "r_29-09-2026"
    assert figure.layout.xaxis.range == (0, 1) and figure.data[0].name == "Zufall" and figure.layout.meta is None
    assert figure.data[0].showlegend is False and figure.layout.annotations[0].text == "Zufall"  # named in the plot
    assert figure.layout.title.yref == "container" and figure.layout.annotations[-1].yshift == -72  # below the axis title
    figure, _ = bars(Bars("b", "Vorlauf", "x", ["1–7", "verpasst"], [("Rot", [3, 1]), ("Gelb", [5, 0])], "Tage", "Ereignisse",
                          legend_title="Ampel"), "light")
    figure = validated(figure)
    assert figure.layout.barmode == "group" and figure.layout.yaxis.dtick == 1 and figure.data[1].y == (5, 0)
    assert figure.layout.xaxis.tickangle == 0 and figure.layout.legend.title.text == "Ampel"
