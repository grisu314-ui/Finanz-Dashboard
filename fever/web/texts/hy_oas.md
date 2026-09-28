# HY-OAS

## Kurzinfo
Risikoaufschlag von US-Hochzinsanleihen gegenüber Staatsanleihen (ICE BofA, Prozentpunkte). Hoch = Kreditstress. Nur Anzeige, bis die lokale Historie fünf Jahre umfasst (E-75).

## Was die Kennzahl misst
Der Option-Adjusted Spread (OAS) ist der Renditeaufschlag einer Anleihe gegenüber der Zinskurve von US-Staatsanleihen, bereinigt um eingebettete Kündigungsrechte. Die Reihe von ICE BofA fasst alle auf US-Dollar lautenden Unternehmensanleihen ohne Investment-Grade-Rating zusammen, die am US-Markt öffentlich begeben wurden, gewichtet nach Marktwert (FRED, Reihe BAMLH0A0HYM2).

## Warum sie für Marktstress oder Fallhöhe zählt
Hochzinsanleihen reagieren früh auf schlechtere Finanzierungsbedingungen: Steigen ihre Aufschläge, verlangen Anleger mehr Ausgleich für Ausfallrisiken. Der Bericht setzt den HY-OAS auf Rang 2 seiner Rangliste, mit der Höchstnote für Evidenz (docs/recherche.md, Abschn. 2) und nennt einen sehr engen Spread zugleich als Zeichen von Selbstgefälligkeit, also als mögliche Komponente der Fallhöhe (Abschn. 4.3, Schritt 4).

## So liest du sie
- Ein steigender Spread heißt: Kredit für schwächere Unternehmen wird teurer.
- Ein sehr niedriger Spread heißt nicht Sicherheit, sondern wenig Puffer (Bericht, Abschn. 4.3, Schritt 4).
- Zusammen mit CCC−BB lesen: Weitet sich vor allem der Abstand der schwächsten Bonitäten, trifft der Stress zuerst die Schwächsten.

## Grenzen und Fallstricke
- FRED liefert die ICE-Reihen seit April 2026 nur noch für drei Jahre (FRED, ebenda). Das Dashboard archiviert jeden Tag lokal, für ein Perzentil reicht die Historie aber noch nicht; deshalb nur Anzeige. Bis dahin steht der Kreditspread Baa (Moody's) im Score (Entscheidung E-75).
- Die Rot-Regel über den Anstieg des Kreditspreads nutzt aus demselben Grund vorerst den Kreditspread Baa (E-75).
- Lizenz: ICE Data Indices untersagt die Wiedergabe ohne schriftliche Zustimmung (FRED, ebenda). Charts mit dieser Reihe nur für dich selbst verwenden.

## Quellen
- FRED, St. Louis Fed: Reihe BAMLH0A0HYM2, Notes, abgerufen 27.09.2026
- docs/recherche.md, Abschnitte 2 und 4.3 (Stand 25.09.2026)
