"""View 8 of report 6.3: backtest and validation (M10, report 4.3 step 7, E-93).

Shows the report the worker stores (fever.validate); nothing is computed here beyond formatting and
the bins of the lead histogram. A look back: no probability for today, no trading signal, and
nothing here feeds back into the traffic light.
"""

import math
from datetime import date, datetime

from dash import dcc, html

from fever.config import validation_config
from fever.web import components as ui
from fever.web import db
from fever.web import format as fmt
from fever.web.figures import Bars, Roc, bars, roc

SOURCE = "eigene Berechnung (Validierung)"
EVENT_ORDER = ("drawdown", "vix", "bear")
LEVELS = (1, 2, 3)
SIGNAL_NAMES = {"stress": "Stress", "vulnerability": "Fallhöhe", "level": "Ampelstufe", "vix": "VIX-Perzentil"}
FILTER_NAMES = {
    "level1": "Ampel mindestens Gelb", "vix1": "VIX-Filter wie Gelb",
    "level2": "Ampel mindestens Orange", "vix2": "VIX-Filter wie Orange",
    "level3": "Ampel Rot", "vix3": "VIX-Filter wie Rot",
    "vix_elevated": "VIX-Perzentil über „erhöht“", "always": "Immer Alarm (Basisrate)",
}
LEAD_FILTERS = ("level1", "vix1", "level2", "vix2", "level3", "vix3")
VERDICTS = {"better": "besser", "same": "nicht unterscheidbar", "worse": "schlechter"}
LIMITS = [
    "Wenige Ereignisse: Die Intervalle sind breit, einzelne Krisen entscheiden viel.",
    "Überlappende Zeiträume: Benachbarte Tage haben fast dasselbe Ergebnis; deshalb Block-Bootstrap statt einfacher Intervalle.",
    "Nicht streng außerhalb der Stichprobe: Die Regeln des Berichts und die Entscheidungen vom 29.09.2026 (etwa die "
    "Sahm-Regel mit Trend, E-91) entstanden mit Kenntnis dieser Jahre.",
    "Phase 1: Je Beobachtung zählt der neueste Stand, und die Veröffentlichung der Rückfüllung ist geschätzt (E-14); "
    "revisionsgenau erst in Phase 2.",
    "Das Ereignis „VIX über …“ begünstigt den VIX-Filter: Er misst dieselbe Größe, die das Ereignis bestimmt.",
    "Rückgänge nach Lunde und Timmermann (2004): Nach einer Erholung um dieselbe Schwelle zählt jeder neue Rückgang als "
    "eigenes Ereignis, auch innerhalb eines Bärenmarkts.",
    "Nicht enthalten: Brier-Score (erst mit dem Logit-Modell, Phase 3) und der ökonomische Test mit Put-Absicherung "
    "(Optionsdaten, Phase 3).",
]


def _n(value: float) -> str:
    return fmt.number(value, 0) if float(value).is_integer() else fmt.number(value, 1)


def event_name(event: str, config: dict) -> str:
    """Short name of an event with its threshold from scoring.toml [validation], e.g. for chart titles."""
    if event == "drawdown":
        return f"Rückgang ab {_n(config['drawdown'])} %"
    if event == "vix":
        return f"VIX über {_n(config['vix_level'])}"
    return f"Bärenmarkt ab {_n(config['bear'])} %"


def event_label(event: str, config: dict) -> str:
    """Name of an event with its threshold and horizon."""
    if event == "vix":
        return f"{event_name(event, config)} (in {config['vix_horizon']} Handelstagen)"
    horizon = config["drawdown_horizon"] if event == "drawdown" else config["bear_horizon"]
    return f"{event_name(event, config)} (Beginn in {horizon} Handelstagen)"


def frame() -> list:
    """Static frame; a callback fills the content, so the choice of event survives the refresh."""
    config = vars(validation_config())
    options = [{"label": event_label(event, config), "value": event} for event in EVENT_ORDER]
    return [
        html.H1("Validierung"),
        html.P(["Rückblick: Wie gut kündigten Ampel, Stress und Fallhöhe frühere Einbrüche an, verglichen mit einem "
                "einfachen VIX-Filter? Nur Auswertung: keine Wahrscheinlichkeit für heute, kein Handelssignal, keine "
                "Rückwirkung auf die Ampel. Begriffe und Methode: ",
                dcc.Link("Erklärseite Validierung", href="/kennzahl/validation"), "."], className="lead"),
        dcc.RadioItems(id="validation-event", options=options, value="drawdown", inline=True, persistence=True,
                       persistence_type="session", className="switch"),
        html.Div(id="validation-content"),
    ]


@ui.guarded
def content(event: str | None, theme: str, now: datetime) -> list:
    stored = db.validation_report()
    if stored is None:
        return [ui.note("Noch keine Validierung berechnet. Der Worker rechnet sie nach dem nächsten Scoring-Lauf; "
                        "sofort mit python -m fever.validate (docs/einrichtung.md).")]
    report = stored.content
    event = event if event in report["events"] else EVENT_ORDER[0]
    result, config = report["events"][event], report["config"]
    latest = db.latest_composite()
    stale = latest is None or latest["computed_at"] != stored.score_computed_at
    parts = [_header(result, stored.computed_at, stale, now)]
    if not result["filters"] and not result["days"]:
        return parts + [ui.note(f"Keine auswertbaren Tage: Es fehlen Schlusskurse (S&P 500 von Cboe, VIX) oder Scores ab "
                                f"{config['walk_forward_start']}. Nach dem nächsten Abruf rechnet der Worker die Validierung neu.")]
    if not result["filters"]:
        return parts + [ui.note("Zu wenige Ereignisse im Auswertungszeitraum: keine Kennzahlen.")]
    filters = {entry["id"]: entry for entry in result["filters"]}
    observed = date.fromisoformat(result["last"])
    names = (event_name(event, config), event_label(event, config))
    return parts + [
        _summary(result, filters),
        _roc_card(result, names, observed, stored.computed_at, theme),
        _table(result, filters),
        _leads(event, result, filters, names, observed, stored.computed_at, theme),
        _false_alarms(filters),
        _stability(result, report["thresholds"]),
        html.Section(className="card card-wide", children=[html.H2("Grenzen"), html.Ul([html.Li(t) for t in LIMITS])]),
    ]


def _header(result: dict, computed_at: datetime, stale: bool, now: datetime) -> html.Section:
    first, last = (date.fromisoformat(result[key]) if result[key] else None for key in ("first", "last"))
    facts = (f"Auswertung {fmt.day(first)} bis {fmt.day(last)}: {fmt.number(result['days'], 0)} Handelstage, das Ereignis "
             f"folgte auf {_percent(result['base_rate'])} davon. {len(result['occurrences'])} Ereignisse seit Beginn der Kurse")
    if result["filters"]:
        facts += f", davon {result['filters'][0]['events']} mit ganzem Vorlauf ab Beginn der Auswertung"
    facts += "."
    children = [html.P(facts, className="detail"),
                ui.freshness(last, computed_at, stale=stale, now=now, retrieved_label="berechnet")]
    if stale:
        children.append(ui.note("Beruht auf älteren Scores; der Worker rechnet die Validierung nach dem Scoring neu."))
    return html.Section(className="card card-wide", children=children)


def _summary(result: dict, filters: dict) -> html.Section:
    auc, difference = result["auc"], result["auc_difference"]
    lines = [f"Stress gegen VIX-Perzentil (AUC, 0,5 = Zufall): {_auc(auc['stress'])} gegen {_auc(auc['vix'])}; "
             f"Unterschied {_signed(difference, 2)}: {VERDICTS[difference['verdict']]}."]
    verdicts = [difference["verdict"]]
    for k in LEVELS:
        level, vix = filters[f"level{k}"], filters[f"vix{k}"]
        gap = level["precision_difference"]
        verdicts.append(gap["verdict"])
        lines.append(f"{FILTER_NAMES[f'level{k}']}: Precision {_percent(level['precision']['value'])} gegen "
                     f"{_percent(vix['precision']['value'])} beim VIX-Filter mit gleichem Alarmanteil; Unterschied "
                     f"{_signed(gap, 0, scale=100, unit=' Prozentpunkte')}: {VERDICTS[gap['verdict']]}.")
    return html.Section(className="card card-wide", children=[
        html.H2("Kurzfazit"), html.P(html.Strong(overall(verdicts))), html.Ul([html.Li(line) for line in lines]),
        ui.note("Bericht 4.3, Schritt 7: Schlägt der Composite den naiven VIX-Filter nicht, ist er Ballast. Intervalle: "
                "Block-Bootstrap; „belastbar“ heißt, das ganze Intervall des Unterschieds liegt auf einer Seite von null."),
    ])


def overall(verdicts: list[str]) -> str:
    """One sentence over the comparisons with the VIX filter (AUC of stress, precision of each level)."""
    if "better" in verdicts and "worse" not in verdicts:
        return "Ampel und Stress sind in mindestens einem Vergleich belastbar besser als der VIX-Filter, in keinem schlechter."
    if "worse" in verdicts and "better" not in verdicts:
        return "Der VIX-Filter ist in mindestens einem Vergleich belastbar besser, Ampel und Stress in keinem."
    if "worse" in verdicts:
        return "Gemischt: In einem Vergleich sind Ampel oder Stress belastbar besser, in einem anderen der VIX-Filter."
    return "Kein belastbarer Unterschied zwischen Ampel bzw. Stress und dem VIX-Filter."


def _roc_card(result, names, observed, computed_at, theme) -> html.Section:
    name, label = names
    aucs = " · ".join(f"{SIGNAL_NAMES[signal]} {_auc(result['auc'][signal], interval=False)}" for signal in SIGNAL_NAMES)
    curves = [(SIGNAL_NAMES[signal], *result["roc"][signal]) for signal in SIGNAL_NAMES]
    chart = Roc("validation-roc", f"ROC-Kurve: {name}", SOURCE, curves, observed=observed, retrieved=computed_at,
                note=f"{label}<br>AUC: {aucs}")
    rows = [html.Tr([html.Td(SIGNAL_NAMES[signal]), html.Td(_auc(result["auc"][signal]))]) for signal in SIGNAL_NAMES]
    return html.Section(className="card card-wide", children=[
        html.H2("Trennschärfe"),
        ui.note("Trefferquote: Anteil der Tage vor einem Ereignis mit Alarm; Fehlalarmrate: Anteil der übrigen Tage mit "
                "Alarm. Jeder Punkt einer Kurve ist eine andere Alarmschwelle. Je höher die Kurve über der Diagonale "
                "(Zufall), desto besser trennt das Signal die Tage vor einem Ereignis von den übrigen."),
        ui.figure_card("validation-roc", *roc(chart, theme), box="chart-box chart-box-tall"),  # room for the curves
        html.Div(className="table-scroll", children=html.Table(className="table", children=[
            html.Thead(html.Tr([html.Th("Signal"), html.Th("AUC (Intervall)")])), html.Tbody(rows)])),
        ui.note("AUC: Fläche unter der Kurve, zugleich die Wahrscheinlichkeit, dass ein Tag vor einem Ereignis einen "
                "höheren Wert zeigt als ein Tag ohne; 0,5 = Zufall, 1 = perfekte Trennung."),
    ])


def _table(result: dict, filters: dict) -> html.Section:
    rows = []
    for name in (*LEAD_FILTERS, "vix_elevated", "always"):
        entry = filters[name]
        rows.append(html.Tr([
            html.Td(FILTER_NAMES[name]), html.Td(_percent(entry["share"])), html.Td(_with_interval(entry["precision"])),
            html.Td(_with_interval(entry["recall"])), html.Td(f"{entry['warned']} von {entry['events']}"),
            html.Td(fmt.DASH if entry["lead_median"] is None else f"{fmt.number(entry['lead_median'], 0)} Tage"),
            html.Td(fmt.number(entry["false_per_year"], 1)),
        ]))
    return html.Section(className="card card-wide", children=[
        html.H2("Treffer und Fehlalarme"),
        ui.note("Precision: Anteil der Alarmtage, auf die das Ereignis folgte. Recall: Anteil der Tage vor einem Ereignis mit "
                "Alarm. Der VIX-Filter „wie Gelb“ gibt so oft Alarm, wie die Ampel in den Jahren davor mindestens Gelb "
                "zeigte (jedes Jahr neu, nur mit Daten davor); der Alarmanteil ist deshalb nur ungefähr gleich (Spalte "
                f"„Alarm an“). Vorlauf: vom ersten Alarm in den {result['horizon']} "
                f"Handelstagen vor dem Beginn bis zum Beginn, also höchstens {result['horizon']} Tage."),
        html.Div(className="table-scroll", children=html.Table(className="table", children=[
            html.Thead(html.Tr([html.Th(t) for t in ("Signal", "Alarm an", "Precision", "Recall", "Ereignisse gewarnt",
                                                      "Vorlauf (Median)", "Fehlalarme je Jahr")])),
            html.Tbody(rows),
        ])),
    ])


LEAD_BINS = 3  # with "verpasst" and the horizon five categories: they fit unturned on a phone


def lead_bins(horizon: int) -> list[tuple[int, int]]:
    """LEAD_BINS equal bins of lead days from 1 to horizon - 1, then the horizon alone: the alarm was on
    already on the first day of the lead window (or earlier)."""
    width = max(1, math.ceil((horizon - 1) / LEAD_BINS))
    return [(low, min(low + width - 1, horizon - 1)) for low in range(1, horizon, width)] + [(horizon, horizon)]


def _bin_label(low: int, high: int, horizon: int) -> str:
    if low == horizon:
        return f"≥ {horizon}"
    return f"{low}–{high}" if low != high else f"{low}"


def _leads(event, result, filters, names, observed, computed_at, theme) -> html.Section:
    name, label = names
    horizon = result["horizon"]
    bins = lead_bins(horizon)
    # "verpasst" first: from no warning to the longest lead (and the long label has room at the edge)
    categories = ["verpasst"] + [_bin_label(low, high, horizon) for low, high in bins]
    series = []
    for level, short in zip(("level1", "level2", "level3"), ("mind. Gelb", "mind. Orange", "Rot")):
        leads = filters[level]["leads"]
        counts = [sum(1 for v in leads if v is not None and low <= v <= high) for low, high in bins]
        series.append((short, [sum(1 for v in leads if v is None)] + counts))
    chart = Bars("validation-leads", f"Vorlauf: {name}", SOURCE, categories, series, "Vorlauf in Handelstagen",
                 "Ereignisse", observed=observed, retrieved=computed_at, legend_title="Ampel",
                 note=f"{label}<br>≥ {horizon}: Alarm schon am ersten Tag des Vorlaufs; nur Ereignisse mit ganzem Vorlauf")
    return html.Section(className="card card-wide", children=[
        html.H2("Vorlauf"),
        ui.note(f"Handelstage vom ersten Alarm der Ampel im Vorlauf bis zum Beginn des Ereignisses. „≥ {horizon}“: Der "
                "Alarm war schon am ersten Tag des Vorlaufs an, vielleicht auch länger. „verpasst“: kein Alarm im "
                "Vorlauf. Gezählt sind Ereignisse, deren ganzer Vorlauf ab Beginn der Auswertung liegt."),
        ui.figure_card("validation-leads", *bars(chart, theme)),
        html.Details([html.Summary("Ereignisse mit Vorlauf je Signal (Handelstage, – = verpasst)"),
                      _occurrence_table(event, result)]),
    ])


def _occurrence_cells(event: str, occurrence: dict) -> list[str]:
    day = lambda key: fmt.day(date.fromisoformat(occurrence[key]))  # noqa: E731
    if event == "vix":
        return [day("start"), day("end"), fmt.number(occurrence["max"], 1)]
    return [day("high"), day("low") + ("" if occurrence["ended"] else " (läuft)"), f"{fmt.number(occurrence['depth'], 1)} %"]


def _occurrence_table(event: str, result: dict) -> html.Div:
    head = ["Beginn", "Ende", "Höchster Schluss"] if event == "vix" else ["Hoch", "Tief", "Rückgang"]
    rows = [html.Tr([html.Td(c) for c in _occurrence_cells(event, o)]
                    + [html.Td(fmt.DASH if o["leads"][name] is None else str(o["leads"][name])) for name in LEAD_FILTERS])
            for o in result["occurrences"] if "leads" in o]
    return html.Div(className="table-scroll", children=html.Table(className="table", children=[
        html.Thead(html.Tr([html.Th(t) for t in head] + [html.Th(FILTER_NAMES[name]) for name in LEAD_FILTERS])),
        html.Tbody(rows),
    ]))


def _false_alarms(filters: dict) -> html.Section:
    details = []
    for name in LEAD_FILTERS:
        alarms = filters[name]["false_alarms"]
        items = [html.Li(f"{fmt.day(date.fromisoformat(first))} bis {fmt.day(date.fromisoformat(last))}") for first, last in alarms]
        details.append(html.Details([html.Summary(f"{FILTER_NAMES[name]}: {len(alarms)} Fehlalarme"),
                                     html.Ul(items) if items else ui.note("Keine.")]))
    return html.Section(className="card card-wide", children=[
        html.H2("Fehlalarme"),
        ui.note("Alarmphasen ohne Ereignis im Horizont; Alarmtage mit wenigen Tagen Abstand zählen als eine Phase "
                "(Abstand auf der Erklärseite)."),
        *details,
    ])


def _stability(result: dict, thresholds: dict) -> html.Section:
    rows = [html.Tr([html.Td(f"{p['from']}–{p['to']}"), html.Td(fmt.number(p["days"], 0)), html.Td(str(p["events"])),
                     html.Td(_auc({"value": p["auc_stress"]}, interval=False)), html.Td(_auc({"value": p["auc_vix"]}, interval=False))])
            for p in result["periods"]]
    years = [html.Tr([html.Td(year)] + [html.Td("nie" if by_level[str(k)] is None else fmt.number(by_level[str(k)], 1))
                                        for k in LEVELS])
             for year, by_level in sorted(thresholds.items())]
    return html.Section(className="card card-wide", children=[
        html.H2("Stabilität über die Zeit"),
        ui.note("AUC je Zeitraum, nur wenn darin ein Ereignis beginnt; die Jahre vor der Auswertung ab dem ersten "
                "VIX-Perzentil. Gewichte gibt es nicht zu prüfen: Die Blöcke zählen gleich, geschätzt wird nichts."),
        html.Div(className="table-scroll", children=html.Table(className="table", children=[
            html.Thead(html.Tr([html.Th(t) for t in ("Zeitraum", "Handelstage", "Ereignisse", "AUC Stress", "AUC VIX-Perzentil")])),
            html.Tbody(rows),
        ])),
        html.Details([html.Summary("Schwellen des VIX-Filters je Jahr (VIX-Perzentil, walk-forward)"),
                      html.Div(className="table-scroll", children=html.Table(className="table", children=[
                          html.Thead(html.Tr([html.Th(t) for t in ("Jahr", "wie Gelb", "wie Orange", "wie Rot")])),
                          html.Tbody(years),
                      ]))]),
    ])


def _percent(value: float | None) -> str:
    return fmt.DASH if value is None else f"{fmt.number(100 * value, 0)} %"


def _auc(entry: dict, *, interval: bool = True) -> str:
    if entry.get("value") is None:
        return fmt.DASH
    text = fmt.number(entry["value"], 2)
    if interval and entry.get("low") is not None:
        text += f" ({fmt.number(entry['low'], 2)}–{fmt.number(entry['high'], 2)})"
    return text


def _with_interval(entry: dict) -> str:
    if entry["value"] is None:
        return fmt.DASH
    if entry["low"] is None:
        return _percent(entry["value"])
    return f"{_percent(entry['value'])} ({fmt.number(100 * entry['low'], 0)}–{fmt.number(100 * entry['high'], 0)} %)"


def _signed(entry: dict, decimals: int, scale: float = 1.0, unit: str = "") -> str:
    """'+6 Prozentpunkte (Intervall +3 bis +12)' with the sign always shown."""
    def signed(value):
        text = fmt.number(abs(scale * value), decimals)
        return ("+" if value >= 0 else "−") + text

    if entry["value"] is None:
        return fmt.DASH
    if entry["low"] is None:
        return signed(entry["value"]) + unit
    return f"{signed(entry['value'])}{unit} (Intervall {signed(entry['low'])} bis {signed(entry['high'])})"
