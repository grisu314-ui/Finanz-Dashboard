# Validierung

## Kurzinfo
Rückblick: Wie gut kündigten Ampel, Stress und Fallhöhe frühere Einbrüche an, verglichen mit einem einfachen VIX-Filter? Keine Wahrscheinlichkeit für heute.

## Was die Kennzahl misst
Die Ansicht „Validierung“ prüft die Ampel gegen die eigene Geschichte, wie es der Bericht verlangt (docs/recherche.md, Abschn. 4.3, Schritt 7). Für jeden Handelstag ab dem Beginn der Auswertung steht fest, ob danach innerhalb eines Horizonts ein Ereignis begann: ein Rückgang des S&P 500, ein VIX-Schluss über einer Marke oder ein Bärenmarkt. Die genauen Marken und Horizonte stehen unten unter „Schwellen und Farben“. Rückgänge werden mechanisch bestimmt, nach Lunde und Timmermann (2004): Ein Rückgang beginnt am Schlusskurs-Hoch, sobald der Kurs die Schwelle darunter schließt, und endet am Tief, sobald er von dort um dieselbe Schwelle steigt.

Gemessen wird dann, wie gut die Signale Tage vor einem Ereignis von den übrigen trennen:
- **AUC** (Fläche unter der ROC-Kurve): 0,5 heißt so gut wie Zufall, 1 heißt perfekte Trennung. Sie gilt für die stetigen Signale Stress, Fallhöhe, Ampelstufe und VIX-Perzentil.
- **Precision**: Anteil der Alarmtage, auf die das Ereignis folgte. **Recall**: Anteil der Tage vor einem Ereignis, an denen Alarm war.
- **Vorlauf**: Handelstage vom ersten Alarm im Horizont bis zum Beginn des Ereignisses, höchstens der Horizont selbst: Dann war der Alarm schon am ersten Tag an, oft auch lange davor. **Fehlalarme**: Alarmphasen, auf die kein Ereignis folgte.

**Geschätzte Gewichte** (Abschnitt unten in der Ansicht): Der Stress zählt seine Blöcke gleich. Zum Vergleich schätzt eine logistische Regression jedes Jahr neu, wie die Blöcke mit langer Historie gewichtet sein müssten, um die Tage vor einem Ereignis zu trennen; welche Blöcke das sind, steht unter „Schwellen und Farben“. Geschätzt wird nur mit Tagen, deren Ergebnis zu Jahresbeginn feststand, und die Ereignisse werden dafür aus den Kursen bis zu diesem Tag bestimmt. Ausgewertet wird das mit diesen Gewichten gebildete Mittel der Blöcke gegen das gleichgewichtete Mittel, den Stress und das VIX-Perzentil; eine zweite Variante nimmt die Fallhöhe hinzu und zeigt, ob sie über den Stress hinaus etwas über den Zeitpunkt sagt.

## Warum sie für Marktstress oder Fallhöhe zählt
Die meisten veröffentlichten Frühindikatoren versagen außerhalb der Stichprobe, in der sie gefunden wurden (Goyal und Welch 2008, laut Bericht, Kurzfazit). Der Bericht nennt deshalb einen Maßstab: Schlägt der Composite einen naiven Filter auf das VIX-Perzentil nicht, ist er Ballast. Der Vergleichsfilter hier gibt genau so oft Alarm, wie die Ampel in den Jahren zuvor Alarm gab; seine Schwelle entsteht jedes Jahr neu nur aus den Jahren davor (Walk-forward), ohne Blick auf spätere Ereignisse. Die Konfidenzintervalle stammen aus einem Block-Bootstrap, weil benachbarte Tage fast dasselbe Ergebnis haben.

## So liest du sie
- „Besser“ oder „schlechter“ steht nur, wenn das ganze Intervall des Unterschieds auf einer Seite von null liegt; sonst „nicht unterscheidbar“.
- Die Ampel ist eine Regime- und Risikoanzeige. Eine niedrige Precision heißt nicht, dass Alarme wertlos sind: Viele Alarme fallen in Phasen erhöhter Schwankung, die ohne großen Rückgang enden.
- Der Zeitraum-Vergleich zeigt, ob ein Ergebnis nur an einer Krise hängt. Eine AUC je Zeitraum steht nur, wenn darin ein Ereignis beginnt.
- Viele „gewarnte“ Ereignisse bei einer Stufe, die oft an ist, sagen wenig: Maßstab ist der Vergleich mit dem VIX-Filter, der etwa gleich oft Alarm gibt.
- Geschätzte Gewichte gelten nur als besser, wenn das ganze Intervall ihres Unterschieds zu gleichen Gewichten vor Rückgängen über null liegt und sie vor VIX-Spitzen nicht schlechter sind. Auch dann ändert sich die Ampel nur auf Anweisung. Die Tabelle „Gewichte je Jahr“ zeigt, wie stabil die Schätzung ist.

## Grenzen und Fallstricke
- Wenige unabhängige Ereignisse seit 1990: Die Intervalle sind breit.
- Nicht streng außerhalb der Stichprobe: Die Regeln des Berichts und spätere Entscheidungen entstanden mit Kenntnis dieser Jahre.
- In Phase 1 zählt je Beobachtung der neueste Stand, und die Veröffentlichung der Rückfüllung ist geschätzt; revisionsgenau rechnet erst Phase 2.
- Das Ereignis mit dem VIX begünstigt den VIX-Filter, weil er dieselbe Größe misst.
- Nichts aus der Validierung geht in die Ampel ein: Schwellen, die im Rückblick besser gewesen wären, werden nicht übernommen (CLAUDE.md).
- Geschätzte Gewichte stützen sich auf wenige Ereignisse; die ersten Jahre kennen nur die 1990er. Gleiche Gewichte sind außerhalb der Stichprobe erfahrungsgemäß schwer zu schlagen (Forecast-Combination-Puzzle).
- Nicht enthalten: Wahrscheinlichkeiten und Brier-Score (die geschätzten Gewichte liefern hier bewusst nur eine Rangfolge) sowie der ökonomische Test mit Put-Absicherung (Optionsdaten), beides Phase 3.

## Quellen
- docs/recherche.md, Abschnitte 4.3 (Schritt 7) und 6.3 (Ansicht 8), Stand 25.09.2026
- Asger Lunde, Allan Timmermann: Duration Dependence in Stock Prices: An Analysis of Bull and Bear Markets, Journal of Business & Economic Statistics 22(3), 2004, S. 253–273
- Amit Goyal, Ivo Welch: A Comprehensive Look at the Empirical Performance of Equity Premium Prediction, Review of Financial Studies 21(4), 2008, S. 1455–1508
- James H. Stock, Mark W. Watson: Combination Forecasts of Output Growth in a Seven-Country Data Set, Journal of Forecasting 23(6), 2004, S. 405–430
- Jeremy Smith, Kenneth F. Wallis: A Simple Explanation of the Forecast Combination Puzzle, Oxford Bulletin of Economics and Statistics 71(3), 2009, S. 331–355
- docs/umsetzungsplan.md, Meilensteine M10 und M11, Entscheidungen E-93 und E-94 (29.09.2026)
