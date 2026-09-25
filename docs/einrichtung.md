# Einrichtung und Betrieb auf dem Raspberry Pi

Stand: 25.09.2026 · Für: dich als Anwender · Status: **M0 erledigt.** Image, Compose und `.env`-Vorlage existieren. Die Schritte 1–6 kannst du schon ausführen; ab Schritt 7 wird es mit Meilenstein M3 lauffähig (siehe `docs/umsetzungsplan.md`).

Markierungen:
- ✅ geprüft: ausgeführt, mit Datum und Ort
- ⏳ geplant oder ungeprüft: Der Befehl steht fest, wurde aber noch nicht gegen den fertigen Code bzw. auf deinem Pi ausgeführt

Beispielwerte, die du anpasst:
- Datenordner `/srv/fever/data`
- Web-Port `8050`
- Projektordner `~/Finanz-Dashboard`

Befehle stehen in grauen Kästen. Was nach `#` folgt, ist ein Kommentar und wird nicht mit eingegeben.

---

## 0. Überblick

Das Dashboard läuft als zwei Docker-Container auf dem Pi:
- `worker` holt alle 15 Minuten Marktdaten, speichert sie und rechnet die Scores.
- `web` zeigt die Oberfläche im Browser.

Die Daten liegen in einer SQLite-Datei in deinem Datenordner. Zugang: nur aus dem Heimnetz, ohne Passwort (Entscheidung O-3 vom 25.09.2026).

## 1. Was du brauchst

- Raspberry Pi mit **64-Bit**-Raspberry-Pi-OS (Modell und RAM sind noch offen: O-2)
- SSD statt SD-Karte für den Datenordner (empfohlen; eine SD-Karte verschleißt durch dauernde Schreibzugriffe)
- einen kostenlosen FRED-API-Schlüssel (Schritt 4)
- Zugang zum Pi per Terminal (direkt oder per `ssh`)

## 2. Pi vorbereiten ⏳

### 2.1 64-Bit prüfen

```bash
uname -m                     # erwartet: aarch64
dpkg --print-architecture    # erwartet: arm64
```

Entscheidend ist die zweite Zeile. Zeigt sie `armhf`, läuft ein 32-Bit-System (auch wenn `uname -m` `aarch64` meldet). Dann den Pi mit dem Raspberry Pi Imager neu mit „Raspberry Pi OS (64-bit)“ aufsetzen. Docker Engine 28 ist laut Docker-Doku die letzte Hauptversion mit Paketen für 32-Bit-Raspberry-Pi-OS.

### 2.2 System aktualisieren

```bash
sudo apt update && sudo apt full-upgrade -y
```

### 2.3 Uhrzeit prüfen

Das Dashboard entscheidet anhand der Uhrzeit, ob ein Wert veraltet ist. Die Uhr muss synchronisiert sein.

```bash
timedatectl    # erwartet: "System clock synchronized: yes"
```

Steht dort `no`:

```bash
sudo timedatectl set-ntp true
```

### 2.4 Datenordner anlegen

Der Datenordner muss auf einem **lokalen** Dateisystem liegen (z. B. ext4 auf der SSD), nicht auf einer Netzwerkfreigabe (NFS/SMB), weil die Datenbank dort nicht zuverlässig funktioniert.

```bash
sudo mkdir -p /srv/fever/data
sudo chown "$(id -u):$(id -g)" /srv/fever/data
df -T /srv/fever/data        # Spalte "Type": ext4 o. Ä., NICHT nfs oder cifs
id -u; id -g                 # deine Benutzer- und Gruppen-ID, meist 1000 und 1000; für Schritt 6 notieren
```

Ist die SSD z. B. unter `/mnt/ssd` eingehängt, nimm stattdessen `/mnt/ssd/fever/data`.

Der Ordner muss **vor** dem ersten Start existieren. Compose legt ihn bewusst nicht an, damit bei einem Tippfehler im Pfad keine Daten in einem falschen, neu angelegten Ordner landen.

### 2.5 IP-Adresse des Pi

```bash
hostname -I    # die erste Adresse, z. B. 192.168.178.23
```

Empfehlung: Im Router eine feste IP-Adresse (DHCP-Reservierung) für den Pi einrichten, damit das Lesezeichen im Browser gültig bleibt. Wie das geht, hängt vom Router ab.

## 3. Docker installieren ⏳

Quelle: offizielle Docker-Anleitung für Debian, die für 64-Bit-Raspberry-Pi-OS gilt (`github.com/docker/docs`, Datei `content/manuals/engine/install/debian.md`, abgerufen 25.09.2026).

```bash
# Docker-Paketquelle einrichten
sudo apt update
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/debian
Suites: $(. /etc/os-release && echo "$VERSION_CODENAME")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update

# Docker installieren
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Test
sudo docker run hello-world    # erwartet u. a.: "Hello from Docker!"
```

Docker ohne `sudo` nutzen:

```bash
sudo usermod -aG docker $USER
```

Danach ab- und wieder anmelden (bzw. die SSH-Verbindung neu aufbauen), dann prüfen:

```bash
docker run --rm hello-world
docker compose version
```

Hinweis aus der Docker-Doku: Die Gruppe `docker` gewährt Rechte auf Root-Niveau. Nimm nur deinen eigenen Benutzer auf.

## 4. FRED-API-Schlüssel beantragen

FRED (Federal Reserve Bank of St. Louis) liefert einen Großteil der Daten. Der Schlüssel ist kostenlos.

1. Unter https://fredaccount.stlouisfed.org/ ein Konto anlegen und die E-Mail-Adresse bestätigen.
2. Unter https://fredaccount.stlouisfed.org/apikeys auf „Request API Key“ klicken, den Zweck kurz beschreiben (z. B. „private dashboard, personal use“) und den Nutzungsbedingungen zustimmen.
3. Den Schlüssel sicher notieren. Er kommt in Schritt 6 in die Datei `.env` und nirgendwo sonst hin: nicht in Chats, nicht in Git.

Quelle der Schritte: FRED-Dokumentation zum API-Schlüssel, per Websuche am 25.09.2026 ermittelt. Die FRED-Seite selbst war aus der Entwicklungsumgebung nicht abrufbar. Weicht die Seite ab, gilt die Seite.

## 5. Projekt auf den Pi holen ⏳

```bash
cd ~
git clone https://github.com/grisu314-ui/Finanz-Dashboard.git
cd Finanz-Dashboard
```

Welcher Branch auf dem Pi läuft, wird bei M3 festgelegt; bis dahin gibt es nichts Lauffähiges.

**Falls das Repository privat ist:** GitHub akzeptiert beim Klonen über HTTPS kein Passwort. Einfachster Weg ist ein nur lesender Deploy-Key für genau dieses Repository:

```bash
ssh-keygen -t ed25519 -C "fever-pi" -f ~/.ssh/fever_deploy    # ohne Passphrase: zweimal Enter
cat ~/.ssh/fever_deploy.pub                                    # Ausgabe kopieren
```

Auf GitHub: Repository → Settings → Deploy keys → „Add deploy key“ → Ausgabe einfügen, „Allow write access“ **nicht** anhaken. Dann:

```bash
GIT_SSH_COMMAND="ssh -i ~/.ssh/fever_deploy" git clone git@github.com:grisu314-ui/Finanz-Dashboard.git
cd Finanz-Dashboard
git config core.sshCommand "ssh -i ~/.ssh/fever_deploy"    # damit spätere "git pull" den Schlüssel nutzen
```

## 6. Konfiguration `.env` anlegen ⏳ (Vorlage `.env.example` existiert seit M0)

```bash
cd ~/Finanz-Dashboard
cp .env.example .env
chmod 600 .env    # nur du darfst die Datei lesen
nano .env         # speichern: Strg+O, Enter; beenden: Strg+X
```

Inhalt (Beispiel; `<…>` durch deinen Wert ersetzen, keine Leerzeichen um `=`):

```ini
FRED_API_KEY=<dein Schlüssel aus Schritt 4>
FEVER_DATA_DIR=/srv/fever/data
FEVER_UID=1000
FEVER_GID=1000
FEVER_WEB_PORT=8050
```

| Variable | Bedeutung | Pflicht | leer bedeutet |
|---|---|---|---|
| `FRED_API_KEY` | FRED-API-Schlüssel (Schritt 4) | ja | Abbruch mit Fehlermeldung |
| `FEVER_DATA_DIR` | absoluter Pfad des Datenordners (Schritt 2.4) | ja | Abbruch mit Fehlermeldung |
| `FEVER_UID`, `FEVER_GID` | Ausgabe von `id -u` bzw. `id -g` (Schritt 2.4) | nein | 1000 |
| `FEVER_WEB_PORT` | Port des Dashboards im Heimnetz | nein | 8050 |

Prüfen, ohne dass der Schlüssel auf dem Bildschirm erscheint (`-q` gibt bei Erfolg nichts aus):

```bash
docker compose config -q && echo "Konfiguration ok"
```

Mögliche Fehlermeldungen (Verhalten ✅ geprüft am 25.09.2026 in der Entwicklungsumgebung, noch nicht auf dem Pi):
- `required variable FEVER_DATA_DIR is missing a value: FEVER_DATA_DIR fehlt in .env …` bzw. dasselbe für `FRED_API_KEY`: Wert in `.env` eintragen.
- Beim Start `bind source path does not exist: …`: Der Datenordner aus Schritt 2.4 fehlt oder der Pfad in `.env` ist falsch.

## 7. Ersteinrichtung und Start ⏳ (ab M3)

```bash
cd ~/Finanz-Dashboard
docker compose build                                   # dauert auf dem Pi einige Minuten
docker compose run --rm worker alembic upgrade head    # legt die Datenbank an
docker compose up -d
docker compose ps                                      # nach etwa 1–2 Minuten: beide Dienste "(healthy)"
```

Bei der Ersteinrichtung entfallen „stoppen“ und „Backup“ aus dem Migrationsablauf, weil es noch keine Datenbank gibt (Umsetzungsplan W-7).

Der Worker beginnt sofort mit dem Abruf. Die erste Rückfüllung der Historien kann dauern; den Fortschritt siehst du mit:

```bash
docker compose logs -f worker    # beenden mit Strg+C, der Worker läuft weiter
```

## 8. Dashboard aufrufen ⏳ (ab M6)

Im Browser eines Geräts im Heimnetz: `http://<IP-aus-Schritt-2.5>:8050`, z. B. `http://192.168.178.23:8050`.

Sicherheit (Entscheidungen E-3/E-4 vom 25.09.2026):
- Es gibt **kein Passwort**. Jedes Gerät in deinem Heimnetz (auch Gäste-Handys im selben WLAN) kann das Dashboard öffnen. Es zeigt nur öffentliche Marktdaten, keine Kontodaten.
- **Keine Portweiterleitung** im Router einrichten; sonst wäre das Dashboard aus dem Internet erreichbar.
- Docker-Portfreigaben umgehen die Regeln der Firewall `ufw` (Docker-Doku, Abschnitt „Firewall limitations“). Eine ufw-Regel schützt den Port also nicht.

## 9. Update auf eine neue Version ⏳

Standardablauf. Er schadet nie; gibt es keine neue Migration, ist `alembic upgrade head` wirkungslos.

```bash
cd ~/Finanz-Dashboard
git pull
docker compose build
docker compose stop
docker compose run --rm worker python -m fever.backup    # Sicherung vor der Migration
docker compose run --rm worker alembic upgrade head
docker compose up -d
docker compose ps
```

Kurzform, nur wenn sicher keine Migration dabei ist (steht dann im Umsetzungsplan bzw. in der Commit-Nachricht):

```bash
cd ~/Finanz-Dashboard && git pull && docker compose up -d --build
```

## 10. Backup, Kopie außerhalb des Pi, Wiederherstellung

### 10.1 Backup ⏳ (ab M1)

Der Worker sichert täglich automatisch nach `/srv/fever/data/backup/` und hält eine begrenzte Anzahl Sicherungen (Anzahl wird bei M1 entschieden). Sofortiges Backup:

```bash
cd ~/Finanz-Dashboard
docker compose run --rm worker python -m fever.backup
ls -lh /srv/fever/data/backup/
```

### 10.2 Kopie außerhalb des Pi ⏳

**Wichtig:** Die lokal archivierten ICE-BofA-Spreads (HY-OAS u. a.) lassen sich nicht wieder beschaffen; FRED liefert seit April 2026 nur noch drei Jahre. Stirbt die SSD, sind sie ohne externe Kopie verloren. Ein automatisches Ziel außerhalb des Pi ist noch nicht entschieden (O-4). Bis dahin von Zeit zu Zeit manuell kopieren, z. B. von deinem PC oder Mac aus:

```bash
scp <dein-benutzer>@<IP-des-Pi>:/srv/fever/data/backup/<backup-datei> .
```

Die Daten nur für dich selbst verwenden, nicht weitergeben (ICE-Lizenz).

### 10.3 Wiederherstellung ⏳ (exakte Dateinamen folgen in M1)

Nie eine laufende Datenbank überschreiben. Ablauf:

```bash
cd ~/Finanz-Dashboard
docker compose stop
ls /srv/fever/data/                   # Datenbankdatei und ggf. zugehörige -wal/-shm-Dateien ansehen
mkdir -p /srv/fever/data/alt-$(date +%F)
mv /srv/fever/data/<db-datei> /srv/fever/data/alt-$(date +%F)/
# vorhandene <db-datei>-wal und <db-datei>-shm ebenfalls dorthin verschieben; sie gehören zur alten Datei
cp /srv/fever/data/backup/<backup-datei> /srv/fever/data/<db-datei>
docker compose up -d
docker compose ps
```

Den Ordner `alt-…` erst löschen, wenn das Dashboard wieder korrekt läuft.

## 11. Fehlersuche ⏳

| Symptom | Prüfen |
|---|---|
| Seite lädt nicht | `docker compose ps` (läuft `web`?), `ping <IP-des-Pi>` von deinem Gerät, richtige Portnummer? |
| Banner „Keine Verbindung zum Pi“ | wie oben; die angezeigten Werte sind eingefroren |
| Banner „Worker ohne Lebenszeichen“ | `docker compose ps`, `docker compose logs --tail 100 worker` |
| Einzelne Quelle veraltet | Ansicht „Datenstand“ im Dashboard: letzter Erfolg, letzter Versuch, letzter Fehler je Quelle |
| Dienst „unhealthy“ | `docker compose ps` zeigt den Containernamen; dann `docker inspect --format '{{json .State.Health}}' <containername>` |
| Speicher voll | `df -h /srv/fever/data` |
| Werte fälschlich „veraltet“ | Uhrzeit: `timedatectl` (Schritt 2.3) |

Logs werden in der Größe begrenzt (Compose-Einstellung), damit sie die SSD nicht füllen.

## 12. Befehlsübersicht

| Zweck | Befehl | Status |
|---|---|---|
| Start / Update ohne Migration | `docker compose up -d --build` | ⏳ |
| Status | `docker compose ps` | ⏳ |
| Worker-Log live | `docker compose logs -f worker` | ⏳ |
| Sofort-Backup | `docker compose run --rm worker python -m fever.backup` | ⏳ |
| Migration | `docker compose stop` → Backup → `docker compose run --rm worker alembic upgrade head` → `docker compose up -d` | ⏳ |
| Stoppen | `docker compose stop` | ⏳ |
