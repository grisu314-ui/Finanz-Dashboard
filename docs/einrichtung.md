# Einrichtung und Betrieb auf TrueNAS mit Dockge

Stand: 26.09.2026 · Für: dich als Anwender · Status: **Worker läuft auf TrueNAS seit 26.09.2026 („healthy“).** Image, Compose-Dateien, Datenbank, Worker, Healthcheck, Backup und Wiederherstellung sind zusätzlich in der Entwicklungsumgebung geprüft (x86_64, Container als UID 568). Die Oberfläche folgt mit Meilenstein M6 (siehe `docs/umsetzungsplan.md`).

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
| Branch | `claude-testing` |
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

### 3.2 Projekt holen (Branch `claude-testing`, E-30)

Das Repository ist öffentlich; es braucht keine Zugangsdaten. `git clone` verlangt ein leeres Verzeichnis und scheitert, sobald das Dataset `data` existiert („destination path '.' already exists and is not an empty directory“). Deshalb holen diese Befehle das Projekt in das bestehende Verzeichnis. `data/` bleibt dabei unberührt, weil Git es ignoriert. Die Reihenfolge von 3.2 und 3.3 ist damit egal.

```bash
cd /mnt/Daten-Z1/apps/feewer
git init
git remote add origin https://github.com/grisu314-ui/Finanz-Dashboard.git
git fetch origin claude-testing
git checkout -b claude-testing origin/claude-testing
#   erwartet: Switched to a new branch 'claude-testing'
#             branch 'claude-testing' set up to track 'origin/claude-testing'.
git status    # erwartet: "On branch claude-testing", "Your branch is up to date …", "nothing to commit, working tree clean"
```

✅ 26.09.2026, Entwicklungsumgebung: in einem Verzeichnis mit vorhandenem `data/`; dessen Inhalt blieb unverändert. Meldet `git init` „Permission denied“, fehlt Schritt 3.1.

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
3. Im `.env`-Bereich des Stacks den Inhalt von `.env.example` einfügen und nur `FRED_API_KEY=` ergänzen (Schlüssel aus Schritt 4). Die übrigen Werte sind vorbelegt:
   ```bash
   cat /mnt/Daten-Z1/apps/feewer/.env.example
   ```
4. Speichern und „Deploy“ bzw. „Start“.

| Variable | Bedeutung | Fehlt sie … |
|---|---|---|
| `FRED_API_KEY` | FRED-Schlüssel (Schritt 4) | Start bricht mit „FRED_API_KEY fehlt in .env“ ab |
| `FEVER_DATA_DIR` | Datenordner `/mnt/Daten-Z1/apps/feewer/data` | Start bricht mit „FEVER_DATA_DIR fehlt in .env“ ab |
| `FEVER_UID`, `FEVER_GID` | Benutzer der Container, 568 (`apps`) | Start bricht mit „FEVER_UID fehlt in .env“ bzw. „FEVER_GID fehlt …“ ab |
| `FEVER_WEB_PORT` | Port des Dashboards (ab M6), 8003 | – |

Ein fehlender Datenordner ist ein Fehler und wird nicht stillschweigend angelegt.

Prüfen:

```bash
sudo docker logs --tail 20 finanz-dashboard-worker-1
#   erwartet u. a.: INFO __main__: Worker gestartet: 41 Reihen in 29 Abrufgruppen, Takt 15 Minuten
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
#   am Ende: INFO __main__: Sofort-Abruf beendet: 41 Reihen, 0 mit Problemen   (Exit-Code 0)
#   ein zweiter Lauf meldet je Reihe "0 neue Zeilen"
```

✅ 26.09.2026, Entwicklungsumgebung (41 Reihen, zweimal; Worker-Startzeile ebenfalls). Auf TrueNAS lief am 26.09.2026 die frühere Einzeiler-Fassung (23 Reihen, 101 363 Zeilen); das Kommando ist dort ⏳. Meldet es „mit Problemen“ (Exit-Code 1), nennen die `ERROR`-Zeilen darüber Reihe und Grund.

## 8. Dashboard aufrufen ⏳ (ab M6)

Im Browser eines Geräts im Heimnetz: `http://<IP-von-TrueNAS>:8003`.

- Es gibt **kein Passwort**. Jedes Gerät in deinem Heimnetz kann das Dashboard öffnen. Es zeigt nur öffentliche Marktdaten, keine Kontodaten.
- **Keine Portweiterleitung** im Router einrichten; sonst wäre das Dashboard aus dem Internet erreichbar.

## 9. Update auf eine neue Version ⏳

Standardablauf, alles in der SSH-Shell auf TrueNAS; nur Stopp und Start des Stacks in Dockge. Er schadet nie: Gibt es keine neue Migration, ändert `alembic upgrade head` nichts, und die Sicherung davor ist nur eine zusätzliche Kopie. Ob eine neue Migration dabei ist, zeigt die dritte Zeile.

```bash
cd /mnt/Daten-Z1/apps/feewer
git pull
git diff --stat HEAD@{1} -- compose.dockge.yaml .env.example    # Ausgabe? Dann Schritt 7.2/7.3 wiederholen
git diff --stat HEAD@{1} -- migrations/                          # Ausgabe = neue Migration
sudo docker compose build
# in Dockge: Stack "finanz-dashboard" stoppen
RUN='sudo docker run --rm --user 568:568 -e FEVER_DATA=/data -v /mnt/Daten-Z1/apps/feewer/data:/data fever:local'    # wie Schritt 6, gilt bis zum Abmelden
$RUN python -m fever.backup        # Sicherung vor der Migration
#   erwartet: INFO __main__: Backup erstellt und geprüft: /data/backup/fever-…-manual.sqlite3
$RUN alembic upgrade head
#   erwartet ohne neue Migration nur zwei Zeilen "INFO [alembic.runtime.migration] …", kein "Running upgrade"
$RUN alembic current
#   erwartet: die neueste Nummer mit "(head)", derzeit 0001 (head)
# in Dockge: Stack "finanz-dashboard" starten
sudo docker exec finanz-dashboard-worker-1 python -m fever.sources.update    # nur wenn neue Reihen dazukamen (Schritt 7)
```

Neue Reihen holt der Worker sonst selbst, am nächsten New-Yorker Werktag ab ihrer Veröffentlichungszeit.

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
| Worker startet immer wieder neu | `sudo docker logs --tail 50 finanz-dashboard-worker-1`. „Datenbank fehlt“: Schritt 6. „Datenordner fehlt“ oder „Permission denied“: Schritt 3.3 |
| Worker „unhealthy“ | Das Lebenszeichen ist älter als 45 Minuten (E-33). `sudo docker inspect --format '{{json .State.Health}}' finanz-dashboard-worker-1`, dazu das Log |
| Keine neuen Werte | Wochenende oder US-Feiertag? Sonst Log: Zeilen mit „Nichts gespeichert“ oder „verworfen“ nennen Reihe und Grund |
| Einzelne Quelle veraltet | ab M6 Ansicht „Datenstand“: letzter Erfolg, letzter Versuch, letzter Fehler je Quelle |
| Speicher | `zfs list -o name,used,avail Daten-Z1/apps/feewer/data` |
| Im Log steht `api_key=***` | Gewollt: Der FRED-Schlüssel wird in Logs und Fehlermeldungen nie ausgegeben |
| Log-Zeilen „Abruf fehlgeschlagen …, Versuch 1/3“ | Einzelne Aussetzer sind normal. Erst „nach 3 Versuchen“ ist ein echter Fehler; der Worker versucht es nach einer Stunde erneut |
| Werte fälschlich „veraltet“ | Uhrzeit: Schritt 2.2 |

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
| Sofort-Abruf aller Reihen | `sudo docker exec finanz-dashboard-worker-1 python -m fever.sources.update` | ✅ Entwicklungsumgebung 26.09.2026, ⏳ TrueNAS |
| Mountpunkt und Benutzer prüfen | `sudo docker inspect finanz-dashboard-worker-1 --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{end}} user={{.Config.User}}'` (erwartet: `/mnt/Daten-Z1/apps/feewer/data -> /data user=568:568`) | ✅ TrueNAS 26.09.2026 |
| Sofort-Backup | `sudo docker exec finanz-dashboard-worker-1 python -m fever.backup` (Stack gestoppt: `$RUN python -m fever.backup`) | ✅ Entwicklungsumgebung 25.09.2026 |
| Migration (Ablauf) | Stack stoppen → `$RUN python -m fever.backup` → `$RUN alembic upgrade head` → Stack starten | ⏳ |
