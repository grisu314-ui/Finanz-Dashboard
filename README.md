# Finanz-Dashboard („Fieberthermometer“)

Selbst gehostetes Web-Dashboard, das den Stresszustand des US- und des globalen Aktienmarkts anzeigt: **akuter Stress** und **Fallhöhe** als zwei getrennte Achsen, kombiniert zu einer vierstufigen Ampel. Betrieb als Docker-Compose-Stack auf einem Raspberry Pi im Heimnetz, ein Nutzer, nur öffentliche Marktdaten.

Zweck ist Regime- und Risikoanzeige, **keine Crash-Prognose, keine Handelssignale, keine Anlageberatung.**

## Status

Stand 25.09.2026: **Planung abgeschlossen, M0 erledigt** (Projektgerüst, Docker-Image für den Pi, Compose, Laden der Konfiguration, Tests). Noch nicht lauffähig: Datenabruf (ab M3) und Oberfläche (ab M6). Fortschritt: `docs/umsetzungsplan.md`, Abschnitt 1.

## Dokumentation

| Du willst … | Lies |
|---|---|
| das Dashboard auf dem Pi einrichten, aktualisieren, sichern | [`docs/einrichtung.md`](docs/einrichtung.md) |
| verstehen, was das Dashboard zeigt und wie man es bedient | [`docs/bedienung.md`](docs/bedienung.md) |
| wissen, was gebaut wird, was entschieden und was offen ist | [`docs/umsetzungsplan.md`](docs/umsetzungsplan.md) |
| die fachliche Grundlage (Indikatoren, Methodik, Quellen) | [`docs/recherche.md`](docs/recherche.md) |
| Erklärtexte für Kennzahlen schreiben | [`docs/leitfaden-erklaertexte.md`](docs/leitfaden-erklaertexte.md) |
| als KI am Projekt weiterarbeiten | [`CLAUDE.md`](CLAUDE.md), dann `docs/umsetzungsplan.md`; Regeln in `.claude/rules/` |
