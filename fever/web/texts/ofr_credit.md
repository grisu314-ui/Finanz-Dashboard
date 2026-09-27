# OFR FSI: Kredit

## Kurzinfo
Beitrag der Kreditspreads zum Finanzstressindex des Office of Financial Research (täglich). Hoch = Kreditaufschläge über dem Üblichen; mehr Stress.

## Was die Kennzahl misst
Der OFR Financial Stress Index (FSI) ist laut Office of Financial Research ein täglicher, marktbasierter Schnappschuss des Stresses an den globalen Finanzmärkten. Er wird aus 33 Marktvariablen gebildet, etwa Renditeaufschlägen, Bewertungsmaßen und Zinsen, und in fünf Kategorien zerlegt. Die Kategorie Kredit enthält Kreditspreads, also den Unterschied der Finanzierungskosten zwischen Unternehmen unterschiedlicher Bonität (OFR, Financial Stress Index). Der Indikator ist der Beitrag dieser Kategorie zum Gesamtindex; die fünf Kategorien addieren sich zum Gesamtwert (geprüft an der OFR-Datei `fsi.csv`).

## Warum sie für Marktstress oder Fallhöhe zählt
Steigende Kreditaufschläge zeigen, dass Anleger für das Risiko von Zahlungsausfällen mehr verlangen. Der OFR FSI erkennt laut Bericht Stressepisoden gut, ist aber vor allem ein gleichlaufender Schnappschuss und kaum ein Frühindikator (docs/recherche.md, Kurzfazit, Punkt 3). Die Kategorie Kredit bringt die Kreditspreads in den Score, solange der HY-OAS wegen seiner kurzen Historie fehlt (offener Punkt O-5 in CLAUDE.md).

## So liest du sie
- Ein hohes Perzentil heißt: Die Kreditspreads tragen ungewöhnlich viel zum Finanzstress bei.
- Der Wert ist ein Beitrag zum Gesamtindex: Null heißt durchschnittlicher Beitrag, positive Werte überdurchschnittlichen Stress (OFR, ebenda).
- Zusammen mit der Excess Bond Premium lesen: Beide hoch spricht für echten Kreditstress, nicht nur für eine technische Bewegung.

## Grenzen und Fallstricke
- Verzug: Der FSI erscheint mit Daten von zwei Geschäftstagen zuvor (OFR, ebenda).
- Die Gewichte der Variablen bestimmt ein statistisches Verfahren aus ihrem Gleichlauf (OFR, ebenda); eine Neuschätzung kann frühere Werte verändern (Einschätzung).
- Der Index ist global; US-Kreditstress und Stress in anderen Regionen mischen sich.

## Quellen
- Office of Financial Research: OFR Financial Stress Index (financialresearch.gov), abgerufen 26.09.2026
- docs/recherche.md, Kurzfazit und Abschnitt 2 (Stand 25.09.2026)
