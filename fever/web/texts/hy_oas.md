# HY-OAS

## Kurzinfo
Risikoaufschlag von US-Hochzinsanleihen gegenüber Staatsanleihen (ICE BofA, Prozentpunkte). Hoch = Kreditstress. Perzentil vorerst nur über die Jahre seit 2023.

## Was die Kennzahl misst
Der Option-Adjusted Spread (OAS) ist der Renditeaufschlag einer Anleihe gegenüber der Zinskurve von US-Staatsanleihen, bereinigt um eingebettete Kündigungsrechte. Die Reihe von ICE BofA fasst alle auf US-Dollar lautenden Unternehmensanleihen ohne Investment-Grade-Rating zusammen, die am US-Markt öffentlich begeben wurden, gewichtet nach Marktwert (FRED, Reihe BAMLH0A0HYM2). Der Indikator nimmt das Niveau unverändert.

## Warum sie für Marktstress oder Fallhöhe zählt
Hochzinsanleihen reagieren früh auf schlechtere Finanzierungsbedingungen: Steigen ihre Aufschläge, verlangen Anleger mehr Ausgleich für Ausfallrisiken. Der Bericht setzt den HY-OAS auf Rang 2 seiner Rangliste, mit der Höchstnote für Evidenz (docs/recherche.md, Abschn. 2). Seit dem 29.09.2026 zählt sein Niveau im Block Kredit/Funding (Entscheidung E-90). Einen sehr engen Spread nennt der Bericht zugleich als Zeichen von Selbstgefälligkeit, also als mögliche Komponente der Fallhöhe (Abschn. 4.3, Schritt 4); diese Rolle übernimmt vorerst der Kreditspread Baa mit seiner langen Historie (E-85).

## So liest du sie
- Ein steigender Spread heißt: Kredit für schwächere Unternehmen wird teurer.
- Ein hohes Perzentil heißt hier nur: hoch gemessen an den Jahren seit 2023. Krisen wie 2008 oder 2020 liegen nicht im Fenster; der Wert selbst ist deshalb aussagekräftiger als sein Perzentil.
- Ein sehr niedriger Spread heißt nicht Sicherheit, sondern wenig Puffer (Bericht, Abschn. 4.3, Schritt 4).
- Zusammen mit CCC−BB lesen: Weitet sich vor allem der Abstand der schwächsten Bonitäten, trifft der Stress zuerst die Schwächsten.

## Grenzen und Fallstricke
- FRED liefert die ICE-Reihen seit April 2026 nur noch für drei Jahre (FRED, ebenda). Das Dashboard archiviert jeden Tag lokal; das Perzentil beginnt, sobald drei Jahre vorliegen (Entscheidung E-82), und misst sich bis auf Weiteres an einer ruhigen Phase ohne große Kreditkrise. Schon ein mäßiger Anstieg kann deshalb als Extrem erscheinen.
- Der Anstieg über 20 Handelstage und die Rot-Regel nutzen weiter den Kreditspread Baa mit Historie ab 1986 (E-75).
- Lizenz: ICE Data Indices untersagt die Wiedergabe ohne schriftliche Zustimmung (FRED, ebenda). Charts mit dieser Reihe nur für dich selbst verwenden.

## Quellen
- FRED, St. Louis Fed: Reihe BAMLH0A0HYM2, Notes, abgerufen 27.09.2026
- docs/recherche.md, Abschnitte 2 und 4.3 (Stand 25.09.2026)
- docs/umsetzungsplan.md, Entscheidungen E-75 (28.09.2026), E-82, E-85 und E-90 (29.09.2026)
