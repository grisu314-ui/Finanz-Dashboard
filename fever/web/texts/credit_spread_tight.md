# Kreditspread Baa: Enge

## Kurzinfo
Derselbe Kreditspread Baa wie im Block Kredit, hier umgedreht: Je enger der Aufschlag gemessen an seiner Historie, desto mehr Fallhöhe (Selbstgefälligkeit).

## Was die Kennzahl misst
Der Wert ist die Rendite von Unternehmensanleihen der Ratingstufe Baa minus die Rendite zehnjähriger US-Staatsanleihen (FRED, Reihe BAA10Y), also genau der Wert der Kennzahl „Kreditspread Baa (Niveau)“. In der Fallhöhe zählt er mit umgedrehter Orientierung: Ein niedriger Spread ergibt ein hohes Perzentil.

## Warum sie für Marktstress oder Fallhöhe zählt
Der Bericht nennt einen sehr engen Kreditspread als Komponente der Fallhöhe: Er zeigt, dass Anleger kaum Ausgleich für Ausfallrisiken verlangen (docs/recherche.md, Abschn. 4.3, Schritt 4). López-Salido, Stein und Zakrajšek (2017) finden, dass sehr enge Spreads eine spätere Ausweitung der Spreads und schwächeres Wachstum rund zwei Jahre später vorhersagen. Krishnamurthy und Muir (2025) zeigen, dass Spreads vor Finanzkrisen ungewöhnlich niedrig waren, während die Kredite wuchsen. Der Bericht nennt dafür den HY-OAS; weil dessen Historie auf FRED nur drei Jahre umfasst, steht vorerst der Baa-Spread mit Historie ab 1986 an seiner Stelle (Entscheidung E-85).

## So liest du sie
- Ein hohes Perzentil heißt: Der Aufschlag ist gemessen an den letzten Jahren ungewöhnlich eng; der Markt preist wenig Risiko ein.
- Derselbe Wert zählt im Block Kredit als Stress, dort mit der Orientierung hoch = mehr Stress. Beide Rollen stehen als Marken neben dem Namen.
- Die Fallhöhe sagt nichts über den Zeitpunkt; enge Spreads können lange enge Spreads bleiben.

## Grenzen und Fallstricke
- Eigene Auswertung (29.09.2026): Nicht jede Übertreibung am Aktienmarkt kommt mit engen Spreads. 1998 bis 2000 weiteten sie sich schon, während Aktien noch stiegen; für diese Jahre senkt die Komponente die Fallhöhe.
- Investment Grade statt Hochzins: Der Baa-Spread schwankt weniger als der HY-OAS, den der Bericht meint.
- Lizenz Moody's: nur private Nutzung, keine Weitergabe (Entscheidung E-75).

## Quellen
- López-Salido, Stein, Zakrajšek: Credit-Market Sentiment and the Business Cycle, Quarterly Journal of Economics 132(3), 2017, S. 1373–1426
- Krishnamurthy, Muir: How Credit Cycles across a Financial Crisis, Journal of Finance, 2025
- FRED, St. Louis Fed: Reihe BAA10Y, Notes, abgerufen 28.09.2026
- docs/recherche.md, Abschnitt 4.3 (Stand 25.09.2026)
- docs/umsetzungsplan.md, Entscheidungen E-75 (28.09.2026) und E-85 (29.09.2026)
