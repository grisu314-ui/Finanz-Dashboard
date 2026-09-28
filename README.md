# Finanz-Dashboard („Fieberthermometer“)

Selbst gehostetes Web-Dashboard, das den Stresszustand des US- und des globalen Aktienmarkts anzeigt: **akuter Stress** und **Fallhöhe** als zwei getrennte Achsen, kombiniert zu einer vierstufigen Ampel. Betrieb als Docker-Compose-Stack auf TrueNAS im Heimnetz, verwaltet mit Dockge (bis 26.09.2026 war ein Raspberry Pi geplant), ein Nutzer, nur öffentliche Marktdaten.

Zweck ist Regime- und Risikoanzeige, **keine Crash-Prognose, keine Handelssignale, keine Anlageberatung.**

## Status

Stand 28.09.2026: **M0 bis M7 erledigt**: Docker-Image, Datenbank mit geschütztem Archiv, Backup und Wiederherstellung, 61 Datenreihen von Cboe (Indizes und VX-Futures), FRED, EZB, OFR, Fed, CFTC und Shiller mit Prüfung und Veröffentlichungszeitpunkt, Worker mit Abrufplan und Healthcheck; der Worker läuft auf TrueNAS. Das Scoring (M5) berechnet Stress, Fallhöhe und Ampel; die Oberfläche (M6, M7) zeigt sie unter Port 8003 nach Bericht 6.3: Übersicht mit Ampelmatrix, Themen-Ansichten, Visualisierung mit Heatmap, Perzentilbändern und Krisenmarken, dazu Datenstand und Erklärseiten; US-Rezessionen als graue Flächen. Fortschritt: `docs/umsetzungsplan.md`, Abschnitt 1.

## Dokumentation

| Du willst … | Lies |
|---|---|
| das Dashboard auf TrueNAS mit Dockge einrichten, aktualisieren, sichern | [`docs/einrichtung.md`](docs/einrichtung.md) |
| verstehen, was das Dashboard zeigt und wie man es bedient | [`docs/bedienung.md`](docs/bedienung.md) |
| wissen, was gebaut wird, was entschieden und was offen ist | [`docs/umsetzungsplan.md`](docs/umsetzungsplan.md) |
| die fachliche Grundlage (Indikatoren, Methodik, Quellen) | [`docs/recherche.md`](docs/recherche.md) |
| Erklärtexte für Kennzahlen schreiben | [`docs/leitfaden-erklaertexte.md`](docs/leitfaden-erklaertexte.md) |
| als KI am Projekt weiterarbeiten | [`CLAUDE.md`](CLAUDE.md), dann `docs/umsetzungsplan.md`; Regeln in `.claude/rules/` |
