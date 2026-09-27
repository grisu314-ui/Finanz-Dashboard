# OFR Financial Stress Index

## Kurzinfo
Täglicher Finanzstressindex des Office of Financial Research mit Zerlegung nach fünf Kategorien und drei Regionen. Null = normal, hoch = mehr Stress. Nur Anzeige.

## Was die Kennzahl misst
Der OFR FSI ist laut Office of Financial Research ein täglicher, marktbasierter Schnappschuss des Stresses an den globalen Finanzmärkten, gebildet aus 33 Marktvariablen wie Renditeaufschlägen, Bewertungsmaßen und Zinsen. Er ist null, wenn der Stress auf normalem Niveau liegt, positiv bei überdurchschnittlichem Stress. Der Index zerfällt in die Beiträge von fünf Kategorien (Kredit, Aktienbewertung, Refinanzierung, sichere Anlagen, Volatilität) und drei Regionen (USA, andere Industrieländer, Schwellenländer) (OFR, Financial Stress Index). Die fünf Kategorien addieren sich zum Gesamtwert, ebenso die drei Regionen (geprüft an der OFR-Datei `fsi.csv`).

## Warum sie für Marktstress oder Fallhöhe zählt
Die Zerlegung zeigt, woher Stress kommt: aus dem Kreditmarkt, von den Aktienbewertungen, aus der Refinanzierung oder aus einer Region. Der Bericht nennt die Zerlegung nach Regionen und Kategorien als Teil der Ansicht „Makro und Liquidität“ (docs/recherche.md, Abschn. 6.3). Der Gesamtindex ist laut Bericht vor allem ein gleichlaufender Schnappschuss (Kurzfazit, Punkt 3). In den Score gehen nur die Kategorien Kredit und Funding ein (Entscheidung E-49).

## So liest du sie
- Die Linien der Kategorien bzw. Regionen zeigen ihren Beitrag; die größte positive Linie ist die wichtigste Stressquelle.
- Steigt vor allem der Beitrag der Region USA, liegt der Stress im Heimatmarkt des S&P 500.

## Grenzen und Fallstricke
- Verzug von zwei Geschäftstagen (OFR, ebenda).
- Die Gewichte bestimmt ein statistisches Verfahren; eine Neuschätzung kann frühere Werte verändern (Einschätzung).
- Einschätzung: Die Aktienbewertung geht als Beitrag ein; hohe Bewertungen senken den Stress, obwohl sie die Fallhöhe erhöhen.

## Quellen
- Office of Financial Research: OFR Financial Stress Index (financialresearch.gov), abgerufen 26.09.2026
- docs/recherche.md, Kurzfazit und Abschnitt 6.3 (Stand 25.09.2026)
- docs/umsetzungsplan.md, Entscheidung E-49 (26.09.2026)
