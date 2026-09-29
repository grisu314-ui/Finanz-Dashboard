# Block Kredit/Funding

## Kurzinfo
Median der Perzentile von HY-OAS, Kreditspread Baa (Niveau, Anstieg), Excess Bond Premium, SOFR − IORB und OFR-Teilindizes Kredit und Funding (0–100). Hoch = Kreditstress.

## Was die Kennzahl misst
Der Block fasst zusammen, wie teuer und wie leicht Geld für Unternehmen und Finanzinstitute zu haben ist: der Risikoaufschlag für Hochzinsanleihen (HY-OAS, Niveau), der Kreditspread Baa (Rendite von Unternehmensanleihen der Ratingstufe Baa minus zehnjährige Staatsanleihe, als Niveau und als Anstieg), die Excess Bond Premium (der Teil der Risikoaufschläge von Unternehmensanleihen, der nicht durch erwartete Ausfälle erklärt ist), die Differenz SOFR − IORB (Zins für besicherte Übernachtkredite gegen den Zins, den Banken auf ihre Reserven bei der Fed erhalten) sowie die Teilindizes Kredit und Funding des OFR Financial Stress Index. Jeder Indikator wird in ein Perzentil gegenüber seiner eigenen Vergangenheit übersetzt; der Blockwert ist der Median der gültigen Perzentile.

## Warum sie für Marktstress oder Fallhöhe zählt
In kreditgetriebenen Abschwüngen wie 2000–02 und 2007–09 liefen laut Bericht Kreditaufschläge und Excess Bond Premium den Aktienmärkten Monate voraus (docs/recherche.md, Abschn. 3; dort als Einschätzung gekennzeichnet). Bei Liquiditätsschocks zeigten Funding-Signale dagegen nur Tage vorher Anspannung (ebenda). Der Block deckt damit beide Geschwindigkeiten ab: langsamen Kreditstress und plötzliche Engpässe am Geldmarkt.

## So liest du sie
- Ein hoher Wert heißt: Kredit wird teurer oder Refinanzierung schwieriger, und zwar gemessen an den letzten Jahren.
- Steigt der Block, während der Block Volatilität ruhig bleibt, baut sich Stress eher langsam auf.
- Ein Sprung nur bei SOFR − IORB deutet auf einen Engpass am Geldmarkt hin, nicht unbedingt auf Kreditangst.

## Grenzen und Fallstricke
- Der wichtigste Kreditindikator des Berichts, der HY-OAS, zählt seit dem 29.09.2026 als Niveau mit (Entscheidung E-90). FRED liefert die ICE-Reihen aber nur noch für drei Jahre; sein Perzentil misst sich deshalb vorerst nur an den Jahren seit 2023. Anstieg und Rot-Regel nutzen weiter den Kreditspread Baa (Moody's) mit Historie ab 1986 (E-75).
- Die Excess Bond Premium erscheint nur monatlich und mit Verzug; sie ist deshalb öfter veraltet und fällt dann aus dem Median.
- SOFR − IORB hat eine kurze Historie, weil es den IORB-Satz erst seit dem 29.07.2021 gibt (FRED, Reihe IORB).
- Einschätzung: HY-OAS und Kreditspread Baa messen Ähnliches und ziehen den Median gemeinsam; fehlen einzelne Werte, verschiebt er sich spürbar.

## Quellen
- docs/recherche.md, Abschnitte 2, 3 und 4.3 (Stand 25.09.2026)
- FRED, St. Louis Fed: Reihe IORB, Notes, abgerufen 26.09.2026
- docs/umsetzungsplan.md, Entscheidungen E-47 bis E-49 (26.09.2026), E-75 (28.09.2026) und E-90 (29.09.2026)
