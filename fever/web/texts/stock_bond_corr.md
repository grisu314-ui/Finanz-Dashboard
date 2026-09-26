# Aktien-Anleihen-Korrelation

## Kurzinfo
Wie stark sich S&P 500 und US-Staatsanleihen zuletzt im Gleichschritt bewegt haben (Korrelation, −1 bis 1). Hoch = Anleihen schützen Aktien nicht mehr; mehr Stress.

## Was die Kennzahl misst
Der Indikator berechnet die Korrelation der täglichen Kursänderungen des S&P 500 mit den Kursänderungen zehnjähriger US-Staatsanleihen über ein rollierendes Fenster. Weil FRED die Rendite liefert und nicht den Anleihekurs, steht eine sinkende Rendite für einen steigenden Kurs; der Indikator nutzt deshalb die negative Renditeänderung (Entscheidung E-49). Fenster und Berechnung stehen unten im Steckbrief. Ein Wert nahe 1 heißt: Aktien und Anleihen steigen und fallen zusammen.

## Warum sie für Marktstress oder Fallhöhe zählt
In vielen Portfolios sollen Anleihen Verluste bei Aktien abfedern. Das klappt nur bei negativer Korrelation. Campbell, Pflueger und Viceira (2020) zeigen, dass das Vorzeichen vom makroökonomischen Regime abhängt: Wenn Inflation die Anleihen treibt, bewegen sich Aktien und Anleihen eher gemeinsam. Laut Bericht drehte die Korrelation im Inflations- und Zinsregime 2022 ins Positive, während klassische Stressindizes moderat blieben (docs/recherche.md, Abschn. 3). Der Bericht führt sie als Kernindikator mit kurz- bis mittelfristigem Horizont (Abschn. 2).

## So liest du sie
- Ein hohes Perzentil heißt: Aktien und Anleihen bewegen sich ungewöhnlich stark im Gleichschritt; die übliche Absicherung durch Anleihen fällt aus.
- Einschätzung: Eine hohe Korrelation zusammen mit steigenden Renditen deutet auf Zins- oder Inflationsdruck als Stressquelle hin, nicht auf Kreditangst.
- Die Korrelation ist träge; sie ändert sich über Wochen, nicht über Tage.

## Grenzen und Fallstricke
- Kurze Historie: Der S&P 500 kommt von FRED und reicht dort nur rund zehn Jahre zurück (offener Punkt O-1 in CLAUDE.md).
- Eine positive Korrelation ist nicht immer Stress: In einer gemeinsamen Erholung steigen beide ebenfalls zusammen (Einschätzung).
- Die S&P-500-Daten von FRED unterliegen der Lizenz von S&P Dow Jones Indices: nur privat, keine Weitergabe.

## Quellen
- Campbell, Pflueger, Viceira: Macroeconomic Drivers of Bond and Equity Risks, Journal of Political Economy 128(8), 2020, S. 3148–3185 (Kurzfassung über NBER und RePEc, abgerufen 26.09.2026)
- docs/recherche.md, Abschnitte 2 und 3 (Stand 25.09.2026)
- docs/umsetzungsplan.md, Entscheidung E-49 (26.09.2026)
