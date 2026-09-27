# Excess CAPE Yield

## Kurzinfo
Ertragsrendite der US-Aktien aus dem zyklisch bereinigten KGV (1/CAPE) minus realer Zins zehnjähriger Staatsanleihen. Niedrig = teure Aktien; mehr Fallhöhe.

## Was die Kennzahl misst
Das Shiller-CAPE teilt den Kurs des S&P 500 durch den Durchschnitt der inflationsbereinigten Gewinne der letzten zehn Jahre. Sein Kehrwert ist eine Art Ertragsrendite der Aktien. Die Excess CAPE Yield zieht davon den realen Zins ab: die Rendite zehnjähriger US-Staatsanleihen minus die durchschnittliche Inflation der letzten zehn Jahre. So steht es in Robert J. Shillers Datendatei; das Projekt hat die Spalte für alle Monate nachgerechnet (docs/umsetzungsplan.md, Ergebnis M4c). Der Wert ist ein Anteil, 0,01 entspricht einem Prozentpunkt.

## Warum sie für Marktstress oder Fallhöhe zählt
Die Excess CAPE Yield ist eine Art Risikoprämie der Aktien gegenüber realen Anleihen: Sie sagt, wie viel mehr Ertrag Aktien im Verhältnis zu ihrem Preis bieten. Ist sie niedrig, sind Aktien teuer, gemessen an dem, was sichere Anlagen real bringen, und ein Rückschlag hat mehr Raum. Der Bericht setzt sie, umgedreht, als erste Komponente der Fallhöhe ein und bewertet sie mit guter Evidenz, aber ohne Vorlauf für den Zeitpunkt (docs/recherche.md, Abschn. 2 und 4.3, Schritt 4). Deshalb gilt hier niedrig = mehr Fallhöhe.

## So liest du sie
- Die Orientierung ist umgedreht: Ein hohes Perzentil entsteht bei niedriger Excess CAPE Yield, also bei teuren Aktien.
- Hohe Fallhöhe heißt nicht, dass bald etwas passiert; Bewertungen können jahrelang hoch bleiben.
- Steigt der reale Zins, sinkt die Excess CAPE Yield auch ohne Kursanstieg.

## Grenzen und Fallstricke
- Monatlich und spät; die Werte des laufenden Monats in Shillers Datei sind vorläufig und werden später ersetzt.
- Einschätzung: Bewertungsmaße sind über Jahrzehnte gewandert, etwa durch veränderte Bilanzierung und Zinsniveaus; das rollierende Fenster dämpft das, beseitigt es aber nicht.
- Die Daten enthalten S&P-Werte: nur private Nutzung, keine Weitergabe.

## Quellen
- Robert J. Shiller, Online Data (ie_data.xls, Spalte „Excess CAPE Yield“), abgerufen über das Projekt ab 26.09.2026
- docs/recherche.md, Abschnitte 2 und 4.3 (Stand 25.09.2026)
- docs/umsetzungsplan.md, Entscheidung E-43 und Ergebnis M4c (26.09.2026)
