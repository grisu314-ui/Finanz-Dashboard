# SOS-Indikator

## Kurzinfo
Anstieg der versicherten US-Arbeitslosenquote (26-Wochen-Schnitt) über ihr Tief der 52 Wochen davor, in Prozentpunkten. Hoch = Rezessionswarnung; zählt nur als Ampelregel.

## Was die Kennzahl misst
Die versicherte Arbeitslosenquote ist der Anteil der Beschäftigten mit Arbeitslosenversicherung, die gerade Arbeitslosengeld beziehen (Continued Claims geteilt durch die versicherte Beschäftigung; FRED, Reihe IURSA, wöchentlich). Der SOS-Indikator wendet darauf die Konstruktion der Sahm-Regel an: Er nimmt den Durchschnitt der letzten 26 Wochen und zieht den niedrigsten dieser Durchschnitte aus den 52 Wochen davor ab. Entwickelt haben ihn John O'Trakoun (Federal Reserve Bank of Richmond) und Adam Scavette (Federal Reserve Bank of Philadelphia); der Name steht für „Scavette-O'Trakoun-Sahm-style“. Das Dashboard rechnet ihn aus der FRED-Reihe nach; die Fenster stehen im Steckbrief.

## Warum sie für Marktstress oder Fallhöhe zählt
Rezessionen gehen mit steigender Arbeitslosigkeit einher, und in Rezessionen fielen Aktien meist deutlich. Laut Richmond Fed hat der Indikator die sieben Rezessionen seit 1971 angezeigt, ohne Fehlalarm in dieser Zeit, und im Mittel früher als die Sahm-Regel; die Daten kommen wöchentlich statt monatlich und beruhen auf Verwaltungsdaten statt auf einer Umfrage (Richmond Fed, SOS Recession Indicator). Eigene Auswertung (29.09.2026, Tage der Veröffentlichung): Seit 1990 schlug er 1990, 2001, 2008 und 2020 an, zwischen zwei Wochen und gut drei Monaten vor der Sahm-Regel, und nie ohne Rezession. Deshalb dient er als Vorwarnstufe der Gesamtampel (Entscheidung E-80). In Stress und Fallhöhe geht er nicht ein.

## So liest du sie
- Ein Wert um null heißt: Die versicherte Arbeitslosigkeit liegt nahe ihrem jüngsten Tief.
- Steigt er über die Schwelle unter „Schwellen und Farben“, steht die Ampel mindestens auf Gelb, solange das so bleibt.
- Violette Flächen im Verlauf: Tage, an denen die Ampelregel galt.
- Zusammen mit der Sahm-Regel lesen: Der SOS-Indikator warnt meist zuerst, die Sahm-Regel bestätigt.

## Grenzen und Fallstricke
- Gleichlaufend statt vorlaufend: Auch der SOS-Indikator meldet eine Rezession erst, wenn sie begonnen hat, und bleibt bis in die Erholung hinein erhöht, wenn Aktienkurse oft schon steigen.
- Die Richmond Fed nennt eine Schwelle von 0,2 Prozentpunkten; sie ist an wenigen Rezessionen gewonnen. Dass es seit 1971 keinen Fehlalarm gab, schließt künftige nicht aus.
- Veränderte Regeln der Arbeitslosenversicherung, etwa Sonderprogramme wie 2020, verschieben die Quote.
- Wochenwerte werden revidiert; wie bei allen Reihen zählt je Woche der neueste Stand.
- Das Perzentil ist nur Anzeige; die Ampelregel liest den Wert selbst.

## Quellen
- Federal Reserve Bank of Richmond: SOS Recession Indicator (richmondfed.org, Research, National Economy) und Economic Brief 25-07 (2025), abgerufen 29.09.2026
- FRED, St. Louis Fed: Reihe IURSA, Notes, abgerufen 29.09.2026
- docs/umsetzungsplan.md, Entscheidung E-80 (29.09.2026)
