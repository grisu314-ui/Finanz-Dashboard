# OFR FSI: Funding

## Kurzinfo
Beitrag der Refinanzierungsbedingungen zum Finanzstressindex des Office of Financial Research (täglich). Hoch = Finanzinstitute kommen schwerer an Geld; mehr Stress.

## Was die Kennzahl misst
Der OFR Financial Stress Index (FSI) ist ein täglicher, marktbasierter Schnappschuss des Stresses an den globalen Finanzmärkten aus 33 Marktvariablen in fünf Kategorien. Die Kategorie Funding enthält Maße dafür, wie leicht sich Finanzinstitute finanzieren können (OFR, Financial Stress Index). Der Indikator ist der Beitrag dieser Kategorie zum Gesamtindex; die fünf Kategorien addieren sich zum Gesamtwert (geprüft an der OFR-Datei `fsi.csv`).

## Warum sie für Marktstress oder Fallhöhe zählt
Engpässe bei der Refinanzierung von Banken und Händlern können Verkäufe erzwingen und Stress schnell verbreiten. Bei Liquiditäts- und Positionierungsschocks zeigten laut Bericht neben dem Optionsmarkt vor allem Funding-Signale Tage vorher Anspannung (docs/recherche.md, Abschn. 3; dort als Einschätzung gekennzeichnet). Der OFR FSI insgesamt ist ein gleichlaufendes Maß und kaum ein Frühindikator (Kurzfazit, Punkt 3).

## So liest du sie
- Ein hohes Perzentil heißt: Die Refinanzierung trägt ungewöhnlich viel zum Finanzstress bei.
- Null heißt durchschnittlicher Beitrag, positive Werte überdurchschnittlichen Stress (OFR, ebenda).
- Zusammen mit SOFR − IORB lesen: Beide hoch spricht für einen echten Engpass am Geldmarkt.

## Grenzen und Fallstricke
- Verzug: Der FSI erscheint mit Daten von zwei Geschäftstagen zuvor (OFR, ebenda).
- Das OFR hat den Index auf neue Referenzzinsen umgestellt (Arbeitspapier „The Transition to Alternative Reference Rates in the OFR Financial Stress Index“, 2023); Funding-Maße vor und nach der Umstellung sind nicht völlig gleich gebaut (Einschätzung).
- Die Gewichte bestimmt ein statistisches Verfahren; eine Neuschätzung kann frühere Werte verändern (Einschätzung).

## Quellen
- Office of Financial Research: OFR Financial Stress Index (financialresearch.gov), abgerufen 26.09.2026
- docs/recherche.md, Kurzfazit und Abschnitt 3 (Stand 25.09.2026)
