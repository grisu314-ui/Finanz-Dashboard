# Shiller-CAPE

## Kurzinfo
Kurs des S&P 500 geteilt durch den Durchschnitt der inflationsbereinigten Gewinne der letzten zehn Jahre (zyklisch bereinigtes KGV). Hoch = teurer Markt. Nur Anzeige.

## Was die Kennzahl misst
Das CAPE (Cyclically Adjusted Price Earnings Ratio) von Robert J. Shiller setzt den Kurs des S&P 500 ins Verhältnis zu den durchschnittlichen, um Inflation bereinigten Gewinnen der vergangenen zehn Jahre. Der lange Durchschnitt glättet Gewinneinbrüche in Rezessionen und Gewinnspitzen in Booms. Die Werte stammen aus Shillers Datendatei, die bis 1881 zurückreicht (docs/umsetzungsplan.md, Ergebnis M4c).

## Warum sie für Marktstress oder Fallhöhe zählt
Campbell und Shiller zeigen, dass Bewertungskennzahlen wie das Kurs-Gewinn-Verhältnis vor allem künftige Kursänderungen über lange Zeiträume vorhersagen (Journal of Portfolio Management 24(2), 1998). Ein hohes CAPE heißt: Die Kurse sind im Verhältnis zu den Gewinnen weit gelaufen, ein Rückschlag hat mehr Raum. Der Bericht nennt CAPE und Excess CAPE Yield als Kern der Fallhöhe, ohne Vorlauf für den Zeitpunkt (docs/recherche.md, Abschn. 2). In die Fallhöhe geht die Excess CAPE Yield ein, weil sie den Zins berücksichtigt (Entscheidung E-49); das CAPE selbst ist Anzeige.

## So liest du sie
- Ein hohes CAPE heißt: Aktien sind teuer im Vergleich zu ihren Gewinnen der letzten zehn Jahre.
- Es sagt nichts über den Zeitpunkt; der Markt kann jahrelang teuer bleiben.
- Zusammen mit der Excess CAPE Yield lesen: Diese zeigt, ob hohe Bewertungen durch niedrige Realzinsen gerechtfertigt erscheinen.

## Grenzen und Fallstricke
- Monatlich; der laufende Monat ist vorläufig.
- Einschätzung: Veränderte Bilanzierung und ein höherer Anteil gewinnstarker Technologiewerte können das CAPE langfristig nach oben verschieben.
- Die Daten enthalten S&P-Werte: nur private Nutzung, keine Weitergabe.

## Quellen
- Campbell, Shiller: Valuation Ratios and the Long-Run Stock Market Outlook, Journal of Portfolio Management 24(2), 1998, S. 11–26 (Angaben über NBER und SSRN, abgerufen 27.09.2026)
- Robert J. Shiller, Online Data (ie_data.xls), abgerufen über das Projekt ab 26.09.2026
- docs/recherche.md, Abschnitt 2 (Stand 25.09.2026)
- docs/umsetzungsplan.md, Entscheidung E-49 und Ergebnis M4c (26.09.2026)
