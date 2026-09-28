# Kreditspread Baa (Niveau)

## Kurzinfo
Rendite von US-Unternehmensanleihen der Ratingstufe Baa minus Rendite zehnjähriger Staatsanleihen, in Prozentpunkten. Hoch = Kreditstress.

## Was die Kennzahl misst
FRED berechnet die Reihe als Differenz zwischen der Rendite von Moody's Seasoned Baa Corporate Bonds und der Rendite zehnjähriger US-Staatsanleihen mit konstanter Laufzeit (FRED, Reihe BAA10Y, Notes). Baa ist die unterste Stufe von Investment Grade, also Unternehmen mit noch gutem, aber schwächstem Anlage-Rating. Der Abstand ist der Aufschlag, den Anleger für das Ausfallrisiko und die geringere Handelbarkeit dieser Anleihen verlangen.

## Warum sie für Marktstress oder Fallhöhe zählt
Kreditspreads sind im Bericht einer der stärksten Stressindikatoren; dort steht der Risikoaufschlag für Hochzinsanleihen (HY-OAS) auf Rang 2 (docs/recherche.md, Abschn. 2). Weil FRED die ICE-Reihen nur noch für drei Jahre liefert, reicht deren Historie nicht für ein Perzentil. Als langer Ersatz mit Historie ab 1986 ist BAA10Y im offenen Punkt O-5 der Projektvorgaben genannt (CLAUDE.md); das Projekt nutzt ihn im Kreditblock, bis die ICE-Reihen fünf Jahre Historie haben (Entscheidung E-75).

## So liest du sie
- Ein hohes Perzentil heißt: Der Aufschlag ist gemessen an den letzten Jahren ungewöhnlich weit.
- Das Niveau zeigt anhaltende Anspannung; wie schnell sie zunimmt, zeigt die Kennzahl „Kreditspread Baa: Anstieg“.

## Grenzen und Fallstricke
- Investment Grade statt Hochzins: Der Spread schwankt weniger als der HY-OAS und reagiert auf Ausfallsorgen schwächer.
- Die Rendite der Baa-Anleihen wird ohne Optionsbereinigung gemessen, der HY-OAS mit; die Niveaus sind nicht vergleichbar.
- Lizenz Moody's: Die Daten dürfen laut Hinweis bei FRED ohne Zustimmung nicht kopiert oder weitergegeben werden; das Projekt nutzt sie wie die ICE-Reihen nur privat (Entscheidung E-75).

## Quellen
- FRED, St. Louis Fed: Reihe BAA10Y, Notes und Copyright-Hinweis, abgerufen 28.09.2026
- docs/recherche.md, Abschnitt 2 (Stand 25.09.2026)
- CLAUDE.md, offener Punkt O-5
- docs/umsetzungsplan.md, Entscheidung E-75 (28.09.2026)
