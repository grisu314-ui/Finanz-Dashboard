# Finanz-Dashboard („Fieberthermometer“)

Selbst gehostetes Web-Dashboard, das den Stresszustand des US- und des globalen Aktienmarkts anzeigt: **akuter Stress** und **Fallhöhe** als zwei getrennte Achsen, kombiniert zu einer vierstufigen Ampel. Betrieb als Docker-Compose-Stack auf TrueNAS im Heimnetz, verwaltet mit Dockge (bis 26.09.2026 war ein Raspberry Pi geplant), ein Nutzer, nur öffentliche Marktdaten.

Zweck ist Regime- und Risikoanzeige, **keine Crash-Prognose, keine Handelssignale, keine Anlageberatung.**

## Status

Stand 26.09.2026: **M0 bis M2 und M4 bis M6 erledigt, M3 in Betrieb**: Docker-Image, Datenbank mit geschütztem Archiv, Backup und Wiederherstellung, 61 Datenreihen von Cboe (Indizes und VX-Futures), FRED, EZB, OFR, Fed, CFTC und Shiller mit Prüfung und Veröffentlichungszeitpunkt, Worker mit Abrufplan und Healthcheck; der Worker läuft auf TrueNAS. Das Scoring (M5) berechnet Stress, Fallhöhe und Ampel; die Oberfläche (M6) zeigt sie mit Datenstand, Erklärseiten und US-Rezessionen als graue Flächen unter Port 8003; darunter lassen sich die vier Bereiche mit allen 19 Score-Indikatoren aufklappen (M7a), die Themen-Ansichten folgen in M7. Fortschritt: `docs/umsetzungsplan.md`, Abschnitt 1.

## Dokumentation

| Du willst … | Lies |
|---|---|
| das Dashboard auf TrueNAS mit Dockge einrichten, aktualisieren, sichern | [`docs/einrichtung.md`](docs/einrichtung.md) |
| verstehen, was das Dashboard zeigt und wie man es bedient | [`docs/bedienung.md`](docs/bedienung.md) |
| wissen, was gebaut wird, was entschieden und was offen ist | [`docs/umsetzungsplan.md`](docs/umsetzungsplan.md) |
| die fachliche Grundlage (Indikatoren, Methodik, Quellen) | [`docs/recherche.md`](docs/recherche.md) |
| Erklärtexte für Kennzahlen schreiben | [`docs/leitfaden-erklaertexte.md`](docs/leitfaden-erklaertexte.md) |
| als KI am Projekt weiterarbeiten | [`CLAUDE.md`](CLAUDE.md), dann `docs/umsetzungsplan.md`; Regeln in `.claude/rules/` |
