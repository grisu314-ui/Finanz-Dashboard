# Konfidenz

## Kurzinfo
Anteil der Indikatoren mit aktuellen, gültigen Daten, gewichtet nach ihrem historischen Vorlauf (0–100 %). Niedrig = Ampel auf dünner Datenbasis.

## Was die Kennzahl misst
Jeder Indikator hat ein Gewicht aus der Vorlauf-Bewertung des Berichts (Tabelle 2, Spalte V). Die Konfidenz ist die Summe der Gewichte aller Indikatoren, die am Tag aktuell und gültig sind, geteilt durch die Summe aller Gewichte. Veraltete Indikatoren und solche mit zu kurzer Historie zählen nicht als gültig.

## Warum sie für Marktstress oder Fallhöhe zählt
Die Ampel ist nur so gut wie die Daten dahinter. Der Bericht schlägt einen Konfidenzwert vor, der zeigt, wie viel der erwarteten Information tatsächlich vorliegt (docs/recherche.md, Abschn. 4.3, Schritt 5, und die FMEA-Prüfung in Abschn. 4.1). Das Gewicht nach Vorlauf sorgt dafür, dass der Ausfall eines Indikators mit langem Vorlauf stärker ins Gewicht fällt.

## So liest du sie
- Ein Wert nahe 100 % heißt: fast alle Indikatoren sind aktuell.
- Sinkt die Konfidenz, zeigt der Datenstand, welche Quelle oder Reihe fehlt oder veraltet ist.
- Kurze Einbrüche um Feiertage oder Veröffentlichungstermine sind normal; ein anhaltend niedriger Wert deutet auf ein Abrufproblem.

## Grenzen und Fallstricke
- Die Gewichte sind Einschätzungen des Berichts, keine gemessenen Vorlaufzeiten (Abschn. 2, Hinweis unter der Tabelle).
- Indikatoren, die es in Phase 1 noch nicht gibt (Breite, Positionierung), gehen gar nicht ein; die Konfidenz misst nur die Vollständigkeit der vorhandenen.
- Eine hohe Konfidenz sagt nichts darüber, ob die Ampel richtig liegt.

## Quellen
- docs/recherche.md, Abschnitte 2, 4.1 und 4.3 (Stand 25.09.2026)
- docs/umsetzungsplan.md, Entscheidung E-48 (26.09.2026)
