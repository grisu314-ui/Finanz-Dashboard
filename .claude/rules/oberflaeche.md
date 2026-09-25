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
- Jeder Chart entsteht über die Fabrikfunktion in `fever/web/figures.py`.
- Zoom, Verschieben und Doppelklick-Reset (Plotly-Standard); `scrollZoom` aus.
- Zeitreihen haben Zeitraum-Buttons „1 M, 6 M, 1 J, 5 J, Max“, keinen Rangeslider.
- PNG-Export über die Modebar (`scale=2`, Dateiname mit Kennzahl und Datum), `displaylogo=False`.
- Titel, Quelle, letztes Beobachtungsdatum und Abrufzeit stehen als Annotation im Chart selbst, damit exportierte Bilder datiert sind.
- Vollbild per CSS-Overlay (ohne Fullscreen-API), Druck/PDF per `assets/print.css`, immer hell druckbar.
- `uirevision` fest setzen, damit die 5-Minuten-Aktualisierung den Zoom nicht zurücksetzt.
- `connectgaps=False`; veraltete Abschnitte sichtbar absetzen, nie interpolieren.
- `separators=",."` und numerische Datumsformate (`%d.%m.%Y`).
- In Plotly-Titeln, Annotationen und Hovertexten nur Texte aus der Konfiguration und selbst formatierte Werte, nie Rohtexte aus Quellen (Plotly interpretiert eine HTML-Teilmenge).

## Aktualität
- `dcc.Interval` alle 5 Minuten liest Daten und Status neu.
- Kopfzeile: letzte Worker-Aktualisierung und letzte Seitenaktualisierung.
- Banner bei überfälligem Worker-Heartbeat und bei verlorener Verbindung (clientseitig über die Browserzeit der letzten erfolgreichen Antwort).
- Jeder Wert zeigt Beobachtungsdatum, Abrufzeit (Europe/Berlin, MEZ/MESZ) und relatives Alter. „Veraltet“ wird ausgegraut, schraffiert und als Text markiert.

## Gestaltung
- Hell/dunkel folgt dem System: CSS-Variablen in `assets/base.css`, Plotly-Templates `fever_light` und `fever_dark`, Umschaltung über `assets/theme.js` und einen `dcc.Store`.
- Systemschriften, `tabular-nums`, Karten im CSS-Grid; die Übersicht wird zuerst für 390 px Breite entworfen.
- Nur lokale Ressourcen. Ein Test prüft, dass das ausgelieferte HTML keine externe URL enthält.
- Rangfolge bei Zielkonflikten: fachliche Korrektheit, Aktualität, Lesbarkeit, Schönheit.
