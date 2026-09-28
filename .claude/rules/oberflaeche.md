---
paths:
  - "fever/web/**"
  - "assets/**"
---
# Oberfläche (Phase 1, Entscheidungen vom 25.09.2026)

Details, Begründungen und Entscheidungsprotokoll (E-1 bis E-7): `docs/umsetzungsplan.md`, Abschnitte 2 und 7. Dash 4.x und Plotly 7.x sind neuer als das Trainingswissen vieler Modelle: Signaturen im installierten Paket nachsehen, nicht raten.

## Kennzahlen und Erklärungen
- Kennzahl = jede angezeigte Größe: Indikatoren aus `series.toml`, Blockscores, Stress, Fallhöhe, Ampel, Konfidenz, Diffusionsindex.
- Jede Kennzahl erscheint über die gemeinsame Kopf-Komponente: Name als Link auf `/kennzahl/<id>`, daneben ein Info-Symbol mit Kurzinfo. Die Kurzinfo ist ein reiner CSS-Tooltip über ein `data-`-Attribut, sichtbar bei `:hover` und `:focus` (Antippen auf Touchgeräten), als Klartext und nie als HTML.
- Die Texte liegen in `fever/web/texts/<id>.md` nach `docs/leitfaden-erklaertexte.md`. Ohne Text erscheint keine Kennzahl in der Oberfläche; ein Test erzwingt das.
- Steckbrief und „Schwellen und Farben“ werden aus `series.toml` bzw. `scoring.toml` erzeugt. Schwellenzahlen stehen nie im Freitext.
- Einzelkennzahlen: neutrale Perzentil-Farbskala plus Markierung „erhöht“ ab der Diffusionsschwelle aus `scoring.toml`. Die Ampelfarben Grün, Gelb, Orange und Rot sind der Gesamtampel vorbehalten und stehen immer mit Text, nie als Farbe allein.

## Charts
- Jeder Chart entsteht über die Fabrikfunktion in `fever/web/figures.py`, als einfaches Dict im plotly.js-Format (Datum als ISO-Text), nie als `go.Figure`: dessen Prüfung und Kopien kosteten rund 70 % der Seitenzeit (28.09.2026). Die Tests prüfen jede Figur mit `go.Figure`.
- Zoom, Verschieben und Doppelklick-Reset (Plotly-Standard); `scrollZoom` aus.
- Zeitreihen haben Zeitraum-Buttons „1 M, 6 M, 1 J, 5 J, Max“, keinen Rangeslider.
- PNG-Export über die Modebar (`scale=2`, Dateiname mit Kennzahl und Datum), `displaylogo=False`, `showSendToCloud=False` (Plotly.js 4 lädt sonst per „Share chart…“ Chart und Daten zu Plotly Cloud hoch).
- Titel, Quelle, letztes Beobachtungsdatum und Abrufzeit stehen als Annotation im Chart selbst, damit exportierte Bilder datiert sind; Abstand zur Achse in Pixeln (`yshift`), nicht als Anteil der Plot-Höhe.
- US-Rezessionen (FRED `USREC`, E-56) als graue Flächen hinter den Linien in allen Zeitreihen-Charts, mit Hinweis in der Datierung; nur Anzeige.
- Der Graph steckt in `.chart-box` mit fester Höhe (`responsive` ohne Elternhöhe fällt nach einem Relayout auf 0 px); Vollbild-Button in eigener Zeile über dem Chart, nie über der Modebar.
- Vollbild per CSS-Overlay (ohne Fullscreen-API), Druck/PDF per `assets/print.css`, immer hell druckbar.
- `uirevision` fest setzen, damit die 5-Minuten-Aktualisierung den Zoom nicht zurücksetzt.
- `connectgaps=False`; veraltete Abschnitte sichtbar absetzen, nie interpolieren.
- `separators=",."` und numerische Datumsformate (`%d.%m.%Y`).
- In Plotly-Titeln, Annotationen und Hovertexten nur Texte aus der Konfiguration und selbst formatierte Werte, nie Rohtexte aus Quellen (Plotly interpretiert eine HTML-Teilmenge).

## Übersicht und Ansichten (Bericht 6.3; eine Version seit E-67)
- `/` ist die Übersicht (Ansicht 1: Karten, Ampelmatrix, Quellen); `/ansicht/<name>` die Ansichten 2–7; Navigation in einer Zeile. Die alte Adresse `/uebersicht-b` leitet auf `/` um.
- Reine Anzeigereihen sind Kennzahlen in `texts.DISPLAYS`: mit Text, Steckbrief und „nur Anzeige, kein Score“; nie in einem Score.
- Linienfarben in der Reihenfolge der Referenzpalette; ab drei Linien Endbeschriftungen. Violett = markierte Phasen (Backwardation, Inversion), Grau = Rezessionen, Statusfarben nur für die Ampel und die Ampelmatrix.
- Verläufe der Ansichten starten mit der ganzen Historie ab dem ersten Wert; die Erklärseiten mit 5 Jahren.
- Ansicht 7 ist ein statischer Rahmen mit eigenen Callbacks; Schalter und Auswahl tragen `persistence`, damit die Aktualisierung sie nicht zurücksetzt. Perzentilbänder kommen aus dem Scoring (Spalten `band_p10/p50/p90`), die Oberfläche rechnet sie nie selbst.
- „So fließt der Wert in den Bereich ein“ auf der Erklärseite jedes Indikators wird aus `series.toml` und `scoring.toml` erzeugt (`texts.contribution`); die heutige Rolle kommt aus den gespeicherten Scores.
- Unter jedem Verlauf steht der Hinweis, dass je Beobachtung der neueste Stand zählt (`views.HISTORY_NOTE`).

## Aktualität
- `dcc.Interval` alle 5 Minuten liest Daten und Status neu.
- Kopfzeile: letzte Worker-Aktualisierung und letzte Seitenaktualisierung.
- Banner bei fehlender Migration (E-70), bei überfälligem Worker-Heartbeat und bei verlorener Verbindung (clientseitig über die Browserzeit der letzten erfolgreichen Antwort).
- Jeder Wert zeigt Beobachtungsdatum, Abrufzeit (Europe/Berlin, MEZ/MESZ) und relatives Alter. „Veraltet“ wird ausgegraut, schraffiert und als Text markiert.

## Ladezeit (28.09.2026, E-77, E-78)
- Lange Lesezugriffe in `fever/web/db.py` tragen `@per_data_version`: Das Ergebnis gilt bis zur nächsten gespeicherten Beobachtung oder zum nächsten Scoring-Lauf. Aufrufer verändern es nie.
- Abfragen lesen nur die Spalten, die der Chart braucht; für einen letzten Wert keine ganze Historie.
- gunicorn mit einem Thread: Callbacks in parallelen Threads bremsen sich über den GIL gegenseitig aus.
- Vor und nach Änderungen an Seiten messen (Methode: `docs/umsetzungsplan.md`, Abschnitt 10).

## Gestaltung
- Hell/dunkel folgt dem System: CSS-Variablen in `assets/base.css`, Plotly-Templates `fever_light` und `fever_dark` (`figures.TEMPLATES`, in jede Figur eingebettet), Umschaltung über `assets/theme.js` und einen `dcc.Store`.
- Systemschriften, `tabular-nums`, Karten im CSS-Grid; die Übersicht wird zuerst für 390 px Breite entworfen.
- Nur lokale Ressourcen. Ein Test prüft, dass das ausgelieferte HTML keine externe URL enthält.
- Rangfolge bei Zielkonflikten: fachliche Korrektheit, Aktualität, Lesbarkeit, Schönheit.
