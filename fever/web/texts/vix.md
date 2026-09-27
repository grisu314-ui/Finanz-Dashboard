# VIX-Niveau

## Kurzinfo
Vom Optionsmarkt erwartete Schwankung des S&P 500 über die nächsten 30 Tage (Cboe VIX, in Prozent auf das Jahr gerechnet). Hoch = mehr Stress.

## Was die Kennzahl misst
Der VIX misst laut Cboe die für 30 Tage erwartete Volatilität des S&P 500. Cboe berechnet ihn aus den Preisen von Optionen auf den S&P 500 (SPX und SPXW) und aus Zinsen der US-Staatsanleihenkurve (Cboe Volatility Index Methodology). Der Wert ist eine Schwankungsbreite in Prozent, auf ein Jahr gerechnet. Der Indikator nimmt den täglichen Schlusswert unverändert.

## Warum sie für Marktstress oder Fallhöhe zählt
Optionen sind Versicherungen gegen Kursbewegungen. Wird Absicherung stark nachgefragt, steigen ihre Preise und damit der VIX. Der Bericht führt das VIX-Niveau als Kernindikator mit guter Evidenz, aber sehr kurzem Vorlauf: Es zeigt, dass Stress herrscht, kaum, dass er kommt (docs/recherche.md, Abschn. 2, Horizont kurzfristig). Ein einfacher VIX-Filter ist im Bericht außerdem die Messlatte für den ganzen Composite: Schlägt der Composite ihn nicht, ist er Ballast (Abschn. 4.3, Schritt 7).

## So liest du sie
- Ein hohes Perzentil heißt: Der Markt erwartet ungewöhnlich große Schwankungen und bezahlt Absicherung teuer.
- Einschätzung: Der VIX steigt meist, wenn Aktien fallen, und sinkt nach Schocks oft schnell wieder. Lange Phasen mit sehr niedrigem VIX sind ruhig, aber nicht ungefährlich.
- Zusammen mit VIX/VIX3M lesen: Ein hoher VIX bei normaler Termstruktur ist erhöhte Unruhe, ein hoher VIX bei umgedrehter Termstruktur akuter Stress.

## Grenzen und Fallstricke
- Kein Frühwarnsignal: Bei exogenen Schocks steigt der VIX erst mit dem Ereignis (Bericht, Abschn. 3).
- Der VIX misst erwartete, nicht tatsächlich eintretende Schwankung und enthält eine Risikoprämie (siehe Variance Risk Premium).
- Einschätzung: Der starke Handel mit sehr kurz laufenden Optionen (0DTE) kann das Verhalten des VIX verändern; der Bericht nennt 0DTE als möglichen Strukturbruch (Abschn. 4.3, Schritt 1).
- Cboe-Daten dürfen nur privat und nicht kommerziell genutzt werden.

## Quellen
- Cboe Global Indices: Cboe Volatility Index Methodology (cdn.cboe.com), abgerufen 26.09.2026
- docs/recherche.md, Abschnitte 2, 3 und 4.3 (Stand 25.09.2026)
