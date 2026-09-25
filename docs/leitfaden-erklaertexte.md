# Leitfaden für Kennzahl-Texte

Stand: 25.09.2026 · Gilt für `fever/web/texts/<id>.md` (Meilenstein M8, siehe `docs/umsetzungsplan.md`).

Jede Kennzahl im Dashboard hat genau eine Textdatei. Daraus entstehen zwei Dinge:
- die **Kurzinfo**, die beim Überfahren oder Antippen des Info-Symbols erscheint,
- die **Erklärseite** `/kennzahl/<id>`, auf die der Name der Kennzahl verlinkt.

`<id>` ist der Bezeichner der Kennzahl in `config/series.toml` bzw. für Scores ein fester Bezeichner: `stress`, `vulnerability`, `traffic_light`, `confidence`, `diffusion`, `block_<name>`. Für die Konzeptseiten gelten `percentile` und `staleness`.

## Was du schreibst und was erzeugt wird

| Teil der Erklärseite | Herkunft |
|---|---|
| Name, Kurzinfo, Was/Warum/Lesen/Grenzen, Quellen | **handgeschrieben** in `<id>.md` |
| Aktueller Stand (Wert, Datum, Abrufzeit, Perzentil, Status) | erzeugt aus der Datenbank |
| Verlauf mit Perzentilbändern | erzeugt |
| Steckbrief (Quelle, Serien-ID, Frequenz, Verzug, Toleranz, Historie ab, Orientierung, Block, Transformation, Mindesthistorie, Lizenz) | erzeugt aus `series.toml` |
| Schwellen und Farben | erzeugt aus `scoring.toml` |

So können Text und Rechnung nicht auseinanderlaufen: Ändert sich eine Schwelle in `scoring.toml`, ändert sich die Erklärung automatisch mit.

## Aufbau (Pflichtüberschriften in dieser Reihenfolge; ein Test prüft sie)

```markdown
# <Anzeigename>

## Kurzinfo
<1–2 Sätze, höchstens 200 Zeichen>

## Was die Kennzahl misst

## Warum sie für Marktstress oder Fallhöhe zählt

## So liest du sie

## Grenzen und Fallstricke

## Quellen
```

## Regeln

1. **Kurzinfo:** Sie sagt, was die Kennzahl repräsentiert und in welche Richtung „hoch“ zeigt, z. B. „hoch = mehr Stress“. Keine Abkürzung ohne Auflösung, höchstens 200 Zeichen.
2. **Belegpflicht:** Jede Tatsachenbehauptung (Wirkmechanismus, Evidenz, Vorlauf, Historie) nennt ihre Quelle: den Berichtsabschnitt (`docs/recherche.md`, Abschn. 1–3, 4.3, 6.1) oder eine Primärquelle mit Abrufdatum. Eigene Einschätzungen beginnen mit „Einschätzung:“, Unbestätigtes wird als unbestätigt markiert.
3. **Keine Momentaufnahmen:** keine Werte aus Abschnitt 5 des Berichts, keine aktuellen Kurse oder Stände. Das Aktuelle liefert die App.
4. **Keine Schwellenzahlen im Freitext:** Perzentilgrenzen, Ampelregeln und Hysterese stehen im erzeugten Abschnitt. Konventionelle Schwellen aus der Literatur (etwa die 0,5-Prozentpunkte-Grenze der Sahm-Regel) sind erlaubt, aber nur mit Quelle und dem Satz, dass sie nicht in den Score eingehen.
5. **Keine Handelssignale, keine Renditeprognosen, keine Crash-Wahrscheinlichkeit** (`CLAUDE.md`, „Was ausdrücklich NICHT gebaut wird“).
6. **Sprache:** Deutsch mit Dezimalkomma und Datum TT.MM.JJJJ. Fachbegriffe wie VIX, OAS oder Contango bleiben, werden aber beim ersten Auftreten in einem Halbsatz erklärt. Zielgruppe ist ein informierter Privatanleger; Länge etwa 200–600 Wörter.
7. **Nur Markdown, kein HTML.** Die Seite rendert mit `dcc.Markdown` ohne HTML.
8. **Orientierung und Block** stehen im Steckbrief. Der Freitext erklärt nur, *warum* die Orientierung so gewählt ist (z. B. warum eine enge Kreditspanne als Fallhöhe gilt).
9. **Revisionen und Lizenz:** Revisionsanfällige Reihen (z. B. NFCI, Erstanträge) und lizenzbeschränkte Reihen (ICE-Spreads) sprechen das unter „Grenzen und Fallstricke“ an.

## Inhaltliche Leitfragen je Abschnitt

- **Was die Kennzahl misst:** Definition in Klartext; bei abgeleiteten Indikatoren auch die Rohreihen dahinter.
- **Warum sie zählt:** ökonomischer Kanal, Evidenz aus dem Bericht, typischer Vorlauf (K/M/L laut Bericht Tabelle 2).
- **So liest du sie:** Was ein hohes bzw. niedriges Perzentil bedeutet, typische Muster (z. B. Backwardation bei VIX/VIX3M), Zusammenspiel mit anderen Kennzahlen desselben Blocks.
- **Grenzen und Fallstricke:** Strukturbrüche, Datenverzug, Revisionen, kurze Historie, Lizenz, bekannte Fehlsignale.
- **Quellen:** Liste mit Titel, Herausgeber, Datum bzw. Abrufdatum.

## Prüfung

- Automatisch (`pytest -q`, ab M6 aktiv): Datei je Kennzahl vorhanden, Pflichtüberschriften, Länge der Kurzinfo, keine Muster wie „90. Perzentil“ im Freitext, kein HTML.
- Durch den Nutzer: inhaltliche Freigabe je Ansicht (M8).
