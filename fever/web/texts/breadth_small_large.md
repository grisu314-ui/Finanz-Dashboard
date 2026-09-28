# Kleine gegen große Werte

## Kurzinfo
Relative Stärke der kleinen gegenüber den großen US-Aktien (Nasdaq US Small Cap gegen Large Cap). Niedrig = kleine Werte fallen zurück, mehr Stress.

## Was die Kennzahl misst
Nasdaq teilt die Aktien seines US-Gesamtmarktindex (Nasdaq US Benchmark) in Größenklassen; der Nasdaq US Small Cap Index bildet das Segment der kleinen Werte ab, der Nasdaq US Large Cap Index das der großen, beide nach frei handelbarem Börsenwert gewichtet (Nasdaq Global Indexes, Indexbeschreibung NQUSS). Der Indikator ist die Veränderung des Verhältnisses klein zu groß über ein festes Fenster von Handelstagen (Steckbrief unten). Er ersetzt das Verhältnis der ETFs IWM (Russell 2000) und SPY aus dem Bericht (Entscheidung E-68).

## Warum sie für Marktstress oder Fallhöhe zählt
Der Bericht zählt kleine gegen große Werte zur Marktbreite (docs/recherche.md, Abschn. 6.3, Ansicht 3). Einschätzung: Kleine Unternehmen hängen stärker von Bankkrediten und variablen Zinsen ab und haben weniger Puffer; verschlechtern sich Finanzierungsbedingungen oder Konjunkturerwartungen, fallen sie oft zuerst zurück.

## So liest du sie
- Ein hohes Perzentil heißt: Die kleinen Werte bleiben ungewöhnlich stark hinter den großen zurück.
- Allein ist die Kennzahl wenig aussagekräftig, weil kleine Werte auch lange Phasen struktureller Schwäche haben; aussagekräftiger ist sie, wenn andere Breitemaße gleichzeitig nachgeben.

## Grenzen und Fallstricke
- Historie ab 16.05.2011; die Finanzkrise 2008 liegt nicht im Fenster.
- Andere Abgrenzung der Größenklassen als der Russell 2000 des Berichts.
- Kursindizes ohne Dividenden.
- Lizenz Nasdaq, Inc. über FRED: nur private Nutzung, keine Weitergabe.

## Quellen
- Nasdaq Global Indexes: Nasdaq US Small Cap Index (NQUSS), Indexbeschreibung, abgerufen 28.09.2026
- FRED, St. Louis Fed: Reihen NASDAQNQUSS und NASDAQNQUSL, abgerufen 28.09.2026
- docs/recherche.md, Abschnitte 4.3 und 6.3 (Stand 25.09.2026)
- docs/umsetzungsplan.md, Entscheidungen E-68 und E-74 (28.09.2026)
