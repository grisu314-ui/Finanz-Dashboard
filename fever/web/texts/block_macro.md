# Block Makro/Finanzierungsbedingungen

## Kurzinfo
Median der Perzentile von acht Indikatoren zu Finanzierungsbedingungen, Arbeitsmarkt, Aktien-Anleihen-Korrelation und Yen (0–100). Hoch = breite Anspannung.

## Was die Kennzahl misst
Der Block bündelt drei Arten von Signalen: breite Stress- und Finanzierungsindizes der Notenbanken (NFCI der Chicago Fed, STLFSI4 der St. Louis Fed, CISS der EZB für den Euroraum), den Arbeitsmarkt (Sahm-Regel in Echtzeit, Erstanträge auf Arbeitslosenhilfe) und zwei Marktsignale mit makroökonomischem Hintergrund: die Korrelation von Aktien und Anleihen sowie die Bewegung des Yen gegenüber dem US-Dollar. Jeder Indikator wird in ein Perzentil gegenüber seiner eigenen Vergangenheit übersetzt; der Blockwert ist der Median der gültigen Perzentile.

## Warum sie für Marktstress oder Fallhöhe zählt
In kreditgetriebenen Abschwüngen liefen laut Bericht Arbeitsmarkt und Zinskurve den Aktienmärkten Monate voraus (docs/recherche.md, Abschn. 3; dort als Einschätzung gekennzeichnet); die Financial-Conditions-Indizes ordnet er dem mittleren Horizont von ein bis sechs Monaten zu (Abschn. 2). Im Inflations- und Zinsregime 2022 drehte die Aktien-Anleihen-Korrelation ins Positive, während klassische Stressindizes moderat blieben (Abschn. 3). Beim Abbau der mit Yen finanzierten Carry-Trades im August 2024 gehörten Carry-Signale laut Bericht zu den wenigen, die Tage vorher Anspannung zeigten (Abschn. 3; zum Ablauf BIS Bulletin Nr. 90). Der Block soll diese langsameren Kanäle abbilden, getrennt vom schnellen Optionsmarkt (Abschn. 4.3, Schritt 2).

## So liest du sie
- Ein hoher Wert heißt: Viele der acht Indikatoren stehen gleichzeitig weit oben in ihrer Historie.
- Der Block bewegt sich meist in Wochen, nicht in Tagen; ein schneller Anstieg kommt eher von der Korrelation oder vom Yen.
- Welche Gruppe den Block trägt (Stressindizes, Arbeitsmarkt oder Marktsignale), zeigen die Zeilen darunter.

## Grenzen und Fallstricke
- Revisionen: NFCI und STLFSI4 werden rückwirkend neu geschätzt, Erstanträge revidiert (Bericht, Abschn. 4.3, Schritt 6). In Phase 1 zählt je Beobachtung der neueste Stand; die Vergangenheit sieht deshalb glatter aus, als sie sich damals angefühlt hätte.
- Unterschiedliche Frequenzen: täglich, wöchentlich und monatlich stehen nebeneinander; die monatliche Sahm-Regel ändert sich selten.
- Die drei Stressindizes messen teils dasselbe; der Bericht führt den STLFSI4 ausdrücklich als Redundanz-Check (Abschn. 2).
- Die Zinskurve ist im Bericht ein Kernindikator, geht aber nur als Anzeige ein (Entscheidung E-49).

## Quellen
- docs/recherche.md, Abschnitte 2, 3 und 4.3 (Stand 25.09.2026)
- Aquilina, Lombardi, Schrimpf, Sushko: The market turbulence and carry trade unwind of August 2024, BIS Bulletin Nr. 90 (27.08.2024), abgerufen 26.09.2026
- docs/umsetzungsplan.md, Entscheidung E-49 (26.09.2026)
