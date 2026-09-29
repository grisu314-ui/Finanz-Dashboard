# Finanz-Dashboard („Fieberthermometer“)

Selbst gehostetes Web-Dashboard, das den Stresszustand des US- und des globalen Aktienmarkts anzeigt: **akuter Stress** und **Fallhöhe** als zwei getrennte Achsen, kombiniert zu einer vierstufigen Ampel. Betrieb als Docker-Compose-Stack auf TrueNAS im Heimnetz, verwaltet mit Dockge (bis 26.09.2026 war ein Raspberry Pi geplant), ein Nutzer, nur öffentliche Marktdaten.

Zweck ist Regime- und Risikoanzeige, **keine Crash-Prognose, keine Handelssignale, keine Anlageberatung.**

## Status

Stand 29.09.2026: **M0 bis M8 erledigt**, Seiten seit 28.09.2026 deutlich schneller (Ansicht Makro rund 3-mal, Visualisierung rund 6-mal), Entscheidungsrunde vom 29.09.2026 umgesetzt (Sahm-Regel mit Trendbedingung und SOS-Indikator als Ampelregeln, Rollen-Marken, Aktienquote und Kreditspread-Enge in der Fallhöhe, y-Achse passt sich beim Zoomen an), dazu die Validierung (M10, in der Entwicklungsumgebung geprüft, auf TrueNAS mit Migration 0004 einzuspielen): Rückblick, wie gut Ampel und Stress frühere Einbrüche ankündigten, verglichen mit einem einfachen VIX-Filter, dazu der Walk-forward-Test geschätzter Stress-Gewichte (M11: gleiche Gewichte bleiben besser). Vorhanden: Docker-Image, Datenbank mit geschütztem Archiv, Backup und Wiederherstellung, 81 Datenreihen von Cboe (Indizes, S&P 500 und VX-Futures), FRED (auch Nasdaq-Indizes für die Marktbreite und die Fed-Statistik Z.1), EZB, OFR, Fed, CFTC, Shiller und SEC (Top-10-Konzentration) mit Prüfung und Veröffentlichungszeitpunkt, Worker mit Abrufplan und Healthcheck; der Worker läuft auf TrueNAS. Das Scoring (M5) berechnet Stress, Fallhöhe und Ampel; die Oberfläche (M6, M7) zeigt sie unter Port 8003 nach Bericht 6.3: Übersicht mit Ampelmatrix, Themen-Ansichten, Visualisierung mit Heatmap, Perzentilbändern und Krisenmarken, Validierung, dazu Datenstand und Erklärseiten; US-Rezessionen als graue Flächen; Erklärtexte vom Nutzer freigegeben. Betrieb vom Branch `claude-raramo`. Fortschritt: `docs/umsetzungsplan.md`, Abschnitt 1.

## Dokumentation

| Du willst … | Lies |
|---|---|
| das Dashboard auf TrueNAS mit Dockge einrichten, aktualisieren, sichern | [`docs/einrichtung.md`](docs/einrichtung.md) |
| verstehen, was das Dashboard zeigt und wie man es bedient | [`docs/bedienung.md`](docs/bedienung.md) |
| wissen, was gebaut wird, was entschieden und was offen ist | [`docs/umsetzungsplan.md`](docs/umsetzungsplan.md) |
| die fachliche Grundlage (Indikatoren, Methodik, Quellen) | [`docs/recherche.md`](docs/recherche.md) |
| Erklärtexte für Kennzahlen schreiben | [`docs/leitfaden-erklaertexte.md`](docs/leitfaden-erklaertexte.md) |
| als KI am Projekt weiterarbeiten | [`CLAUDE.md`](CLAUDE.md), dann `docs/umsetzungsplan.md`; Regeln in `.claude/rules/` |
