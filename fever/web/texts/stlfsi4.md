# St. Louis Fed Financial Stress Index

## Kurzinfo
Finanzmarktstress laut St. Louis Fed aus 18 wöchentlichen Reihen (STLFSI4). Null = normal, hoch = mehr Stress als üblich.

## Was die Kennzahl misst
Der STLFSI4 misst laut St. Louis Fed den Grad des Stresses an den Finanzmärkten. Er wird aus 18 wöchentlichen Reihen gebildet: sieben Zinsreihen, sechs Renditeaufschlägen und fünf weiteren Indikatoren. Sein Durchschnitt seit Ende 1993 ist auf null ausgelegt; null steht für normale Bedingungen, Werte darüber für überdurchschnittlichen Stress (FRED, Reihe STLFSI4). Die Version 4 ersetzt in zwei Renditeaufschlägen den rückblickenden durch den vorausschauenden 90-Tage-SOFR (ebenda).

## Warum sie für Marktstress oder Fallhöhe zählt
Der Index fasst Zinsen, Kreditaufschläge und Volatilität zu einer Zahl zusammen und ist damit ein breiter Stressmesser. Der Bericht führt ihn als Kernindikator, aber ausdrücklich als Redundanz-Check neben NFCI und OFR FSI (docs/recherche.md, Abschn. 2, Horizont mittelfristig).

## So liest du sie
- Ein hohes Perzentil heißt: Der Stress ist gemessen an den letzten Jahren hoch.
- Weichen STLFSI4 und NFCI stark voneinander ab, lohnt der Blick in die übrigen Indikatoren des Blocks (Einschätzung).

## Grenzen und Fallstricke
- Revisionen: Der STLFSI4 wird rückwirkend neu geschätzt; ALFRED führt seine Stände (Bericht, Abschn. 4.3, Schritt 6). Hier zählt je Beobachtung der neueste Stand.
- Starke Überschneidung mit NFCI und OFR FSI: Alle drei nutzen ähnliche Marktdaten; der Median im Block dämpft das, hebt es aber nicht auf.
- Wöchentlich, Stichtag Freitag (FRED, ebenda).

## Quellen
- FRED, St. Louis Fed: Reihe STLFSI4, Notes, abgerufen 26.09.2026
- docs/recherche.md, Abschnitte 2 und 4.3 (Stand 25.09.2026)
