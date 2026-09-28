# Block Breite/Internals

## Kurzinfo
Median der Perzentile von fünf Verhältnissen, die zeigen, ob der US-Markt breit oder nur von wenigen Teilen getragen wird (0–100). Hoch = schmale, nachlassende Breite.

## Was die Kennzahl misst
Der Block fasst fünf relative Stärken zusammen: gleich- gegen kapitalgewichtet, kleine gegen große Werte, Halbleiter und Regionalbanken gegen den Gesamtmarkt sowie Zykliker gegen Defensive. Jede ist die Veränderung eines Verhältnisses zweier Nasdaq-Indizes; jede wird in ein Perzentil gegenüber ihrer eigenen Vergangenheit übersetzt, gedreht so, dass hoch mehr Stress heißt. Der Blockwert ist der Median der gültigen Perzentile (docs/recherche.md, Abschn. 4.3, Schritt 2).

## Warum sie für Marktstress oder Fallhöhe zählt
Breite/Internals ist einer der fünf Stressblöcke des Berichts (Abschn. 4.3, Schritt 2); RSP/SPY ist dort ein Kernindikator mit mittlerem Horizont (Abschn. 2, Rang 9). Einschätzung: Der Block soll zeigen, ob ein Anstieg auf vielen Schultern steht oder nur auf wenigen, und ergänzt damit die Blöcke, die Optionen, Kredit und Makro messen.

## So liest du sie
- Ein hoher Wert heißt: Mehrere der fünf Verhältnisse verschlechtern sich gleichzeitig ungewöhnlich stark.
- Der Median dämpft einzelne Ausreißer; welche Verhältnisse den Block tragen, zeigen die Zeilen der Ansicht Breite.

## Grenzen und Fallstricke
- Der Anteil der Aktien über ihrer 50- bzw. 200-Tage-Linie aus dem Bericht fehlt, weil es keine freie, speicherbare Quelle gibt (Entscheidung E-72).
- Kurze Historien: Die Verhältnisse beginnen zwischen 2011 und 2020; ein Indikator zählt erst mit der Mindesthistorie (Steckbrief der Indikatoren).
- Nasdaq-Indizes statt der ETFs des Berichts (Entscheidung E-68).

## Quellen
- docs/recherche.md, Abschnitte 2, 4.3 und 6.3 (Stand 25.09.2026)
- docs/umsetzungsplan.md, Entscheidungen E-68, E-72 bis E-74 (28.09.2026)
