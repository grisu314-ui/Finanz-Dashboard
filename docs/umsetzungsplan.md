# Umsetzungsplan Phase 1 – Fieberthermometer

Stand: 25.09.2026 · Status: **M0 erledigt** · Nächster Schritt: M1 (vorher Entscheidungen zu Schema, Backup-Aufbewahrung und W-5)

Für wen:
- **KI, die das Projekt fortsetzt:** Lies zuerst `CLAUDE.md`, dann Abschnitt 1–3 dieses Dokuments, dann den Meilenstein, an dem du arbeitest. Arbeite nach `CLAUDE.md` → „Arbeitsweise“ (planen, Freigabe, umsetzen, prüfen, Selbst-Review). Aktualisiere am Ende jeder Sitzung Abschnitt 1 und bei Entscheidungen Abschnitt 2.
- **Nutzer:** Abschnitt 1 (Stand), 2 (was entschieden ist), 5 (was noch zu entscheiden ist).

Verwandte Dokumente: `docs/einrichtung.md` (Aufsetzen und Betrieb), `docs/bedienung.md` (Dashboard lesen), `docs/leitfaden-erklaertexte.md` (Kennzahl-Texte), `.claude/rules/` (Regeln für KI-Sitzungen).

---

## 1. Stand der Meilensteine

Legende: ☐ offen · ◐ in Arbeit · ☑ erledigt (umgesetzt und geprüft, Belege im Meilenstein)

| Nr. | Meilenstein | Status | Voraussetzung | Freigabe nötig |
|---|---|---|---|---|
| M0 | Projektgerüst, Image, Compose | ☑ 25.09.2026 | – | erteilt 25.09.2026 |
| M1 | Speicher, Migrationen, Backup | ☐ | M0, Schema-Freigabe, W-5 | ja (Schema) |
| M2 | HTTP-Client, Serienkatalog, Quellen Cboe und FRED/ALFRED | ☐ | M1, L-5, L-10 (betroffene Reihen) | ja |
| M3 | Worker und erste Inbetriebnahme auf dem Pi (ICE-Archiv startet) | ☐ | M2 | ja |
| M4 | Weitere Quellen: CFTC, EZB, OFR, EBP, Shiller-CAPE, FINRA | ☐ | M3, L-10 | ja |
| M5 | Scoring Schritte 1–6, Aggregation Stufe 1 | ☐ | M4, L-1 bis L-9, L-11, L-12 | ja (Scoring) |
| M6 | Web-Grundgerüst, Gestaltung, Aktualität, Datenstand | ☐ | M1 (Lesen), M3 (Heartbeat) | ja |
| M7 | Ansichten 1–7 | ☐ | M5, M6, L-13 | ja |
| M8 | Erklärtexte je Kennzahl | ☐ | parallel zu M6/M7 | ja (Texte prüfen) |
| M9 | Abnahme Phase 1 | ☐ | M0–M8 | – |

**Warum diese Reihenfolge:** FRED liefert die ICE-BofA-Spreads seit April 2026 nur noch für drei Jahre (Bericht, TL;DR). Jeder Tag ohne laufenden Worker verschiebt den Anfang des lokalen Archivs um einen Tag nach hinten. Deshalb geht ein minimaler Worker mit FRED und Cboe (M0–M3) auf den Pi, bevor Scoring und Oberfläche entstehen.

---

## 2. Entscheidungsprotokoll

| Datum | Nr. | Frage | Entscheidung | Folge |
|---|---|---|---|---|
| 25.09.2026 | E-1 | Farben für einzelne Kennzahlen | Neutrale Perzentil-Farbskala plus Markierung „erhöht“ ab der Diffusionsschwelle aus `scoring.toml` (Startwert laut Bericht 4.3: 80. Perzentil) | Keine neuen Parameter. Ampelfarben (Grün, Gelb, Orange, Rot) nur für die Gesamtampel. Keine Einzelampel, keine absoluten Schwellen je Kennzahl |
| 25.09.2026 | E-2 | Chart-Funktionen über Zoom, Verschieben und PNG hinaus | Zeitraum-Buttons, Druck-/PDF-Ansicht, Vollbild je Chart | CSV-Export nicht gewählt (in `CLAUDE.md` unter „NICHT gebaut“ eingetragen) |
| 25.09.2026 | E-3 | Zugang (O-3) | Nur Heimnetz, kein Passwort | Kein Reverse-Proxy, kein Passwort-Hash. Jedes Gerät im Heimnetz sieht das Dashboard. Keine Portweiterleitung im Router |
| 25.09.2026 | E-4 | Bindung des Web-Ports | `0.0.0.0` (alle Schnittstellen) | Funktioniert auch bei wechselnder IP. Docker-Portfreigaben umgehen ufw-Regeln; der Port ist auf jeder Schnittstelle des Pi offen (auch VPN, falls vorhanden) |
| 25.09.2026 | E-5 | Farbschema | Automatisch hell/dunkel nach Systemeinstellung | CSS-Variablen, zwei Plotly-Templates, Umschaltung per Clientside-Callback |
| 25.09.2026 | E-6 | Ort des Langtexts | Eigene Erklärseite je Kennzahl (`/kennzahl/<id>`) | Verlinkbar, Zurück-Taste funktioniert |
| 25.09.2026 | E-7 | Aktualisierung offener Seiten | Alle 5 Minuten automatisch | Zoom bleibt erhalten (`uirevision`); neue Worker-Daten nach höchstens rund 20 Minuten sichtbar |
| 25.09.2026 | E-8 | Aufbewahrung der Backups | 14 tägliche, 5 vor Migrationen | Zwei Wochen zurück; geringer Platzbedarf |
| 25.09.2026 | E-9 | Fehlerstatus im Datenstand (W-5) | Letzter Fehler je Quelle in `source_status`, wird überschrieben | Fehlerhafte Werte werden nie gespeichert; keine Fehlerhistorie. `CLAUDE.md` entsprechend präzisiert |

---

## 3. Anforderungen aus den Nutzerwünschen vom 25.09.2026

„Kennzahl“ heißt hier jede angezeigte Größe: Indikatoren aus `series.toml`, Blockscores, Stress, Fallhöhe, Ampel, Konfidenz, Diffusionsindex, dazu das Konzept „Perzentil“ als eigene Erklärseite.

| Nr. | Anforderung | Umsetzung | Meilenstein |
|---|---|---|---|
| A-1 | Kurzinfo bei Mouseover je Kennzahl | Info-Symbol mit Tooltip aus reinem CSS (`data-`-Attribut, Anzeige über `:hover` und `:focus`, damit Antippen auf dem Smartphone funktioniert). Text als Klartext, nie als HTML | M6, M8 |
| A-2 | Ausführlicher, verlinkter Text je Kennzahl | Name der Kennzahl verlinkt auf `/kennzahl/<id>`. Die Seite besteht aus einem handgeschriebenen Teil (`fever/web/texts/<id>.md`) und einem erzeugten Teil (Steckbrief, Schwellen, aktueller Stand) | M6, M8 |
| A-3 | Schwellen erklärt (ab wann welche Farbe) | Erzeugter Abschnitt „Schwellen und Farben“ aus `scoring.toml`, nie als Freitext. Für die Ampel: alle vier Stufen mit Regeln, Hysterese und inaktiven Regeln (z. B. HY-OAS-Regel wegen O-5). Für Einzelkennzahlen: Perzentilskala und „erhöht“ (E-1) | M8 |
| A-4 | Schönheit und Aktualität | Designsystem (Abschnitt 7.4) und Aktualitätsanzeige (Abschnitt 7.3). Annahme: „Aktualität“ heißt Datenaktualität, nicht modisches Design | M6, M7 |
| A-5 | Charts zoombar, Screenshots | Chart-Standard (Abschnitt 7.1): Zoom, Verschieben, Doppelklick-Reset, Zeitraum-Buttons, PNG-Export mit eingebettetem Datenstand, Vollbild, Druck-/PDF-Ansicht | M6, M7 |
| A-6 | Dokumentation für KI und Anwender, inkl. Einrichtung mit Befehlen | `.claude/rules/dokumentation.md` (Pflichten), `docs/einrichtung.md`, `docs/bedienung.md`, dieses Dokument | laufend, Abschluss M9 |

**Rangfolge bei Zielkonflikten:** fachliche Korrektheit vor Aktualität vor Lesbarkeit vor Schönheit. Zwei Beispiele: Eine Datenlücke wird nicht zu einer glatten Linie interpoliert, und ein veralteter Wert wird nicht in der Farbe eines aktuellen gezeigt, auch wenn das unruhiger aussieht.

---

## 4. Meilensteine im Detail

Für jeden Meilenstein gilt die Definition of Done:
- `pytest -q` grün
- betroffene Doku im selben Commit aktualisiert (`.claude/rules/dokumentation.md`)
- Selbst-Review mit Belegen (Befehl und Ausgabe)
- Status in Abschnitt 1 nachgetragen

### M0 – Projektgerüst, Image, Compose

**Ziel:** Das Image baut für linux/arm64, `pytest -q` läuft, Compose ist gültig.

**Dateien:**
- `requirements.txt` mit gepinnten Versionen, je Bibliothek ein Kommentar zum Zweck
- `requirements-dev.txt` (pytest, nicht im Image)
- `Dockerfile`, `.dockerignore`, `docker-compose.yml`, `.env.example`, `.gitignore`
- `fever/__init__.py`, `fever/config.py` (TOML laden und validieren)
- `config/series.toml` und `config/scoring.toml` (nur Gerüst)
- `tests/test_config.py`

**Schritte:**
1. Python-Minor wählen: die neueste Version, für die numpy, pandas, SQLAlchemy, Alembic, Dash und gunicorn aarch64-Wheels haben. Prüfen mit `pip download --platform manylinux2014_aarch64 --only-binary=:all: --python-version <X.Y> -r requirements.txt -d /tmp/wheels`.
2. Versionen pinnen. Stand 25.09.2026 laut PyPI: Dash 4.4.1 (Major 4.0.0 erschien am 03.02.2026), Plotly 7.1.0.
3. Dockerfile: slim-Basis mit gepinnter Minor-Version, Nicht-root-Benutzer mit UID/GID als Build-Arg (Standard 1000), keine Schreibzugriffe ins Image. Prüfen, ob `zoneinfo` die Zone `Europe/Berlin` im Image findet; sonst das Paket `tzdata` (reines Python) aufnehmen.
4. Compose:
   - Dienste `web` und `worker` aus einem Image, `restart: unless-stopped`
   - Datenordner als Bind-Mount aus `.env`, Logging `json-file` mit `max-size` und `max-file`
   - Web-Port `0.0.0.0:${FEVER_WEB_PORT}` (E-4)
   - Healthchecks folgen in M3 (worker) und M6 (web)
5. Geplante `.env`-Variablen (Namen werden hier festgelegt, in `.env.example` mit leeren Werten): `FRED_API_KEY`, `FEVER_DATA_DIR`, `FEVER_UID`, `FEVER_GID`, `FEVER_WEB_PORT`.

**Risiken:** Der QEMU-Build unter x86 ist langsam. Fehlen Wheels für die neueste Python-Version, eine Minor zurückgehen.

**Prüfung:** `pytest -q`, `docker buildx build --platform linux/arm64 .`, `docker compose config`.

**Doku:**
- `CLAUDE.md` → Befehle
- `docs/einrichtung.md` → Abschnitt `.env` von ⏳ auf die echten Variablennamen

**Ergebnis (25.09.2026, erledigt):**
- **Python 3.14**, Basis-Image `python:3.14-slim-trixie` (enthält 3.14.7). Python 3.15 ist erst `3.15.0rc2`. Die Zeitzonendaten sind im Image vorhanden (`ZoneInfo("Europe/Berlin")` getestet), deshalb kein Paket `tzdata`.
- **Abhängigkeiten:** Alle 36 Laufzeitpakete wurden im arm64-Container mit `pip install --only-binary=:all:` aufgelöst und installiert; es sind ausschließlich Wheels, nichts wird kompiliert. Direkte und transitive Pakete sind gepinnt.
- **Abweichungen vom Plan:**
  - SQLAlchemy **2.0.49** statt 2.1.x: 2.1.0 erschien am 24.09.2026, 2.1.1 am 25.09.2026. Für den Pi ist die gereifte 2.0-Linie gewählt.
  - Die Netzwerksperre für Tests (`tests/conftest.py`) ist schon in M0 statt M2 umgesetzt.
- **Befund Compose 5.1.1:** Auch mit Langform-Bind-Mount legte Compose einen fehlenden Datenordner stillschweigend an. Erst `bind.create_host_path: false` macht daraus einen Fehler (getestet).
- **Compose-Details:**
  - Nur `worker` baut, `web` nutzt dasselbe Image (`pull_policy: never`).
  - `web` hat bewusst kein `depends_on`, damit es bei stehendem Worker weiterläuft und warnen kann.
  - Die Startbefehle von `worker` (M3) und `web` (M6) verweisen auf noch nicht existierende Module; `docker compose up` ist deshalb erst ab M3 sinnvoll.
- **Belege:**
  - `pytest -q`: 11 passed (Python 3.14, amd64)
  - arm64-Build: erfolgreich in 4:55 min unter QEMU
  - Image: `arch=arm64`, Benutzer `fever` (1000:1000), alle Importe laden, `/app` nicht beschreibbar, keine `.env` und keine Tests im Image
  - Compose: `config` gültig, deutsche Fehlermeldung bei fehlendem `FEVER_DATA_DIR` bzw. `FRED_API_KEY`, Schreiben in einen Datenordner mit Eigentümer 1000:1000 funktioniert
- **Einschränkung der Probe:** Die Cloud-Entwicklungsumgebung läuft hinter einem Proxy mit eigenem Zertifikat. Die Build-Probe nutzte deshalb eine per `sed` erzeugte Kopie des Dockerfiles mit zwei zusätzlichen Zeilen für dieses Zertifikat (Abschnitt 10). Auf dem Pi ist das nicht nötig.
- **Nicht geprüft:** Build und Start auf einem echten Pi (erst M3).

### M1 – Speicher, Migrationen, Backup

**Ziel:** Append-only-Speicher mit Vintages, Alembic-Erstmigration, Backup per `VACUUM INTO`.

**Dateien:**
- `fever/store/` mit `tables.py`, `db.py` (Verbindung und PRAGMAs), `observations.py`, `status.py`
- `migrations/` (Alembic), `fever/backup.py`, `tests/test_store.py`, `tests/test_backup.py`

**Schema-Entwurf** (zur Freigabe, nicht final):
- `observation`: `series_id`, `obs_date`, `vintage`, `value`, `published_at`, `published_estimated`, `retrieved_at`. Primärschlüssel (`series_id`, `obs_date`, `vintage`).
- `source_status`: je Quelle eine Zeile mit letztem Erfolg, letztem Versuch, letztem Fehler (Zeit und Meldung). Wird überschrieben; eine Fehlerhistorie gibt es nicht (siehe W-5).
- `heartbeat`: Komponente, Zeitpunkt.
- Score-Tabellen folgen in M5 als eigene Migration.

**Schritte:**
1. Jede Verbindung setzt `foreign_keys = ON`, WAL und `busy_timeout`; `web` zusätzlich `query_only = ON`.
2. Schreibfunktion: ein identischer Wert erzeugt keine Zeile, ein geänderter eine neue Vintage-Zeile. Es gibt keine Lösch- oder Update-Funktion für Beobachtungen.
3. Rohantworten gzip-komprimiert unter `raw/`, nur bei geändertem Inhalt (Hash-Vergleich).
4. Backup:
   - täglich und vor jeder Migration per `VACUUM INTO` nach `backup/`
   - Aufbewahrung: 14 tägliche, 5 vor Migrationen (E-8)
   - Fehlt die Datenbank noch (Ersteinrichtung), bricht `fever.backup` mit klarer Meldung und Exit-Code ≠ 0 ab

**Entscheidungen bei M1:** Aufbewahrung (E-8) und W-5 (E-9) entschieden; Schema-Freigabe offen.

**Tests:**
- append-only (identisch, geändert, neue Vintage)
- PRAGMAs sind gesetzt
- `query_only` verhindert Schreiben
- Backup ist lesbar, die Aufbewahrung löscht nur Backups
- Rohdatei nur bei geändertem Inhalt
- `alembic upgrade head` auf leerer Datenbank in `tmp_path`

**Risiko:** Das ICE-Archiv ist unwiederbringlich. Kein Code darf Beobachtungen löschen; ein Test prüft, dass `fever/store` kein `DELETE`/`UPDATE` auf `observation` ausführt.

**Doku:** `docs/einrichtung.md` → Backup, Wiederherstellung (echte Dateinamen inkl. `-wal`/`-shm`), Migration.

### M2 – HTTP-Client, Serienkatalog, Cboe und FRED/ALFRED

**Ziel:** Rohreihen von Cboe und FRED abrufen, validieren und speichern; Rückfüllung mit geschätzter Veröffentlichung.

**Dateien:**
- `fever/http.py`: Host-Allowlist, Timeouts, Backoff, eigener User-Agent, Ratenlimit je Host
- `fever/sources/cboe.py`, `fever/sources/fred.py`
- `config/series.toml` (Cboe- und FRED-Reihen)
- `tests/fixtures/…`, `tests/test_sources_*.py` (die Netzwerksperre in `tests/conftest.py` besteht seit M0)

**Schritte:**
1. Serien-IDs mit (*) aus Bericht 6.1 per FRED-Metadatenabruf prüfen; Ergebnis mit Datum hier protokollieren.
2. Je Quelle: Endpoint real abrufen, Antwort in eine Datei schreiben, nur Anfang und Ende ansehen, gekürzt als Fixture ablegen, dann Parser und Test.
3. `series.toml` je Reihe: Quelle, ID, Frequenz, Veröffentlichungszeit (America/New_York), Verzug, Toleranz (L-5), Plausibilitätsgrenzen. Indikatoren: Transformation (L-10), Orientierung, Block bzw. Fallhöhe.
4. Der FRED-API-Schlüssel steht als Query-Parameter in der URL. Der HTTP-Client maskiert ihn in jeder Log- und Fehlermeldung (Test).

**Entscheidung bei M2:** Phase 1 speichert den aktuellen Stand und fortlaufend beobachtete Revisionen. Historische ALFRED-Vintages rückwirkend zu laden gehört zur revisionsgenauen Rückrechnung in Phase 2. Vorschlag: nicht in Phase 1.

**Tests:**
- Parser gegen Fixtures
- Plausibilitätsverletzung wird geloggt und nicht gespeichert
- Allowlist lehnt fremde Hosts ab
- API-Schlüssel erscheint nie im Log

### M3 – Worker und erste Inbetriebnahme auf dem Pi

**Ziel:** Der Worker läuft dauerhaft auf dem Pi und archiviert ab jetzt täglich.

**Dateien:** `fever/worker.py`, Healthcheck `worker` in Compose, `tests/test_worker_schedule.py`.

**Schritte:**
1. Schleife alle 15 Minuten; fällige Abrufe nach Veröffentlichungsplan in America/New_York.
2. Heartbeat schreiben, sauberes Beenden bei SIGTERM (`docker compose stop`), tägliches Backup.
3. Healthcheck: Heartbeat-Alter (Vorschlag: höchstens 45 Minuten, also drei Takte).
4. Branch für den Betrieb auf dem Pi festlegen (Auswahlfrage). Bisher existiert nur der Entwicklungsbranch `claude-testing`.
5. Einrichtung auf dem Pi nach `docs/einrichtung.md`. Führt der Nutzer aus, weil die KI keinen Zugriff auf den Pi hat. Jeder ausgeführte Schritt wird mit ✅ und Datum markiert.

**Tests:**
- Fälligkeit rund um die Sommerzeitwechsel: USA endet am 01.11.2026, EU am 25.10.2026
- handelsfreie Tage sind kein Fehler
- Heartbeat wird geschrieben

### M4 – Weitere Quellen

**Ziel:** CFTC (COT), EZB (CISS), OFR (FSI), Fed-Board (EBP), Shiller-CAPE, FINRA Margin Debt.

**Schritte:**
1. Je Quelle wie in M2.
2. Unverifizierte Endpoints zuerst prüfen: OFR-FSI-Download, EBP-CSV, CISS `SS_CIN`, TFF-IDs bei CFTC, FINRA ohne Login.
3. Excel-Dateien (Shiller `ie_data.xls`, FINRA) brauchen ggf. eine Leser-Bibliothek. Das ist eine neue Abhängigkeit mit Begründung und geprüftem aarch64-Wheel, deshalb vorher fragen.
4. Nutzungsbedingungen je Quelle prüfen (kein Scraping gegen AGB).

**Tests:** Parser gegen Fixtures; Formatänderung der Quelle führt zu einem sichtbaren Fehler, nicht zu stillem Ausfall.

### M5 – Scoring (Schritte 1–6, Stufe 1)

**Voraussetzung:** L-1 bis L-9, L-11 und L-12 entschieden; `scoring.toml` mit Startwerten aus Bericht 4.3 und den Entscheidungen; Freigabe.

**Dateien:**
- `fever/scoring/` mit Perzentil, Transformationen, Veraltung, Blockmedian, Composite, Fallhöhe, Glättung, Matrixregeln mit Hysterese, Konfidenz, Diffusionsindex. Reine Funktionen mit Stichtag t, ohne Import aus `web/` oder `store/`.
- Migration der Score-Tabellen
- Neuberechnung im Worker bei neuen Daten oder geändertem Hash von `scoring.toml`

**Pflichttests** (`CLAUDE.md`):
- Ergebnis für t identisch mit und ohne Beobachtungen nach t
- Perzentil mit Gleichständen gegen ein handgerechnetes Beispiel
- Veraltung, Toleranz, Konfidenz
- Matrixregeln genau auf der Schwelle, Hysterese
- Block ohne gültigen Indikator

**Sichtbare Platzhalter:** Block „Breite“ ohne Datenquelle (O-1), HY-OAS-Rot-Regel inaktiv (O-5). Beides erscheint in der Oberfläche, nicht nur im Code.

**Risiko:** Rechenzeit auf dem Pi (rollierende Perzentile über bis zu 10 Jahre je Indikator). Erst messen, dann optimieren.

### M6 – Web-Grundgerüst, Gestaltung, Aktualität, Datenstand

**Ziel:** Lauffähige Dash-App mit Designsystem, Chart-Standard, Tooltip- und Erklärseiten-Mechanik, Aktualitätsanzeige und Ansicht „Datenstand“.

**Dateien:**
- `fever/web/app.py`: Dash mit `serve_locally=True` (Standard), gunicorn mit 1–2 Prozessen
- `fever/web/db.py`: nur lesend
- `fever/web/health.py`, `fever/web/figures.py` (Chart-Fabrik), `fever/web/components.py` (Kennzahl-Kopf mit Info-Symbol, Aktualitäts-Badge), `fever/web/texts.py` (Laden der Texte und Erzeugen von Steckbrief und Schwellen)
- `fever/web/pages/`: Übersicht, Themen-Ansichten, Visualisierung, Datenstand, Erklärungen, `/kennzahl/<id>`
- `assets/`: `base.css` (Tokens hell/dunkel, Layout), `tooltip.css`, `print.css`, `fullscreen.js`, `theme.js`

**Schritte:** Abschnitt 7 umsetzen. Healthcheck `web` in Compose.

**Tests:**
- Smoke-Test: App startet, `/_dash-layout` und Health-Endpunkt liefern 200
- das ausgelieferte HTML enthält keine externe URL (kein CDN)
- die Chart-Fabrik setzt den Standard aus 7.1: Config, Zeitraum-Buttons, Datenstand-Annotation, `uirevision`
- kein `dangerously_allow_html` im Code
- jede angezeigte Kennzahl hat einen Text (siehe M8)

**Sichtprüfung:** Playwright mit dem vorinstallierten Chromium in der Entwicklungsumgebung (kein Projekt-Requirement), Breiten 390 px und 1440 px, hell und dunkel, Druckvorschau. Screenshots bleiben außerhalb des Repos.

### M7 – Ansichten 1–7

Laut Bericht 6.3, soweit Daten vorhanden:
- **1 Übersicht:** Ampelmatrix aus Stress (x) und Fallhöhe (y), Regionen aus `scoring.toml`, 60-Tage-Spur. Dazu Ampelstufe als Text, Konfidenz, Diffusionsindex und letzte Aktualisierung je Quelle.
- **2 Schnelle Marktsignale:** VIX-Termstruktur, VIX/VIX3M mit Backwardation-Schattierung, VRP, VVIX, SKEW, USD/JPY. Nicht in Phase 1: MOVE (Lizenz, siehe W-6).
- **3 Marktbreite:** ohne Datenquelle (O-1). Die Ansicht zeigt das ausdrücklich, statt leer zu wirken.
- **4 Sentiment und Positionierung:** VX-COT, Margin Debt ggü. Vorjahr. AAII kommt in Phase 2.
- **5 Makro und Liquidität:** NFCI/ANFCI, STLFSI4, OFR FSI, CISS, HY-OAS und CCC−BB (nur Anzeige, O-5), EBP, SOFR−IORB, Zinskurve, Sahm-Regel, Erstanträge.
- **6 Fallhöhe:** CAPE bzw. Excess CAPE Yield, Margin Debt. Konzentration fehlt (O-1).
- **7 Visualisierung:** Heatmap (Perzentilskala nach E-1), Perzentilbänder 10/50/90, Sparklines mit Zeitstempel, Composite-Historie mit Krisenmarken (L-13), Regime-Zeitleiste.
- Historienansicht mit Hinweis: je Beobachtung zählt der neueste Stand (Phase-1-Ausnahme, `CLAUDE.md`).

### M8 – Erklärtexte

**Ziel:** Für jede Kennzahl eine Datei `fever/web/texts/<id>.md` nach `docs/leitfaden-erklaertexte.md`.

**Schritte:**
1. Texte je Ansicht schreiben, bevor die Ansicht abgenommen wird.
2. Fakten aus Bericht Abschnitt 1–3 und Primärquellen, mit Quelle. Einschätzungen sind gekennzeichnet.
3. Der Nutzer prüft die Texte (Freigabe).

**Tests** (ab M6 aktiv):
- Datei je Kennzahl vorhanden
- Pflichtüberschriften in fester Reihenfolge
- Kurzinfo höchstens 200 Zeichen
- keine Perzentil-Schwellenzahlen im Freitext (Muster wie „90. Perzentil“)
- kein HTML

### M9 – Abnahme Phase 1

1. `pytest -q`, arm64-Build-Probe, Update auf dem Pi nach `docs/einrichtung.md`.
2. Sichtprüfung aller Ansichten auf Smartphone und Desktop.
3. `docs/bedienung.md` und `docs/einrichtung.md` von ⏳ auf ✅, wo geprüft.
4. README-Status aktualisieren.

---

## 5. Fachliche Lücken (vor dem betroffenen Meilenstein per Auswahlfrage klären)

Nichts davon wird geraten. Die Vorschläge sind begründete Startpunkte, keine Entscheidungen.

| Nr. | Lücke | Betrifft | Vorschlag mit Begründung | Klären vor |
|---|---|---|---|---|
| L-1 | Perzentil bei Gleichständen; gehört xₜ zur Referenzmenge? | jeder Score | Mittelrang: p = 100 · (Anzahl kleiner + ½ · Anzahl gleich) / n, Referenz = alle gültigen Werte im Fenster bis einschließlich t. Symmetrisch; Reihen mit vielen gleichen Werten (Sahm-Regel, SOFR−IORB) werden nicht systematisch verschoben | M5 |
| L-2 | Fenster für Reihen mit 5–10 Jahren Historie | jeder Score | Rollierend höchstens 10 Jahre; solange weniger vorhanden ist (aber ≥ Mindesthistorie), alle vorhandenen Werte. Passt zu „expandierend mit mindestens 5 Jahren“ (Bericht 4.3) | M5 |
| L-3 | Worauf beziehen sich die Ampelschwellen („Stress-Composite ≥ 90. Perzentil“, „Fallhöhe ≥ 80“): auf den Wert selbst (Mittel der Blockperzentile, 0–100) oder auf einen erneut perzentilierten Composite? | Ampel | Auf den Wert selbst. Der CISS aggregiert ebenfalls ohne zweites Ranking. Ein neu gerankter Composite läge per Konstruktion an rund 10 % aller Tage ≥ 90, auch in ruhigen Jahrzehnten. Folge: Rot über den Composite nur bei breitem Stress, schnelle Schocks fangen die Einzelregeln | M5 |
| L-4 | Composite, wenn Blöcke fehlen. In Phase 1 fehlt „Breite“ dauerhaft (O-1) | Stress, Ampel | Mittel der vorhandenen Blöcke, mindestens 3 von 5, sonst kein Composite (sichtbar). Fehlende Blöcke werden in der Übersicht benannt und senken die Konfidenz | M5 |
| L-5 | Toleranz je Frequenz (ab wann „veraltet“) | Veraltung, Score | Kalendertage ab erwarteter Veröffentlichung (Beobachtung + Verzug): täglich 4, wöchentlich 3, monatlich 10. Kalendertage decken lange Wochenenden (z. B. Karfreitag) ohne Börsenkalender ab. Abweichungen je Reihe begründet in `series.toml` (z. B. Shiller mit unregelmäßigen Updates) | M2 |
| L-6 | Konfidenz „gewichtet mit dem historischen Vorlauf“: welche Gewichte? | Konfidenz | V-Score aus Bericht Tabelle 2 (1–5) als Gewicht. Konfidenz = Summe der Gewichte aktueller, gültiger Indikatoren / Summe der Gewichte aller scorerelevanten Indikatoren. Tabelle 2 ist die einzige vorhandene Vorlaufbewertung; die Werte sind Einschätzungen und in `series.toml` sichtbar | M5 |
| L-7 | Hysterese für Regeln ohne Perzentilskala (VIX/VIX3M > 1 an 3 Tagen, Diffusionsindex ≥ 40 %) | Ampel | VIX/VIX3M: Die Regel endet, wenn das Verhältnis an 3 Tagen in Folge < 1 liegt (spiegelbildlich). Diffusionsindex: 5 Prozentpunkte unter der Schwelle, analog zur Perzentil-Hysterese | M5 |
| L-8 | Glättung: welcher Block ist „schnell“, in welcher Reihenfolge wird geglättet, nutzt die Ampel geglättete Werte? | Stress, Ampel | Schnell = Volatilität/Optionen (HWZ 3 auf den Blockscore). Composite HWZ 10. Die Ampel nutzt den geglätteten Composite, die Einzelregeln (VIX/VIX3M, HY-OAS) Rohwerte. Folge: Bei HWZ 10 wirkt ein Sprung erst nach 10 Handelstagen zur Hälfte, der Composite-Weg zu Rot ist also träge | M5 |
| L-9 | VX-COT-Perzentil über 3 Jahre (Bericht 6.3) vs. 10-Jahres-Fenster (4.3) | Positionierung | Im Score das Standardfenster (4.3), in Ansicht 4 zusätzlich das 3-Jahres-Perzentil als Anzeige | M5 |
| L-10 | Transformationen ohne Definition: Erstanträge „Veränderung ggü. Tief“ (welches Fenster?), USD/JPY-Vola (Fenster), Re-Steepening-Flag (Definition), Aktien-Anleihen-Korrelation (Anleiherendite aus DGS10-Änderung?), COT-Maß und Orientierung, Definition der Excess CAPE Yield, Margin Debt nur ggü. Vorjahr (keine Marktkapitalisierung in Phase 1), VIX6M (nicht in 6.1, Endpoint prüfen) | Indikatoren | Je Indikator beim Anlegen in `series.toml` einzeln vorschlagen und fragen | M2/M4 |
| L-11 | Fallhöhe in Phase 1: Top-10-Konzentration (O-1), HY-OAS-Niveau (O-5) und AAII (Phase 2) fehlen | Fallhöhe | Mittel der vorhandenen Komponenten (Excess CAPE Yield, Margin Debt ggü. Vorjahr, VX-COT-Short-Vol), mindestens 2; Fehlende sichtbar | M5 |
| L-12 | Diffusionsindex: welche Einzelreihen zählen? | Ampel (Gelb) | Nur Stress-Indikatoren mit gültigem, aktuellem Wert und ausreichender Historie. Fallhöhe-Indikatoren nicht, sonst ginge Fallhöhe doppelt in „Gelb“ ein | M5 |
| L-13 | Krisenmarken in der Composite-Historie: genaue Zeiträume | Anzeige | Start und Ende je Episode mit Quelle in einer eigenen Datei `config/episodes.toml` (Anzeige, kein Score) | M7 |

---

## 6. Widersprüche und Inkonsistenzen

| Nr. | Befund | Umgang |
|---|---|---|
| W-1 | Der Nutzerwunsch nennt drei Farben (Grün, Gelb, Rot), die Ampel des Berichts hat vier Stufen (mit Orange) | Vier Stufen bleiben; die Erklärseite „Ampel“ erklärt alle vier |
| W-2 | VX-COT-Fenster 3 Jahre (6.3) vs. 10 Jahre (4.3) | L-9 |
| W-3 | Bericht 4.3, Schritt 4 nennt Fallhöhe-Komponenten, die in Phase 1 größtenteils fehlen | L-11 |
| W-4 | Die Rot-Regel „HY-OAS-Anstieg über 20 Tage ≥ 95. Perzentil“ braucht HY-OAS im Score; O-5 schließt das bis zur Entscheidung aus | Regel ist inaktiv und in der Oberfläche als inaktiv markiert, bis O-5 entschieden ist |
| W-5 | `CLAUDE.md`: Fehler „werden geloggt, nicht gespeichert, und erscheinen im Datenstand“. Die Web-Oberfläche kann Worker-Logs nicht lesen | Entschieden (E-9): Fehlerhafte Werte werden nie gespeichert. Der letzte Fehler je Quelle (Zeit und Meldung) steht in `source_status`, ohne Historie |
| W-6 | Bericht 6.3, Ansicht 2 nennt MOVE (ICE-Lizenz, nicht in Phase 1) und VIX6M (nicht in Tabelle 6.1) | MOVE entfällt in Phase 1; VIX6M unter L-10 |
| W-7 | Der Migrationsablauf in `CLAUDE.md` (stop → Backup → upgrade → up) gilt „auch bei der Ersteinrichtung“; dann gibt es aber nichts zu stoppen oder zu sichern | Die Einrichtungsanleitung lässt Stop und Backup bei der Ersteinrichtung aus; `fever.backup` meldet eine fehlende Datenbank klar |

---

## 7. Technische Leitlinien der Oberfläche

Kurzfassung als Regel für KI-Sitzungen: `.claude/rules/oberflaeche.md`. Hier stehen Details und Begründungen.

### 7.1 Chart-Standard (gilt für jeden Chart)

- **Eine Fabrikfunktion** in `fever/web/figures.py` erzeugt Figure und Config. Kein Chart wird an ihr vorbei gebaut, damit Standard und Test an einer Stelle hängen.
- **Zoom und Verschieben:** Plotly-Standard (Rahmen aufziehen, Verschieben über die Modebar, Doppelklick setzt zurück). `scrollZoom` aus, weil sonst das Scrollen der Seite auf dem Smartphone im Chart hängen bleibt.
- **Zeitraum-Buttons (E-2):** `xaxis.rangeselector` mit „1 M“, „6 M“, „1 J“, „5 J“, „Max“. Kein Rangeslider; er kostet auf dem Smartphone zu viel Höhe.
- **Bildexport:** Modebar-Button „Download als PNG“ über `toImageButtonOptions` (`format="png"`, `scale=2`, Dateiname `<kennzahl>_<TT-MM-JJJJ>`), `displaylogo=False`. Die Bilderzeugung läuft im Browser, ohne Server-Bibliothek; geprüft am Quelltext von Dash 4.4.1 (`dcc.Graph`, Prop `config`).
- **Datenstand im Bild:** Titel, Quelle, letztes Beobachtungsdatum und Abrufzeitpunkt stehen als Annotation *im* Chart. Ein exportiertes oder ausgedrucktes Bild darf nie zeitlos wirken.
- **Vollbild (E-2):** ein Button je Chart-Karte, der die Karte per CSS-Klasse als Overlay über den ganzen Bildschirm legt (`position: fixed; inset: 0`); Plotly passt sich über `responsive` an. Bewusst ohne Fullscreen-API, damit das Verhalten nicht vom Browser abhängt. ESC oder Button schließt.
- **Druck-/PDF-Ansicht (E-2):** `assets/print.css` blendet Navigation, Modebar und Buttons aus, druckt hell, bricht nicht mitten in einer Karte um. Nutzung: Browser → Drucken → „Als PDF speichern“. Risiko: Plotly setzt Farben inline im SVG, deshalb im Browser prüfen, ob ein dunkler Chart hell druckt; sonst beim Drucken per `beforeprint` auf das helle Template umschalten.
- **Auto-Aktualisierung ohne Zoomverlust:** `uirevision` je Chart fest setzen.
- **Ehrliche Darstellung:** `connectgaps=False`. Veraltete Abschnitte werden abgesetzt, nicht interpoliert. Keine geglättete Linie ohne Hinweis auf die Glättung.
- **Deutsches Format:** `layout.separators=",."` für Dezimalkomma; Achsen- und Hoverformate numerisch (`%d.%m.%Y`, bei Zoom über `tickformatstops`). So entstehen keine englischen Monatsnamen und es braucht keine Plotly-Locale-Datei.
- **Kein HTML aus Daten:** Plotly interpretiert in Titeln, Annotationen und Hovertexten eine HTML-Teilmenge. Dort stehen nur Texte aus der Konfiguration und selbst formatierte Zahlen und Daten, nie Rohtexte aus Quellen.

### 7.2 Kurzinfo und Erklärseite

- **Kennzahl-Kopf** (eine Komponente für alle): Name als `dcc.Link` auf `/kennzahl/<id>`, daneben ein Info-Symbol mit Tooltip.
- **Tooltip:** `html.Span("ⓘ", tabIndex=0, **{"data-tip": kurzinfo, "aria-label": kurzinfo})`, Anzeige per CSS über `:hover` und `:focus`, Text über `content: attr(data-tip)`, also nie als HTML. Dash-HTML-Komponenten erlauben `data-*`- und `aria-*`-Attribute (geprüft: `_valid_wildcard_attributes` in Dash 4.4.1). Auf Touchgeräten gibt es kein Mouseover; Antippen setzt den Fokus und zeigt die Kurzinfo.
- **Erklärseite `/kennzahl/<id>`:**
  1. Name und Kurzinfo
  2. Karte „Aktueller Stand“: Wert, Beobachtungsdatum, Abrufzeit, Perzentil, Status
  3. Verlauf mit Perzentilbändern
  4. handgeschriebener Teil aus `fever/web/texts/<id>.md`, gerendert mit `dcc.Markdown` ohne HTML
  5. erzeugter „Steckbrief“ aus `series.toml`: Quelle, Serien-ID, Frequenz, Veröffentlichung und Verzug, Toleranz, Historie ab, Orientierung, Block bzw. Fallhöhe, Transformation, Mindesthistorie, Lizenzhinweis
  6. erzeugter Abschnitt „Schwellen und Farben“ aus `scoring.toml`
  7. Quellen
- **Übersichtsseite „Erklärungen“:** alle Kennzahlen nach Block gruppiert, dazu die Konzeptseiten „Perzentil“, „Ampel“, „Konfidenz“, „Veraltung“.

### 7.3 Aktualität

- **Je Wert:** Beobachtungsdatum, Abrufzeitpunkt (Europe/Berlin mit Zonenkürzel MEZ/MESZ) und relatives Alter („vor 3 Std.“).
- **Veraltet** (älter als Frequenz plus Toleranz): ausgegraut und schraffiert, dazu das Wort „veraltet“. Nie nur über Farbe.
- **Kopfzeile auf jeder Seite:** letzte erfolgreiche Worker-Aktualisierung und Zeitpunkt der letzten Seitenaktualisierung.
- **Worker-Banner:** Ist der Heartbeat überfällig (dieselbe Grenze wie der Healthcheck), erscheint ein roter Hinweis „Worker ohne Lebenszeichen seit …, Werte werden nicht aktualisiert“.
- **Seiten-Aktualisierung (E-7):** `dcc.Interval` alle 5 Minuten liest Daten und Status neu.
- **Verbindungs-Wächter:** Ist der Pi nicht erreichbar, schlagen die Interval-Callbacks fehl und die Seite zeigt still alte Werte. Deshalb merkt sich ein Clientside-Callback die Browserzeit der letzten erfolgreichen Antwort. Ein zweiter Clientside-Timer blendet nach mehr als 2 Intervallen ohne Antwort ein Banner ein: „Keine Verbindung zum Pi – angezeigte Werte vom …“. Es wird die Browserzeit verglichen, nicht die Serverzeit, damit abweichende Uhren keine Rolle spielen.
- **Uhrzeit des Pi:** Die Veraltungslogik hängt an der Systemzeit. Die Einrichtungsanleitung prüft die NTP-Synchronisation.

### 7.4 Gestaltung

- **Grundsatz:** ruhig, konsistent, lesbar; Zahlen stehen im Vordergrund. Keine Animationen, keine Tachometer-Spielereien, keine 3D-Charts.
- **Farbschema (E-5):** CSS-Variablen in `assets/base.css`, hell und dunkel über `prefers-color-scheme`. Zwei registrierte Plotly-Templates (`fever_light`, `fever_dark`). `assets/theme.js` erkennt das Schema und meldet Wechsel über `matchMedia(...).addEventListener("change", …)` an einen `dcc.Store`; die Figure-Callbacks lesen ihn.
- **Semantische Farben:**
  - Ampel: vier Stufen, farbenblind-tauglich gewählt, immer mit Text („Grün“, „Gelb“, „Orange“, „Rot“)
  - Perzentilskala für Einzelkennzahlen: eine einfarbige, sequenzielle Skala, bewusst getrennt von den Ampelfarben (E-1)
  - „erhöht“: Textmarke plus Rahmen
- **Typografie:** Systemschriften (`system-ui, …`), `font-variant-numeric: tabular-nums` für Zahlenkolonnen. Keine Webfonts.
- **Layout:** Karten in einem CSS-Grid; die Übersicht ist zuerst für 390 px Breite entworfen (eine Spalte) und wird ab Tablet mehrspaltig. Navigation als Leiste, auf dem Smartphone horizontal scrollbar.
- **Nur lokale Ressourcen:** Dash 4.4.1 liefert plotly.js aus dem Python-Paket aus, solange `serve_locally=True` (Standard) gilt; ein CDN wird nur bei `serve_locally=False` benutzt (geprüft in `dash/dash.py`, `_setup_plotlyjs`). Ein Test sichert das ab.

---

## 8. Risiken

| Risiko | Wirkung | Gegenmaßnahme |
|---|---|---|
| Verzögerter Start des Workers | ICE-Historie geht tageweise verloren | M0–M3 zuerst, früh auf den Pi |
| Dash 4 / Plotly 7 sind neuer als das Trainingswissen vieler KI-Modelle | erfundene oder veraltete Signaturen | Signaturen im installierten Paket nachsehen; bei Unsicherheit sagen |
| Unverifizierte Endpoints (OFR, EBP, CISS, TFF-IDs, VIX6M) | Quelle fällt aus oder liefert anderes Format | real abrufen vor dem Parser (M2/M4), Fixture, sichtbarer Fehler |
| Rechenzeit rollierender Perzentile auf dem Pi | langsame Neuberechnung | messen in M5, erst dann optimieren |
| Druck von dunklen Charts | unlesbare PDFs | Prüfung in M6, Fallback `beforeprint` |
| Kein Passwort im Heimnetz (E-3) | jedes Gerät im WLAN sieht das Dashboard | akzeptiert; die Daten sind öffentliche Marktdaten ohne Kontobezug |
| Docker umgeht ufw (E-4) | Firewall-Regeln greifen nicht für den Web-Port | in `docs/einrichtung.md` dokumentiert; keine Portweiterleitung im Router |

---

## 9. Übergabe an die nächste Sitzung

- **Stand (25.09.2026):** Planung und Doku angelegt, M0 erledigt: Gerüst, Image (arm64 geprüft), Compose, Laden der Konfiguration, 11 Tests grün. Kein Speicher, keine Quellen, kein Worker, keine Oberfläche.
- **Nächster Schritt:** M1-Plan liegt dem Nutzer zur Freigabe vor (Schema). E-8 und E-9 sind entschieden. Nach Freigabe umsetzen.
- **Offene Entscheidungen des Nutzers:** O-1, O-2, O-4, O-5, O-6 (`CLAUDE.md`), L-1 bis L-13 (Abschnitt 5), dazu die Entscheidungen bei M1, M2 und M3 (Betriebs-Branch).
- **Befehle:** `pytest -q` (Python 3.14 mit `requirements-dev.txt`), arm64-Probe siehe Abschnitt 10; Betriebsbefehle in `CLAUDE.md` gelten ab M3.

---

## 10. Entwicklungsumgebung (für KI-Sitzungen in der Cloud)

Stand 25.09.2026, erprobt in der Claude-Code-Cloud-Umgebung. Die Umgebung ist ein flüchtiger Container: Docker-Daemon, QEMU-Registrierung und Hilfs-Images sind nach einem Neustart weg.

1. **Docker-Daemon starten** (CLI und `dockerd` sind installiert, laufen aber nicht):
   ```bash
   nohup dockerd > /tmp/dockerd.log 2>&1 &
   ```
2. **arm64-Emulation registrieren** (für Build-Probe und arm64-Container):
   ```bash
   sudo mount -t binfmt_misc binfmt_misc /proc/sys/fs/binfmt_misc
   docker run --privileged --rm tonistiigi/binfmt --install arm64
   ```
3. **Proxy-Zertifikat:** Ausgehender Verkehr läuft über einen Proxy (`$HTTPS_PROXY` auf 127.0.0.1) mit eigener CA (`/root/.ccr/ca-bundle.crt`). `pip` in Containern braucht deshalb `--network host`, die Proxy-Variablen und `PIP_CERT`. Die CA kommt nie ins Projekt-Dockerfile.
4. **Tests mit Python 3.14** (lokal gibt es nur 3.10–3.13): ein Hilfs-Image außerhalb des Repos, z. B. im Scratchpad:
   ```dockerfile
   FROM python:3.14-slim-trixie
   COPY --from=proxyca ca-bundle.crt /tmp/proxy-ca.crt
   ENV PIP_CERT=/tmp/proxy-ca.crt PYTHONDONTWRITEBYTECODE=1
   COPY requirements.txt requirements-dev.txt /tmp/req/
   RUN pip install -q --only-binary=:all: -r /tmp/req/requirements-dev.txt
   WORKDIR /src
   ```
   ```bash
   docker build -f <scratch>/Dockerfile.devtest --build-context proxyca=/root/.ccr \
     --network host --build-arg HTTPS_PROXY --build-arg HTTP_PROXY -t fever-devtest .
   docker run --rm -v "$PWD":/src fever-devtest pytest -q -p no:cacheprovider
   ```
5. **arm64-Build-Probe:** Kopie des Dockerfiles mit den zwei Zertifikatszeilen nach `FROM`, sonst unverändert:
   ```bash
   sed '/^FROM /a COPY --from=proxyca ca-bundle.crt /tmp/proxy-ca.crt\nENV PIP_CERT=/tmp/proxy-ca.crt' \
     Dockerfile > <scratch>/Dockerfile.probe
   docker buildx build --platform linux/arm64 -f <scratch>/Dockerfile.probe \
     --build-context proxyca=/root/.ccr --network host \
     --build-arg HTTPS_PROXY --build-arg HTTP_PROXY --load -t fever:probe-arm64 .
   ```
6. **Compose prüfen ohne `.env`** (die echte `.env` wird nie gelesen): eine Testdatei mit Platzhaltern im Scratchpad anlegen und `docker compose --env-file <scratch>/probe.env config` aufrufen.
7. **Abhängigkeiten ändern:** im arm64-Container mit `pip install --only-binary=:all: -r <direkte Pakete>` auflösen, `pip freeze` übernehmen, direkte Pakete mit Zweckkommentar oben in `requirements.txt`, transitive darunter.
