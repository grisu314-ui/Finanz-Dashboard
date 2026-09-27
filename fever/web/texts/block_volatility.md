# Block Volatilität/Optionen

## Kurzinfo
Median der Perzentile von VIX, VIX/VIX3M, VVIX und Variance Risk Premium (0–100). Hoch = der Optionsmarkt preist mehr Stress als üblich; reagiert in Tagen.

## Was die Kennzahl misst
Der Block fasst die schnellen Signale aus dem Optionsmarkt auf den S&P 500 zusammen: das Niveau des VIX, das Verhältnis VIX/VIX3M (die Termstruktur, also kurzfristig gegen längerfristig erwartete Schwankung), den VVIX (die erwartete Schwankung des VIX selbst) und die Variance Risk Premium (VIX minus tatsächlich gemessene Schwankung). Jeder Indikator wird zuerst in ein Perzentil gegenüber seiner eigenen Vergangenheit übersetzt; der Blockwert ist der Median der gültigen Perzentile. Bevor der Block in den Stress eingeht, wird er leicht geglättet. Wie genau, steht unten im Steckbrief.

## Warum sie für Marktstress oder Fallhöhe zählt
Bei Liquiditäts- und Positionierungsschocks wie 1987, 1998, Februar 2018 und August 2024 zeigten laut Bericht nur der Optionsmarkt und Funding-Signale Tage vorher Anspannung, Makroreihen dagegen nicht (docs/recherche.md, Abschn. 3; dort als Einschätzung gekennzeichnet). Der Bericht fordert deshalb einen schnellen Block für Schocks neben den langsamen Kredit- und Makroblöcken (Abschn. 3, „Konsequenz“, und Abschn. 4.3, Schritt 2). Der Median sorgt dafür, dass die Mehrheit der Indikatoren zählt und nicht ein einzelner Ausreißer (Abschn. 4.3, Schritt 2).

## So liest du sie
- Ein hoher Wert heißt: Mehrere Optionsmaße stehen gleichzeitig weit über ihrem üblichen Niveau.
- Der Block steigt bei Schocks schnell und fällt danach oft ebenso schnell zurück.
- Vergleiche mit dem Block Kredit/Funding: Steigt nur die Volatilität, ist es eher ein Marktschock; ziehen die Kreditmaße mit, wird der Stress breiter.
- Welcher Indikator den Block gerade trägt, zeigen die Zeilen darunter.

## Grenzen und Fallstricke
- Kurzer Vorlauf: Der Bericht bewertet den Vorlauf aller vier Indikatoren als schwach (Abschn. 2, Spalte V). Sie zeigen eher, dass Stress da ist, als dass er kommt.
- Alle vier hängen am selben Optionsmarkt. Der Median dämpft die Doppelzählung, hebt sie aber nicht auf.
- Einschätzung: Strukturbrüche wie der starke Handel mit sehr kurz laufenden Optionen (0DTE) können das Verhalten dieser Maße verändern; der Bericht nennt 0DTE als Grund für das rollierende Fenster (Abschn. 4.3, Schritt 1).
- Cboe-Daten dürfen nur privat und nicht kommerziell genutzt werden.

## Quellen
- docs/recherche.md, Abschnitte 2, 3 und 4.3 (Stand 25.09.2026)
- docs/umsetzungsplan.md, Entscheidungen E-47 bis E-49 (26.09.2026)
