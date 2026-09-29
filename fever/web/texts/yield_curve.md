# Zinskurve

## Kurzinfo
Rendite zehnjähriger US-Staatsanleihen minus drei Monate (und minus zwei Jahre), Prozentpunkte. Unter null = inverse Kurve, farbig hinterlegt. Nur Anzeige.

## Was die Kennzahl misst
Die Reihe T10Y3M ist die Differenz der Renditen zehnjähriger Staatsanleihen und dreimonatiger Schatzwechsel, beide mit konstanter Laufzeit; die Daten stammen direkt vom US-Finanzministerium (FRED, Reihe T10Y3M). T10Y2Y ist die entsprechende Differenz zu zweijährigen Anleihen. Die Ansicht schattiert jede Phase, in der 10 Jahre minus 3 Monate unter null liegt (Inversion); das Ende einer Fläche ist das Re-Steepening (Entscheidung E-65). Ansicht und Erklärseite nennen das Datum des letzten Re-Steepening, also den ersten Wert ab null nach dem letzten Tag der Inversion (Entscheidung E-84).

## Warum sie für Marktstress oder Fallhöhe zählt
Die Steigung der Zinskurve gilt als guter Frühindikator der Konjunktur; ihre Bewegungen haben laut Estrella und Trubin frühere Rezessionen angezeigt (Federal Reserve Bank of New York, Current Issues 12(5), 2006). Der Bericht führt den Abstand 10 Jahre minus 3 Monate mit Re-Steepening-Marker als Kernindikator mit langem Horizont und nennt als Einschätzung: Die Kurve invertierte lange vor kreditgetriebenen Abschwüngen, der Bärenmarkt setzte typischerweise nach dem Re-Steepening ein (docs/recherche.md, Abschn. 2 und 3).

## So liest du sie
- Eine schattierte Fläche heißt: Kurzfristige Zinsen liegen über langfristigen.
- Einschätzung: Wichtiger als der Beginn einer Inversion ist oft ihr Ende, wenn die Kurve wieder steiler wird.
- Eigene Auswertung (29.09.2026, S&P 500 ab 1989): Der Beginn einer Inversion ging keinem Einbruch unmittelbar voraus. Nach den Re-Steepenings von 1990, 2001 und 2007 fiel der S&P 500 in den folgenden zwölf Monaten um höchstens 16, 27 und 17 Prozent, nach dem von 2019/20 um 24 Prozent, dort aber durch die Pandemie, also einen äußeren Schock. Das sind nur vier Fälle; die Kurve bleibt deshalb reine Anzeige ohne Wirkung auf die Ampel (Entscheidung E-84).
- Zusammen mit den grauen Rezessionsflächen lesen: So zeigt sich der Abstand zwischen Inversion und Rezession.

## Grenzen und Fallstricke
- Sehr langer und schwankender Vorlauf; für Tage bis Wochen ist die Zinskurve kaum nützlich (Bericht, Abschn. 2, Spalte O).
- Kurze Unterschreitungen der Nulllinie erscheinen als schmale Flächen, auch wenn sie keine Bedeutung haben. Auch das Datum des letzten Re-Steepening kann deshalb von einer solchen kurzen Unterschreitung stammen; die Flächen im Verlauf zeigen, wie lang die Inversion davor war.
- Geldpolitik und Anleihekäufe der Notenbank können die Kurve verzerren (Einschätzung).

## Quellen
- FRED, St. Louis Fed: Reihen T10Y3M und T10Y2Y, Notes, abgerufen 27.09.2026
- Estrella, Trubin: The Yield Curve as a Leading Indicator: Some Practical Issues, Current Issues in Economics and Finance 12(5), Federal Reserve Bank of New York, Juli/August 2006, abgerufen 27.09.2026
- docs/recherche.md, Abschnitte 2 und 3 (Stand 25.09.2026)
- docs/umsetzungsplan.md, Entscheidung E-84 (29.09.2026)
