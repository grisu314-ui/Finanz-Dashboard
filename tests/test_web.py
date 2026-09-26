"""Web interface (M6): smoke test, local resources only, chart standard, texts, formats."""

import json
from dataclasses import replace
import re
from datetime import date, datetime, timezone
from pathlib import Path

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
    pages = [views.overview("light", NOW), views.areas(), views.data_status(NOW), views.explanations()]
    pages += [views.kennzahl(k, "light", NOW) for k in texts.all_ids() if texts.has_text(k)]
    shown = set(re.findall(r"/kennzahl/([a-z0-9_]+)", rendered(pages)))
    assert shown and all(texts.has_text(k) for k in shown)


def test_generated_sections_come_from_the_configuration():
    lines = texts.thresholds("traffic_light")
    assert any(line.startswith("Rot: Stress mindestens 90") for line in lines)
    assert any("inaktiv" in line for line in lines)
    facts = dict(texts.steckbrief("vix_vix3m"))
    assert facts["Orientierung"] == "hoch = mehr Stress" and facts["Frequenz"] == "täglich"


def test_unknown_kennzahl_page(data):
    assert "nicht gefunden" in rendered(views.kennzahl("gibt_es_nicht", "light", NOW))


def test_data_status_marks_stale_series(data):
    page = rendered(views.data_status(NOW))
    assert "veraltet" in page and "aktuell" in page and "Cboe (Indizes)" in page


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
    figure, _ = time_series(chart, "light", today=date(2026, 9, 26))
    shapes = figure.layout.shapes
    assert [(s.x0, s.x1) for s in shapes] == [periods[0], periods[1]]  # 1990 lies before the data
    assert all(s.layer == "below" and s.yref == "paper" for s in shapes)
    assert figure.layout.annotations[0].text.endswith("Grau: US-Rezessionen nach NBER (über FRED)")
    plain, _ = time_series(replace(chart, recessions=()), "light")
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


def test_areas_frame_lists_the_four_areas_with_exactly_their_indicators():
    from fever.config import indicator_catalog
    frame = views.areas()
    toggles = [i for i in component_ids(frame) if isinstance(i, dict) and i["type"] == "area-toggle"]
    assert [t["area"] for t in toggles] == ["volatility", "credit", "macro", "vulnerability"]
    shown = []
    for section in (c for c in frame if getattr(c, "className", "") == "card card-wide area"):
        area = next(i["area"] for i in component_ids(section) if isinstance(i, dict) and i["type"] == "area-toggle")
        rows = [i["id"] for i in component_ids(section) if isinstance(i, dict) and i["type"] == "indicator-toggle"]
        assert rows == [k for k, ind in indicator_catalog().items() if ind.block == area], area
        shown += rows
    assert sorted(shown) == sorted(indicator_catalog())  # all 19, each once
    bodies = [c for c in _walk_components(frame) if isinstance(getattr(c, "id", None), dict) and c.id["type"].endswith("-body")]
    assert bodies and all(body.hidden is True for body in bodies)  # everything starts closed
    assert "Breite/Internals" in rendered(frame) and "Positionierung/Sentiment" in rendered(frame)


def _walk_components(node):
    if isinstance(node, (list, tuple)):
        for child in node:
            yield from _walk_components(child)
    elif hasattr(node, "to_plotly_json"):
        yield node
        yield from _walk_components(getattr(node, "children", None))


def test_areas_live_outside_the_refreshed_overview(client):
    """The 5-minute refresh replaces overview-content only, so open sections stay open."""
    from fever.web.pages import uebersicht
    page = uebersicht.layout()
    assert [c.id for c in page.children[1:]] == ["overview-content", "areas"]
    assert page.children[1].children is None
    dependencies = json.dumps(client.get("/_dash-dependencies").get_json())
    for output in ("area-chart", "indicator-body", "area-summary", "indicator-summary", "aria-expanded"):
        assert output in dependencies, output


def test_sections_build_charts_only_when_open():
    assert [views.is_open(n) for n in (None, 0, 1, 2, 3)] == [False, False, True, False, True]


def test_open_area_and_indicator_charts_carry_recession_bars(data):
    engine = make_engine(data)
    with engine.begin() as conn:
        months = [date(2026, m, 1) for m in range(1, 10)]  # the scores of the fixture cover September 2026
        append_observations(conn, "usrec", [NewObservation(d, 1.0 if d.month == 9 else 0.0, NOW, True) for d in months],
                            retrieved_at=NOW)
    for part in (views.area_chart("volatility", "light", NOW), views.indicator_detail("vix", "light", NOW)):
        graphs = [c for c in _walk_components(part) if type(c).__name__ == "Graph"]
        assert graphs and all(g.figure.layout.shapes for g in graphs)
    detail = rendered(views.indicator_detail("vix", "light", NOW))
    assert "So fließt der Wert in den Bereich ein" in detail and "Umrechnung: Niveau der Reihe." in detail


def test_summaries_follow_the_order_dash_asks_for(data):
    areas, indicators = views.summaries(["credit", "volatility"], ["vvix", "vix"], NOW)
    assert len(areas) == 2 and len(indicators) == 2
    assert "0 von 4 gültig" in rendered(areas[0]) and "Median" in rendered(areas[1])
    assert "noch kein veröffentlichter Wert" in rendered(indicators[0]) and "Stand 25.09.2026" in rendered(indicators[1])


def test_summaries_without_scores(migrated_dir, monkeypatch):
    monkeypatch.setenv("FEVER_DATA", str(migrated_dir))
    web_db.engine.cache_clear()
    areas, indicators = views.summaries(["macro"], ["nfci"], NOW)
    assert "Noch keine Scores berechnet." in rendered(areas + indicators)
    web_db.engine.cache_clear()


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
    for page in (views.overview("light", NOW), views.areas(), views.kennzahl("vix", "light", NOW),
                 views.kennzahl("stress", "light", NOW)):
        assert views.HISTORY_NOTE in rendered(page)


def test_area_charts_start_with_the_whole_history():
    """E-61: charts in the areas start with all years (all recessions visible); others with the last years."""
    days = [date(2000, 1, 3), date(2026, 9, 25)]
    chart = Chart("vix", "VIX", "Cboe", [Line("VIX", days, [20.0, 15.0])], "Punkte")
    assert time_series(chart, "light")[0].layout.xaxis.range[0] > date(2020, 1, 1)
    assert time_series(replace(chart, full_history=True), "light")[0].layout.xaxis.range[0] == date(2000, 1, 3)


def test_area_and_indicator_charts_use_the_whole_history(data, monkeypatch):
    charts = []
    real = views.ui.chart_card
    monkeypatch.setattr(views.ui, "chart_card", lambda graph_id, chart, theme: charts.append(chart) or real(graph_id, chart, theme))
    views.area_chart("volatility", "light", NOW)
    views.indicator_detail("vix", "light", NOW)
    assert len(charts) == 3 and all(chart.full_history for chart in charts)
    charts.clear()
    views.kennzahl("vix", "light", NOW)  # the Kennzahl page keeps the last years
    assert charts and not any(chart.full_history for chart in charts)
