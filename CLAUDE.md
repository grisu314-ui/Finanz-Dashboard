# CLAUDE.md – Fieberthermometer

<!-- Pflegehinweise (werden vor dem Laden entfernt, kosten keinen Kontext):
- Unter 200 Zeilen halten. Eine Regel kommt nur dazu, wenn Claude ohne sie nachweislich Fehler macht.
- Harte Sperren gehören in .claude/settings.json (permissions.deny, z. B. Read(./.env)) oder in Hooks. CLAUDE.md ist Kontext, keine Durchsetzung.
- Sobald Code existiert: Architektur-Abschnitt auf Nicht-Ableitbares kürzen; Docker-Regeln können als pfadgebundene Regel nach .claude/rules/ wandern. Die Scoring-Regeln bleiben hier.
- Entschiedene offene Punkte unten mit Antwort eintragen. -->

Du arbeitest an genau einem Projekt: einem selbst gehosteten Web-Dashboard („Fieberthermometer"), das den Stresszustand des US- und des globalen Aktienmarkts anzeigt. Ein Nutzer, private Nutzung.

Ein Worker ruft öffentliche Marktdaten ab und speichert sie mit Zeitstempel. Daraus entstehen zwei Scores (akuter Stress, Fallhöhe) und eine Ampel; eine Dash-Oberfläche stellt alles interaktiv dar. Betrieb als Docker-Compose-Stack auf TrueNAS (x86_64), verwaltet mit Dockge (E-21).

Zweck ist Regime- und Risikoanzeige, keine Crash-Prognose. Ziel ist genau die hier beschriebene Anwendung, korrekt und von einer Einzelperson wartbar – nicht „eine möglichst gute Anwendung".

## Quellen der Wahrheit

- `docs/recherche.md`: Recherchebericht, Stand 25.09.2026 – Indikatorbewertung (Abschn. 1–3), Methodik (4.3), Datenquellen (6.1), Ansichten (6.3). Lies nur den Abschnitt, den die Aufgabe betrifft.
- Diese Datei entscheidet. Sie ersetzt die Berichtsabschnitte 6.2 (Architektur) und 6.4 (Ausbaustufen).
- `docs/umsetzungsplan.md`: Meilensteine, Stand, Entscheidungsprotokoll, Übergabe. Regeln für Oberfläche (pfadgebunden) und Dokumentation: `.claude/rules/`.
- Abschnitt 5 des Berichts ist eine Momentaufnahme: keine Werte daraus in Code, Konfiguration oder Tests.
- Endpoints und Serien-IDs im Bericht sind teils unverifiziert (markiert mit (*) oder „prüfen").
- Widersprüche zwischen Bericht und dieser Datei oder innerhalb eines der beiden benennst du, statt still eine Variante umzusetzen.

## Phasen – gebaut wird nur die aktuelle

**Aktuelle Phase: 2** (seit 30.09.2026, Phase 1 abgenommen mit M9). Zuerst Alerts (M12, E-99; umgesetzt 30.09.2026, Einrichtung auf TrueNAS offen); die übrigen Punkte von Phase 2 erst nach Entscheidung des Nutzers. Umfang aus späteren Phasen: erst fragen.

1. MVP:
   - Worker, Speicher, Serienkatalog, Backups, Healthchecks.
   - Quellen nur über offizielle APIs, CSVs und Datei-Downloads ohne Login: Cboe, FRED/ALFRED (auch Nasdaq-Indizes, E-68), CFTC, EZB, OFR, Fed-Board (EBP, Z.1 über FRED), Shiller-CAPE, SEC EDGAR (N-PORT für die Top-10-Konzentration, E-71); Margin Debt aus Fed Z.1 statt FINRA (E-42).
   - Scoring nach Bericht 4.3, Schritte 1–6, Aggregation nur Stufe 1.
   - Ansichten 1–7 aus Bericht 6.3, soweit Daten vorhanden, dazu „Datenstand".
   - Kurzinfo und Erklärseite je Kennzahl, Chart-Bedienung (Zoom, Zeitraum, Bildexport, Vollbild, Druck), Auto-Aktualisierung; Doku für KI und Anwender.
   - Validierung nach Bericht 4.3, Schritt 7 (Walk-forward, ROC, Vorlauf, Vergleich mit reinem VIX-Filter), vorgezogen als Meilenstein M10 (Nutzer 29.09.2026, E-89); umgesetzt 29.09.2026 als Ansicht 8 (E-93). Dazu der Walk-forward-Test geschätzter Stress-Gewichte (M11, E-94; Logit aus Phase 3 als reine Auswertung vorgezogen). Nur Auswertung, nie Rückwirkung auf Scores.
2. Alerts, AAII, Aggregation Stufe 2 (korrelationsgewichtet; nur, wenn sie in der Validierung besser abschneidet, E-89), revisionsgenaue Rückrechnung.
3. Optionsdaten (ThetaData/IBKR: Termstruktur, Skew, GEX), Logit-Modell (Stufe 3).

## Stack (festgelegt)

| Aspekt | Festlegung |
|---|---|
| Sprache | Python ≥ 3.11 (`tomllib`), Minor-Version im Dockerfile gepinnt |
| Oberfläche | Dash (Plotly) unter gunicorn, 1–2 Prozesse (derzeit 1 Prozess mit 1 Thread, E-54, E-77) |
| Berechnung | pandas, numpy |
| Datenbank | SQLite im WAL-Modus; SQLAlchemy Core, Migrationen mit Alembic |
| Abrufe | requests, synchron |
| Konfiguration | TOML in `config/`, Secrets aus `.env` |
| Tests | pytest, ohne Netzwerkzugriff |
| Deployment | Dienste `web` und `worker` aus einem Image; Build im Projektverzeichnis, Betrieb über eine Compose-Datei ohne Build als Dockge-Stack (E-21, Umsetzung M3) |
| Zielplattform | TrueNAS, x86_64 (linux/amd64); entschieden 26.09.2026 (E-21), vorher Raspberry Pi |

Bewusste Abweichungen vom Bericht:
- SQLite statt DuckDB: `web` und `worker` sind getrennte Prozesse, DuckDB erlaubt aber nur einen schreibenden Prozess oder mehrere nur lesende, nicht beides zugleich.
- Kein Prefect, Grafana oder Streamlit: zu schwer oder doppelt.
- Shiller-CAPE und Margin Debt schon in Phase 1, sonst bleibt die Fallhöhe-Achse leer. Margin Debt kommt aus der Fed-Statistik Z.1 (FRED `BOGZ1FL663067003Q`, quartalsweise), nicht von FINRA (E-42).
- Entscheidungsrunde 29.09.2026 (E-80 bis E-92): Mindesthistorie 3 statt 5 Jahre; Sahm-Regel (Orange nur mit S&P 500 unter der 200-Tage-Linie, E-91) und SOS-Indikator als feste Ampelregeln; Aktienquote der Anleger (Z.1) und umgedrehter Kreditspread Baa in der Fallhöhe; S&P 500 für VRP und Aktien-Anleihen-Korrelation von Cboe statt FRED.
- Kein Gelb allein aus hoher Fallhöhe (Nutzer 29.09.2026, E-95, nach der Validierung M10/M11; Bericht 4.3, Schritt 5 sah es vor): Die Fallhöhe hebt die Ampel nur zusammen mit Stress (Orange) und steht sonst für sich, auch als eigener Streifen in der Regime-Zeitleiste (E-96).

Kein Node, kein npm, kein Build-Schritt; eigene CSS- und JS-Dateien liegen in `assets/`. Alternative Stacks schlägst du nicht vor.

## Befehle (einrichten und hier aktuell halten)

- `pytest -q`: alle Tests (Python 3.14 mit `requirements-dev.txt`; Cloud-Umgebung: `docs/umsetzungsplan.md`, Abschn. 10)
- `docker build .`: Build-Probe auf dem Entwicklungsrechner (x86_64 wie TrueNAS; Cloud-Umgebung: `docs/umsetzungsplan.md`, Abschn. 10)
- Betrieb auf TrueNAS (Details: `docs/einrichtung.md`); Projektverzeichnis `/mnt/Daten-Z1/apps/feewer`, Datenordner dort `data/`:
  - Build: `sudo docker compose build` im Projektverzeichnis (Bau-Datei `docker-compose.yml`, E-32)
  - Start, Stopp, Update: Dockge-Stack `finanz-dashboard` aus einer Kopie von `compose.dockge.yaml` mit eigener `.env`
  - Einmal-Container: `RUN='sudo docker run --rm --user 568:568 -e FEVER_DATA=/data -v /mnt/Daten-Z1/apps/feewer/data:/data fever:local'`
  - Migration, auch bei der Ersteinrichtung: Stack stoppen → `$RUN python -m fever.backup` → `$RUN alembic upgrade head` → Stack starten; Stand: `$RUN alembic current`
  - Sofort-Backup bei laufendem Stack: `sudo docker exec finanz-dashboard-worker-1 python -m fever.backup`
  - Log: `sudo docker logs -f finanz-dashboard-worker-1`, Dashboard: `sudo docker logs -f finanz-dashboard-web-1`
  - Dashboard im Heimnetz: `http://<IP-von-TrueNAS>:8003`; Health: `curl -s http://127.0.0.1:8003/health`
  - Sofort-Abruf aller Reihen (unabhängig vom Abrufplan): `sudo docker exec finanz-dashboard-worker-1 python -m fever.sources.update`
  - Scores sofort neu berechnen: `sudo docker exec finanz-dashboard-worker-1 python -m fever.score`
  - Validierung sofort neu berechnen: `sudo docker exec finanz-dashboard-worker-1 python -m fever.validate`
  - Testnachricht der Alerts (M12): `sudo docker exec finanz-dashboard-worker-1 python -m fever.alerts --test`
  - Veröffentlichungszeiten im Betrieb prüfen (M3, Schritt 9), nur lesend: `sudo docker exec finanz-dashboard-worker-1 python -m fever.release_check`
  - SEC-Kontakt prüfen, ohne den Wert zu zeigen: `sudo docker exec finanz-dashboard-worker-1 python -c "import os; from fever.sources.sec import contact_problem; print(contact_problem(os.environ.get('FEVER_SEC_CONTACT')) or 'SEC-Kontakt in Ordnung')"`
  - Neue Migration vorher an einer Backup-Kopie proben: `docs/einrichtung.md`, Schritt 9

## Architektur

```
fever/sources/     je Quelle ein Modul (fetch, parse); update.py lädt je Abrufgruppe einmal, prüft, datiert (Vintage) und speichert
fever/store/       Tabellen (SQLAlchemy Core), Lese- und Schreibfunktionen
fever/scoring/     reine Berechnung, importiert nichts aus web/ oder store/
fever/worker.py    Abrufschleife, Heartbeat, stößt den Scoring-Lauf an
fever/score.py     Scoring-Lauf: Werte lesen, fever/scoring rechnen lassen, Score-Tabellen ersetzen; vom Worker und direkt aufrufbar
fever/validation.py  Backtest der Ampel und Walk-forward-Logit (M10, M11; E-93, E-94): reine Berechnung, importiert nichts aus web/ oder store/
fever/validate.py  Validierungslauf nach dem Scoring: Scores und Kurse lesen, Bericht in validation_report ersetzen; vom Worker und direkt aufrufbar
fever/release.py   geschätzte Veröffentlichung einer Beobachtung (E-14), für Abruf, Worker und Scoring
fever/backup.py    VACUUM INTO und Aufbewahrung; vom Worker und direkt aufrufbar
fever/release_check.py  Prüfbericht: erste Abrufe neuer Werte gegen release_time/lag_days, Cboe-Dateien aus der Handelszeit (M3, Schritt 9); nur lesend
fever/alerts.py    Alerts über ntfy.sh (M12, E-99, E-100): Auslöser, gemeldeter Stand in alert_state, Versand über den zentralen HTTP-Client; vom Worker nach jedem Takt, Testnachricht per --test
fever/web/         Dash-App: Layouts, Callbacks, Health-Endpunkt
config/series.toml   Rohreihen (Quelle, ID, Frequenz, Veröffentlichungszeit, Verzug, Toleranz,
                     Plausibilitätsgrenzen) und abgeleitete Indikatoren (Transformation,
                     Orientierung, Block bzw. Fallhöhe)
config/scoring.toml  Fenster, Mindesthistorie, Schwellen, Halbwertszeiten, Matrixregeln, Parameter der Validierung
migrations/  tests/  tests/fixtures/  docs/
```

- Nur der Worker schreibt. `web` setzt auf jeder Verbindung `PRAGMA query_only = ON` und berechnet keine Scores.
- Der Worker ist eine einfache Schleife, die alle 15 Minuten fällige Abrufe ausführt; kein Scheduler-Framework, kein Cron im Container. Nach neuen Daten, geänderter `scoring.toml`/`series.toml` oder neuer Programmversion des Scorings rechnet er die Scores neu und speichert sie, danach bei Bedarf die Validierung (E-93).
- Ausgangspunkt für `series.toml` sind die Berichtsabschnitte 2 und 6.1.

## Was ausdrücklich NICHT gebaut wird

Ein Assistent ergänzt diese Dinge erfahrungsgemäß ungefragt. Hier nicht. Bei zwingendem Grund: erst fragen, nicht bauen.

- Kein Login, keine Benutzerverwaltung, keine Sessions. Zugangsschutz ist Infrastruktur (O-3), nie Anwendungscode.
- Kein CSV-Export von Chartdaten, keine eigene Ampel und keine absoluten Schwellen je Einzelkennzahl (entschieden 25.09.2026). Das betrifft die Einfärbung einzelner Kennzahlen; Regeln der Gesamtampel auf einzelnen Werten (VIX/VIX3M, Sahm-Regel mit S&P-500-Trend, SOS-Indikator) sind entschieden (E-48, E-80, E-91).
- Kein Abruf, Import oder Speichern der FINRA-Margin-Statistik, auch nicht per manuellem Download: Die Nutzungsbedingungen untersagen Speichern und Datenbanken ohne schriftliche Zustimmung (entschieden 26.09.2026, E-42).
- Keine Konto-, Positions- oder Orderfunktionen, auch nicht über IBKR. Nur Marktdaten.
- Keine Handelssignale, keine Renditeprognosen, keine „Crash-Wahrscheinlichkeit" ohne validiertes Modell.
- Kein Machine Learning. Im Backtest optimierte Gewichte oder Schwellen gehen nie automatisch in den Produktivscore; bei so wenigen Krisen wäre das Overfitting. Einziges geschätztes Modell ist das Logit: bis Phase 3 nur als Auswertung in der Validierung (M11, E-94), ohne Wahrscheinlichkeiten und ohne Rückwirkung auf Scores.
- Keine Intraday-Daten, kein Streaming, keine WebSockets.
- Kein Celery, kein Redis, keine Queue, kein asyncio. Kein Caching-Layer außer dem Lesepuffer im Web-Prozess je Datenstand (E-78, `fever/web/db.py`; Nutzer 28.09.2026: nur, weil gemessen nützlich).
- Kein Postgres, keine DuckDB, keine Abstraktion für einen Datenbankwechsel.
- Keine Telemetrie, keine externen CDNs, Webfonts oder Stylesheets per URL (auch nicht `dbc.themes`). Der Browser lädt nur vom eigenen Server.
- Kein Scraping gegen Nutzungsbedingungen, keine Umgehung von Lizenzgrenzen, keine Weitergabe lizenzierter Daten (ICE, Moody's, S&P, Nasdaq).
- Keine Optimierung ohne Messung: keine vorsorglichen Indizes, keine Pagination, keine Denormalisierung.
- Keine generischen Basisklassen oder Plugin-Mechanismen. Zwischen einfacher und erweiterbarer Lösung wählst du die einfache.
- Keine zweite Übersicht mit aufklappbaren Bereichen und Einzelreihen (Variante M7a, entfernt 27.09.2026, E-67): Die Übersicht folgt Bericht 6.3, die Einzelreihen stehen in den Ansichten.

Entscheidet der Nutzer gegen eine Funktion, trägst du sie hier ein.

## Arbeitsweise

1. Lesen, dann planen: Ansatz, betroffene Dateien, Schritte, Risiken, Tests. Dabei keine Dateiänderung.
2. Auf ausdrückliche Freigabe warten. Ausnahme: Der Diff lässt sich in einem Satz beschreiben und berührt weder Scoring noch Datenbankschema.
3. Umsetzen.
4. Prüfen:
   - `pytest -q` muss grün sein.
   - Nach Änderungen an Dockerfile oder Compose: Build-Probe.
   - Nach Oberflächenänderungen: Smoke-Test (App startet, `/_dash-layout` und Health-Endpunkt liefern 200), wo möglich Sichtprüfung im Browser.
   - Was sich nicht prüfen ließ, benennst du als offen.
5. Selbst-Review: Funktion, Fehlerbehandlung, Randfälle, Einschränkungen. Belege statt Erfolgsbehauptungen (Befehl und Ausgabe), dazu der pytest-Befehl, der die Änderung abdeckt.

- Spekuliere nie über Code, den du nicht geöffnet hast. Erfinde keine Funktionen oder Parameter; bei unsicherer Signatur sag es.
- Neue Quelle: Endpoint real abrufen, Antwort in eine Datei schreiben und nur Anfang und Ende ansehen (ganze Historien füllen den Kontext), gekürzt als Fixture in `tests/fixtures/` ablegen, dann Parser und Test schreiben. Das Repository ist öffentlich: Bei lizenzierten Quellen (ICE, S&P, Moody's, Cboe) übernimmt die Fixture nur das Format, die Werte sind synthetisch (`tests/fixtures/README.md`, E-27).
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
- Abruf- und Plausibilitätsfehler werden geloggt; fehlerhafte Werte nie speichern. Der letzte Fehler je Quelle steht in `source_status` und erscheint im Datenstand (entschieden 25.09.2026). Kein leeres `except`, kein stiller Fehler.
- Oberfläche auf Deutsch mit Dezimalkomma und Datum TT.MM.JJJJ; Fachbegriffe wie VIX, OAS, Contango bleiben. Die Übersicht ist auf Smartphone-Breite lesbar.
- Daten werden nie als HTML gerendert (kein `dangerously_allow_html`).

## Datenbank und Daten

- Schema nur per Alembic-Migration; kein `metadata.create_all()`, keine Migration beim Containerstart.
- Jede Verbindung: `PRAGMA foreign_keys = ON`, WAL, `busy_timeout` (120 s: Einmal-Befehle neben dem Worker warten die Score-Ersetzung ab, statt mit „database is locked“ abzubrechen).
- Beobachtungen nur anfügen, nie überschreiben. Schlüssel: (Reihe, Beobachtungsdatum, Vintage). Ein identischer Wert erzeugt keine Zeile, ein geänderter eine neue.
- Zeitstempel in UTC. Abrufe nach `America/New_York` planen; die Sommerzeit wechselt dort an anderen Tagen als in Berlin. Handelsfreie Tage sind kein Fehler.
- Rohantworten gzip-komprimiert unter `raw/` im Datenordner ablegen, nur bei geändertem Inhalt.
- Backup täglich per `VACUUM INTO` nach `backup/` mit begrenzter Aufbewahrung, zusätzlich vor jeder Migration. Nie `cp` auf die laufende Datenbank.
- **Das lokale Archiv der ICE-BofA-Spreads ist unwiederbringlich**: FRED und ALFRED liefern seit April 2026 nur noch drei Jahre. Nichts, was diese Daten löschen oder überschreiben kann, ohne Rückfrage.
- Entwicklung und Tests nie gegen die Produktivdatenbank; lokal gilt `data-dev/`. Migrationen zuerst auf einer Kopie eines Produktiv-Backups durchspielen.

## TrueNAS und Docker

- Nur Abhängigkeiten mit Wheels für linux/amd64, nichts, was beim Build kompiliert; vor der Aufnahme prüfen.
- Ein Image für `web` und `worker`, `restart: unless-stopped`, Nicht-root-Benutzer: im Image `fever` (1000), im Betrieb `apps` (568:568) über `user:` aus der `.env` des Stacks (E-29).
- Datenordner als Bind-Mount auf einem Dataset des TrueNAS-Hosts selbst (kein NFS/SMB, auch nicht von einem anderen Rechner eingebunden: SQLite-WAL funktioniert dort nicht), Host-Pfad aus `.env`: das Kind-Dataset `/mnt/Daten-Z1/apps/feewer/data` im Projektverzeichnis, von Git und Docker-Build ignoriert (`data*/`, E-28). Nie `git clean -x` im Projektverzeichnis. Ins Image wird nie geschrieben.
- Logs nur auf stdout, in Compose begrenzt (`json-file` mit `max-size` und `max-file`), um das Speichermedium zu schonen.
- Healthchecks ohne Zusatzpakete (`python -c …`): `web` per HTTP-Endpunkt, `worker` per Alter des Heartbeats.
- Secrets nur in `.env` (wie `data*/` in `.gitignore`); im Repo liegt `.env.example`: Secrets leer, nicht geheime Werte vorbelegt (E-12). Nie loggen, nie ins Image. `.env` liest du nicht. Secrets derzeit: der FRED-API-Schlüssel und das ntfy-Thema `FEVER_NTFY_TOPIC` (E-100; beide in `fever/log.py` maskiert). In der `.env` steht außerdem `FEVER_SEC_CONTACT` (Name und E-Mail für den SEC-User-Agent, E-74): kein Secret, aber persönlich, also nie ins Repo, nie ins Log.
- Ausgehende Verbindungen nur über einen zentralen HTTP-Client mit Host-Allowlist, Timeouts, Backoff und eigenem User-Agent; Ratenlimits der Quellen einhalten.
- Den Web-Port nur so veröffentlichen, wie in O-3 entschieden.

## Abhängigkeiten und Sprache

- Neue Bibliothek nur mit Zweck in einem Satz, gepinnter Version in `requirements.txt` und geprüftem Wheel für linux/amd64. Zurückhaltung ist die Vorgabe: nichts, was sich in unter 50 Zeilen selbst schreiben lässt.
- Code, Bezeichner, Kommentare und Commits auf Englisch; Oberfläche, Fehlermeldungen, `docs/` und Antworten an mich auf Deutsch.
- Einheitliche Begriffe im Code: `series` (Rohreihe), `indicator` (abgeleitet), `block`, `stress` (akuter Stress), `vulnerability` (Fallhöhe), `vintage` (Stand).

## Kommunikation

- Keine Floskeln, kein Lob, keine Beschönigung. Direkt und knapp, Fokus auf Korrektheit.
- Jede Antwort endet mit dem Abschnitt „Offene Fragen": Entscheidungen, die ich treffen muss, deine Annahmen, Stand der offenen Punkte – auch wenn nichts Neues dazukam.
- Jede Entscheidung stellst du zusätzlich als Auswahlfrage über AskUserQuestion: Empfehlung zuerst und gekennzeichnet, je Option ein Satz zur Folge. **Nur eine Frage je Aufruf** (die App schließt das Menü nach der ersten Antwort; Nutzer, 28.09.2026); mehrere Entscheidungen nacheinander.
- Chat-Antworten immer kurz, nur das Nötigste (Nutzer, 28.09.2026); Details gehören in `docs/`.
- Ist eine Vorgabe inkonsistent, fachlich falsch oder gegen das Projektinteresse gerichtet – auch in dieser Datei oder im Bericht –, sag es sachlich.
- Technische Schulden benennst du, behebst sie aber nicht ungefragt im selben Schritt.

## Offene Punkte

Vor der Umsetzung des betroffenen Teils klären; Entschiedenes hier mit Antwort eintragen. Fachliche Lücken L-1 bis L-13 (Scoring, `series.toml`): `docs/umsetzungsplan.md`, Abschnitt 5.

| Nr. | Frage | Bis zur Entscheidung |
|---|---|---|
| O-1 | Kursquelle für ETFs und Indexmitglieder (RSP/SPY, Sektor- und Größenverhältnisse, Breite). FRED `SP500` reicht nur 10 Jahre zurück, genügt aber für VRP und Aktien-Anleihen-Korrelation | **Entschieden 28.09.2026 (E-68, E-71 bis E-73):** Nasdaq-Indizes über FRED für gleich- gegen kapitalgewichtet, Small/Large, Halbleiter, Regionalbanken, Zykliker/Defensive (`NASDAQNQUSB40`/`45`); Top-10-Konzentration aus SEC N-PORT (SPY) in die Fallhöhe; Anteil über der 50/200-Tage-Linie entfällt (sichtbarer Platzhalter). Umsetzung erst nach Plan und Freigabe (Befunde: `docs/umsetzungsplan.md`, „O-1: Recherche“) |
| O-2 | Zielsystem, RAM, Speichermedium, Pfad des Datenordners | **Entschieden 26.09.2026 (E-21, E-28, E-29):** TrueNAS 25.10.7 statt Pi (Pi: CM4 mit 1,8 GiB RAM, SD-Karte mit 2,6 GB frei). Projekt `/mnt/Daten-Z1/apps/feewer`, Datenordner Kind-Dataset `data/`, Container als `apps` 568:568, Dockge-Stack `finanz-dashboard` (E-34), Betrieb vom Branch `claude-raramo` (E-76, vorher `claude-testing`, E-30); Worker läuft seit 26.09.2026 |
| O-3 | Zugang: nur Heimnetz oder Tailscale, ggf. mit Basic-Auth-Pforte | **Entschieden 25.09.2026:** nur Heimnetz, kein Passwort; Port an `0.0.0.0`; keine Portweiterleitung im Router |
| O-4 | Backup-Ziel außerhalb des Servers | **Entschieden 26.09.2026 (E-22):** Backups bleiben im Datenordner auf TrueNAS, kein weiteres Ziel; Aufwand für Backups gering halten |
| O-5 | ICE-Spreads: drei Jahre Historie bei fünf Jahren Mindesthistorie; betrifft Kreditblock und Rot-Regel. Optionen: BAA10Y (FRED, täglich ab 1986, Moody's-Lizenz) als langer Ersatz, Lizenz direkt bei ICE, befristete Ausnahme mit Kennzeichnung | **Entschieden 28.09.2026 (E-75):** `BAA10Y` über FRED als Ersatz im Kreditblock (Niveau und 20-Tage-Anstieg) und für die Rot-Regel, umgesetzt; Moody's-Lizenz wie ICE nur privat. **Ergänzt 29.09.2026:** Mindesthistorie 3 Jahre (E-82), HY-OAS-Niveau zusätzlich im Kreditblock (E-90); 20-Tage-Anstieg, Rot-Regel und die Enge in der Fallhöhe (E-85) bleiben auf `BAA10Y`; HY-OAS weiter archivieren |
| O-6 | Alert-Kanal (ntfy, Telegram, E-Mail), Phase 2 | **Entschieden 30.09.2026 (E-100):** ntfy über den öffentlichen Server ntfy.sh; das Thema (langer Zufallsname) ist ein Secret in der `.env`. Alerts sind der erste Schritt von Phase 2 nach M9 (E-99), erst nach Plan und Freigabe |
| O-7 | FRED-Bedingungen verbieten das Speichern von FRED-Daten in einer Datenbank ohne schriftliche Zustimmung (W-11) | **Entschieden 28.09.2026 (E-79):** Zustimmung der St. Louis Fed liegt vor (Nutzer). Reihen Dritter über FRED (ICE, S&P, Nasdaq, Moody's) bleiben private Nutzung ohne Weitergabe (E-69) |
