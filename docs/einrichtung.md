# Einrichtung und Betrieb auf TrueNAS mit Dockge

Stand: 30.09.2026 · Für: dich als Anwender · Status: **Worker läuft auf TrueNAS seit 26.09.2026 („healthy“).** Betrieb vom Branch `claude-raramo` (E-76), Datenbank auf Migration 0004, Stand mit der Sperr-Korrektur vom 30.09.2026; Phase 1 abgenommen (M9, Rückmeldung des Nutzers 30.09.2026). Nächstes Update: Alerts (M12) mit Migration 0005, Abschnitt 9 und Schritt 8.1. Image, Compose-Dateien, Datenbank, Worker, Healthcheck, Backup und Wiederherstellung sind zusätzlich in der Entwicklungsumgebung geprüft (x86_64, Container als UID 568). Die Oberfläche (Dienst `web`, seit M6) ist in der Entwicklungsumgebung geprüft und läuft auf TrueNAS (Rückmeldung des Nutzers; Einzelprüfungen in den Abschnitten).

Markierungen:
- ✅ geprüft: ausgeführt, mit Datum und Ort
- ⏳ geplant oder ungeprüft: Der Befehl steht fest, wurde aber noch nicht auf deinem TrueNAS ausgeführt

Festgelegt (Entscheidungen E-21, E-28 bis E-33 vom 26.09.2026):

| Was | Wert |
|---|---|
| TrueNAS | 25.10.7 „Goldeye“ |
| Projektverzeichnis (Dataset, Git-Klon, Build) | `/mnt/Daten-Z1/apps/feewer` |
| Datenordner (Kind-Dataset, von Git ignoriert) | `/mnt/Daten-Z1/apps/feewer/data` |
| Benutzer der Container | `apps`, UID/GID 568:568 |
| Branch | `claude-raramo` (seit 28.09.2026, E-76; vorher `claude-testing`, E-30) |
| Web-Port (ab M6) | 8003 |
| Dockge-Stack | Name `finanz-dashboard`, Container `finanz-dashboard-worker-1` (die Befehle unten setzen ihn voraus) |

Befehle stehen in grauen Kästen. Was nach `#` folgt, ist ein Kommentar und wird nicht mit eingegeben. Die Befehle laufen in der TrueNAS-Shell als `admin`.

---

## 0. Überblick

- **Build:** Das Image `fever:local` wird im Projektverzeichnis mit `docker-compose.yml` gebaut (Bau-Datei, startet nichts).
- **Betrieb:** Dockge startet den Stack `finanz-dashboard` aus einer Kopie von `compose.dockge.yaml`. Einstellungen und der FRED-Schlüssel stehen in der `.env` dieses Stacks.
- **Container:**
  - `worker` holt Marktdaten nach Veröffentlichungsplan (America/New_York), speichert sie, schreibt alle 15 Minuten ein Lebenszeichen und legt täglich ein Backup an.
  - `web` (die Oberfläche) folgt mit M6.
- **Daten:** SQLite-Datei, Rohantworten und Backups im Datenordner `data/`.
- **Zugang:** nur aus dem Heimnetz, ohne Passwort (O-3).

```
/mnt/Daten-Z1/apps/feewer/        Dataset: Projektverzeichnis (git clone, Build)
├── fever/, config/, Dockerfile, docker-compose.yml, compose.dockge.yaml, …
└── data/                         Kind-Dataset, Eigentümer apps (568:568)
    ├── fever.sqlite3             Datenbank (daneben im Betrieb -wal und -shm)
    ├── raw/                      Rohantworten der Quellen (gzip)
    └── backup/                   Backups
```

> **Warnung:** Im Projektverzeichnis nie `git clean -fdx` ausführen. `-x` löscht auch von Git ignorierte Ordner, also Datenbank und Backups zugleich. Das lokale Archiv der ICE-Spreads ist nicht wiederbeschaffbar. `git pull` und `git status` sind unbedenklich.

## 1. Was du brauchst

- TrueNAS mit Dockge (läuft bei dir bereits)
- Shell-Zugang als `admin` mit `sudo`
- einen kostenlosen FRED-API-Schlüssel (Schritt 4)

## 2. TrueNAS prüfen ⏳

### 2.1 Werkzeuge

```bash
git --version          # erwartet: git version 2.…
sudo docker version    # erwartet: Abschnitte "Client" und "Server"
sudo docker compose version    # erwartet: Docker Compose version v2.… oder neuer
```

`git` ist auf TrueNAS 25.10.7 vorhanden (✅ 26.09.2026, TrueNAS: Git-Befehl lief). Nur falls der erste Befehl doch `command not found` meldet, übernimmt ein Container die Rolle von Git. Dann in allen folgenden Git-Befehlen `git` durch `$GIT` ersetzen:

```bash
GIT="sudo docker run --rm -u $(id -u):$(id -g) -v /mnt/Daten-Z1/apps/feewer:/git -w /git alpine/git"
$GIT --version    # erwartet: git version 2.…
```

`$GIT` gilt nur in der aktuellen Shell; nach einem neuen Login die erste Zeile erneut ausführen.

### 2.2 Uhrzeit

Das Dashboard entscheidet anhand der Uhrzeit, ob ein Wert veraltet ist, und plant die Abrufe danach.

```bash
timedatectl    # erwartet: "System clock synchronized: yes"
```

Steht dort `no`: in TrueNAS unter System → General → NTP-Server prüfen.

## 3. Projekt holen und Datenordner anlegen ⏳

### 3.1 Projektverzeichnis beschreibbar machen

Das Dataset gehört `root`. `admin` braucht Schreibrechte für den Klon:

```bash
sudo chown admin:admin /mnt/Daten-Z1/apps/feewer
ls -ld /mnt/Daten-Z1/apps/feewer    # erwartet: … admin admin … /mnt/Daten-Z1/apps/feewer
```

### 3.2 Projekt holen (Branch `claude-raramo`, E-76)

Das Repository ist öffentlich; es braucht keine Zugangsdaten. `git clone` verlangt ein leeres Verzeichnis und scheitert, sobald das Dataset `data` existiert („destination path '.' already exists and is not an empty directory“). Deshalb holen diese Befehle das Projekt in das bestehende Verzeichnis. `data/` bleibt dabei unberührt, weil Git es ignoriert. Die Reihenfolge von 3.2 und 3.3 ist damit egal.

```bash
cd /mnt/Daten-Z1/apps/feewer
git init
git remote add origin https://github.com/grisu314-ui/Finanz-Dashboard.git
git fetch origin claude-raramo
git checkout -b claude-raramo origin/claude-raramo
#   erwartet: Switched to a new branch 'claude-raramo'
#             branch 'claude-raramo' set up to track 'origin/claude-raramo'.
git status    # erwartet: "On branch claude-raramo", "Your branch is up to date …", "nothing to commit, working tree clean"
```

✅ 26.09.2026, Entwicklungsumgebung (damals mit Branch `claude-testing`): in einem Verzeichnis mit vorhandenem `data/`; dessen Inhalt blieb unverändert. Meldet `git init` „Permission denied“, fehlt Schritt 3.1.

### 3.3 Kind-Dataset `data` anlegen (E-28)

✅ 26.09.2026, TrueNAS: Worker schreibt als 568:568 in `/mnt/Daten-Z1/apps/feewer/data` (per `docker inspect` und `ls -ln` geprüft).

In der TrueNAS-Oberfläche:
1. Datasets → `Daten-Z1/apps/feewer` auswählen → „Add Dataset“.
2. Name `data`, als Preset „Apps“ oder „Generic“ → Speichern.
3. `data` auswählen → Permissions → Edit: Owner User `apps`, Owner Group `apps` → Speichern.

Prüfen in der Shell:

```bash
zfs list -o name,mountpoint Daten-Z1/apps/feewer/data
#   erwartet: Daten-Z1/apps/feewer/data  /mnt/Daten-Z1/apps/feewer/data
stat -c '%u:%g %n' /mnt/Daten-Z1/apps/feewer/data
#   erwartet: 568:568 /mnt/Daten-Z1/apps/feewer/data
cd /mnt/Daten-Z1/apps/feewer && git status --short    # erwartet: keine Ausgabe (data/ ist ignoriert)
```

Zeigt `stat` andere Zahlen, ersatzweise: `sudo chown 568:568 /mnt/Daten-Z1/apps/feewer/data`.

## 4. FRED-API-Schlüssel beantragen

FRED (Federal Reserve Bank of St. Louis) liefert einen Großteil der Daten. Der Schlüssel ist kostenlos.

1. Unter https://fredaccount.stlouisfed.org/ ein Konto anlegen und die E-Mail-Adresse bestätigen.
2. Unter https://fredaccount.stlouisfed.org/apikeys auf „Request API Key“ klicken, den Zweck kurz beschreiben (z. B. „private dashboard, personal use“) und den Nutzungsbedingungen zustimmen.
3. Den Schlüssel sicher notieren. Er kommt in Schritt 7 in die `.env` des Dockge-Stacks und nirgendwo sonst hin: nicht in Chats, nicht in Git.

Quelle der Schritte: FRED-Dokumentation zum API-Schlüssel, per Websuche am 25.09.2026 ermittelt. Weicht die Seite ab, gilt die Seite.

## 5. Image bauen

✅ 26.09.2026, TrueNAS (Worker läuft mit diesem Image); zuvor Entwicklungsumgebung: x86_64, 42 s, Image 125 MB.

```bash
cd /mnt/Daten-Z1/apps/feewer
sudo docker compose build
sudo docker image ls fever    # erwartet: fever   local   …
```

`sudo docker compose up` in diesem Verzeichnis startet nichts, es gibt nur den Hinweis „Nur zum Bauen …“ aus (✅ Entwicklungsumgebung 26.09.2026).

## 6. Datenbank anlegen

✅ 26.09.2026, TrueNAS (der Worker startet nur mit Datenbank); zuvor Entwicklungsumgebung als UID 568.

Einmalig vor dem ersten Start. Der Hilfsbefehl `$RUN` startet einen Einmal-Container mit dem Datenordner. Er wird unten mehrfach verwendet; nach einem neuen Login in der Shell muss er neu gesetzt werden:

```bash
RUN='sudo docker run --rm --user 568:568 -e FEVER_DATA=/data -v /mnt/Daten-Z1/apps/feewer/data:/data fever:local'
echo "$RUN"    # erwartet: sudo docker run --rm --user 568:568 … fever:local  (leer? Zeile darüber erneut ausführen)
$RUN alembic upgrade head
#   erwartet u. a.: Running upgrade  -> 0001, Initial schema: …
$RUN alembic current
#   erwartet: 0001 (head)
```

Ohne diesen Schritt startet der Worker nicht, sondern meldet im Log „Datenbank fehlt …“.

## 7. Dockge-Stack anlegen und starten

✅ 26.09.2026, TrueNAS mit Dockge: Container `finanz-dashboard-worker-1` „Up (healthy)“, Healthcheck „gesund: letzter Heartbeat vor 2 Minuten“. Zuvor Entwicklungsumgebung: Stopp in unter 1 s.

1. In Dockge „+ Compose“, Stack-Name `finanz-dashboard`.
2. Als `compose.yaml` den Inhalt von `compose.dockge.yaml` einfügen:
   ```bash
   cat /mnt/Daten-Z1/apps/feewer/compose.dockge.yaml
   ```
3. Im `.env`-Bereich des Stacks den Inhalt von `.env.example` einfügen und `FRED_API_KEY=` (Schlüssel aus Schritt 4) sowie `FEVER_SEC_CONTACT=` ergänzen (dein Name und deine E-Mail-Adresse, z. B. `FEVER_SEC_CONTACT=Max Mustermann max@example.org`; die SEC verlangt einen Kontakt von jedem automatischen Abrufer). Die übrigen Werte sind vorbelegt:
   ```bash
   cat /mnt/Daten-Z1/apps/feewer/.env.example
   ```
4. Speichern und „Deploy“ bzw. „Start“. Nach jeder Änderung an `compose.yaml` oder `.env` des Stacks ebenfalls „Deploy“: Ein Neustart übernimmt geänderte Einstellungen nicht, die Container behalten die alten.

| Variable | Bedeutung | Fehlt sie … |
|---|---|---|
| `FRED_API_KEY` | FRED-Schlüssel (Schritt 4) | Start bricht mit „FRED_API_KEY fehlt in .env“ ab |
| `FEVER_DATA_DIR` | Datenordner `/mnt/Daten-Z1/apps/feewer/data` | Start bricht mit „FEVER_DATA_DIR fehlt in .env“ ab |
| `FEVER_UID`, `FEVER_GID` | Benutzer der Container, 568 (`apps`) | Start bricht mit „FEVER_UID fehlt in .env“ bzw. „FEVER_GID fehlt …“ ab |
| `FEVER_WEB_PORT` | Port des Dashboards, 8003 | Start bricht mit „FEVER_WEB_PORT fehlt in .env“ ab |
| `FEVER_SEC_CONTACT` | Name und E-Mail-Adresse für den Abruf bei der SEC (Top-10-Konzentration, E-71); kein Secret, aber persönlich | Stack startet; der Worker warnt beim Start im Log, und die Quelle SEC meldet im Datenstand, was fehlt (Abschnitt 11) |
| `FEVER_NTFY_TOPIC` | Thema der Alerts auf ntfy.sh (M12, E-100), ein Secret; erzeugen wie in Schritt 8.1 | Stack startet; Alerts sind aus, der Worker warnt beim Start, der Datenstand zeigt „Alerts aus“ |

Ein fehlender Datenordner ist ein Fehler und wird nicht stillschweigend angelegt.

Prüfen:

```bash
sudo docker logs --tail 20 finanz-dashboard-worker-1
#   erwartet u. a.: INFO __main__: Worker gestartet: 72 Reihen in 44 Abrufgruppen, Takt 15 Minuten
#                   INFO __main__: Tägliches Backup erstellt und geprüft: fever-…-daily.sqlite3
sudo docker exec finanz-dashboard-worker-1 python -c "import sys; from fever.worker import healthcheck; sys.exit(healthcheck())"
#   erwartet: gesund: letzter Heartbeat vor 0 Minuten
```

Dockge zeigt den Worker nach spätestens rund 5 Minuten als „healthy“; vorher steht dort „starting“.

**Wann die ersten Daten kommen:** Der Worker ruft jede Reihe an New-Yorker Werktagen ab ihrer Veröffentlichungszeit ab (E-31); an Wochenenden ruft er nichts ab. Als Erstes kommt SOFR um 08:15 New York (derzeit 14:15 Uhr deutscher Zeit). Im Log steht dann z. B. `INFO fever.sources.update: sofr: 2118 neue Zeilen (Erstabruf)`. Das lokale ICE-Archiv beginnt mit dem ersten Abruf der ICE-Reihen um 10:15 New York (derzeit 16:15 Uhr).

**Sofort-Abruf:** ruft alle Reihen einmal sofort ab, unabhängig vom Abrufplan. Sinnvoll nach der Einrichtung an einem Wochenende und nach einem Update mit neuen Reihen: FRED liefert die ICE-Spreads nur für drei Jahre rückwirkend, jeder Tag Warten kostet den ältesten Tag. Doppelte Abrufe schaden nicht; unveränderte Werte werden nicht erneut gespeichert.

```bash
sudo docker exec finanz-dashboard-worker-1 python -m fever.sources.update
#   erwartet je Reihe eine Zeile, z. B.: INFO __main__: ecb_ciss: 12199 neue Zeilen (Erstabruf)
#   am Ende: INFO __main__: Sofort-Abruf beendet: 72 Reihen, 0 mit Problemen   (Exit-Code 0)
#   der erste Abruf der SEC (sec_spy_top10) lädt 28 Meldungen, rund 13 MB, etwa 10 Sekunden
#   der erste Abruf der VX-Futures (Gruppe cfe_vx) lädt rund 175 Dateien und dauert etwa 3 Minuten
#   ein zweiter Lauf meldet je Reihe "0 neue Zeilen"
```

✅ 26.09.2026, TrueNAS nach den Updates auf M4b (41 Reihen) und M4c (44 Reihen), jeweils 0 mit Problemen. Mit M4d (60 Reihen): ✅ TrueNAS 26.09.2026 („60 Reihen, 0 mit Problemen“); ✅ Entwicklungsumgebung (Worker-Startzeile ebenfalls; Shiller dort nur mit Proxy-Abbrüchen der Cloud-Umgebung). Mit der Rezessionsreihe `usrec` (61 Reihen, 33 Abrufgruppen): ✅ Entwicklungsumgebung 26.09.2026 (Zählung aus Katalog und Abrufgruppen, Abruf von `USREC`); ⏳ TrueNAS. Mit den Nasdaq-Reihen und der SEC-Reihe (71 Reihen, 43 Abrufgruppen, E-68, E-71): ✅ Entwicklungsumgebung 28.09.2026 („71 Reihen, 2 mit Problemen“: nur die zwei Shiller-Reihen, Proxy-Abbruch der Cloud-Umgebung; 9 Nasdaq-Reihen mit 1569 bis 5424 Zeilen, `sec_spy_top10` mit 28 Zeilen). Mit `baa10y` (72 Reihen, 44 Abrufgruppen, E-75): ✅ Entwicklungsumgebung 28.09.2026 (10183 Zeilen ab 02.01.1986); ⏳ TrueNAS. Meldet es „mit Problemen“ (Exit-Code 1), nennen die `ERROR`-Zeilen darüber Reihe und Grund.

## 8. Dashboard aufrufen

✅ 26.09.2026, Entwicklungsumgebung: Dienst `web` über `compose.dockge.yaml` als 568:568, „healthy“, `0.0.0.0:8003`; `/health`, `/`, `/datenstand` liefern 200. ✅ 26.09.2026, TrueNAS: Dashboard läuft (Rückmeldung des Nutzers).

Der Stack enthält seit M6 zwei Dienste, `worker` und `web`. Nach dem Update auf M6 muss die Kopie in Dockge den neuen Inhalt von `compose.dockge.yaml` bekommen (Schritt 7.2), sonst startet nur der Worker.

Im Browser eines Geräts im Heimnetz: `http://<IP-von-TrueNAS>:8003`.

```bash
curl -s http://127.0.0.1:8003/health       # auf TrueNAS; erwartet: {"status":"ok"}
sudo docker logs --tail 20 finanz-dashboard-web-1
#   erwartet u. a.: [INFO] Listening at: http://0.0.0.0:8050
#                   [INFO] Using worker: gthread
```

Dockge zeigt `web` nach rund einer Minute als „healthy“.

- Es gibt **kein Passwort**. Jedes Gerät in deinem Heimnetz kann das Dashboard öffnen. Es zeigt nur öffentliche Marktdaten, keine Kontodaten.
- **Keine Portweiterleitung** im Router einrichten; sonst wäre das Dashboard aus dem Internet erreichbar.

### 8.1 Alerts aufs Handy (M12) ⏳

✅ Entwicklungsumgebung 30.09.2026: Testnachricht an ein Wegwerf-Thema auf ntfy.sh angenommen (HTTP 200) und mit Titel, Priorität und Tags zurückgelesen; ⏳ TrueNAS.

Der Worker meldet über ntfy.sh, wenn die Ampel die Stufe wechselt, ein Indikator veraltet oder ein Fehler auch den nächsten Versuch übersteht (`docs/bedienung.md`, Alerts). Alle Themen auf ntfy.sh sind öffentlich; geschützt ist dein Kanal nur durch den unratbaren Namen des Themas. Die Nachrichten enthalten nur Ampel, Stress, Fallhöhe, Konfidenz, Regeln und Namen, keine Kurse oder Spreads.

1. App **ntfy** installieren (Android: Google Play oder F-Droid; iPhone: App Store).
2. Thema erzeugen, in der SSH-Shell auf TrueNAS:
   ```bash
   echo "fever-$(openssl rand -hex 20)"
   #   erwartet: fever- und 40 Zeichen aus 0–9 und a–f; diese Zeile ist dein Thema, wie ein Passwort behandeln
   ```
3. In der App „+“ bzw. „Thema abonnieren“, das Thema einfügen, Server `ntfy.sh` (Voreinstellung) lassen.
4. In Dockge beim Stack `finanz-dashboard` in der `.env` ergänzen: `FEVER_NTFY_TOPIC=<dein Thema>`. `compose.yaml` muss beim Worker die Zeile `FEVER_NTFY_TOPIC: ${FEVER_NTFY_TOPIC:-}` enthalten (neuer Inhalt aus `compose.dockge.yaml`, Schritt 7.2). Speichern, „Deploy“.
5. Testnachricht:
   ```bash
   sudo docker exec finanz-dashboard-worker-1 python -m fever.alerts --test
   #   erwartet: INFO __main__: Testnachricht gesendet; sie erscheint in der ntfy-App unter dem abonnierten Thema.
   #   und auf dem Handy: „Test: Alerts kommen an“
   ```
6. Innerhalb von 15 Minuten kommt leise „Alerts aktiv: Ampel …“, gegebenenfalls dazu „Veraltet: …“. Danach meldet sich der Worker nur bei Änderungen. Im Datenstand zeigt die Karte „Alerts (ntfy.sh)“, was zuletzt gemeldet wurde.

Wann das Handy klingelt, stellst du in der App ein (je Thema, etwa Ruhezeiten oder ab welcher Priorität). Die Prioritäten: Rot 5, Orange 4, Gelb und Probleme 3; Rückgänge, Erholungen und die erste Nachricht 2 (ohne Ton).

## 9. Update auf eine neue Version

✅ 26.09.2026, TrueNAS: Update auf M4b ohne Migration (Pull, Build, Neustart, Sofort-Abruf). Ablauf mit Migration (M5, 0001 → 0002): ✅ Entwicklungsumgebung 26.09.2026 mit dem gebauten Image als 568:568 auf einer Backup-Kopie; ✅ TrueNAS 26.09.2026. Migration 0002 → 0003 (Perzentilbänder, M7): ✅ Entwicklungsumgebung 27.09.2026 mit dem gebauten Image als 568:568 auf einer Backup-Kopie (danach Scoring 11,8 s, Werte unverändert); ✅ TrueNAS (Datenbank auf 0004, Nutzer 29.09.2026). Prüfung der Migration beim Start (E-70): ✅ Entwicklungsumgebung 28.09.2026 mit dem gebauten Image auf einer Datenbank mit Stand 0002 (Worker und `fever.score` melden „Migration fehlt“ und starten nicht, `/health` 503, Banner im Browser; `fever.backup` läuft; nach `alembic upgrade head` normaler Start); ⏳ TrueNAS.

**Update auf Alerts (M12, 30.09.2026, mit Migration 0005, `compose.dockge.yaml` und `.env.example` geändert):** ✅ Entwicklungsumgebung 30.09.2026 (Tests, Migration an einer Kopie der Entwicklungsdatenbank, Probe gegen ntfy.sh, Datenstand im Browser); ⏳ TrueNAS. Das neue Programm startet erst nach der Migration.

```bash
cd /mnt/Daten-Z1/apps/feewer
git pull
git diff --stat HEAD@{1} -- compose.dockge.yaml .env.example    # erwartet: beide Dateien mit neuen Zeilen (FEVER_NTFY_TOPIC)
git diff --stat HEAD@{1} -- migrations/                          # erwartet: migrations/versions/0005_alert_state.py
sudo docker compose build
```

1. Migration an einer Backup-Kopie proben: Block „Neue Migration zuerst an einer Kopie testen“ unten (erwartet `Running upgrade 0004 -> 0005, Alert state …`).
2. Standardablauf unten ab „Stack stoppen“: Backup, `$RUN alembic upgrade head`, `$RUN alembic current` (erwartet `0005 (head)`).
3. Schritt 8.1, Punkte 1 bis 4: App, Thema, `.env` und neue `compose.yaml` in Dockge, dann „Deploy“ (nicht „Neustart“).
4. Schritt 8.1, Punkte 5 und 6: Testnachricht und erste Meldung.

Ohne Thema läuft alles wie bisher; der Worker warnt beim Start, und der Datenstand zeigt bei den Quellen „Alerts aus“.

**Update: Wartezeit bei gesperrter Datenbank (30.09.2026, ohne Migration, `compose.dockge.yaml` unverändert):** ✅ Entwicklungsumgebung 30.09.2026 (Fehler nachgestellt und behoben); ✅ TrueNAS 30.09.2026 (Nutzer: Update und Sichtprüfung in Ordnung). Behebt „database is locked“, wenn ein Einmal-Befehl (Sofort-Abruf, `fever.score`) läuft, während der Worker schreibt: Er wartet jetzt bis zu 2 Minuten, statt nach 5 s abzubrechen (`docs/umsetzungsplan.md`, Abschnitt 4, „Datenbank gesperrt“).

```bash
cd /mnt/Daten-Z1/apps/feewer
git pull
git diff --stat HEAD@{1} -- compose.dockge.yaml .env.example    # erwartet: keine Ausgabe
git diff --stat HEAD@{1} -- migrations/                          # erwartet: keine Ausgabe
sudo docker compose build
```

In Dockge beim Stack `finanz-dashboard` „Deploy“. Danach als Probe den Sofort-Abruf; er darf auch laufen, während der Worker rechnet (dann wartet er einige Sekunden an einer Reihe):

```bash
sudo docker exec finanz-dashboard-worker-1 python -m fever.sources.update
#   am Ende: INFO __main__: Sofort-Abruf beendet: 81 Reihen, 0 mit Problemen
sudo docker logs finanz-dashboard-worker-1 2>&1 | grep "Scores berechnet" | tail -3
#   erwartet: Zeilen „Scores berechnet: … (… s)“; die Dauer am Ende bitte melden (Maß für die Wartezeit)
```

Der alte Sperrfehler bleibt bei der EZB im Datenstand unter „Letzter Fehler“ stehen, bis ein neuer ihn ersetzt; maßgeblich ist, dass „Letzter Erfolg“ neuer ist. Die Werte selbst waren gespeichert.

**Update auf M11, E-95 und die Farben der Fallhöhe (E-94 bis E-98, ohne Migration, `compose.dockge.yaml` unverändert):** ✅ Entwicklungsumgebung 29.09.2026 (Tests, Scoring, Validierung, Browser); ✅ TrueNAS 30.09.2026 (Nutzer: Update eingespielt; danach der Sperrfehler oben).

```bash
cd /mnt/Daten-Z1/apps/feewer
git pull
git diff --stat HEAD@{1} -- compose.dockge.yaml .env.example    # erwartet: keine Ausgabe
git diff --stat HEAD@{1} -- migrations/                          # erwartet: keine Ausgabe
sudo docker compose build
```

In Dockge beim Stack `finanz-dashboard` „Deploy“ (nicht „Neustart“). Waren M11 und E-95 noch nicht eingespielt, rechnet der Worker Scores und Validierung danach von selbst neu (geänderte `scoring.toml`); sofort statt im nächsten Takt:

```bash
sudo docker exec finanz-dashboard-worker-1 python -m fever.score
#   erwartet: INFO __main__: Scores berechnet: 9… Tage ab 02.01.1990, zuletzt <letzter Handelstag>: … (rund 20 bis 30 s)
sudo docker exec finanz-dashboard-worker-1 python -m fever.validate
#   erwartet: INFO __main__: Validierung berechnet: Rückgang: AUC Stress …, VIX … (…), geschätzte Gewichte … gegen gleiche … (…); … (rund 5 s)
```

Danach im Dashboard: alles zur Fallhöhe in Lila (Namen, Titel, Linien, der untere Teil der Heatmap, der Streifen in der Regime-Zeitleiste, die gestrichelte Kurve in der Validierung), Stress und alles Übrige in Blau; in der Ansicht „Validierung“ der Abschnitt „Geschätzte Gewichte“; kein Gelb mehr allein wegen hoher Fallhöhe (E-95).

**Update auf die Entscheidungsrunde 29.09.2026 und die Validierung (E-80 bis E-96, mit Migration 0004, `compose.dockge.yaml` unverändert):** ✅ Entwicklungsumgebung 29.09.2026 (Abruf der zehn neuen Reihen, Scoring, Validierung mit geschätzten Gewichten (M11), Fallhöhe-Streifen, Browser; Migrationsprobe mit dem gebauten Image als 568:568 auf einer Kopie mit Stand 0003); ✅ TrueNAS 29.09.2026 (Nutzer: Migration 0004 erledigt). Voraussetzung: TrueNAS läuft schon vom Branch `claude-raramo` (sonst zuerst der nächste Block). Neu sind zehn Reihen (S&P 500 von Cboe, versicherte Arbeitslosenquote, acht Z.1-Reihen), fünf Indikatoren, geänderte Ampelregeln (die Ampel ändert sich auch rückwirkend, `docs/umsetzungsplan.md`, Abschnitt 4, „Entscheidungsrunde 29.09.2026“) und die Ansicht „Validierung“ mit der neuen Tabelle `validation_report` (M10). Das neue Programm startet erst nach der Migration.

```bash
cd /mnt/Daten-Z1/apps/feewer
git pull
git diff --stat HEAD@{1} -- compose.dockge.yaml .env.example    # erwartet: keine Ausgabe
git diff --stat HEAD@{1} -- migrations/                          # erwartet: migrations/versions/0004_validation_report.py
sudo docker compose build
```

1. Migration an einer Backup-Kopie proben: Block „Neue Migration zuerst an einer Kopie testen“ unten (Stack läuft dabei weiter).
2. Standardablauf unten ab „Stack stoppen“: Backup, `$RUN alembic upgrade head` (erwartet u. a. `Running upgrade 0003 -> 0004, Validation report …`), `$RUN alembic current` (erwartet `0004 (head)`).
3. In Dockge beim Stack `finanz-dashboard` „Deploy“ (nicht „Neustart“: nur „Deploy“ startet die Container mit dem neuen Image).
4. Die neuen Reihen sofort holen, Scores und Validierung neu rechnen (sonst holt der Worker die Reihen am nächsten New-Yorker Werktag ab ihrer Veröffentlichungszeit und rechnet danach selbst):

```bash
sudo docker exec finanz-dashboard-worker-1 python -m fever.sources.update
#   erwartet u. a.: INFO __main__: spx: 130… neue Zeilen (Erstabruf)
#                   INFO __main__: iursa: 29… neue Zeilen (Erstabruf)
#                   INFO __main__: ncbeilq027s: 305 neue Zeilen (Erstabruf)   (ebenso die sieben übrigen Z.1-Reihen)
#   am Ende: INFO __main__: Sofort-Abruf beendet: 81 Reihen, 0 mit Problemen   (FRED SP500 entfällt, E-92)
sudo docker exec finanz-dashboard-worker-1 python -m fever.score
#   erwartet: INFO __main__: Scores berechnet: 9… Tage ab 02.01.1990, zuletzt <letzter Handelstag>: … (rund 20 bis 30 s)
sudo docker exec finanz-dashboard-worker-1 python -m fever.validate
#   erwartet: INFO __main__: Validierung berechnet: Rückgang: AUC Stress …, VIX … (…), geschätzte Gewichte … gegen gleiche … (…);
#             VIX-Spitze: …; Bärenmarkt: … (rund 5 s)
#   „keine auswertbaren Tage“ bei Rückgang und Bärenmarkt: Der S&P 500 (spx) fehlt noch, Sofort-Abruf prüfen
```

Danach im Dashboard: Marken neben den Namen (blau Stress mit Bereich, lila Fallhöhe, grau nur Anzeige, umrandet Ampelregel), in der Ansicht Makro Sahm-Regel, S&P-500-Trend und SOS-Indikator mit violetten Flächen für aktive Regeln und das Datum des letzten Re-Steepening, in der Ansicht Fallhöhe Aktienquote, Geldmarktfonds und Kreditspread-Enge, in der Navigation die Ansicht „Validierung“. Die y-Achse passt sich nach Zoom und Zeitraum-Knopf an (`docs/bedienung.md`). Seit E-95 gibt es kein Gelb mehr allein wegen hoher Fallhöhe: Die Ampel ändert sich auch rückwirkend und steht bei hoher Fallhöhe und niedrigem Stress auf Grün (Entwicklungsdatenbank 25.09.2026: Grün statt Gelb).

**Update auf schnellere Seiten und Branch `claude-raramo` (28.09.2026, E-76 bis E-78, ohne Migration):** ✅ TrueNAS 29.09.2026 (Nutzer: läuft vom Branch `claude-raramo`, Seiten spürbar schneller, vor allem beim wiederholten Aufruf). Einmal den Branch wechseln; danach gilt wieder der Standardablauf unten mit `git pull`.

```bash
cd /mnt/Daten-Z1/apps/feewer
git status                      # erwartet: "nothing to commit, working tree clean"
git fetch origin claude-raramo
git checkout -b claude-raramo origin/claude-raramo
#   erwartet: Switched to a new branch 'claude-raramo'
#             branch 'claude-raramo' set up to track 'origin/claude-raramo'.
sudo docker compose build
cat compose.dockge.yaml          # neuer Inhalt für compose.yaml in Dockge
```

1. In Dockge den Stack `finanz-dashboard` bearbeiten und `compose.yaml` vollständig durch die Ausgabe von `cat compose.dockge.yaml` ersetzen (neu: Dienst `web` mit einem Thread, E-77; beim Worker die Zeile `FEVER_SEC_CONTACT: ${FEVER_SEC_CONTACT:-}`).
2. In der `.env` des Stacks (nicht im Projektordner) steht `FEVER_SEC_CONTACT=Vorname Nachname name@beispiel.de`.
3. Speichern, dann „Deploy“ (nicht „Neustart“).
4. Prüfen und die SEC-Reihe sofort holen:

```bash
sudo docker logs finanz-dashboard-web-1 2>&1 | grep "Using worker"      # erwartet: [INFO] Using worker: gthread
sudo docker exec finanz-dashboard-worker-1 python -c "import os; from fever.sources.sec import contact_problem; print(contact_problem(os.environ.get('FEVER_SEC_CONTACT')) or 'SEC-Kontakt in Ordnung')"
#   erwartet: SEC-Kontakt in Ordnung   (sonst nennt die Zeile die Ursache, Abschnitt 11)
sudo docker exec finanz-dashboard-worker-1 python -m fever.sources.update
#   erwartet u. a.: INFO __main__: sec_spy_top10: 28 neue Zeilen (Erstabruf)
#   am Ende: INFO __main__: Sofort-Abruf beendet: 72 Reihen, 0 mit Problemen
```

Der Worker rechnet danach die Scores einmal neu (neue Programmversion von `fever/config.py`, rund 15 s); die Werte bleiben gleich (geprüft in der Entwicklungsumgebung: alle 9281 Tage identisch). Mit der Top-10-Konzentration ändert sich die Fallhöhe wie unter E-71 beschrieben.

**Update auf Breite und Top-10 (E-68, E-71, ohne Migration):** `compose.dockge.yaml` hat eine neue Zeile (`FEVER_SEC_CONTACT` für den Worker): die Kopie in Dockge aktualisieren (Schritt 7.2) und in der `.env` des Stacks `FEVER_SEC_CONTACT=<Name> <E-Mail>` ergänzen (Schritt 7.3). Nach dem Start den Sofort-Abruf ausführen (Schritt 7, lädt die 11 neuen Reihen, mit BAA10Y aus E-75); der Worker rechnet die Scores danach von selbst neu, weil sich `series.toml` geändert hat. Stress und Ampel ändern sich dabei auch rückwirkend (Block Breite, Top-10 in der Fallhöhe). Steht die Datenbank noch auf 0002, gilt zusätzlich der Ablauf mit Migration unten. ⏳ TrueNAS als eigener Schritt; im Stand mit Migration 0004 enthalten (Nutzer 29.09.2026), der SEC-Kontakt dort ungeprüft (Abschnitt 11).

**Update auf M7 (Migration 0003):** Das neue Dashboard liest die Spalten der Perzentilbänder. Der Stack darf deshalb erst nach `alembic upgrade head` wieder starten. Seit E-70 prüfen Worker und Dashboard die Migration beim Start: Fehlt sie, startet der Worker nicht, und das Dashboard zeigt das rote Banner „Migration fehlt“ (Fehlersuche, Abschnitt 11). Nach dem Start einmal `python -m fever.score` (unten), damit die Bänder sofort gefüllt sind.

Standardablauf, alles in der SSH-Shell auf TrueNAS; nur Stopp und Start des Stacks in Dockge. Er schadet nie: Gibt es keine neue Migration, ändert `alembic upgrade head` nichts, und die Sicherung davor ist nur eine zusätzliche Kopie. Ob eine neue Migration dabei ist, zeigt die Zeile mit `migrations/`.

```bash
cd /mnt/Daten-Z1/apps/feewer
git pull
git diff --stat HEAD@{1} -- compose.dockge.yaml .env.example    # Ausgabe? Dann Schritt 7.2/7.3 wiederholen
git diff --stat HEAD@{1} -- migrations/                          # Ausgabe = neue Migration
sudo docker compose build
# in Dockge: Stack "finanz-dashboard" stoppen
RUN='sudo docker run --rm --user 568:568 -e FEVER_DATA=/data -v /mnt/Daten-Z1/apps/feewer/data:/data fever:local'    # wie Schritt 6, gilt bis zum Abmelden
echo "$RUN"    # erwartet: sudo docker run --rm --user 568:568 … fever:local; leer heißt: neue Sitzung, Zeile darüber erneut ausführen
$RUN python -m fever.backup        # Sicherung vor der Migration
#   erwartet: INFO __main__: Backup erstellt und geprüft: /data/backup/fever-…-manual.sqlite3
$RUN alembic upgrade head
#   erwartet ohne neue Migration nur zwei Zeilen "INFO [alembic.runtime.migration] …", kein "Running upgrade"
$RUN alembic current
#   erwartet: die neueste Nummer mit "(head)", derzeit 0005 (head)
# in Dockge: Stack "finanz-dashboard" starten
sudo docker exec finanz-dashboard-worker-1 python -m fever.sources.update    # nur wenn neue Reihen dazukamen (Schritt 7)
```

Neue Reihen holt der Worker sonst selbst, am nächsten New-Yorker Werktag ab ihrer Veröffentlichungszeit.

**Neue Migration zuerst an einer Kopie testen** (`CLAUDE.md`: nie zuerst an der Produktivdatenbank). Nur wenn die Zeile mit `migrations/` etwas ausgibt; nach dem Build und bevor der Stack gestoppt wird:

```bash
cd /mnt/Daten-Z1/apps/feewer
sudo docker exec finanz-dashboard-worker-1 python -m fever.backup      # frisches Backup, Stack läuft weiter
PROBE=/mnt/Daten-Z1/apps/feewer/data/migrationsprobe
sudo mkdir -p $PROBE
sudo cp "data/backup/$(sudo ls -t data/backup | grep manual | head -1)" $PROBE/fever.sqlite3    # Kopie des Backups, nicht der laufenden Datenbank
sudo chown -R 568:568 $PROBE
sudo docker run --rm --user 568:568 -e FEVER_DATA=/data -v $PROBE:/data fever:local alembic upgrade head
#   erwartet u. a. (Update auf M12): Running upgrade 0004 -> 0005, Alert state (M12, decisions E-99, E-100): …
sudo docker run --rm --user 568:568 -e FEVER_DATA=/data -v $PROBE:/data fever:local python -m fever.score
#   erwartet: INFO __main__: Scores berechnet: … Tage ab …, zuletzt …: Stress …, Fallhöhe …, Ampel …, Konfidenz … % (… s)
sudo docker run --rm --user 568:568 -e FEVER_DATA=/data -v $PROBE:/data fever:local python -m fever.validate
#   erwartet: INFO __main__: Validierung berechnet: … (… s); vor dem ersten Abruf von spx bei Rückgang und Bärenmarkt „keine auswertbaren Tage“
sudo rm -r $PROBE
```

Klappt beides, weiter mit dem Standardablauf oben ab „Stack stoppen“. Scheitert die Probe, nichts an der Produktivdatenbank ändern und die Ausgabe melden.

**Scores (ab M5):** Nach neuen Daten, einer geänderten `scoring.toml`/`series.toml` oder einer neuen Programmversion des Scorings (seit 28.09.2026) rechnet der Worker am Ende seines Takts alle Scores neu; im Log steht dann `INFO __main__: Scores berechnet: …`. Sofort statt erst im nächsten Takt (dauert rund 15 s):

```bash
sudo docker exec finanz-dashboard-worker-1 python -m fever.score
#   erwartet: INFO __main__: Scores berechnet: 9… Tage ab 02.01.1990, zuletzt <letzter Handelstag>: Stress …, Fallhöhe …, Ampel …, Konfidenz … % (… s)
```

Die Werte zeigt ab M6 die Oberfläche; bis dahin nur diese Log-Zeile.

**Validierung (ab M10, E-93):** Nach jedem Scoring-Lauf mit neuen Scores und nach einer Änderung von `scoring.toml` oder des Validierungscodes rechnet der Worker die Validierung neu (Ansicht „Validierung“); im Log steht dann `INFO __main__: Validierung berechnet: …`. Sofort (wenige Sekunden):

```bash
sudo docker exec finanz-dashboard-worker-1 python -m fever.validate
#   erwartet: INFO __main__: Validierung berechnet: Rückgang: AUC Stress …, VIX … (…); VIX-Spitze: …; Bärenmarkt: … (… s)
```

## 10. Backup und Wiederherstellung

### 10.1 Backup

✅ 25.09.2026 (manuell) und 26.09.2026 (täglich durch den Worker), Entwicklungsumgebung. ⏳ auf TrueNAS.

Backups liegen in `/mnt/Daten-Z1/apps/feewer/data/backup/` und werden vor dem Ablegen auf Fehlerfreiheit geprüft (`integrity_check`). Ein weiteres Ziel außerhalb gibt es nicht (E-22).

| Art | Dateiname (Zeit in UTC) | entsteht | aufbewahrt (E-8) |
|---|---|---|---|
| täglich | `fever-20260926T105602Z-daily.sqlite3` | automatisch durch den Worker, einmal pro UTC-Tag | die neuesten 14 |
| manuell | `fever-20260925T203329Z-manual.sqlite3` | mit dem Befehl unten, auch vor jeder Migration | die neuesten 5 |

Andere Dateien in `backup/` werden nie gelöscht. Sofortiges Backup bei laufendem Stack:

```bash
sudo docker exec finanz-dashboard-worker-1 python -m fever.backup
#   erwartet: … INFO __main__: Backup erstellt und geprüft: /data/backup/fever-…-manual.sqlite3
sudo ls -lh /mnt/Daten-Z1/apps/feewer/data/backup/
```

Bei gestopptem Stack stattdessen `$RUN python -m fever.backup`. Bei einem Fehler endet der Befehl mit Exit-Code 2 und einer Meldung, z. B. `Keine Datenbank vorhanden: /data/fever.sqlite3`.

### 10.2 Wiederherstellung

✅ 25.09.2026, Entwicklungsumgebung: Backup zurückgespielt, Werte identisch. ⏳ auf TrueNAS.

Nie eine laufende Datenbank überschreiben. Die Datenbank heißt `fever.sqlite3`. Nach einem Absturz können daneben `fever.sqlite3-wal` und `fever.sqlite3-shm` liegen; sie gehören zur alten Datei und müssen mit weg. Die Kopie läuft über `$RUN`, damit sie `apps` gehört.

```bash
# in Dockge: Stack "finanz-dashboard" stoppen
D=/mnt/Daten-Z1/apps/feewer/data
sudo ls -l $D $D/backup                        # was liegt da? gewünschtes Backup aussuchen
ALT=$D/alt-$(date +%F)
sudo mkdir -p "$ALT"
sudo mv $D/fever.sqlite3 "$ALT"/
sudo sh -c "mv $D/fever.sqlite3-* '$ALT'/ 2>/dev/null; true"
$RUN cp /data/backup/<backup-datei> /data/fever.sqlite3
$RUN alembic current                           # erwartet: "0001 (head)" oder neuer
# in Dockge: Stack "finanz-dashboard" starten
```

Den Ordner `alt-…` erst löschen, wenn wieder alles korrekt läuft. Zeigt `alembic current` kein `(head)`, stammt das Backup von vor einer Migration: dann `$RUN alembic upgrade head` ausführen.

## 11. Fehlersuche ⏳

| Symptom | Prüfen |
|---|---|
| Worker startet immer wieder neu | `sudo docker logs --tail 50 finanz-dashboard-worker-1`. „Datenbank fehlt“: Schritt 6. „Datenordner fehlt“ oder „Permission denied“: Schritt 3.3. „Migration fehlt“: nächste Zeile |
| „Migration fehlt: Datenbank auf …, Programm erwartet …“ (Worker-Log, rotes Banner im Dashboard, `/health` mit 503; E-70) | Das Image ist neuer als die Datenbank, `alembic upgrade head` fehlt. Worker, `fever.score` und `fever.sources.update` starten dann nicht und ändern nichts. Standardablauf in Abschnitt 9 ab „Stack stoppen“ ausführen. „die dieses Programm nicht kennt“ heißt umgekehrt: Die Datenbank ist neuer als das Image; Image auf den aktuellen Stand bauen |
| Worker „unhealthy“ | Das Lebenszeichen ist älter als 45 Minuten (E-33). `sudo docker inspect --format '{{json .State.Health}}' finanz-dashboard-worker-1`, dazu das Log |
| Keine neuen Werte | Wochenende oder US-Feiertag? Sonst Log: Zeilen mit „Nichts gespeichert“ oder „verworfen“ nennen Reihe und Grund |
| Einzelne Quelle veraltet | ab M6 Ansicht „Datenstand“: letzter Erfolg, letzter Versuch, letzter Fehler je Quelle |
| Speicher | `zfs list -o name,used,avail Daten-Z1/apps/feewer/data` |
| Im Log steht `api_key=***` | Gewollt: Der FRED-Schlüssel wird in Logs und Fehlermeldungen nie ausgegeben |
| Log-Zeilen „Abruf fehlgeschlagen …, Versuch 1/3“ | Einzelne Aussetzer sind normal. Erst „nach 3 Versuchen“ ist ein echter Fehler; der Worker versucht es nach einer Stunde erneut |
| Werte fälschlich „veraltet“ | Uhrzeit: Schritt 2.2 |
| Dashboard nicht erreichbar | `sudo docker ps` zeigt `finanz-dashboard-web-1`? Sonst fehlt der Dienst in der Compose-Kopie von Dockge (Schritt 8). Dann `curl -s http://127.0.0.1:8003/health` und `sudo docker logs finanz-dashboard-web-1` |
| Rotes Banner „Worker ohne Lebenszeichen“ | Der Worker schreibt seit über 45 Minuten keinen Heartbeat: Worker-Log und Healthcheck prüfen |
| Rotes Banner „Keine Verbindung zum Server“ | Der Browser erreicht den Dienst `web` nicht mehr; die angezeigten Werte stammen von der genannten Uhrzeit |
| `$RUN …` meldet `ImportError` mit Pfad `/usr/lib/python3/dist-packages` | Die Variable `RUN` ist in dieser Shell leer (etwa nach neuem Anmelden); der Befehl lief ohne Container mit dem Python von TrueNAS und brach beim Import ab, ohne etwas zu ändern. `RUN` neu setzen (Schritt 6), mit `echo "$RUN"` prüfen, Befehl wiederholen |
| Datenstand oder Worker-Log: „FEVER_SEC_CONTACT kommt nicht im Container an …“ | Die `compose.yaml` in Dockge ist älter als `compose.dockge.yaml`: beim Worker fehlt die Zeile `FEVER_SEC_CONTACT: ${FEVER_SEC_CONTACT:-}`. `compose.yaml` ersetzen (Schritt 7.2), „Deploy“, Prüfbefehl unten |
| „FEVER_SEC_CONTACT ist im Container leer …“ | Der Wert fehlt in der `.env` des Dockge-Stacks (die `.env` im Projektordner liest der Stack nicht), oder der Stack wurde danach nur neu gestartet: eintragen, „Deploy“ |
| „FEVER_SEC_CONTACT enthält keine E-Mail-Adresse …“ | Schreibweise `FEVER_SEC_CONTACT=Vorname Nachname name@beispiel.de` |
| Log-Zeile „Scoring fehlgeschlagen“ | Die Abrufe laufen weiter; der Fehler steht unter `scoring` im Datenstand. Mit `sudo docker exec finanz-dashboard-worker-1 python -m fever.score` wiederholen und die Ausgabe melden |
| Log-Zeile „Validierung fehlgeschlagen“ | Abrufe und Scores laufen weiter; der Fehler steht unter „Validierung (Berechnung im Worker)“ im Datenstand. Mit `sudo docker exec finanz-dashboard-worker-1 python -m fever.validate` wiederholen und die Ausgabe melden |
| `sqlite3.OperationalError: database is locked` im Log eines Einmal-Befehls oder des Workers | Zwei Schreiber zugleich, einer länger als die Wartezeit. Seit dem Update vom 30.09.2026 wartet jeder Schreiber bis zu 2 Minuten; tritt es danach noch auf, die Log-Zeilen melden. Werte, deren Zeile „… neue Zeilen“ im Log steht, sind gespeichert |
| Datenstand bei den Quellen: „Alerts aus: FEVER_NTFY_TOPIC ist nicht gesetzt“ | Das Thema fehlt in der `.env` des Dockge-Stacks oder `compose.yaml` ist älter als `compose.dockge.yaml`: Schritt 8.1, Punkt 4 |
| Testbefehl meldet „Testnachricht nicht gesendet: … HTTP 429“ | ntfy.sh drosselt (zu viele Anfragen); in einigen Minuten wiederholen. Andere HTTP-Fehler oder „ConnectionError“: Netzwerk von TrueNAS prüfen, Ausgabe melden |
| Testbefehl meldet „gesendet“, aber nichts kommt an | In der App dasselbe Thema abonniert (Tippfehler?), Server `ntfy.sh`? Auf Android die Akku-Optimierung für ntfy ausschalten |
| Datenstand bei den Quellen: „Alerts“ mit Fehler | Ein Versand scheiterte; der Worker versucht es im nächsten Takt erneut. Hält der Fehler an, Log-Zeilen „Alert nicht gesendet“ melden |
| Ansicht „Validierung“: „Keine auswertbaren Tage“ | Es fehlen Schlusskurse des S&P 500 (Reihe `spx`, Cboe) oder des VIX: Datenstand prüfen, Sofort-Abruf (Schritt 7), danach `python -m fever.validate` wie oben |

SEC-Kontakt prüfen, ohne den Wert anzuzeigen (✅ Entwicklungsumgebung 28.09.2026 im gebauten Image: fehlend, leer und gesetzt; ⏳ TrueNAS):

```bash
sudo docker exec finanz-dashboard-worker-1 python -c "import os; from fever.sources.sec import contact_problem; print(contact_problem(os.environ.get('FEVER_SEC_CONTACT')) or 'SEC-Kontakt in Ordnung')"
#   erwartet: SEC-Kontakt in Ordnung
```

Danach die Reihe sofort holen: Sofort-Abruf (Schritt 7). Der nächste planmäßige SEC-Abruf ist sonst erst am nächsten New-Yorker Werktag ab 18:00 New York.

Logs werden in der Größe begrenzt (je Container 3 Dateien à 10 MB).

## 12. Befehlsübersicht

`$RUN` wie in Schritt 6; Containername bei Stack-Name `finanz-dashboard`.

| Zweck | Befehl | Status |
|---|---|---|
| Image bauen | `cd /mnt/Daten-Z1/apps/feewer && sudo docker compose build` | ✅ TrueNAS 26.09.2026 |
| Datenbank anlegen / migrieren | `$RUN alembic upgrade head` | ✅ Entwicklungsumgebung 26.09.2026 (UID 568) |
| Stand der Datenbank | `$RUN alembic current` | ✅ Entwicklungsumgebung 25.09.2026 |
| Start, Stopp | Dockge, Stack `finanz-dashboard` | ✅ TrueNAS 26.09.2026 (Start) |
| Worker-Log | `sudo docker logs -f finanz-dashboard-worker-1` | ⏳ |
| Healthcheck von Hand | `sudo docker exec finanz-dashboard-worker-1 python -c "import sys; from fever.worker import healthcheck; sys.exit(healthcheck())"` | ✅ TrueNAS 26.09.2026 |
| Sofort-Abruf aller Reihen | `sudo docker exec finanz-dashboard-worker-1 python -m fever.sources.update` | ✅ TrueNAS und Entwicklungsumgebung 26.09.2026 |
| Mountpunkt und Benutzer prüfen | `sudo docker inspect finanz-dashboard-worker-1 --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{end}} user={{.Config.User}}'` (erwartet: `/mnt/Daten-Z1/apps/feewer/data -> /data user=568:568`) | ✅ TrueNAS 26.09.2026 |
| Sofort-Backup | `sudo docker exec finanz-dashboard-worker-1 python -m fever.backup` (Stack gestoppt: `$RUN python -m fever.backup`) | ✅ Entwicklungsumgebung 25.09.2026 |
| Migration (Ablauf) | Probe an einer Backup-Kopie (Schritt 9) → Stack stoppen → `$RUN python -m fever.backup` → `$RUN alembic upgrade head` → Stack starten | ✅ TrueNAS 26.09.2026 (0001 → 0002; Scoring danach erfolgreich), bis 0004 am 29.09.2026 (Nutzer), und Entwicklungsumgebung (mit Probe, 0003 → 0004 am 29.09.2026 mit dem gebauten Image; 0004 → 0005 am 30.09.2026 im Test-Image an einer Kopie der Entwicklungsdatenbank) |
| Dashboard-Log | `sudo docker logs -f finanz-dashboard-web-1` | ✅ Entwicklungsumgebung 26.09.2026, ⏳ TrueNAS |
| Dashboard-Health | `curl -s http://127.0.0.1:8003/health` (erwartet `{"status":"ok"}`) | ✅ Entwicklungsumgebung 26.09.2026, ⏳ TrueNAS |
| Scores sofort neu berechnen | `sudo docker exec finanz-dashboard-worker-1 python -m fever.score` | ✅ TrueNAS und Entwicklungsumgebung 26.09.2026 |
| Validierung sofort neu berechnen | `sudo docker exec finanz-dashboard-worker-1 python -m fever.validate` (Stack gestoppt: `$RUN python -m fever.validate`) | ✅ Entwicklungsumgebung 29.09.2026 (gebautes Image als 568:568), ⏳ TrueNAS |
| SEC-Kontakt prüfen | Befehl in Abschnitt 11 (erwartet `SEC-Kontakt in Ordnung`) | ✅ Entwicklungsumgebung 28.09.2026, ⏳ TrueNAS |
| Testnachricht der Alerts | `sudo docker exec finanz-dashboard-worker-1 python -m fever.alerts --test` (Schritt 8.1) | ✅ Entwicklungsumgebung 30.09.2026 (Wegwerf-Thema auf ntfy.sh), ⏳ TrueNAS |
