# CLAUDE.md – Fieberthermometer

<!-- Pflegehinweise (werden vor dem Laden entfernt, kosten keinen Kontext):
- Unter 200 Zeilen halten. Eine Regel kommt nur dazu, wenn Claude ohne sie nachweislich Fehler macht.
- Harte Sperren gehören in .claude/settings.json (permissions.deny, z. B. Read(./.env)) oder in Hooks. CLAUDE.md ist Kontext, keine Durchsetzung.
- Sobald Code existiert: Architektur-Abschnitt auf Nicht-Ableitbares kürzen; Docker-Regeln können als pfadgebundene Regel nach .claude/rules/ wandern. Die Scoring-Regeln bleiben hier.
- Entschiedene offene Punkte unten mit Antwort eintragen. -->

Du arbeitest an genau einem Projekt: einem selbst gehosteten Web-Dashboard („Fieberthermometer"), das den Stresszustand des US- und des globalen Aktienmarkts anzeigt. Ein Nutzer, private Nutzung.

Ein Worker ruft öffentliche Marktdaten ab und speichert sie mit Zeitstempel. Daraus entstehen zwei Scores (akuter Stress, Fallhöhe) und eine Ampel; eine Dash-Oberfläche stellt alles interaktiv dar. Betrieb als Docker-Compose-Stack auf einem Raspberry Pi (linux/arm64).

Zweck ist Regime- und Risikoanzeige, keine Crash-Prognose. Ziel ist genau die hier beschriebene Anwendung, korrekt und von einer Einzelperson wartbar – nicht „eine möglichst gute Anwendung".

## Quellen der Wahrheit

- `docs/recherche.md`: Recherchebericht, Stand 25.09.2026 – Indikatorbewertung (Abschn. 1–3), Methodik (4.3), Datenquellen (6.1), Ansichten (6.3). Lies nur den Abschnitt, den die Aufgabe betrifft.
- Diese Datei entscheidet. Sie ersetzt die Berichtsabschnitte 6.2 (Architektur) und 6.4 (Ausbaustufen).
- Abschnitt 5 des Berichts ist eine Momentaufnahme: keine Werte daraus in Code, Konfiguration oder Tests.
- Endpoints und Serien-IDs im Bericht sind teils unverifiziert (markiert mit (*) oder „prüfen").
- Widersprüche zwischen Bericht und dieser Datei oder innerhalb eines der beiden benennst du, statt still eine Variante umzusetzen.

## Phasen – gebaut wird nur die aktuelle

**Aktuelle Phase: 1.** Umfang aus späteren Phasen: erst fragen.

1. MVP:
   - Worker, Speicher, Serienkatalog, Backups, Healthchecks.
   - Quellen nur über offizielle APIs, CSVs und Datei-Downloads ohne Login: Cboe, FRED/ALFRED, CFTC, EZB, OFR, Fed-Board (EBP), Shiller-CAPE, FINRA Margin Debt.
   - Scoring nach Bericht 4.3, Schritte 1–6, Aggregation nur Stufe 1.
   - Ansichten 1–7 aus Bericht 6.3, soweit Daten vorhanden, dazu „Datenstand".
2. Validierungsansicht (Schritt 7: Walk-forward, ROC, Vorlauf, Vergleich mit reinem VIX-Filter), Alerts, AAII, Aggregation Stufe 2 (korrelationsgewichtet), revisionsgenaue Rückrechnung.
3. Optionsdaten (ThetaData/IBKR: Termstruktur, Skew, GEX), Logit-Modell (Stufe 3).

## Stack (festgelegt)

| Aspekt | Festlegung |
|---|---|
| Sprache | Python ≥ 3.11 (`tomllib`), Minor-Version im Dockerfile gepinnt |
| Oberfläche | Dash (Plotly) unter gunicorn, 1–2 Prozesse |
| Berechnung | pandas, numpy |
| Datenbank | SQLite im WAL-Modus; SQLAlchemy Core, Migrationen mit Alembic |
| Abrufe | requests, synchron |
| Konfiguration | TOML in `config/`, Secrets aus `.env` |
| Tests | pytest, ohne Netzwerkzugriff |
| Deployment | `docker-compose.yml`: Dienste `web` und `worker` aus einem Image |
| Zielplattform | Raspberry Pi, 64-Bit-OS (linux/arm64) |

Bewusste Abweichungen vom Bericht:
- SQLite statt DuckDB: `web` und `worker` sind getrennte Prozesse, DuckDB erlaubt aber nur einen schreibenden Prozess oder mehrere nur lesende, nicht beides zugleich.
- Kein Prefect, Grafana oder Streamlit: zu schwer für den Pi oder doppelt.
- Shiller-CAPE und FINRA Margin Debt schon in Phase 1, sonst bleibt die Fallhöhe-Achse leer.

Kein Node, kein npm, kein Build-Schritt; eigene CSS- und JS-Dateien liegen in `assets/`. Alternative Stacks schlägst du nicht vor.

## Befehle (einrichten und hier aktuell halten)

- `pytest -q`: alle Tests
- `docker buildx build --platform linux/arm64 .`: Build-Probe auf dem Entwicklungsrechner (unter x86 mit QEMU/binfmt)
- `docker compose up -d --build`: Start und Update auf dem Pi
- `docker compose run --rm worker python -m fever.backup`: sofortiges Backup
- Migration, auch bei der Ersteinrichtung: `docker compose stop` → Backup → `docker compose run --rm worker alembic upgrade head` → `docker compose up -d`
- `docker compose logs -f worker`

## Architektur

```
fever/sources/     je Quelle ein Modul: fetch → parse → validate
fever/store/       Tabellen (SQLAlchemy Core), Lese- und Schreibfunktionen
fever/scoring/     reine Berechnung, importiert nichts aus web/ oder store/
fever/worker.py    Abrufschleife, Scoring-Lauf, Heartbeat
fever/backup.py    VACUUM INTO und Aufbewahrung; vom Worker und direkt aufrufbar
fever/web/         Dash-App: Layouts, Callbacks, Health-Endpunkt
config/series.toml   Rohreihen (Quelle, ID, Frequenz, Veröffentlichungszeit, Verzug, Toleranz,
                     Plausibilitätsgrenzen) und abgeleitete Indikatoren (Transformation,
                     Orientierung, Block bzw. Fallhöhe)
config/scoring.toml  Fenster, Mindesthistorie, Schwellen, Halbwertszeiten, Matrixregeln
migrations/  tests/  tests/fixtures/  docs/
```

- Nur der Worker schreibt. `web` setzt auf jeder Verbindung `PRAGMA query_only = ON` und berechnet keine Scores.
- Der Worker ist eine einfache Schleife, die alle 15 Minuten fällige Abrufe ausführt; kein Scheduler-Framework, kein Cron im Container. Nach neuen Daten oder geänderter `scoring.toml` rechnet er die Scores neu und speichert sie.
- Ausgangspunkt für `series.toml` sind die Berichtsabschnitte 2 und 6.1.

## Was ausdrücklich NICHT gebaut wird

Ein Assistent ergänzt diese Dinge erfahrungsgemäß ungefragt. Hier nicht. Bei zwingendem Grund: erst fragen, nicht bauen.

- Kein Login, keine Benutzerverwaltung, keine Sessions. Zugangsschutz ist Infrastruktur (O-3), nie Anwendungscode.
- Keine Konto-, Positions- oder Orderfunktionen, auch nicht über IBKR. Nur Marktdaten.
- Keine Handelssignale, keine Renditeprognosen, keine „Crash-Wahrscheinlichkeit" ohne validiertes Modell.
- Kein Machine Learning. Im Backtest optimierte Gewichte oder Schwellen gehen nie automatisch in den Produktivscore; bei so wenigen Krisen wäre das Overfitting. Einziges geschätztes Modell ist das Logit in Phase 3.
- Keine Intraday-Daten, kein Streaming, keine WebSockets.
- Kein Celery, kein Redis, keine Queue, kein Caching-Layer, kein asyncio.
- Kein Postgres, keine DuckDB, keine Abstraktion für einen Datenbankwechsel.
- Keine Telemetrie, keine externen CDNs, Webfonts oder Stylesheets per URL (auch nicht `dbc.themes`). Der Browser lädt nur vom Pi.
- Kein Scraping gegen Nutzungsbedingungen, keine Umgehung von Lizenzgrenzen, keine Weitergabe lizenzierter Daten (ICE, Moody's, S&P).
- Keine Optimierung ohne Messung: keine vorsorglichen Indizes, keine Pagination, keine Denormalisierung.
- Keine generischen Basisklassen oder Plugin-Mechanismen. Zwischen einfacher und erweiterbarer Lösung wählst du die einfache.

Entscheidet der Nutzer gegen eine Funktion, trägst du sie hier ein.

## Arbeitsweise

1. Lesen, dann planen: Ansatz, betroffene Dateien, Schritte, Risiken, Tests. Dabei keine Dateiänderung.
2. Auf ausdrückliche Freigabe warten. Ausnahme: Der Diff lässt sich in einem Satz beschreiben und berührt weder Scoring noch Datenbankschema.
3. Umsetzen.
4. Prüfen:
   - `pytest -q` muss grün sein.
   - Nach Änderungen an Dockerfile oder Compose: arm64-Build-Probe.
   - Nach Oberflächenänderungen: Smoke-Test (App startet, `/_dash-layout` und Health-Endpunkt liefern 200), wo möglich Sichtprüfung im Browser.
   - Was sich nicht prüfen ließ, benennst du als offen.
5. Selbst-Review: Funktion, Fehlerbehandlung, Randfälle, Einschränkungen. Belege statt Erfolgsbehauptungen (Befehl und Ausgabe), dazu der pytest-Befehl, der die Änderung abdeckt.

- Spekuliere nie über Code, den du nicht geöffnet hast. Erfinde keine Funktionen oder Parameter; bei unsicherer Signatur sag es.
- Neue Quelle: Endpoint real abrufen, Antwort in eine Datei schreiben und nur Anfang und Ende ansehen (ganze Historien füllen den Kontext), gekürzt als Fixture in `tests/fixtures/` ablegen, dann Parser und Test schreiben.
- Beim Kompaktieren erhalten: geänderte Dateien, Testbefehle, Stand der offenen Punkte.

## Fachliche Korrektheit hat Vorrang

Ein falscher Score fällt nicht auf, bis die Ampel eine falsche Lage zeigt.

- **Kein Look-ahead:** Der Score für Tag t nutzt nur Beobachtungen, die an t veröffentlicht waren (Beobachtungsdatum + Verzug ≤ t). Nie über die Gesamthistorie normieren, auch nicht per z-Score.
- Rückfüllung ohne Vintage: Veröffentlichung = Beobachtungsdatum + konfigurierter Verzug, als geschätzt markiert.
- Revisionen werden gespeichert. Einzige Ausnahme vom Look-ahead-Verbot in Phase 1: Je Beobachtung zählt der neueste Stand; die Historienansicht weist darauf hin.
- Fehlende oder veraltete Werte nie als 0, 50 oder Mittelwert einsetzen und nie über die Toleranz ihrer Frequenz hinaus vortragen. Veraltete Indikatoren fallen aus dem Blockmedian und senken die Konfidenz; ein Block ohne gültigen Indikator fehlt und wird nicht geschätzt.
- Indikatoren unterhalb der Mindesthistorie werden angezeigt, gehen aber nicht in den Score ein.
- Die Orientierung (hoch = mehr Stress bzw. mehr Fallhöhe) steht je Indikator explizit in `series.toml`.
- Stress und Fallhöhe werden nie multipliziert, nur über die Matrixregeln kombiniert.
- Parameter stehen nur in `config/scoring.toml`, Startwerte aus Bericht 4.3. Sie ändern sich nur auf Anweisung, auch wenn ein Backtest bessere Werte nahelegt.
- Pflichttests, vor jeder Scoring-Änderung grün:
  - Ergebnis für t identisch mit und ohne Beobachtungen nach t
  - Perzentil gegen ein handgerechnetes Beispiel mit Gleichständen
  - Veraltung, Toleranz und Konfidenz
  - Matrixregeln genau auf der Schwelle, Hysterese
  - Block ohne gültigen Indikator

**Fachliche Lücken beantwortest du nicht selbst.** Stößt du auf eine Festlegung, die einen Score verändert (Schwelle, Fenster, Sonderfall): anhalten, konkret fragen, begründeten Vorschlag machen. Ein unbemerkt geratener Parameter ist der teuerste Fehler dieses Projekts. Unvermeidliche Platzhalter sind in der Oberfläche sichtbar, nicht nur im Code.

## Anzeige und Datenaktualität

- Jeder Wert zeigt Quelle, Beobachtungsdatum und Abrufzeitpunkt (Europe/Berlin, mit Zeitzone).
- **Ein veralteter Wert, der wie ein aktueller aussieht, ist der gravierendste Fehler dieser Anwendung.** Werte älter als Frequenz plus Toleranz sind sichtbar als veraltet markiert.
- Ansicht „Datenstand": je Quelle letzter Erfolg, letzter Versuch, letzter Fehler.
- Abruf- und Plausibilitätsfehler werden geloggt, nicht gespeichert, und erscheinen im Datenstand. Kein leeres `except`, kein stiller Fehler.
- Oberfläche auf Deutsch mit Dezimalkomma und Datum TT.MM.JJJJ; Fachbegriffe wie VIX, OAS, Contango bleiben. Die Übersicht ist auf Smartphone-Breite lesbar.
- Daten werden nie als HTML gerendert (kein `dangerously_allow_html`).

## Datenbank und Daten

- Schema nur per Alembic-Migration; kein `metadata.create_all()`, keine Migration beim Containerstart.
- Jede Verbindung: `PRAGMA foreign_keys = ON`, WAL, `busy_timeout`.
- Beobachtungen nur anfügen, nie überschreiben. Schlüssel: (Reihe, Beobachtungsdatum, Vintage). Ein identischer Wert erzeugt keine Zeile, ein geänderter eine neue.
- Zeitstempel in UTC. Abrufe nach `America/New_York` planen; die Sommerzeit wechselt dort an anderen Tagen als in Berlin. Handelsfreie Tage sind kein Fehler.
- Rohantworten gzip-komprimiert unter `raw/` im Datenordner ablegen, nur bei geändertem Inhalt.
- Backup täglich per `VACUUM INTO` nach `backup/` mit begrenzter Aufbewahrung, zusätzlich vor jeder Migration. Nie `cp` auf die laufende Datenbank.
- **Das lokale Archiv der ICE-BofA-Spreads ist unwiederbringlich**: FRED und ALFRED liefern seit April 2026 nur noch drei Jahre. Nichts, was diese Daten löschen oder überschreiben kann, ohne Rückfrage.
- Entwicklung und Tests nie gegen die Produktivdatenbank; lokal gilt `data-dev/`. Migrationen zuerst auf einer Kopie eines Produktiv-Backups durchspielen.

## Raspberry Pi und Docker

- Nur Abhängigkeiten mit aarch64-Wheels, nichts, was auf dem Pi kompiliert; vor der Aufnahme prüfen.
- Ein Image für `web` und `worker`, `restart: unless-stopped`, Nicht-root-Benutzer (UID/GID per Build-Arg, Standard 1000).
- Datenordner als Bind-Mount auf lokalem Dateisystem (kein NFS/SMB: SQLite-WAL funktioniert dort nicht), Host-Pfad aus `.env` (O-2). Ins Image wird nie geschrieben.
- Logs nur auf stdout, in Compose begrenzt (`json-file` mit `max-size` und `max-file`), um das Speichermedium zu schonen.
- Healthchecks ohne Zusatzpakete (`python -c …`): `web` per HTTP-Endpunkt, `worker` per Alter des Heartbeats.
- Secrets nur in `.env` (wie `data*/` in `.gitignore`); im Repo liegt `.env.example` mit leeren Werten. Nie loggen, nie ins Image. `.env` liest du nicht. Einziges Secret derzeit: der FRED-API-Schlüssel.
- Ausgehende Verbindungen nur über einen zentralen HTTP-Client mit Host-Allowlist, Timeouts, Backoff und eigenem User-Agent; Ratenlimits der Quellen einhalten.
- Den Web-Port nur so veröffentlichen, wie in O-3 entschieden.

## Abhängigkeiten und Sprache

- Neue Bibliothek nur mit Zweck in einem Satz, gepinnter Version in `requirements.txt` und geprüftem aarch64-Wheel. Zurückhaltung ist die Vorgabe: nichts, was sich in unter 50 Zeilen selbst schreiben lässt.
- Code, Bezeichner, Kommentare und Commits auf Englisch; Oberfläche, Fehlermeldungen, `docs/` und Antworten an mich auf Deutsch.
- Einheitliche Begriffe im Code: `series` (Rohreihe), `indicator` (abgeleitet), `block`, `stress` (akuter Stress), `vulnerability` (Fallhöhe), `vintage` (Stand).

## Kommunikation

- Keine Floskeln, kein Lob, keine Beschönigung. Direkt und knapp, Fokus auf Korrektheit.
- Jede Antwort endet mit dem Abschnitt „Offene Fragen": Entscheidungen, die ich treffen muss, deine Annahmen, Stand der offenen Punkte – auch wenn nichts Neues dazukam.
- Jede Entscheidung stellst du zusätzlich als Auswahlfrage über AskUserQuestion: Empfehlung zuerst und gekennzeichnet, je Option ein Satz zur Folge.
- Ist eine Vorgabe inkonsistent, fachlich falsch oder gegen das Projektinteresse gerichtet – auch in dieser Datei oder im Bericht –, sag es sachlich.
- Technische Schulden benennst du, behebst sie aber nicht ungefragt im selben Schritt.

## Offene Punkte

Vor der Umsetzung des betroffenen Teils klären; Entschiedenes hier mit Antwort eintragen.

| Nr. | Frage | Bis zur Entscheidung |
|---|---|---|
| O-1 | Kursquelle für ETFs und Indexmitglieder (RSP/SPY, Sektor- und Größenverhältnisse, Breite). FRED `SP500` reicht nur 10 Jahre zurück, genügt aber für VRP und Aktien-Anleihen-Korrelation | VRP und Korrelation aus FRED `SP500`; übrige Indikatoren weglassen, keine Quelle selbst wählen |
| O-2 | Pi-Modell, RAM, Speichermedium, Pfad des Datenordners (SSD statt SD-Karte empfohlen) | Pfad nur über `.env` |
| O-3 | Zugang: nur Heimnetz oder Tailscale, ggf. mit Basic-Auth-Pforte | Port nur an `127.0.0.1` |
| O-4 | Backup-Ziel außerhalb des Pi | nur lokale Backups |
| O-5 | ICE-Spreads: drei Jahre Historie bei fünf Jahren Mindesthistorie; betrifft Kreditblock und Rot-Regel. Optionen: BAA10Y (FRED, täglich ab 1986, Moody's-Lizenz) als langer Ersatz, Lizenz direkt bei ICE, befristete Ausnahme mit Kennzeichnung | archivieren und anzeigen, nicht in den Score |
| O-6 | Alert-Kanal (ntfy, Telegram, E-Mail), Phase 2 | – |
