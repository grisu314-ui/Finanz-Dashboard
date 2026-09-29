"""Kennzahl texts (fever/web/texts/<id>.md, docs/leitfaden-erklaertexte.md) and generated sections.

A Kennzahl is every displayed quantity: the indicators of series.toml, the scores and the
concept pages. Without a text file it is never shown (enforced here and by a test). The
"Steckbrief" and "Schwellen und Farben" come from series.toml and scoring.toml, so text and
calculation cannot drift apart; thresholds never appear in the hand-written text.
"""

import re
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from fever.config import (
    FREQUENCY_DAYS, RULE_ONLY, STRESS_BLOCKS, VULNERABILITY, Indicator, indicator_catalog, scoring_config, series_catalog,
)
from fever.scoring.composite import (
    CREDIT_CHANGE_INDICATOR, RULE_INDICATORS, SAHM_INDICATOR, SOS_INDICATOR, VIX_RATIO_INDICATOR,
)

TEXT_DIR = Path(__file__).resolve().parent / "texts"
HEADINGS = (
    "Kurzinfo",
    "Was die Kennzahl misst",
    "Warum sie für Marktstress oder Fallhöhe zählt",
    "So liest du sie",
    "Grenzen und Fallstricke",
    "Quellen",
)
MAX_SHORT = 200
_HTML = re.compile(r"<\s*[a-zA-Z!/]")
_THRESHOLD = re.compile(r"\b\d{1,3}\s*\.\s*Perzentil|\b\d{1,3}\s*Perzentilpunkte")

GROUPS = {
    "volatility": "Volatilität/Optionen",
    "credit": "Kredit/Funding",
    "macro": "Makro/Finanzierungsbedingungen",
    "breadth": "Breite/Internals",
    "positioning": "Positionierung/Sentiment",
    VULNERABILITY: "Fallhöhe",
    RULE_ONLY: "Nur Ampelregel (kein Perzentil im Score)",
    "scores": "Gesamtbild",
    "display": "Nur Anzeige (kein Score)",
    "concepts": "Begriffe",
}
SCORES = ("traffic_light", "stress", "vulnerability", "confidence", "diffusion") + tuple(f"block_{b}" for b in STRESS_BLOCKS)
CONCEPTS = ("percentile", "staleness", "recessions")
# Display-only Kennzahlen of the views (M7, E-49): raw series shown as they are, never in a score.
DISPLAYS = {
    "vix_term": ("vix9d", "vix", "vix3m", "vix6m", *(f"cfe_vx{n}" for n in range(1, 9))),
    "skew": ("skew",),
    "ccc_bb": ("bamlh0a3hyc", "bamlh0a1hybb"),
    "anfci": ("anfci",),
    "ofr_fsi": ("ofr_fsi", "ofr_fsi_credit", "ofr_fsi_equity_valuation", "ofr_fsi_funding", "ofr_fsi_safe_assets",
                "ofr_fsi_volatility", "ofr_fsi_united_states", "ofr_fsi_other_advanced", "ofr_fsi_emerging_markets"),
    "yield_curve": ("t10y3m", "t10y2y"),
    "cape": ("shiller_cape",),
    "money_market": ("mmmffaq027s", "ncbeilq027s", "fbcellq027s"),  # E-86
}
# Areas with their indicators (E-57), in the order of view 7: the stress blocks with indicators in phase 1,
# then the vulnerability; each with the Kennzahl that heads it. Positioning has none until phase 2.
AREAS = {"volatility": "block_volatility", "credit": "block_credit", "macro": "block_macro", "breadth": "block_breadth",
         VULNERABILITY: VULNERABILITY}
# Role marks next to a Kennzahl's name (E-81): blue "Stress · <area>", violet "Fallhöhe", grey
# "nur Anzeige", neutral "Ampelregel" for the indicators a traffic light rule reads.
AREA_SHORT = {"volatility": "Volatilität", "credit": "Kredit", "macro": "Makro", "breadth": "Breite",
              "positioning": "Positionierung"}
FREQUENCY_NAMES = {"daily": "täglich", "weekly": "wöchentlich", "monthly": "monatlich", "quarterly": "quartalsweise"}
LEVEL_NAMES = ("Grün", "Gelb", "Orange", "Rot")


class TextError(ValueError):
    """A text file is missing or breaks the rules of the guideline."""


@dataclass(frozen=True)
class Text:
    id: str
    title: str
    short: str
    sections: tuple[tuple[str, str], ...]  # (heading, markdown) after the short info


def parse(kennzahl_id: str, content: str) -> Text:
    lines = content.strip().splitlines()
    if not lines or not lines[0].startswith("# "):
        raise TextError(f"{kennzahl_id}.md: erste Zeile muss '# <Anzeigename>' sein")
    if _HTML.search(content):
        raise TextError(f"{kennzahl_id}.md: enthält HTML")
    title = lines[0][2:].strip()
    sections: list[tuple[str, list[str]]] = []
    for line in lines[1:]:
        if line.startswith("## "):
            sections.append((line[3:].strip(), []))
        elif line.startswith("# "):
            raise TextError(f"{kennzahl_id}.md: nur eine Überschrift erster Ebene erlaubt")
        elif sections:
            sections[-1][1].append(line)
        elif line.strip():
            raise TextError(f"{kennzahl_id}.md: Text vor der ersten Überschrift '## Kurzinfo'")
    headings = tuple(heading for heading, _ in sections)
    if headings != HEADINGS:
        raise TextError(f"{kennzahl_id}.md: Überschriften {list(headings)}, erwartet {list(HEADINGS)}")
    bodies = {heading: "\n".join(body).strip() for heading, body in sections}
    short = " ".join(bodies["Kurzinfo"].split())
    if not short or len(short) > MAX_SHORT:
        raise TextError(f"{kennzahl_id}.md: Kurzinfo muss 1 bis {MAX_SHORT} Zeichen haben ({len(short)})")
    for heading, body in bodies.items():
        if not body:
            raise TextError(f"{kennzahl_id}.md: Abschnitt '{heading}' ist leer")
        if _THRESHOLD.search(body):
            raise TextError(f"{kennzahl_id}.md: Schwellenzahl im Freitext ('{heading}'); sie gehört in scoring.toml")
    return Text(kennzahl_id, title, short, tuple((h, bodies[h]) for h in HEADINGS[1:]))


@cache
def text(kennzahl_id: str) -> Text:
    path = TEXT_DIR / f"{kennzahl_id}.md"
    if not path.is_file():
        raise TextError(f"Text fehlt: {path.name} (docs/leitfaden-erklaertexte.md)")
    return parse(kennzahl_id, path.read_text(encoding="utf-8"))


def has_text(kennzahl_id: str) -> bool:
    return (TEXT_DIR / f"{kennzahl_id}.md").is_file()


def all_ids() -> list[str]:
    return [*SCORES, *indicator_catalog(), *DISPLAYS, *CONCEPTS]


def group_of(kennzahl_id: str) -> str:
    if kennzahl_id in SCORES:
        return "scores"
    if kennzahl_id in CONCEPTS:
        return "concepts"
    if kennzahl_id in DISPLAYS:
        return "display"
    return indicator_catalog()[kennzahl_id].block


def roles(kennzahl_id: str) -> list[tuple[str, str]]:
    """Role marks as (text, kind), kind "stress", "vulnerability", "rule" or "display"; none for scores.

    An indicator carries the roles of every indicator with the same value (same series and
    transformation): the Baa spread level counts as stress and, reversed, as vulnerability (E-85).
    """
    if kennzahl_id in DISPLAYS:
        return [("nur Anzeige", "display")]
    catalog = indicator_catalog()
    if kennzahl_id not in catalog:
        return []
    own = catalog[kennzahl_id]
    same = [i for i in catalog.values() if (i.series, i.transform) == (own.series, own.transform)]
    marks = [(f"Stress · {AREA_SHORT[i.block]}", "stress") for i in same if i.block in STRESS_BLOCKS]
    marks += [("Fallhöhe", "vulnerability") for i in same if i.block == VULNERABILITY]
    marks += [("Ampelregel", "rule") for i in same if i.id in RULE_INDICATORS]
    return list(dict.fromkeys(marks))


# --- generated sections ----------------------------------------------------------------------------

_TRANSFORMS = {
    "level": lambda c: "Niveau der Reihe",
    "ratio": lambda c: "Verhältnis der ersten zur zweiten Reihe am selben Tag",
    "difference": lambda c: "Differenz der ersten minus der zweiten Reihe am selben Tag",
    "vrp": lambda c: f"VIX minus realisierte Volatilität des S&P 500 über {c.realized_vol_window} Handelstage (annualisiert, ohne Mittelwertabzug)",
    "stock_bond_corr": lambda c: f"Korrelation der täglichen S&P-500-Logrenditen mit der negativen Änderung der 10-jährigen Rendite über {c.correlation_window} Tage",
    "above_low": lambda c: f"Wert im Verhältnis zu seinem Minimum der letzten {c.low_window} Beobachtungen, minus 1",
    "fx_change": lambda c: f"Aufwertung des Yen gegenüber dem US-Dollar über {c.fx_change_window} EZB-Kurstage (negative Logveränderung von USD/JPY)",
    "fx_vol": lambda c: f"annualisierte Volatilität der täglichen Logveränderungen von USD/JPY über {c.fx_vol_window} EZB-Kurstage",
    "yoy": lambda c: "Veränderung gegenüber der Beobachtung ein Jahr zuvor",
    "cot_net_short": lambda c: "(Short − Long) der Non-Commercials geteilt durch das Open Interest",
    "change": lambda c: f"Veränderung des Werts über {c.change_window} Beobachtungen (Handelstage), in Einheiten der Reihe",
    "relative_change": lambda c: f"relative Stärke: Logveränderung des Verhältnisses der ersten zur zweiten Reihe über {c.relative_change_window} gemeinsame Handelstage",
    "sos": lambda c: f"Durchschnitt der letzten {c.sos_average_window} Wochenwerte minus dem niedrigsten dieser Durchschnitte in den {c.sos_low_window} Wochen davor, in Prozentpunkten",
    "equity_share": lambda c: "Marktwert aller Aktien (nichtfinanzielle und finanzielle Unternehmen) geteilt durch Aktien plus Schuldtitel und Kredite von Bundesregierung, Bundesstaaten und Gemeinden, Haushalten, nichtfinanziellen Unternehmen und Ausland, in Prozent",
}


def rule_line(indicator_id: str) -> str | None:
    """The traffic light rule an indicator feeds, from scoring.toml; None if it feeds none."""
    c = scoring_config()
    return {
        VIX_RATIO_INDICATOR: f"Eigene Ampelregel: Rot, wenn der Wert an {c.red_vix_ratio_days} Handelstagen in Folge über "
                             f"{_n(c.red_vix_ratio, 2)} liegt.",
        CREDIT_CHANGE_INDICATOR: f"Eigene Ampelregel: Rot, solange das Perzentil mindestens {_n(c.red_credit_change)} beträgt "
                                 f"(endet {_n(c.hysteresis)} Punkte darunter).",
        SAHM_INDICATOR: f"Eigene Ampelregel: mindestens Orange, solange der Wert mindestens {_n(c.orange_sahm, 2)} beträgt "
                        "(ohne Hysterese).",
        SOS_INDICATOR: f"Eigene Ampelregel: mindestens Gelb, solange der Wert über {_n(c.yellow_sos, 2)} liegt (ohne Hysterese).",
    }.get(indicator_id)


def steckbrief(kennzahl_id: str, history_from=None) -> list[tuple[str, str]]:
    """Facts from series.toml and scoring.toml; `history_from` is the first observation (database)."""
    config = scoring_config()
    if kennzahl_id == "recessions":
        series = series_catalog()["usrec"]
        return [("Reihe", f"{series.name} (fred: {series.source_id})"), ("Frequenz", FREQUENCY_NAMES[series.frequency]),
                ("Verwendung", "nur Anzeige als graue Flächen, in keinem Indikator und keinem Score"),
                ("Historie ab", "–" if history_from is None else f"{history_from:%d.%m.%Y}"),
                ("Lizenz", series.license or "–")]
    if kennzahl_id in CONCEPTS:
        return []
    if kennzahl_id in DISPLAYS:
        catalog = series_catalog()
        series = [catalog[s] for s in DISPLAYS[kennzahl_id]]
        licenses = sorted({s.license for s in series if s.license})
        return [("Reihen", ", ".join(f"{s.name} ({s.source}: {s.source_id})" for s in series)),
                ("Frequenz", ", ".join(sorted({FREQUENCY_NAMES[s.frequency] for s in series}))),
                ("Verwendung", "nur Anzeige in den Ansichten, in keinem Indikator und keinem Score"),
                ("Historie ab", "–" if history_from is None else f"{history_from:%d.%m.%Y}"),
                *([("Lizenz", "; ".join(licenses))] if licenses else [])]
    if kennzahl_id in SCORES:
        return _score_facts(kennzahl_id, config)
    indicator: Indicator = indicator_catalog()[kennzahl_id]
    stress_or_vulnerability = "Fallhöhe" if indicator.block == VULNERABILITY else "Stress"
    rule_only = indicator.block == RULE_ONLY
    licenses = sorted({series.license for series in indicator.series if series.license})
    facts = [
        ("Reihen", ", ".join(f"{s.name} ({s.source}: {s.source_id})" for s in indicator.series)),
        ("Frequenz", FREQUENCY_NAMES[indicator.frequency]),
        ("Veröffentlichung", f"{max(s.release_time for s in indicator.series):%H:%M} Uhr New York, Verzug {indicator.lag_days} Tage nach dem Beobachtungsdatum"),
        ("Toleranz", f"{indicator.tolerance_days} Tage: veraltet, wenn mehr als {FREQUENCY_DAYS[indicator.frequency] + indicator.tolerance_days} Tage seit der erwarteten Veröffentlichung vergangen sind"),
        ("Historie ab", "–" if history_from is None else f"{history_from:%d.%m.%Y}"),
        ("Orientierung", f"{'hoch' if indicator.orientation == 'high' else 'niedrig'} = mehr {stress_or_vulnerability}"),
        ("Block", GROUPS[indicator.block]),
        ("Transformation", _TRANSFORMS[indicator.transform](config)),
        ("Perzentil", f"Fenster {config.window_years} Jahre über die eigenen Beobachtungen, Mindesthistorie {config.min_history_years} Jahre"
                      + ("; nur zur Anzeige, die Regel liest den Wert" if rule_only else "")),
        ("Gewicht in der Konfidenz", "keins: zählt nur in seiner Ampelregel" if rule_only
         else f"{indicator.v_score} von 5 (Vorlauf-Bewertung, Bericht Tabelle 2)"),
    ]
    if indicator.display_window:
        facts.append(("Zusätzliches Perzentil", f"über {config.display_window_years} Jahre, nur zur Anzeige"))
    if licenses:
        facts.append(("Lizenz", "; ".join(licenses)))
    return facts


def contribution(indicator_id: str) -> list[str]:
    """How an indicator enters its area and the scores, step by step, from series.toml and scoring.toml (E-57)."""
    c = scoring_config()
    indicator = indicator_catalog()[indicator_id]
    vulnerability = indicator.block == VULNERABILITY
    more = "mehr Fallhöhe" if vulnerability else "mehr Stress"
    direction = f"hoch = {more}" if indicator.orientation == "high" else f"umgedreht, weil ein niedriger Wert {more} bedeutet"
    valid = (f"Gültig nur mit mindestens {c.min_history_years} Jahren Historie und solange der Wert nicht veraltet ist "
             f"(mehr als {FREQUENCY_DAYS[indicator.frequency] + indicator.tolerance_days} Tage nach der erwarteten "
             "Veröffentlichung); sonst zählt er nicht und wird nie durch einen Ersatzwert gefüllt.")
    if indicator.block == RULE_ONLY:
        return [
            f"Umrechnung: {_TRANSFORMS[indicator.transform](c)}.",
            f"Perzentil über die letzten {c.window_years} Jahre: nur zur Anzeige.",
            valid,
            "Geht in keinen Bereich ein, nicht in Stress, Fallhöhe, Konfidenz oder Diffusionsindex.",
            rule_line(indicator_id),
        ]
    lines = [
        f"Umrechnung: {_TRANSFORMS[indicator.transform](c)}.",
        f"Perzentil: Rang des Werts unter den eigenen Beobachtungen der letzten {c.window_years} Jahre; {direction}.",
        valid,
    ]
    if vulnerability:
        lines += [
            f"Fallhöhe: Mittel der Perzentile der gültigen Komponenten, mindestens {c.min_vulnerability}; danach "
            f"geglättet (Halbwertszeit {_n(c.vulnerability_half_life)} Handelstage).",
            "Die Fallhöhe geht nicht in den Stress ein; beide wirken nur über die Ampelregeln zusammen.",
        ]
    else:
        lines.append(f"Bereich {GROUPS[indicator.block]}: Median der Perzentile aller gültigen Indikatoren des Bereichs; "
                     "ohne gültigen Indikator fehlt der Bereich.")
        if indicator.block == c.fast_block:
            lines.append(f"Der Bereich wird geglättet (Halbwertszeit {_n(c.fast_block_half_life)} Handelstage), "
                         "bevor er in den Stress eingeht.")
        lines += [
            f"Stress: Mittel der vorhandenen Bereiche, mindestens {c.min_blocks} von {len(STRESS_BLOCKS)}, danach "
            f"geglättet (Halbwertszeit {_n(c.stress_half_life)} Handelstage).",
            f"Diffusionsindex: Der Indikator zählt mit, wenn sein Perzentil über {_n(c.yellow_diffusion_percentile)} liegt.",
        ]
    if rule_line(indicator_id):
        lines.append(rule_line(indicator_id))
    for twin in indicator_catalog().values():  # the same value in another role (E-85)
        if twin.id != indicator_id and (twin.series, twin.transform) == (indicator.series, indicator.transform):
            role = "Fallhöhe" if twin.block == VULNERABILITY else "Stress"
            lines.append(f"Derselbe Wert zählt zusätzlich im Bereich {GROUPS[twin.block]} als „{twin.name}“ "
                         f"({'hoch' if twin.orientation == 'high' else 'niedrig'} = mehr {role}).")
    lines.append(f"Konfidenz: Gewicht {indicator.v_score} von 5 (Vorlauf laut Bericht, Tabelle 2), solange der Wert gültig ist.")
    if indicator.display_window:
        lines.append(f"Zusätzliches Perzentil über {c.display_window_years} Jahre: nur zur Anzeige, nicht im Score.")
    return lines


def _score_facts(kennzahl_id: str, c) -> list[tuple[str, str]]:
    if kennzahl_id == "stress":
        return [
            ("Berechnung", f"Mittel der vorhandenen Stressblöcke, mindestens {c.min_blocks} von {len(STRESS_BLOCKS)}; der Block {GROUPS[c.fast_block]} geht geglättet ein (Halbwertszeit {_n(c.fast_block_half_life)} Handelstage)"),
            ("Glättung", f"exponentiell, Halbwertszeit {_n(c.stress_half_life)} Handelstage"),
            ("Skala", "0 bis 100, hoch = mehr Stress"),
        ]
    if kennzahl_id == "vulnerability":
        return [
            ("Berechnung", f"Mittel der gültigen Fallhöhe-Komponenten, mindestens {c.min_vulnerability}"),
            ("Glättung", f"exponentiell, Halbwertszeit {_n(c.vulnerability_half_life)} Handelstage"),
            ("Skala", "0 bis 100, hoch = mehr Fallhöhe"),
        ]
    if kennzahl_id == "confidence":
        return [("Berechnung", "Summe der Vorlauf-Gewichte (1 bis 5) der aktuellen, gültigen Indikatoren geteilt durch die Summe aller Gewichte, in Prozent")]
    if kennzahl_id == "diffusion":
        return [("Berechnung", f"Anteil der gültigen Stress-Indikatoren mit Perzentil über {_n(c.yellow_diffusion_percentile)}, in Prozent")]
    if kennzahl_id == "traffic_light":
        return [("Stufen", ", ".join(LEVEL_NAMES)),
                ("Berechnung", "Regeln auf dem geglätteten Stress, der Fallhöhe, dem Diffusionsindex, VIX/VIX3M, dem Anstieg des "
                               "Kreditspreads Baa, der Sahm-Regel und dem SOS-Indikator; es gilt die höchste zutreffende Stufe")]
    block = kennzahl_id.removeprefix("block_")
    facts = [("Berechnung", "Median der Perzentile der gültigen Indikatoren im Block; ohne gültigen Indikator fehlt der Block")]
    if block == c.fast_block:
        facts.append(("Glättung", f"vor dem Composite exponentiell, Halbwertszeit {_n(c.fast_block_half_life)} Handelstage"))
    return facts


def thresholds(kennzahl_id: str) -> list[str]:
    """Section "Schwellen und Farben", generated from scoring.toml."""
    c = scoring_config()
    h = _n(c.hysteresis)
    hysteresis = f"Hysterese: Eine Regel endet erst {h} Punkte unter ihrer Schwelle."
    red = (f"Rot: Stress mindestens {_n(c.red_stress)}, oder VIX/VIX3M über {_n(c.red_vix_ratio, 2)} an {c.red_vix_ratio_days} "
           f"Handelstagen in Folge (endet nach {c.red_vix_ratio_days} Tagen in Folge darunter), oder der Anstieg des Kreditspreads Baa "
           f"über {c.change_window} Handelstage im Perzentil mindestens {_n(c.red_credit_change)}.")
    orange = (f"Orange: Stress mindestens {_n(c.orange_stress)}, oder Stress mindestens {_n(c.orange_stress_with_vulnerability)} "
              f"zusammen mit Fallhöhe mindestens {_n(c.orange_vulnerability)}, oder die Sahm-Regel mindestens "
              f"{_n(c.orange_sahm, 2)} (ohne Hysterese).")
    yellow = (f"Gelb: Fallhöhe mindestens {_n(c.yellow_vulnerability)}, oder mindestens {_n(c.yellow_diffusion_share)} % der "
              f"gültigen Stress-Indikatoren über Perzentil {_n(c.yellow_diffusion_percentile)}, oder der SOS-Indikator über "
              f"{_n(c.yellow_sos, 2)} (ohne Hysterese).")
    colors = "Farben: Die Ampelfarben stehen nur für die Gesamtampel und immer mit ihrem Namen."
    if kennzahl_id == "traffic_light":
        return [red, orange, yellow, "Grün: keine Regel trifft zu.", hysteresis, colors]
    if kennzahl_id == "stress":
        return [red, orange, hysteresis]
    if kennzahl_id == "vulnerability":
        return [orange, yellow, hysteresis]
    if kennzahl_id == "diffusion":
        return [yellow, hysteresis]
    if kennzahl_id == "confidence":
        return ["Keine Schwelle; eine niedrige Konfidenz heißt, dass die Ampel auf dünner Datenbasis steht."]
    if kennzahl_id == "percentile":
        return [f"Fenster {c.window_years} Jahre, Mindesthistorie {c.min_history_years} Jahre.", f"Markierung „erhöht“ über Perzentil {_n(c.yellow_diffusion_percentile)}."]
    if kennzahl_id == "recessions":
        return ["Keine Schwelle; die Flächen sind reine Anzeige und gehen in keinen Score ein."]
    if kennzahl_id == "yield_curve":
        return ["Farbige Fläche: 10 Jahre minus 3 Monate unter null (Inversion); keine Schwelle, kein Score."]
    if kennzahl_id in DISPLAYS:
        return ["Keine Schwelle und keine Farbe: reine Anzeige, geht in keinen Score ein."]
    if kennzahl_id == "staleness":
        return [f"{FREQUENCY_NAMES[f]}: veraltet nach mehr als {FREQUENCY_DAYS[f]} Tagen plus Toleranz der Reihe seit der erwarteten Veröffentlichung." for f in FREQUENCY_DAYS]
    if kennzahl_id.startswith("block_"):
        return ["Keine eigene Schwelle; der Block geht mit gleichem Gewicht in den Stress ein."]
    indicator = indicator_catalog()[kennzahl_id]
    if indicator.block == RULE_ONLY:
        return [rule_line(kennzahl_id), "Das Perzentil ist nur Anzeige (Farbskala Blau, dunkler = höher); keine weitere Schwelle."]
    lines = [f"Markierung „erhöht“: Perzentil über {_n(c.yellow_diffusion_percentile)} (Farbskala Blau, dunkler = höher; keine eigene Ampel je Kennzahl)."]
    if indicator.block == VULNERABILITY:
        lines.append("Geht als Komponente in die Fallhöhe ein.")
    else:
        lines.append(f"Zählt im Diffusionsindex: {yellow}")
    if rule_line(kennzahl_id):
        lines.append(rule_line(kennzahl_id))
    return lines


def _n(value: float, decimals: int = 0) -> str:
    text = f"{value:.{decimals}f}"
    return text.replace(".", ",")


def rule_text(rule: str) -> str:
    """Why the traffic light shows its level: one line per active rule, numbers from scoring.toml."""
    c = scoring_config()
    return {
        "red_stress": f"Rot: Stress mindestens {_n(c.red_stress)}",
        "red_vix_ratio": f"Rot: VIX/VIX3M über {_n(c.red_vix_ratio, 2)} an {c.red_vix_ratio_days} Handelstagen in Folge",
        "red_credit_change": f"Rot: Anstieg des Kreditspreads Baa über {c.change_window} Handelstage im Perzentil mindestens {_n(c.red_credit_change)}",
        "orange_stress": f"Orange: Stress mindestens {_n(c.orange_stress)}",
        "orange_stress_vulnerability": f"Orange: Stress mindestens {_n(c.orange_stress_with_vulnerability)} und Fallhöhe mindestens {_n(c.orange_vulnerability)}",
        "orange_sahm": f"Orange: Sahm-Regel mindestens {_n(c.orange_sahm, 2)}",
        "yellow_sos": f"Gelb: SOS-Indikator über {_n(c.yellow_sos, 2)}",
        "yellow_vulnerability": f"Gelb: Fallhöhe mindestens {_n(c.yellow_vulnerability)}",
        "yellow_diffusion": f"Gelb: mindestens {_n(c.yellow_diffusion_share)} % der Stress-Indikatoren über Perzentil {_n(c.yellow_diffusion_percentile)}",
    }.get(rule, rule)
