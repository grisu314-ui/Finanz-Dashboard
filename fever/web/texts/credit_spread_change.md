# Kreditspread Baa: Anstieg

## Kurzinfo
Veränderung des Kreditspreads Baa über ein festes Fenster von Handelstagen, in Prozentpunkten. Hoch = Spreads weiten sich schnell aus, mehr Stress.

## Was die Kennzahl misst
Grundlage ist der Abstand der Rendite von Unternehmensanleihen der Ratingstufe Baa zur zehnjährigen US-Staatsanleihe (FRED, Reihe BAA10Y). Die Kennzahl ist die Differenz zwischen dem heutigen Wert und dem Wert eine feste Zahl von Handelstagen zuvor (Steckbrief unten).

## Warum sie für Marktstress oder Fallhöhe zählt
Der Bericht empfiehlt für Kreditspreads neben dem Niveau die Veränderung über 20 Tage (docs/recherche.md, Abschn. 4.3, Schritt 1) und knüpft daran eine eigene Rot-Regel der Ampel (Abschn. 4.3, Schritt 5; die Regel steht unten). Einschätzung: Ein schneller Anstieg zeigt, dass Anleger ihre Einschätzung von Ausfallrisiken abrupt ändern; das ist oft wichtiger als das absolute Niveau. Das Projekt nutzt BAA10Y dafür, bis die ICE-Reihen fünf Jahre Historie haben (Entscheidung E-75).

## So liest du sie
- Ein hohes Perzentil heißt: Der Spread ist in kurzer Zeit ungewöhnlich stark gestiegen.
- Fällt der Spread wieder, sinkt die Kennzahl schnell; das Niveau kann dann noch hoch sein.

## Grenzen und Fallstricke
- Investment Grade statt Hochzins: Die Ausschläge sind kleiner als beim HY-OAS, auf den sich die Regel im Bericht bezieht.
- Ein einzelner Datenfehler an einem der beiden Tage verfälscht die Veränderung; die Plausibilitätsgrenzen fangen nur grobe Fehler ab.
- Lizenz Moody's: nur private Nutzung, keine Weitergabe (Entscheidung E-75).

## Quellen
- FRED, St. Louis Fed: Reihe BAA10Y, Notes und Copyright-Hinweis, abgerufen 28.09.2026
- docs/recherche.md, Abschnitt 4.3 (Stand 25.09.2026)
- docs/umsetzungsplan.md, Entscheidung E-75 (28.09.2026)
