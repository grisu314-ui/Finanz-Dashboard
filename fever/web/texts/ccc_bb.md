# CCC − BB

## Kurzinfo
Abstand der Risikoaufschläge der schwächsten Hochzinsanleihen (CCC und darunter) zu den besten (BB), Prozentpunkte. Hoch = Stress bei den Schwächsten. Nur Anzeige.

## Was die Kennzahl misst
Die Kennzahl ist die Differenz zweier ICE-BofA-Spreads gegenüber US-Staatsanleihen: CCC und darunter (FRED, Reihe BAMLH0A3HYC) minus BB (FRED, Reihe BAMLH0A1HYBB). Beide sind Option-Adjusted Spreads, also Renditeaufschläge bereinigt um Kündigungsrechte, gewichtet nach Marktwert. Die Differenz bildet das Dashboard für die Anzeige am selben Beobachtungstag.

## Warum sie für Marktstress oder Fallhöhe zählt
Der Bericht nennt die CCC-minus-BB-Differenz ausdrücklich neben dem HY-OAS (docs/recherche.md, Abschn. 2, Rang 2). Einschätzung: Wird Kredit knapp, trifft es zuerst die Schuldner mit der geringsten Bonität; weitet sich der Abstand, preist der Markt Ausfälle bei den Schwächsten ein, bevor der gesamte Hochzinsmarkt reagiert.

## So liest du sie
- Ein steigender Abstand heißt: Anleger unterscheiden stärker nach Bonität, die Risikobereitschaft sinkt.
- Zusammen mit dem HY-OAS lesen: Steigt nur CCC − BB, ist der Stress noch auf die Schwächsten begrenzt.

## Grenzen und Fallstricke
- Wie beim HY-OAS: nur drei Jahre Historie auf FRED, deshalb nur Anzeige (Entscheidung E-75).
- Die CCC-Klasse ist klein und schwankt stark; einzelne große Emittenten können sie verschieben (Einschätzung).
- Lizenz: ICE Data Indices untersagt die Wiedergabe ohne schriftliche Zustimmung; nur für dich selbst verwenden.

## Quellen
- FRED, St. Louis Fed: Reihen BAMLH0A3HYC und BAMLH0A1HYBB, Notes, abgerufen 27.09.2026
- docs/recherche.md, Abschnitt 2 (Stand 25.09.2026)
