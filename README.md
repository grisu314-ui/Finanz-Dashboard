# Finanz-Dashboard („Fieberthermometer“)

Selbst gehostetes Web-Dashboard, das den Stresszustand des US- und des globalen Aktienmarkts anzeigt: **akuter Stress** und **Fallhöhe** als zwei getrennte Achsen, kombiniert zu einer vierstufigen Ampel. Betrieb als Docker-Compose-Stack auf TrueNAS im Heimnetz, verwaltet mit Dockge (bis 26.09.2026 war ein Raspberry Pi geplant), ein Nutzer, nur öffentliche Marktdaten.

Zweck ist Regime- und Risikoanzeige, **keine Crash-Prognose, keine Handelssignale, keine Anlageberatung.**

## Status

Stand 26.09.2026: **M0 bis M2 erledigt, M3 umgesetzt**: Docker-Image, Datenbank mit geschütztem Archiv, Backup und Wiederherstellung, 23 Datenreihen von Cboe und FRED mit Prüfung und Veröffentlichungszeitpunkt, Worker mit Abrufplan und Healthcheck. Offen in M3: die Einrichtung auf TrueNAS nach [`docs/einrichtung.md`](docs/einrichtung.md). Die Oberfläche folgt ab M6. Fortschritt: `docs/umsetzungsplan.md`, Abschnitt 1.

## Dokumentation

| Du willst … | Lies |
|---|---|
| das Dashboard auf TrueNAS mit Dockge einrichten, aktualisieren, sichern | [`docs/einrichtung.md`](docs/einrichtung.md) |
| verstehen, was das Dashboard zeigt und wie man es bedient | [`docs/bedienung.md`](docs/bedienung.md) |
| wissen, was gebaut wird, was entschieden und was offen ist | [`docs/umsetzungsplan.md`](docs/umsetzungsplan.md) |
| die fachliche Grundlage (Indikatoren, Methodik, Quellen) | [`docs/recherche.md`](docs/recherche.md) |
| Erklärtexte für Kennzahlen schreiben | [`docs/leitfaden-erklaertexte.md`](docs/leitfaden-erklaertexte.md) |
| als KI am Projekt weiterarbeiten | [`CLAUDE.md`](CLAUDE.md), dann `docs/umsetzungsplan.md`; Regeln in `.claude/rules/` |
