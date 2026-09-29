# Umsetzungsplan Phase 1 – Fieberthermometer

Stand: 29.09.2026 · Status: **M0 bis M8 erledigt; dazu Block Breite und Top-10-Konzentration (O-1, E-68, E-71 bis E-74); Seiten beschleunigt (E-77, E-78); Entscheidungsrunde 29.09.2026 umgesetzt (E-80 bis E-92); M10 Validierung in der Entwicklungsumgebung umgesetzt (E-93)** · Nächster Schritt: Update auf TrueNAS mit Migration 0004 (Abschnitt 9), danach M9 (Abnahme)

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
| M1 | Speicher, Migrationen, Backup | ☑ 25.09.2026 | M0, Schema-Freigabe, W-5 | erteilt 25.09.2026 |
| M2 | HTTP-Client, Serienkatalog (Rohreihen), Quellen Cboe und FRED | ☑ 26.09.2026 | M1, L-5, Netzfreigabe (Abschn. 9) | Teil A erteilt 25.09.2026; Teil B erteilt 26.09.2026 |
| M3 | Worker und erste Inbetriebnahme auf TrueNAS mit Dockge (ICE-Archiv startet) | ☑ 28.09.2026: erster Werktag mit planmäßigen Abrufen ohne Fehler (Nutzer, Abruf 15:07); Schritt 9 läuft als Nachprüfung weiter (Abschnitt 9) | M2, Angaben zu TrueNAS | erteilt 26.09.2026 |
| M4 | Weitere Quellen: CFTC, EZB (CISS, USD/JPY-Kreuzkurs), OFR, EBP, Shiller-CAPE, Margin Debt (Z.1, E-42), VX-Futures | ☑ 26.09.2026 (M4a bis M4d, E-37) | M3 | M4a bis M4d erteilt 26.09.2026 |
| M5 | Indikatoren (`[indicator.*]`), Scoring Schritte 1–6, Aggregation Stufe 1 | ☑ 26.09.2026 (auf TrueNAS seit 26.09.2026) | M4, L-1 bis L-12 | erteilt 26.09.2026 |
| M6 | Web-Grundgerüst, Gestaltung, Aktualität, Datenstand | ☑ 26.09.2026 (auf TrueNAS seit 26.09.2026; Nachtrag Rezessionsbalken E-56 dort ⏳) | M1 (Lesen), M3 (Heartbeat) | erteilt 26.09.2026 |
| M7 | Ansichten 1–7 | ☑ 27.09.2026: Übersicht (vormals Übersicht B) und Ansichten 2–6 (E-62, E-65, E-67), Perzentilbänder (E-64, Migration 0003) und Ansicht 7 (E-63, E-66); die Variante M7a ist wieder entfernt (E-67); auf TrueNAS ⏳; Ansicht Breite und Top-10-Konzentration mit Daten seit 28.09.2026 (E-68, E-71 bis E-74) | M5, M6, L-13 | M7a erteilt 26.09.2026, M7 erteilt 27.09.2026 |
| M8 | Erklärtexte je Kennzahl | ☑ 28.09.2026: alle Texte und die Krisendaten in `config/episodes.toml` vom Nutzer freigegeben | parallel zu M6/M7 | erteilt 28.09.2026 |
| R-29.09 | Entscheidungsrunde 29.09.2026: Sahm-Regel mit Trendbedingung und SOS-Regel, Rollen-Marken, Mindesthistorie 3 Jahre, Cboe-SPX, Re-Steepening-Hinweis, Kreditspread-Enge und Aktienquote in der Fallhöhe, Geldmarktfonds, y-Achse, HY-OAS-Niveau (E-80 bis E-92) | ☑ 29.09.2026 in der Entwicklungsumgebung (Abschnitt 4, „Entscheidungsrunde 29.09.2026“); auf TrueNAS ⏳ | M8 | erteilt 29.09.2026 |
| M10 | Validierung (Bericht 4.3, Schritt 7): Walk-forward, Treffer und Fehlalarme je Ampelstufe, Vorlauf, Vergleich mit reinem VIX-Filter; vorgezogen aus Phase 2 (E-89) | ☑ 29.09.2026 in der Entwicklungsumgebung (Abschnitt 4, M10, „Ergebnisse“); auf TrueNAS ⏳ (Migration 0004) | R-29.09 | erteilt 29.09.2026 (Plan ohne Rückfrage) |
| M9 | Abnahme Phase 1 | ☐ | M0–M8, M10 | – |

**Warum diese Reihenfolge:** FRED liefert die ICE-BofA-Spreads seit April 2026 nur noch für drei Jahre (Bericht, TL;DR). Jeder Tag ohne laufenden Worker verschiebt den Anfang des lokalen Archivs um einen Tag nach hinten. Deshalb geht ein minimaler Worker mit FRED und Cboe (M0–M3) in Betrieb, bevor Scoring und Oberfläche entstehen.

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
| 26.09.2026 | E-10 | L-5: ab wann ist ein Wert veraltet? | Kalendertage nach erwarteter Veröffentlichung (Beobachtungsdatum + Verzug): täglich > 4, wöchentlich > 10, monatlich > 41. Das ist Frequenz plus Toleranz 3 / 3 / 10 | Kein Börsenkalender nötig; lange Feiertagswochenenden lösen keinen Fehlalarm aus. Die Toleranz steht je Reihe in `series.toml` (so sieht es `CLAUDE.md` vor); Abweichungen vom Standard nur mit Begründung im Eintrag, ein Test prüft das |
| 26.09.2026 | E-11 | Datenordner auf dem Pi (O-2, Teilentscheidung) | `/home/dirk/volumes/fever`, direkt als Datenordner (darin `fever.sqlite3`, `raw/`, `backup/`) | Anlegen ohne `sudo` als Benutzer `dirk`. `FEVER_UID`/`FEVER_GID` müssen die IDs von `dirk` sein. Liegt `/home` auf der SD-Karte, verschleißt sie; Speichermedium bleibt offen (O-2). Pfad kommt weiterhin nur aus `.env`, nicht aus Code oder Compose |
| 26.09.2026 | E-12 | `.env.example` vorbelegen? | Ja: Secrets leer, nicht geheime Werte vorbelegt (Datenordner) | `cp .env.example .env` liefert den richtigen Pfad. `CLAUDE.md`-Regel entsprechend präzisiert |
| 26.09.2026 | E-13 | M2 Teil B: Indikatoren (L-10) schon jetzt? | Nein. Teil B legt nur Rohreihen an; `[indicator.*]` und L-10 folgen in M5 | Keine Parameter ohne Verwendung; L-10 wird im Zusammenhang mit dem Scoring entschieden. Rohreihen für die denkbaren L-10-Varianten (SP500, DGS10, ICSA, IC4WSA) werden trotzdem ab Teil B archiviert |
| 26.09.2026 | E-14 | Veröffentlichungszeit (Vintage) neuer Beobachtungen | Erstabruf einer Reihe: Beobachtungsdatum + Verzug in Kalendertagen; fällt das auf Samstag oder Sonntag, gilt der folgende Montag; Uhrzeit aus `series.toml` in America/New_York; höchstens die Abrufzeit; markiert als geschätzt. Danach bekommen neue Beobachtungen und Revisionen die Abrufzeit, nicht geschätzt | Kein Look-ahead im laufenden Betrieb. US-Feiertage bleiben in der Schätzung unberücksichtigt. Nach Ausfällen des Workers erscheinen Werte in der Historie später als tatsächlich veröffentlicht (konservativ) |
| 26.09.2026 | E-15 | Verletzung der Plausibilitätsgrenzen | Nur der verletzende Wert wird verworfen; die übrigen Werte der Reihe werden gespeichert; Fehler in Log und `source_status` | Vorübergehende Lücke an dieser Stelle. Weil jeder Abruf die volle Historie holt, kommt der Wert nach Korrektur von Grenze oder Quelle nach |
| 26.09.2026 | E-16 | Serien-IDs | Kennung der Quelle in Kleinbuchstaben (`vix`, `bamlh0a0hym2`, `sahmrealtime`); lesbarer Name im Feld `name` | IDs sind dauerhaft, weil Trigger ein UPDATE verhindern; Umbenennen hieße neue Reihe |
| 26.09.2026 | E-17 | Quelle für USD/JPY (Ansicht 2, Ranking Nr. 10) | Nicht FRED DEXJPUS (H.10 erscheint montags 16:15 ET für die Vorwoche). In M4 prüfen: Kreuzkurs EUR/JPY ÷ EUR/USD aus den EZB-Referenzkursen | Bis M4 kein USD/JPY. Endpoint und Veröffentlichungszeit sind ungeprüft; der Kreuzkurs ist eine eigene Einschätzung |
| 26.09.2026 | E-18 | VX-Futures-Termstruktur (Ansicht 2) | In M4 | Eigener Parser je Kontrakt und Kontraktkalender; bis dahin Index-Termstruktur 9D/30D/3M/6M |
| 26.09.2026 | E-19 | Historische ALFRED-Vintages rückwirkend laden | Nicht in Phase 1 (gehört zur revisionsgenauen Rückrechnung, Phase 2) | Rückfüllung mit geschätzter Veröffentlichung (E-14); Revisionen werden ab Inbetriebnahme gespeichert |
| 26.09.2026 | E-20 | Umfang M2 Teil B | 23 Rohreihen (Liste unter M2, „Plan Teil B“). Nicht archiviert: NFCILEVERAGE, DFII10, THREEFYTP10, DTWEXBGS, VIXCLS | Die nicht archivierten Reihen sind in Phase 1 ungenutzt und bei FRED jederzeit vollständig abrufbar |
| 26.09.2026 | E-21 | Zielsystem (O-2). Angaben zum Pi: Compute Module 4 Rev 1.1, 1,8 GiB RAM, SD-Karte (Root 14 GB, davon 2,6 GB frei) | TrueNAS statt Pi. Das Image wird im Projektverzeichnis auf TrueNAS gebaut; der Betrieb läuft über eine eigene Compose-Datei ohne Build, die das Image aufruft, als Dockge-Stack; Datenordner über Volumes dieser Compose-Datei | Zielplattform x86_64 (linux/amd64) statt arm64; TrueNAS gibt es offiziell nur für x86_64. E-11 (Pfad auf dem Pi) ist überholt. In M3: Laufzeit-Compose, `.env.example` und `docs/einrichtung.md` neu. Der Datenordner liegt auf einem Dataset des TrueNAS-Hosts, nie per NFS/SMB |
| 26.09.2026 | E-22 | Backup-Ziel außerhalb (O-4) | Backups bleiben im Datenordner auf TrueNAS, kein weiteres Ziel. Aufwand für Backups gering halten („nur ein Dashboard“) | E-8 (bereits umgesetzt) bleibt unverändert; keine zusätzliche Kopie, keine weitere Mechanik |
| 26.09.2026 | E-23 | Parameter je Reihe (Verzug, Uhrzeit, Toleranz, Grenzen) | Wie vorgeschlagen (Tabelle unter M2, „Ergebnis Teil B“): Verzug = regulärer Höchstwert, Grenzen fangen nur Einheiten- und Formatfehler ab | Bei Shutdown-Verspätungen und US-Feiertagen liegt die geschätzte Veröffentlichung in der Rückfüllung 1–3 Tage zu früh (rund 5 % der DGS10- und SOFR-Werte) |
| 26.09.2026 | E-24 | VVIX-Werte vor dem 03.01.2007 | Nicht speichern (Feld `start`) | Die dünn besetzten, teils unplausiblen Werte von 2006 entfallen ohne Fehlermeldung. Beginn laut Sekundärquellen (arXiv 1506.07554, Macroption) |
| 26.09.2026 | E-25 | IORB-Werte mit Datum in der Zukunft | Bis 7 Tage voraus zulassen (Feld `lead_days`, Standard 0) | Der angekündigte Satz wird gespeichert, sobald FRED ihn listet. Bei allen anderen Reihen bleibt ein Zukunftsdatum ein Fehler |
| 26.09.2026 | E-26 | Cboe-CSV trotz unklarer Speicherklausel in den Nutzungsbedingungen | Weiter verwenden | Private, nicht kommerzielle Nutzung, ein Abruf je Datei und Tag, keine Weitergabe. Die Auslegungsfrage bleibt als Risiko (Abschnitt 8) |
| 26.09.2026 | E-27 | Echte ICE- und Cboe-Werte in Fixtures des öffentlichen Repos (W-9) | Fixtures lizenzierter Quellen mit Originalformat und synthetischen Werten; den betroffenen Commit ersetzen (Force-Push auf `claude-testing`) | Die Werte sind aus der Branch-Historie entfernt; GitHub hält den alten Commit über seine ID noch eine Weile abrufbar. Regel in `CLAUDE.md` (Neue Quelle) ergänzt |
| 26.09.2026 | E-28 | Datenordner auf TrueNAS | Kind-Dataset `data` im Projekt-Dataset: `/mnt/Daten-Z1/apps/feewer/data` (Dataset-Name `feewer` wie angelegt) | Von Git und Docker-Build über `data*/` ignoriert. Eigene Rechte und bei Bedarf eigene Snapshots. `git clean -fdx` im Projektverzeichnis würde Datenbank und Backups löschen; Warnung in Anleitung und `CLAUDE.md` |
| 26.09.2026 | E-29 | Benutzer der Container | TrueNAS `apps`, 568:568, über `user:` in der Laufzeit-Compose aus der `.env` | Kein Neubau des Images für eine andere UID nötig. Kopieren und Wiederherstellen per `sudo` bzw. Einmal-Container |
| 26.09.2026 | E-30 | Betriebs-Branch | `claude-testing` direkt (Empfehlung war `main` mit PR je Meilenstein) | Jeder Push ist beim nächsten `git pull` auf TrueNAS im Betrieb. Auf `claude-testing` nur geprüften Stand pushen (Tests, bei Compose/Dockerfile Build-Probe) |
| 26.09.2026 | E-31 | Abrufplan des Workers | Jede Reihe einmal pro New-Yorker Werktag ab `release_time`; nach einem Fehler stündlich erneut. Tägliche Reihen zusätzlich stündlich bis Tagesende New York, solange der bis jetzt erwartete Wert fehlt. Nach einem Neustart wird nachgeholt | Etwa 23 Vollabrufe pro Werktag plus Nachfassen an Feiertagen und bei Verspätung. An Wochenenden keine Abrufe. Das Nachfassen berechnet den erwarteten Wert mit `lag_days` (E-23) |
| 26.09.2026 | E-32 | Compose-Dateien | Zwei Dateien (Empfehlung war eine): `docker-compose.yml` nur zum Bauen im Projektverzeichnis, `compose.dockge.yaml` für den Betrieb in Dockge | Beide nutzen `fever:local`; ein Test prüft Image, Build-Freiheit der Laufzeit-Datei und die `.env`-Variablen. Die Kopie in Dockge muss nach Änderungen an `compose.dockge.yaml` von Hand nachgezogen werden |
| 26.09.2026 | E-33 | Healthcheck-Grenze des Workers | 45 Minuten Heartbeat-Alter (drei Takte) | Gilt ab M6 auch für den Hinweis „Worker ohne Lebenszeichen“ |
| 26.09.2026 | E-34 | Namen auf TrueNAS | Bleiben wie angelegt: Dataset `feewer`, Dockge-Stack `finanz-dashboard` (Container `finanz-dashboard-worker-1`) | Anleitung, `CLAUDE.md` und Befehle auf diese Namen umgestellt |
| 26.09.2026 | E-35 | Serien-IDs für Quellen ohne einfache Kennung (EZB-Schlüssel, Spaltennamen) | `<quelle>_<kurzname>`, z. B. `ecb_ciss`, `ofr_fsi_credit`, `fed_ebp`; die exakte Kennung steht in `source_id`. FRED und Cboe behalten E-16 | Der Katalog prüft das Präfix und dass keine Quellkennung doppelt vorkommt. Die Namen sind dauerhaft |
| 26.09.2026 | E-36 | Mehrere Reihen aus einer Datei | Gemeinsamer Abruf: Katalogfeld `group`; eine Datei wird je Takt einmal geladen und einmal im Rohdatenarchiv abgelegt (`raw/<quelle>/<gruppe>/`) | Mitglieder einer Gruppe müssen Quelle, Frequenz, `release_time` und `lag_days` teilen. Der Worker plant je Gruppe; das älteste Mitglied entscheidet über das Nachfassen |
| 26.09.2026 | E-37 | Zuschnitt von M4 | Vier Teile mit je eigener Freigabe: M4a EZB/OFR/EBP, M4b CFTC, M4c Shiller/FINRA, M4d VX-Futures | M4a enthält 14 Reihen; die Rezessionswahrscheinlichkeit `est_prob` der EBP-Datei wird nicht archiviert (ungenutzt) |
| 26.09.2026 | E-38 | Parameter der M4a-Reihen | Wie vorgeschlagen (Tabelle unter M4, „Ergebnis M4a“) | OFR: Verzug 4 Kalendertage wegen „two business days“ über das Wochenende. EBP erscheint sofort als veraltet, weil das September-Update der Fed fehlt |
| 26.09.2026 | E-39 | Zuschnitt von M4b | Nur VIX-Futures (`1170E1`) aus dem Legacy-Bericht „Futures Only“: Open Interest, Non-Commercials Long, Short und Spread. Keine E-mini-S&P-500-Positionen, kein TFF-Bericht | Genügt für das COT-Maß der Fallhöhe (L-10, L-11); weitere Märkte lassen sich später als eigene Gruppe ergänzen |
| 26.09.2026 | E-40 | Parameter der M4b-Reihen | Wie vorgeschlagen (Tabelle unter M4, „Ergebnis M4b“) | Geschätzter Stand der Rückfüllung in Feiertagswochen bis zu 3 Tage zu früh (E-14 ohne Feiertage). Ein verspäteter Freitagsbericht kommt erst am Montag an (E-31 fasst wöchentliche Reihen nicht nach) |
| 26.09.2026 | E-41 | Excel-Leser für M4c | `xlrd` wird aufgenommen, sobald M4c es braucht (Shiller `ie_data.xls`, Binärformat); geprüft 26.09.2026: 2.0.2, Wheel `py2.py3-none-any`, BSD | Für `.xlsx` (FINRA) ist keine Bibliothek nötig: Die Datei nutzt Inline-Strings, lesbar mit `zipfile` und `xml.etree` in unter 50 Zeilen |
| 26.09.2026 | E-42 | Quelle für Margin Debt | Fed-Statistik Z.1 über FRED: `BOGZ1FL663067003Q` (Receivables Due from Customers der Broker-Dealer), statt FINRA | FINRA-Bedingungen untersagen Speichern ohne schriftliche Zustimmung (Befunde unter M4). Folgen: quartalsweise statt monatlich, etwa 10 Wochen Verzug nach Quartalsende, anderes Niveau (Median 0,63 × FINRA); neue Frequenz „quartalsweise“ im Katalog, Toleranz im M4c-Plan. `CLAUDE.md` angepasst |
| 26.09.2026 | E-43 | Zuschnitt und Abruf von M4c | Shiller: nur CAPE und Excess CAPE Yield als Reihen (die ganze Datei liegt im Rohdatenarchiv); Link zur Datei aus der Download-Seite, weil der Pfad wechselnde Kennungen trägt; Fixture synthetisch. Margin Debt: eine Z.1-Reihe über FRED | Zwei Abrufe je Takt für Shiller (Seite rund 120 KB, Datei rund 1,7 MB); Rohdatenarchiv nur bei geändertem Inhalt |
| 26.09.2026 | E-44 | Parameter der M4c-Reihen, Toleranz quartalsweise | Wie vorgeschlagen (Tabelle unter M4, „Ergebnis M4c“): Shiller Verzug 45, Z.1 Verzug 175; neue Standardtoleranz quartalsweise 10 Tage (Ergänzung zu E-10) | Rückfüllung Z.1 im Shutdown-Fall Q3 2025 17 Tage zu früh. Shiller-Verzug beruht auf einer einzigen beobachteten Aktualisierung |
| 26.09.2026 | E-45 | Speichermodell der VX-Futures (M4d) | Rangreihen: Settlement und Kalendertage bis Verfall für die Ränge 1 bis 8 der Monatskontrakte als normale Reihen (16), eigene Quelle `cfe`; kein Schemawechsel. Umsetzung von E-18 | Kurve je Tag mit echter Laufzeitachse; VX1/VX2 später direkt nutzbar. Einzelkontrakte sind nur im Rohdatenarchiv; neu berechenbar, weil Cboe die Dateien weiter anbietet |
| 26.09.2026 | E-46 | Rangregel und Parameter der VX-Futures | Am Verfallstag zählt der verfallende Kontrakt nicht mehr; Parameter wie vorgeschlagen (täglich, Verzug 0, 22:00 ET, Toleranz 3, Grenzen 1–300 bzw. 1–400) | Der Schlussabrechnungswert (ein VIX-Wert) geht nicht als Futures-Preis in die Kurve; die Uhrzeit ist unbelegt |
| 26.09.2026 | E-47 | Methode des Scorings (L-1 bis L-4) | Perzentil = Mittelrang einschließlich xₜ; Fenster rollierend 10 Jahre über die eigenen Beobachtungen des Indikators, bei 5 bis 10 Jahren alle vorhandenen, unter 5 Jahren kein Score (Bericht 4.3); Ampelschwellen auf den Composite-Wert selbst; Composite = Mittel der vorhandenen Blöcke, mindestens 3 von 5 | In Phase 1 gibt es 3 Stressblöcke (Breite O-1 und Positionierung fehlen); fällt einer aus, fehlt der Composite sichtbar |
| 26.09.2026 | E-48 | Glättung, Hysterese, Konfidenz, Diffusion (L-6, L-7, L-8, L-12) | EWMA über Handelstage: Volatilitätsblock Halbwertszeit 3, Composite 10, Fallhöhe 20; die Ampel nutzt den geglätteten Composite, die Einzelregeln Rohwerte. Hysterese spiegelbildlich: VIX/VIX3M-Rot endet nach 3 Tagen in Folge < 1, Diffusions-Gelb 5 Prozentpunkte unter 40 %. Konfidenz = Summe der V-Scores (Bericht, Tabelle 2) aktueller gültiger Indikatoren / Summe aller scorerelevanten. Diffusionsindex nur über Stress-Indikatoren | Der Composite-Weg zu Rot wirkt nach 10 Handelstagen zur Hälfte |
| 26.09.2026 | E-49 | Kalender und Indikatoren (L-9 bis L-11) | Ein Score je Cboe-Handelstag (Tage mit VIX-Schluss); eine Beobachtung zählt an t, wenn Datum + Verzug zur `release_time` (Wochenende → Montag) spätestens am Ende des New-Yorker Tages t liegt. 16 Stress-Indikatoren in 3 Blöcken und 3 Fallhöhe-Komponenten (Tabelle unter M5; zunächst irrtümlich als 15 gezählt). VRP: niedrig = Stress; T10Y3M nur Anzeige; USD/JPY als 5-Tage-Veränderung und 21-Tage-Vola; Erstanträge ggü. 52-Wochen-Tief. Fallhöhe = Mittel von mindestens 2 Komponenten; VX-COT im Score mit dem 10-Jahres-Fenster, 3-Jahres-Perzentil zusätzlich gespeichert (Anzeige) | Nur Anzeige: HY-OAS und weitere ICE-Spreads (O-5), ANFCI, OFR gesamt und übrige Teilindizes, T10Y3M/T10Y2Y, SKEW, VIX9D, VIX6M, VX-Futures |
| 26.09.2026 | E-50 | Speicherung der Scores | Migration 0002 mit `indicator_score` und `composite_score`; jede Neuberechnung ersetzt beide Tabellen vollständig in einer Transaktion | Rohdaten (`observation`) bleiben unberührt; keine Historie früherer Rechenläufe |
| 26.09.2026 | E-51 | Randfälle des Scorings (Annahmen aus der Umsetzung von M5) | Bestätigt wie umgesetzt: EWMA beginnt nach einer Lücke neu; realisierte Vola ohne Mittelwertabzug; ein Tag ohne VIX/VIX3M-Wert unterbricht die Serien, beendet eine aktive Rot-Regel aber nicht; ohne Composite bestimmen die übrigen Regeln die Ampel, die Oberfläche zeigt „Composite fehlt“ | Die Kennzeichnung ohne Composite folgt in M6 |
| 26.09.2026 | E-52 | Umfang der Übersicht in M6 | Ampel, Stress, Fallhöhe und Konfidenz mit Aktualität und Verlauf; dafür schon jetzt die Texte dieser vier Kennzahlen und der Konzeptseiten Perzentil und Veraltung | Der Nutzer prüft diese Texte wie in M8; alle übrigen Kennzahlen erscheinen erst mit ihrem Text (M7/M8) |
| 26.09.2026 | E-53 | Umfang der Ansicht „Datenstand“ | Je Quelle (letzter Erfolg, Versuch, Fehler, dazu Worker und Scoring) und je Reihe (letzte Beobachtung, Abruf, Alter, „veraltet“ nach E-10) | Veraltete Reihen stehen oben |
| 26.09.2026 | E-54 | gunicorn-Prozesse | 1 Prozess | 4 Threads im Prozess, damit parallele Callbacks nicht warten; wenig Speicher |
| 26.09.2026 | E-55 | Farbsystem | Validierte Referenzpalette des Dataviz-Skills: Ampel in vier Statusfarben immer mit Text, Perzentile als blaue Einfarbskala (E-1), hell und dunkel je eigene Stufen | Linienfarben mit dem Validator geprüft; Systemschriften, keine Webfonts |
| 26.09.2026 | E-56 | Rezessionsbalken in den Charts (Nutzerwunsch) | FRED `USREC` (NBER-Datierung, Trough-Methode wie in den FRED-Grafiken) als graue Flächen hinter den Linien in allen Zeitreihen-Charts; Hinweis in der Datierung jedes Charts; Konzeptseite „Rezessionsbalken“ | Nur Anzeige, in keinem Indikator und keinem Score; eine laufende Rezession erscheint erst nach der NBER-Datierung, Monate später |
| 26.09.2026 | E-57 | Bereiche und Einzelreihen auf der Übersicht (Nutzerwunsch, M7a) | Unter allem Bisherigen vier Bereiche in fester Reihenfolge: Volatilität/Optionen, Kredit/Funding, Makro/Finanzierungsbedingungen, Fallhöhe; je Bereich nur die Indikatoren, die in den Score eingehen (19). Je Indikator ein erzeugter Abschnitt „So fließt der Wert in den Bereich ein“ aus `series.toml` und `scoring.toml` mit der heutigen Rolle aus den gespeicherten Scores | Reine Anzeige-Reihen (HY-OAS, SKEW, Zinskurve, CAPE, VX-Termstruktur) folgen in M7; M7a ersetzt die Themen-Ansichten 2 und 4–6 für die Score-Indikatoren |
| 26.09.2026 | E-58 | Texte für die neuen Kennzahlen | Alle 22 jetzt (19 Indikatoren, Blöcke Volatilität, Kredit, Makro); E-52 bleibt: keine Kennzahl ohne Text | Fakten aus Bericht Abschn. 1–3 und Primärquellen mit Abrufdatum; der Nutzer prüft die Texte |
| 26.09.2026 | E-59 | Charts je Indikator | Wert und Perzentil untereinander, beide mit Rezessionsflächen | Keine zweite y-Achse |
| 26.09.2026 | E-60 | Aufklappen | Zwei Ebenen: Bereich (Verlauf und Indikatorzeilen), darunter jeder Indikator einzeln; Charts entstehen nur für geöffnete Abschnitte | Gemessen: alle 19 Indikatoren auf einmal wären rund 9,4 MB Chart-Daten je Aufruf und Aktualisierung |
| 26.09.2026 | E-61 | Startzeitraum der Charts | Bereiche und Einzelreihen starten mit der ganzen Historie (alle Rezessionsflächen sichtbar); der Verlauf oben in der Übersicht und die Erklärseiten bleiben bei 5 Jahren | Die letzte US-Rezession endete im April 2020; im 5-Jahres-Startbild wäre keine Fläche zu sehen |
| 27.09.2026 | E-62 | M7 neben M7a (Nutzerwunsch: beide Versionen behalten, später entscheiden) | Die bisherige Übersicht mit den Bereichen bleibt Startseite (`/`); die Ansichten nach Bericht 6.3 kommen als eigene Seiten dazu: „Übersicht B“ (`/uebersicht-b`) und `/ansicht/<name>`, in einer zweiten Navigationszeile „Ansichten“ | Erklär- und Datenstand-Seiten bleiben unverändert; welche Version bleibt oder wie beide zusammengehen, entscheidet der Nutzer später |
| 27.09.2026 | E-63 | Krisenmarken (L-13) | Je Episode des Berichts Start und Ende als Schlusskurs-Hoch und -Tief des S&P 500, recherchiert mit Quelle, in `config/episodes.toml`; nur Anzeige | Unbelegtes wird markiert |
| 27.09.2026 | E-64 | Perzentilbänder 10/50/90 | Im Scoring berechnet und gespeichert (Migration 0003, drei Spalten in `indicator_score`), aus den eigenen Werten im selben Fenster wie das Perzentil, nur mit Daten bis t | Auf TrueNAS Migration mit Probe an einer Backup-Kopie; der Scoring-Lauf wird länger |
| 27.09.2026 | E-65 | Re-Steepening der Zinskurve (L-10) | Violette Fläche, solange 10J − 3M unter null liegt; das Ende einer Fläche ist das Re-Steepening | Keine neuen Parameter; kurze Unterschreitungen erscheinen als schmale Flächen |
| 27.09.2026 | E-66 | Raster der Heatmap | Schalter: Start wöchentlich über die ganze Historie (Perzentil vom letzten Handelstag der Woche), umschaltbar auf täglich für die letzten 2 Jahre | Geladen wird nur das gewählte Raster |
| 27.09.2026 | E-67 | Welche Übersicht bleibt (E-62) | Die Variante nach Bericht 6.3: Übersicht B wird Startseite `/` und bekommt Karten für Stress und Fallhöhe; die bisherige Übersicht mit den aufklappbaren Bereichen und Einzelreihen (M7a) entfällt ganz; Navigation in einer Zeile | Die Einzelreihen stehen in den Ansichten 2–6, „So fließt der Wert in den Bereich ein“ bleibt auf den Erklärseiten; `/uebersicht-b` leitet auf `/` um; in `CLAUDE.md` unter „NICHT gebaut“ eingetragen |
| 28.09.2026 | E-68 | Quelle für die Breite-Reihen (O-1, Befunde unter „O-1: Recherche“) | Nasdaq-Indizes über FRED, gleicher Client und Schlüssel: gleich- gegen kapitalgewichtet `NASDAQNQUS500LCE`/`NASDAQNQUS500LC`, Small/Large `NASDAQNQUSS`/`NASDAQNQUSL`, Halbleiter `NASDAQSOX`, Regionalbanken `NASDAQABAQ`, Zykliker/Defensive `NASDAQNQUSB40`/`NASDAQNQUSB45` (E-73), Gesamtmarkt `NASDAQNQUSB`. Verworfen: MSCI, FTSE Russell, Tiingo, ETF-Dateien von SSGA, IBKR | Umsetzung als eigener Schritt mit Plan und Freigabe; vorher per Auswahlfrage: Transformation, Toleranz, Block. Der Stress-Composite bekommt 4 statt 3 Blöcke, Stress und Ampel verschieben sich. Anteil über der 50/200-Tage-Linie: E-72; Top-10-Konzentration: E-71 |
| 28.09.2026 | E-69 | Speicherverbot in den FRED-Bedingungen (W-11) | Der Nutzer bittet die St. Louis Fed schriftlich um Zustimmung für ein privates, nicht kommerzielles lokales Archiv; der Betrieb läuft bis zur Antwort weiter | Offener Punkt O-7; bei Absage neue Entscheidung. Für Reihen von ICE, S&P und Nasdaq kann die Fed nach ihren eigenen Bedingungen keine Rechte einräumen |
| 28.09.2026 | E-70 | Prüfung der Migration beim Start | Worker, `fever.score` und `fever.sources.update` starten nicht, wenn die Datenbank nicht auf der neuesten Migration des Codes steht („Migration fehlt …“, Exit-Code 2); das Dashboard zeigt dazu ein rotes Banner, `/health` antwortet 503. `fever.backup` prüft nicht, weil die Sicherung vor einer Migration auf dem alten Stand laufen muss | Anlass: TrueNAS am 27.09.2026, Migration 0003 fehlte, Scoring scheiterte mit „no column named band_p10“. Umsetzung `fever/store/schema.py`, Tests `tests/test_schema.py` |
| 28.09.2026 | E-71 | Top-10-Konzentration (O-1) | Aus den öffentlichen N-PORT-Meldungen des SPDR S&P 500 ETF Trust (SEC EDGAR, CIK 884394) als Komponente der Fallhöhe; die SEC kommt als Quelle zu Phase 1 dazu | Quartalsweise, rund 60 Tage nach Quartalsende, ab Stichtag 30.09.2019. Veröffentlichung wie bei allen Reihen nach E-14: beim Erstabruf geschätzt (Stichtag + 62 Tage, nie früher als die tatsächliche Einreichung der 28 Meldungen), danach Abrufzeit; abweichend vom Plan nicht das Einreichungsdatum, weil der Abruf keine Veröffentlichungszeiten je Zeile kennt. Die Fallhöhe verschiebt sich. Details (Aktiengattungen, Vorlaufgewicht, Kontakt im User-Agent) im Plan |
| 28.09.2026 | E-72 | Anteil über der 50/200-Tage-Linie (O-1) | Weglassen; bleibt sichtbarer Platzhalter | Keine freie, speicherbare Quelle (Befunde unter „O-1: Recherche“); kein Branchen-Behelf |
| 28.09.2026 | E-73 | Zykliker/Defensive (E-68) | `NASDAQNQUSB40`/`NASDAQNQUSB45` (Nicht-Basiskonsum gegen Basiskonsum) wie XLY/XLP im Bericht | Historie ab 22.09.2020: Mindesthistorie erfüllt, Fenster anfangs rund 6 statt 10 Jahre |
| 28.09.2026 | E-74 | Festlegungen für Breite und Top-10 (E-68, E-71) | Relative Stärke = Log-Veränderung des Verhältnisses über 63 Handelstage (`scoring.toml`), Orientierung „niedrig = mehr Stress“ (Bericht 4.3); alle fünf Verhältnisse zählen im Block Breite, V = 3 für gleich- gegen kapitalgewichtet (Bericht, Tabelle 2), V = 2 für die übrigen vier; Top-10 je Emittent (Aktiengattungen mit demselben LEI zusammen), V = 1; Kontakt für den SEC-User-Agent als nicht geheime Variable in der `.env` des Stacks, ohne sie kein SEC-Abruf und eine Meldung im Datenstand | Umsetzung erst nach Freigabe des Plans |
| 28.09.2026 | E-75 | Kreditspread bis HY-OAS 5 Jahre Historie hat (O-5) | FRED `BAA10Y` (Moody's Baa minus 10J-Treasury, täglich ab 02.01.1986, FRED-Status „Copyrighted: Citation required“) als Ersatz im Kreditblock und für die Rot-Regel; HY-OAS bleibt Anzeige. Zwei Indikatoren: Niveau und Veränderung über 20 Handelstage (Bericht 4.3, Schritt 1); die Rot-Regel nutzt das Perzentil der Veränderung (Schwelle aus Bericht 4.3, Schritt 5). Lizenz: Moody's untersagt laut FRED-Hinweis Kopieren und Speichern ohne Zustimmung; der Nutzer lässt BAA10Y wie die ICE-Reihen nur privat nutzen | Umgesetzt 28.09.2026 (Ergebnis unter W-4). V = 3 für beide Indikatoren wie HY-OAS im Bericht (Tabelle 2) |
| 28.09.2026 | E-76 | Betriebs-Branch (Diese Sitzung arbeitet auf `claude-raramo`, TrueNAS holte von `claude-testing`) | `claude-raramo` direkt (Empfehlung war `main` per PR) | Ersetzt E-30. TrueNAS wechselt einmal den Branch (`docs/einrichtung.md`, Abschnitt 9); danach ist jeder Push auf `claude-raramo` beim nächsten `git pull` im Betrieb: nur geprüften Stand pushen |
| 28.09.2026 | E-77 | gunicorn-Threads (Nachtrag zu E-54, technisch nach Messung im Rahmen der Freigabe vom 28.09.2026) | 1 Prozess mit 1 Thread (`gthread`) statt 4 Threads | Parallele Callbacks bremsten sich über den GIL gegenseitig (sqlite3 gibt ihn je Zeile ab): Ansicht Visualisierung 5 Callbacks je 1,4–2,7 s parallel, zusammen 0,65 s nacheinander. Anfragen laufen jetzt nacheinander; eine langsame hält die übrigen höchstens rund 1 s auf |
| 28.09.2026 | E-78 | Server-Cache (CLAUDE.md verbot einen Caching-Layer) | Nutzer: ja, wenn er etwas nützt. Gemessen: erneute Aufrufe einer Ansicht ohne neue Daten auf dem Server 5- bis 10-mal schneller (Makro 1,05 → 0,21 s); umgesetzt als Lesepuffer im Web-Prozess | Gilt je Datenstand: größte rowid der nur anfügbaren Tabelle `observation` und `computed_at` des Scoring-Laufs; jede neue Beobachtung und jeder Scoring-Lauf verwirft den ganzen Puffer. Erster Aufruf nach neuen Daten und das Zeichnen im Browser werden dadurch nicht schneller. Rund 60 MB mehr Speicher. Ausnahme in `CLAUDE.md` eingetragen |
| 28.09.2026 | E-79 | O-7: Antwort der St. Louis Fed | Zustimmung erhalten (Nutzer) | O-7 und W-11 erledigt. Reihen Dritter über FRED (ICE, S&P, Nasdaq, Moody's) bleiben wie bisher private Nutzung ohne Weitergabe (E-69) |
| 29.09.2026 | E-80 | Sahm-Regel und Rezessions-Vorwarnung (Entscheidungsrunde F1, F2) | Sahm-Regel (SAHMREALTIME) ab 0,5 → mindestens Orange (am selben Tag durch E-91 ersetzt: Gelb, Orange nur im Abwärtstrend); SOS-Indikator der Richmond Fed (26-Wochen-Schnitt der versicherten Arbeitslosenquote FRED `IURSA` minus Minimum dieses Schnitts in den 52 Wochen davor) über 0,2 → mindestens Gelb. Beide Regeln lesen den Wert, gelten solange er die Schwelle erfüllt, ohne Hysterese; das Sahm-Perzentil bleibt im Makro-Block | Neue Reihe `iursa` (wöchentlich, Verzug 12 Tage), neuer Indikator `sos` mit Block `rule` (nur Ampelregel: in keinem Block, nicht in Konfidenz und Diffusion, kein `v_score`). Parameter `yellow_sos`, `sos_average_window`, `sos_low_window` in `scoring.toml` (für die Sahm-Regel seit E-91 `yellow_sahm`). SOS gerundet auf 10 Stellen, damit Rechenrauschen nie über die Schwelle entscheidet. Wirkung: Abschnitt 4, „Entscheidungsrunde 29.09.2026“ |
| 29.09.2026 | E-81 | Kennzeichnung der Rolle (F3) | Farbige Marke mit Text neben dem Namen: Blau „Stress · Bereich“, Violett „Fallhöhe“, Grau „nur Anzeige“, umrandet „Ampelregel“; ein Wert mit zwei Rollen trägt beide Marken; auch in Heatmap (farbige Quadrate, Rolle im Hover) und Sparklines | `texts.roles`, `components.role_marks`; Violett steht damit auch für die Fallhöhe (in Charts weiter für markierte Phasen) |
| 29.09.2026 | E-82 | Mindesthistorie (F4) | 3 Jahre statt 5 (Empfehlung war 5) | `min_history_years = 3`; Prüfung erlaubt jetzt `display_window_years <= min_history_years`. HY-OAS erreicht die drei Jahre ab 29.09.2026; Perzentile vieler Indikatoren beginnen zwei Jahre früher |
| 29.09.2026 | E-83 | Kursquelle für VRP und Aktien-Anleihen-Korrelation (F5) | Cboe-CSV des S&P 500 (`SPX`, ab 1975, Format wie VVIX) statt FRED `SP500` (zehn Jahre) | Neue Reihe `spx`; beide Indikatoren haben Historie ab 1990 und ändern sich rückwirkend. FRED `SP500` liest kein Indikator mehr (aus dem Katalog genommen, E-92) |
| 29.09.2026 | E-84 | Zinskurve 10J−3M (F6) | Bleibt Anzeige; Datum des letzten Re-Steepening als Hinweis in Ansicht Makro und auf der Erklärseite | `views.resteepening`: erster Wert ab null nach dem letzten Tag unter null; keine neuen Parameter, keine Wirkung auf die Ampel |
| 29.09.2026 | E-85 | Kreditspread-Niveau in der Fallhöhe (F7) | `BAA10Y`-Niveau umgedreht als Fallhöhe-Komponente (Bericht 4.3, Schritt 4), V = 3; später HY-OAS | Neuer Indikator `credit_spread_tight`; derselbe Wert zählt im Kreditblock als Stress (zwei Marken, E-81) |
| 29.09.2026 | E-86 | Investiertes und investierbares Geld (F8) | Aktienquote der Anleger (Livermore 2013, Fed Z.1) als Fallhöhe-Komponente, V = 1; dazu als Anzeige Geldmarktfonds in Prozent der Aktien | Acht neue Z.1-Reihen über FRED (Verzug wie Margin Debt, 175 Tage), Transformation `equity_share`, Indikator `equity_allocation`, Anzeige `money_market` |
| 29.09.2026 | E-87 | Aktien-Anleihen-Korrelation (F9) | Bleibt Stress im Makro-Block (wie Bericht) | Befund im Erklärtext: Seit 2022 fast durchgehend hoch, zeigt eher das Zinsregime; hebt Makro-Block und Diffusion |
| 29.09.2026 | E-88 | y-Achse beim Zoomen (F10) | Alle Zeitreihen passen die y-Achse an den sichtbaren Ausschnitt an (5 % Rand); feste Skalen (Perzentil, Stress, Fallhöhe, Ampelstufe) bleiben | Erste Ansicht auf dem Server (`figures.fitted_range`), danach `assets/autoscale.js` nach Zoom, Zeitraum-Knopf, Doppelklick und Aktualisierung; von Hand gezogene y-Bereiche bleiben bis zur nächsten x-Änderung |
| 29.09.2026 | E-89 | Validierung (F11) | Validierung nach Bericht 4.3, Schritt 7 (Walk-forward, Treffer und Fehlalarme je Stufe, Vergleich mit reinem VIX-Filter) als nächster Meilenstein M10, vorgezogen aus Phase 2; Aggregation Stufe 2 erst danach und nur, wenn sie dort besser abschneidet | `CLAUDE.md`, Phasen angepasst; Umfang von M10 vor Beginn planen und freigeben lassen |
| 29.09.2026 | E-91 | Sahm-Regel begrenzen (Vorher/Nachher: Orange bis weit in Erholungen, 2024 ohne Rezession) | Sahm-Regel ab 0,5 → mindestens Gelb; Orange nur, solange zugleich der S&P 500 (Cboe) unter seiner 200-Tage-Linie liegt (Growth-Trend-Regel nach Livermore 2016; Faber 2007). Ohne gültigen Trendwert bleibt es Gelb. Varianten zur Wahl: Orange 12 bzw. 6 Monate nach dem Auslösen, unverändert | Neuer Indikator `spx_trend` (Transformation `trend_gap`, Block `rule`), Parameter `trend_window = 200`, Regeln `orange_sahm_trend` und `yellow_sahm` (schließen sich aus). Tage, an denen allein die Sahm-Regel Orange auslöst: 1.216 → 262; Rundung auf 10 Stellen wie beim SOS-Indikator. Rund um die Linie wechselt Orange/Gelb öfter (Abschnitt 4) |
| 29.09.2026 | E-92 | FRED `SP500` ohne Verwendung seit E-83 | Aus dem Katalog genommen (Empfehlung) | Kein Abruf mehr; die gespeicherten Beobachtungen und Rohdateien bleiben, nichts wird gelöscht. 81 Reihen |
| 29.09.2026 | E-90 | HY-OAS nach E-82 (Nachfrage) | HY-OAS-Niveau zusätzlich im Kreditblock, V = 3; Anstieg über 20 Tage und Rot-Regel bleiben auf `BAA10Y`, CCC − BB bleibt Anzeige | Indikator `hy_oas` statt Anzeige; das Perzentil misst sich vorerst nur an den Jahren seit 2023 (sichtbarer Hinweis in der Übersicht) |
| 29.09.2026 | E-93 | Festlegungen der Validierung (M10), die der Bericht offenlässt | Eigene Festlegungen im freigegebenen Plan (Nutzer: „ohne Freigabeaufforderung sofort ausführen“), vom Nutzer nach Vorlage der Ergebnisse bestätigt (29.09.2026, Empfehlung): Bärenmarkt ab 20 % mit Horizont 63 Handelstage; Rückgänge nach Lunde/Timmermann (2004) mit gleicher Schwelle in beide Richtungen, Beginn am ersten Handelstag nach dem Hoch; VIX-Filter mit dem Alarmanteil der Ampelstufe in den Jahren davor (walk-forward ab 2000); Auswertung ab 2000 an Tagen mit bekanntem Ergebnis und allen Signalen; Alarmphasen mit Lücken bis 5 Handelstage zusammengefasst; Block-Bootstrap mit Blöcken von 126 Handelstagen, 1.000 Ziehungen, 90-%-Intervalle, fester Startwert; „besser/schlechter“ nur, wenn das ganze Intervall des Unterschieds auf einer Seite von null liegt; AUC je Zeitraum nur mit einem darin beginnenden Ereignis. Brier-Score und Test mit Put-Absicherung entfallen (Phase 3) | Parameter in `scoring.toml`, `[validation]`; Tabelle `validation_report` (Migration 0004); Ansicht 8 „Validierung“. Nur Auswertung: keine Rückwirkung auf Scores oder Ampel. Ergebnisse: Abschnitt 4, M10 |

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
5. Geplante `.env`-Variablen (Namen werden hier festgelegt; `.env.example` ursprünglich mit leeren Werten, seit E-12 nur Secrets leer): `FRED_API_KEY`, `FEVER_DATA_DIR`, `FEVER_UID`, `FEVER_GID`, `FEVER_WEB_PORT`.

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

**Ergebnis (25.09.2026, erledigt):**
- **Umgesetzt wie freigegeben:**
  - Tabellen `observation`, `source_status`, `heartbeat` (Migration `0001`)
  - Trigger gegen UPDATE und DELETE auf `observation`; Downgrade verweigert
  - UTC-Spaltentyp, der naive Zeiten ablehnt
  - Anfügen nur bei neuem oder geändertem Wert
  - Rohdatenarchiv nur bei geändertem Inhalt
  - Backup per `VACUUM INTO` mit `integrity_check`, Aufbewahrung 14 `daily` / 5 `manual` (E-8)
  - `source_status` nach E-9
- **Details, die im Plan offen waren:**
  - Datenordner über die Variable `FEVER_DATA` (Container `/data`, von Compose gesetzt), ohne Standardwert
  - Engines legen nie eine Datenbank an; das macht nur `alembic upgrade head`
  - `busy_timeout` 5000 ms
  - Fehlermeldungen in `source_status` werden auf 2000 Zeichen gekürzt
  - Logging über `fever/log.py`, nur stdout
- **Geprüfte Annahmen (SQLite 3.46.1 im Image):**
  - `VACUUM INTO` liefert auch bei offener Schreibtransaktion eine konsistente Kopie
  - auf einer `query_only`-Verbindung ist `VACUUM INTO` gesperrt, deshalb läuft das Backup über eine normale Verbindung im Autocommit
- **Befund im Selbst-Review, behoben:** Die SQLAlchemy-URL wurde als Text zusammengesetzt; ein `?` im Pfad des Datenordners schnitt ihn ab, und die Migration legte die Datenbank an einem anderen Ort an. Jetzt `URL.create(...)` mit Test (Pfad `daten #1?`).
- **Belege:**
  - `pytest -q`: 49 passed
  - Gegenprobe mit absichtlich eingebauten Fehlern in einer Kopie; jeder wurde von mindestens einem Test erkannt:
    - Trigger entfernt: 2 Tests rot
    - Schema weicht von der Migration ab: 1 rot
    - identische Werte werden erneut gespeichert: 2 rot
    - `query_only` fehlt: 1 rot
    - Aufbewahrung wirkungslos: 1 rot
  - arm64-Image über Compose:
    - `alembic upgrade head` legt die Datenbank an
    - `alembic current` zeigt `0001 (head)`
    - `python -m fever.backup` meldet „Backup erstellt und geprüft“
    - ohne Datenbank: Exit-Code 2, im leeren Datenordner wird nichts angelegt
    - Wert geschrieben, gesichert, in einen neuen Ordner zurückgespielt: Wert identisch
- **Nicht geprüft:** auf einem echten Pi; das tägliche Backup durch den Worker (M3).

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
3. `series.toml` je Reihe: Quelle, ID, Frequenz, Veröffentlichungszeit (America/New_York), Verzug, Toleranz (L-5), Plausibilitätsgrenzen. Indikatoren: Transformation (L-10), Orientierung, Block bzw. Fallhöhe; verschoben nach M5 (E-13).
4. Der FRED-API-Schlüssel steht als Query-Parameter in der URL. Der HTTP-Client maskiert ihn in jeder Log- und Fehlermeldung (Test).

**Entscheidung bei M2:** Phase 1 speichert den aktuellen Stand und fortlaufend beobachtete Revisionen. Historische ALFRED-Vintages rückwirkend zu laden gehört zur revisionsgenauen Rückrechnung in Phase 2. Entschieden (E-19): nicht in Phase 1.

**Tests:**
- Parser gegen Fixtures
- Plausibilitätsverletzung wird geloggt und nicht gespeichert
- Allowlist lehnt fremde Hosts ab
- API-Schlüssel erscheint nie im Log

**Ergebnis Teil A (26.09.2026, erledigt): zentraler HTTP-Client `fever/http.py`**
- **Umgesetzt wie freigegeben:**
  - Allowlist mit Mindestabstand je Host: `cdn.cboe.com` und `api.stlouisfed.org`, je 1 s
  - nur HTTPS auf Standardport, ohne Benutzerangabe in der URL
  - Weiterleitungen folgt der Client selbst, höchstens 3, jede Station wird gegen die Allowlist geprüft
  - Timeouts 10 s / 60 s
  - 3 Versuche bei Verbindungsfehler, Timeout, 429 und 5xx; Wartezeit 2 s, dann 4 s, `Retry-After` beachtet und auf 60 s gedeckelt
  - andere Statuscodes sofort als Fehler; nur HTTP 200 gilt als Erfolg
  - User-Agent `Fieberthermometer/0.1.0 (private, non-commercial)`
- **Schlüssel-Schutz:**
  - `fever/log.py` maskiert den Wert von `FRED_API_KEY` in jeder formatierten Logzeile, auch in Tracebacks und Meldungen fremder Bibliotheken.
  - `FetchError`-Texte sind maskiert. Ungültige URLs werden ohne Exception-Verkettung gemeldet.
  - Anlass (getestet): `requests` und urllib3 schreiben die URL samt `api_key` in Exception-Texte und Retry-Warnungen.
- **Belege:**
  - `pytest -q`: 70 passed (21 davon für den HTTP-Client)
  - Gegenprobe mit acht absichtlich eingebauten Fehlern, jeder erkannt: keine Maskierung im Client, Formatter ohne Maskierung, Allowlist aus, HTTP erlaubt, 404 wiederholt, kein Ratenlimit, `Retry-After` ignoriert, automatisches Folgen von Weiterleitungen
- **Nicht geprüft:** echte Abrufe; die folgen in Teil B, sobald die Hosts freigegeben sind. Dockerfile und Compose sind unverändert, daher keine neue arm64-Probe.

**Plan Teil B (freigegeben 26.09.2026):**
- **Umfang (E-13, E-20):** 23 Rohreihen, je Beobachtung ein Wert (bei Cboe der Schlusskurs); IDs nach E-16:
  - Cboe: `vix`, `vix9d`, `vix3m`, `vix6m`, `vvix`, `skew`
  - FRED, ICE (nur drei Jahre, unwiederbringlich): `bamlh0a0hym2`, `bamlh0a1hybb`, `bamlh0a3hyc`, `bamlc0a0cm`, `bamlc0a4cbbb`
  - FRED: `nfci`, `anfci`, `stlfsi4`, `t10y3m`, `t10y2y`, `sahmrealtime`, `icsa`, `ic4wsa`, `sofr`, `iorb`, `sp500` (nur 10 Jahre, S&P-Lizenz), `dgs10`
- **Abruf:** jedes Mal die volle Historie; der Speicher legt nur neue und geänderte Werte an. So kommen rückwirkende Neuschätzungen (NFCI, STLFSI4) ohne eigenes Revisionsfenster an. Vintage nach E-14, Plausibilität nach E-15.
- **Cboe:** Die Zeile des laufenden US-Handelstags wird vor der Veröffentlichungszeit verworfen, damit kein Zwischenstand dauerhaft als Schlusskurs gespeichert wird. Ob die CSV tagsüber eine solche Zeile enthält, ist ungeprüft.
- **Dateien:**
  - `config/series.toml`: je Reihe `source`, `source_id`, `name`, `unit`, `frequency`, `release_time`, `lag_days`, `tolerance_days` (bei Abweichung von E-10 zusätzlich `tolerance_reason`), `bounds`, `license`
  - Prüfung der Einträge in `fever/config.py`
  - `fever/sources/cboe.py`, `fever/sources/fred.py`: Abruf, Parser, Formatprüfung
  - `fever/sources/__init__.py`: eine Funktion je Reihe: Versuch → Abruf → `raw/` → Parser → Plausibilität → Vintage → Anfügen → `source_status`
  - Fixtures unter `tests/fixtures/`; Tests `test_sources_cboe.py`, `test_sources_fred.py`, `test_sources_update.py`, `test_series_catalog.py`
- **Schritte:**
  1. `fever/config.py` und `fever/http.py` lesen.
  2. Nutzungsbedingungen von Cboe (CSV-Download) und der FRED-API prüfen und hier festhalten.
  3. Echte Abrufe (Abschnitt 10.7): Antworten in Dateien, nur Anfang und Ende ansehen; FRED-Metadaten (Prüfung der (*)-IDs) und Veröffentlichungstermine (`fred/release/dates`).
  4. **Zwischenhalt:** Tabelle je Reihe mit Verzug, Veröffentlichungszeit (ET), Toleranz und Plausibilitätsgrenzen zur Freigabe. Verzug aus den tatsächlichen Terminen, Grenzen aus beobachtetem Minimum und Maximum mit großem Abstand.
  5. Fixtures, Parser, Tests, Katalog, Update-Funktion.
  6. Ende-zu-Ende gegen `data-dev/`: Erstabruf aller Reihen; zweiter Abruf ohne neue Zeilen und ohne neue Rohdatei; Größe von Datenbank und `raw/` messen (Einschätzung vorab: `raw/` grob 0,3–1 GB pro Jahr; gemessen: siehe Ergebnis).
  7. Gegenprobe mit absichtlich eingebauten Fehlern, `pytest -q`, Doku, Commit.
- **Tests:**
  - Parser; der FRED-Platzhalter „.“ für fehlende Werte wird übersprungen
  - Formatänderung und leere Antwort: sichtbarer Fehler, nichts gespeichert
  - Grenzverletzung und Datum in der Zukunft: Wert nicht gespeichert, Fehler in Log und `source_status`
  - Vintage: Wochenende, ET → UTC über die Sommerzeitwechsel, Begrenzung auf die Abrufzeit, Revisionen
  - Cboe-Tageszeile vor der Veröffentlichungszeit
  - Katalog: Toleranz nach E-10 oder begründet; `(source, source_id)` eindeutig
  - API-Schlüssel weder im Log noch in `source_status`, geprüft über den ganzen Ablauf
- **Recherchierte Veröffentlichungszeiten** (abgerufen 26.09.2026):
  - H.10 (DEXJPUS, DTWEXBGS): montags 16:15 ET für die Vorwoche (federalreserve.gov/releases/h10)
  - H.15 (DGS10): werktags 16:15 ET; der Wert vom 24.09. kam auf FRED am 25.09. um 15:16 CDT an
  - NFCI/ANFCI: mittwochs 8:30 ET, Daten bis zum Vorfreitag (chicagofed.org)
  - SOFR: werktags gegen 8:00 ET (newyorkfed.org)
  - HY-OAS: Wert vom 24.09. auf FRED am 25.09. um 9:04 CDT; STLFSI4: Wert vom Freitag, 18.09., auf FRED am Mittwoch, 23.09., um 12:07 CDT. Beides Einzelbeobachtungen, keine Regel
- **Freigabe:** erteilt am 26.09.2026, einschließlich Lesen der beiden Dateien und echter Abrufe.

**Ergebnis Teil B (26.09.2026, erledigt):**
- **Umgesetzt wie freigegeben:**
  - `config/series.toml` mit 23 Rohreihen, geprüft durch `series_catalog()` in `fever/config.py`
  - `fever/sources/cboe.py` und `fever/sources/fred.py`: Abruf, Parser, Formatprüfung
  - `fever/sources/update.py`: Plausibilität, Vintage, Anfügen, `source_status`
  - Fixtures aus gekürzten echten Antworten vom 26.09.2026 unter `tests/fixtures/`; bei ICE und Cboe mit synthetischen Werten (E-27)
- **Abweichungen vom Plan:**
  - Die Ablauf-Funktion liegt in `fever/sources/update.py` statt in `__init__.py`. So importieren die Quellmodule nur aus dem Paket, ohne Zirkelimport.
  - `cdn.cboe.com` leitet auf `cdn-api.cboe.com` weiter. Dieser Host steht jetzt in der Allowlist von `fever/http.py` und wird direkt abgerufen.
  - `(source, source_id)` braucht keine eigene Eindeutigkeitsprüfung: Die ID ist die Quellkennung in Kleinbuchstaben (E-16), ein Duplikat wäre ein doppelter TOML-Schlüssel.
  - Neue Katalogfelder `start` (E-24) und `lead_days` (E-25).
- **Geprüfte Kennungen:** Alle 23 existieren. Die mit (*) markierten (ANFCI, T10Y2Y, ICSA, IC4WSA, SOFR, IORB, VIX9D, VVIX, SKEW) und VIX6M sind per Metadaten bzw. Datei geprüft (26.09.2026).
- **Parameter (E-23):** Verzug = regulärer Höchstwert aus den Erstveröffentlichungen in ALFRED seit 2022. Uhrzeiten aus „last_updated“ (FRED) bzw. „Last-Modified“ (Cboe) mit Aufschlag. Toleranz überall nach E-10.

  | Reihen | Verzug | Uhrzeit ET | Beleg |
  |---|---|---|---|
  | Cboe (6) | 0 | 22:00 | Dateien am 25.09. um 18:01 (VIX9D, VIX3M, VIX6M, VVIX), 20:30 (VIX), 21:51 ET (SKEW) geändert; Einzelbeobachtung |
  | ICE-OAS (5) | 1 | 10:15 | FRED-Update 10:01–10:04 ET am Folgetag; ALFRED verzeichnet Verzug 0 und ist hier unbrauchbar |
  | NFCI, ANFCI | 6 | 08:45 | 5 Tage 208×, 6 Tage 36×, Ausreißer 13/20 |
  | STLFSI4 | 6 | 14:00 | 5 Tage 59×, 6 Tage 143×; Uhrzeit nur einmal beobachtet (13:07 ET) |
  | T10Y3M, T10Y2Y | 0 | 17:15 | 0 Tage 576×, 1 Tag 3×; Update 17:03 ET am selben Tag |
  | DGS10 | 1 | 16:30 | 1 Tag 445×, 3 Tage (Fr → Mo) 104×, Feiertage 29× |
  | SOFR | 1 | 08:15 | 1 Tag 921×, 3 Tage 205×, Feiertage 54× |
  | IORB | 0 | 16:45 | Satz steht 1–6 Tage vorher fest (E-25) |
  | SP500 | 0 | 20:15 | Update 20:01 ET am selben Tag; keine ALFRED-Historie |
  | ICSA, IC4WSA | 5 | 08:45 | 5 Tage 231×, 4 Tage 9×, 7 Ausreißer 12–54 Tage (vermutlich Shutdown 2025, nicht geprüft) |
  | SAHMREALTIME | 37 | 10:00 | 31–37 Tage 50×, 39–45 Tage 4×, 80 Tage 1× |

  Die Plausibilitätsgrenzen stehen in `config/series.toml`. Die historischen Extreme liegen weit innerhalb; im Erstabruf wurde kein Wert verworfen.
- **Nutzungsbedingungen (geprüft 26.09.2026):**
  - [FRED](https://fred.stlouisfed.org/docs/api/terms_of_use.html): Serien mit Copyright (ICE, S&P) nur zur eigenen Nutzung. Pflichthinweis in der Oberfläche: „This product uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis.“ (M6)
  - [Cboe](https://www.cboe.com/terms) (Stand 16.11.2022): „download one copy … for your personal non-commercial use“; ohne Zustimmung untersagt ist, Inhalte „otherwise … store … in an electronic retrieval system“. Kein ausdrückliches Verbot automatisierter Abrufe. Weiterverwendung trotz Auslegungsfrage: E-26.
- **Formate:**
  - Cboe: `DATE,OPEN,HIGH,LOW,CLOSE` (VIX, VIX9D, VIX3M, VIX6M) oder `DATE,<Symbol>` (VVIX, SKEW), Datum MM/DD/YYYY
  - FRED: JSON mit `count`, `offset` und `observations`; „.“ steht für fehlende Werte (bei ICE Feiertage). ICE hat zusätzlich echte Werte an Monatsenden, die auf ein Wochenende fallen.
- **Belege:**
  - `pytest -q`: 143 passed (73 neu)
  - Ende-zu-Ende gegen `data-dev/` mit echten Abrufen:
    - Lauf 1: 101 363 Zeilen aus 23 Reihen, 0 verworfen, 0 Fehler, 22 s
    - Lauf 2: 0 neue Zeilen, keine neue Rohdatei
    - Größe: Datenbank 14,7 MB (plus WAL 6,0 MB), `raw/` 0,64 MB
  - Rohdaten: Ein Vollabruf aller Reihen ergibt 0,68 MB komprimiert. Bei täglichem Abruf sind das grob 0,15–0,25 GB pro Jahr (Einschätzung; FRED-Antworten ändern sich täglich, weil sie das Abrufdatum enthalten).
  - Gegenprobe mit 16 absichtlich eingebauten Fehlern, jeder von mindestens einem Test erkannt:
    - Vintage immer geschätzt, Wochenendregel fehlt, UTC statt New York, keine Begrenzung auf die Abrufzeit
    - Grenzen, `lead_days` oder `start` ignoriert; verworfene Werte nicht in `source_status`
    - Cboe: OPEN statt CLOSE, Schutz der Tageszeile fehlt
    - FRED: „.“ nicht übersprungen, Abschneiden nicht erkannt
    - Duplikate nicht erkannt; Toleranzabweichung ohne Begründung; ID ungleich Quellkennung; `cdn-api.cboe.com` fehlt in der Allowlist (dafür kam ein Test hinzu)
  - API-Schlüssel in keiner Datei des Repos, der Fixtures und der Rohdaten (geprüft per Skript, ohne Ausgabe des Werts)
- **Nicht geprüft:**
  - ob die Cboe-CSV tagsüber eine laufende Tageszeile enthält (frühestens Montag, 28.09.2026, während der US-Handelszeit); der Schutz ist trotzdem aktiv
  - Uhrzeiten, die nur einmal beobachtet wurden (Cboe, ICE, STLFSI4, SP500, T10Y3M, T10Y2Y): in M3 aus dem Rohdatenarchiv prüfen
  - Build und Betrieb auf TrueNAS (M3). Dockerfile und Compose sind unverändert, daher keine Build-Probe.
- **Technische Schuld (behoben 28.09.2026 auf Anweisung):** Der HTTP-Client verwarf bei HTTP-Fehlern den Antworttext. Seitdem hängt er einen kurzen Auszug (ohne Tags, höchstens 160 Zeichen, Secrets maskiert) an die Meldung; er erscheint im Log und im Datenstand.

### M3 – Worker und erste Inbetriebnahme auf TrueNAS

**Ziel:** Der Worker läuft dauerhaft auf TrueNAS als Dockge-Stack (E-21) und archiviert ab jetzt täglich.

**Dateien:**
- `fever/worker.py`, `tests/test_worker_schedule.py`
- Healthcheck `worker` in der Compose-Datei
- Compose-Datei für den Betrieb ohne `build`: ruft das im Projektverzeichnis gebaute Image auf, läuft in Dockge, Datenordner als Volume (E-21)
- `.env.example` (Pfad und IDs für TrueNAS), `docs/einrichtung.md` (Neufassung für TrueNAS und Dockge)

**Schritte:**
1. Schleife alle 15 Minuten; fällige Abrufe nach Veröffentlichungsplan in America/New_York.
2. Heartbeat schreiben, sauberes Beenden bei SIGTERM (`docker compose stop`), tägliches Backup.
3. Healthcheck: Heartbeat-Alter (Vorschlag: höchstens 45 Minuten, also drei Takte).
4. Branch für den Betrieb: `claude-testing` (E-30).
5. Angaben des Nutzers (26.09.2026): TrueNAS 25.10.7, Projekt-Dataset `/mnt/Daten-Z1/apps/feewer`, Datenordner als Kind-Dataset `data` (E-28), `apps` 568:568 (E-29), Web-Port 8003.
6. Build und Betrieb getrennt in zwei Dateien (E-32).
7. Einrichtung auf TrueNAS nach der neuen `docs/einrichtung.md`. Führt der Nutzer aus, weil die KI keinen Zugriff auf TrueNAS hat. Jeder ausgeführte Schritt wird mit ✅ und Datum markiert.
8. Abrufe je Reihe nach `release_time` und `lag_days` aus `config/series.toml` planen. `fever.sources.update.update_series` erledigt Abruf, Prüfung und Speichern einer Reihe.
9. Nach einigen Tagen Betrieb die tatsächlichen Änderungszeiten aus dem Rohdatenarchiv (Zeitstempel bei geändertem Inhalt) mit `release_time` vergleichen. Das betrifft vor allem die nur einmal beobachteten Uhrzeiten (M2, „Ergebnis Teil B“). Abweichungen als Änderung zur Freigabe vorlegen, dazu das Verhalten der Cboe-CSV während der US-Handelszeit.

**Tests:**
- Fälligkeit rund um die Sommerzeitwechsel: USA endet am 01.11.2026, EU am 25.10.2026
- handelsfreie Tage sind kein Fehler
- Heartbeat wird geschrieben

**Ergebnis (26.09.2026, umgesetzt; Einrichtung auf TrueNAS offen):**
- **Umgesetzt wie freigegeben:**
  - `fever/worker.py`: Takt 15 Minuten, Abrufplan E-31, Heartbeat zu Beginn jedes Takts und vor jedem Abruf, tägliches Backup einmal pro UTC-Tag (übersteht Neustarts, weil es an den Backup-Dateien hängt), Ende bei SIGTERM/SIGINT zwischen zwei Reihen, `healthcheck()` nach E-33
  - Ein unerwarteter Fehler bei einer Reihe wird mit Traceback geloggt, maskiert in `source_status` eingetragen, und die übrigen Reihen laufen weiter
  - Ohne Datenbank startet der Worker nicht (Exit-Code 2, Meldung „Datenbank fehlt …“); er legt nie eine an
  - `docker-compose.yml` (Bau-Datei, Projekt `fever-build`, startet nichts) und `compose.dockge.yaml` (Laufzeit, `user:` aus `.env`, `stop_grace_period: 30s`, Healthcheck alle 5 Minuten)
  - `.env.example` für TrueNAS; `docs/einrichtung.md` neu für TrueNAS und Dockge
  - Speicherfunktionen `latest_obs_date`, `record_heartbeat`/`read_heartbeat`; `has_backup` in `fever/backup.py`; `UpdateResult.fetched`
- **Abweichungen vom Plan:**
  - Den Dienst `web` enthält `compose.dockge.yaml` erst ab M6 (statt eines Profils): Bis dahin gibt es kein Modul, das er starten könnte.
  - Das Dockerfile ist nur in zwei Kommentaren geändert (Benutzer kommt im Betrieb aus `user:`).
- **Belege:**
  - `pytest -q`: 178 passed (35 neu: Abrufplan, Worker, Compose)
  - Build-Probe x86_64 mit dem Dockerfile (plus Zertifikatszeilen, Abschnitt 10): 42 s, Image 125 MB, alle Importe laden
  - `docker compose config`: beide Dateien gültig; ohne `.env` Abbruch mit „FEVER_UID fehlt in .env …“; `up` mit der Bau-Datei gibt nur den Hinweis aus
  - Laufzeit-Stack mit `docker compose` (statt Dockge) gegen einen Datenordner mit Eigentümer 568:568:
    - Container läuft als `uid=568 gid=568`
    - Log „Worker gestartet: 23 Reihen, Takt 15 Minuten“ und „Tägliches Backup erstellt und geprüft“
    - Healthcheck „gesund“, Exit-Code 0
    - `docker compose stop` in unter 1 s, Log „Worker beendet“, Exit-Code 0
    - alle Dateien gehören 568:568
  - Gegenprobe mit 12 absichtlich eingebauten Fehlern, jeder erkannt: Wochenende nicht ausgeschlossen, UTC statt New York, kein Warten nach Fehlschlag, Nachfassen bei Wochenreihen, kein Nachfassen bei fehlendem Tageswert, Fehlschlag als Erfolg, kein Heartbeat, Backup in jedem Takt, Ausnahme stoppt den Takt, Stopp-Signal ignoriert, Healthcheck-Grenze falsch, Laufzeit-Compose baut
- **Nicht geprüft:**
  - Abrufe im laufenden Worker: Der Probelauf war an einem Samstag, nach E-31 ist dann nichts fällig. Der Abrufweg selbst ist mit echten Daten in M2 geprüft.
  - Der Docker-Healthcheck-Status (erste Prüfung nach 5 Minuten); geprüft ist der Befehl selbst im Container.
  - Alles auf TrueNAS: ob `git` vorhanden ist, `sudo docker`, das Anlegen des Datasets, Dockge mit `.env`, `timedatectl`. Die Anleitung markiert diese Schritte mit ⏳.
- **Inbetriebnahme auf TrueNAS (26.09.2026, Nutzer):** Stack `finanz-dashboard`, Container `finanz-dashboard-worker-1` „Up (healthy)“, Healthcheck „gesund“. Dataset-Name `feewer` und Stack-Name bleiben (E-34). Der Klon in das schon vorhandene Dataset scheiterte an `git clone` (nicht leeres Verzeichnis); die Anleitung nutzt seitdem `git init` + `fetch` + `checkout`.
- **Erstabruf auf TrueNAS (Samstag, 26.09.2026, 11:32 UTC, Sofort-Abruf per `docker exec`):** 23 Reihen, 101 363 Zeilen, keine verworfenen Werte, keine Fehler; Zeilenzahlen identisch mit dem Probelauf in der Entwicklungsumgebung. Das lokale ICE-Archiv beginnt mit dem Beobachtungsdatum 26.09.2023. Datenbank 14,7 MB (plus WAL 6,0 MB). Mountpunkt `/mnt/Daten-Z1/apps/feewer/data -> /data`, Benutzer 568:568, alle Dateien 568:568.
- **Erster Werktag nach dem Abrufplan (Montag, 28.09.2026, Nutzer):** Die planmäßigen Abrufe liefen um 15:07 durch, ohne Fehler. M3 ☑ auf Anweisung des Nutzers. Schritt 9 (Veröffentlichungszeiten aus dem Rohdatenarchiv gegen `release_time`, Cboe-CSV während der Handelszeit) braucht einige Werktage und läuft als Nachprüfung weiter; Abweichungen kommen als Änderung zur Freigabe.

### M4 – Weitere Quellen

**Ziel:** CFTC (COT), EZB (CISS), OFR (FSI), Fed-Board (EBP), Shiller-CAPE, Margin Debt (Fed Z.1 über FRED, E-42; ursprünglich FINRA); dazu USD/JPY als Kreuzkurs aus EZB-Referenzkursen (E-17) und die VX-Futures-Termstruktur von Cboe (E-18).

**Schritte:**
1. Je Quelle wie in M2.
2. Unverifizierte Endpoints zuerst prüfen: OFR-FSI-Download, EBP-CSV, CISS `SS_CIN`, TFF-IDs bei CFTC, FINRA ohne Login, EZB-Referenzkurse für den USD/JPY-Kreuzkurs, Cboe-CSV je VX-Kontrakt.
3. Excel-Dateien (Shiller `ie_data.xls`, FINRA) brauchen ggf. eine Leser-Bibliothek. Das ist eine neue Abhängigkeit mit Begründung und geprüftem Wheel für linux/amd64, deshalb vorher fragen.
4. Nutzungsbedingungen je Quelle prüfen (kein Scraping gegen AGB).

**Tests:** Parser gegen Fixtures; Formatänderung der Quelle führt zu einem sichtbaren Fehler, nicht zu stillem Ausfall.

**Aufteilung (E-37):** M4a EZB, OFR, EBP · M4b CFTC COT · M4c Shiller-CAPE, Margin Debt (Z.1, E-42) · M4d VX-Futures. Jeder Teil hat einen eigenen Plan und eine eigene Freigabe.

**Befunde für alle Teile (26.09.2026, echte Abrufe):**

| Quelle | Endpoint | Befund |
|---|---|---|
| EZB CISS | `data-api.ecb.europa.eu/service/data/CISS/D.U2.Z0Z.4F.EC.SS_CIN.IDX` | täglich ab 03.01.1980 |
| EZB Referenzkurse | `…/EXR/D.USD.EUR.SP00.A`, `…/EXR/D.JPY.EUR.SP00.A` | täglich ab 04.01.1999; leere Werte an TARGET-Feiertagen bis 2012 |
| OFR FSI | `www.financialresearch.gov/financial-stress-index/data/fsi.csv` | täglich ab 03.01.2000; Gesamtwert, 5 Kategorien, 3 Regionen; die OFR-API (`data.financialresearch.gov/v1`) enthält den FSI nicht |
| Fed EBP | `www.federalreserve.gov/econres/notes/feds-notes/ebp_csv.csv` | monatlich ab 01/1973; Spalten `gz_spread`, `ebp`, `est_prob` |
| CFTC COT (M4b) | Socrata `publicreporting.cftc.gov/resource/6dca-aqww.json` (Legacy, Futures Only), `gpe5-46if` (TFF) | VIX-Futures `1170E1` ab 27.07.2004 (1114 Berichte); E-mini S&P 500 `13874A` |
| Shiller (M4c) | `shillerdata.com` verlinkt `img1.wsimg.com/…/ie_data.xls` (Pfad mit Kennung) | `.xls` (Binärformat), Blatt „Data“, Datum als `JJJJ.MM` (Oktober = `2026.1`), Spalten CAPE, TR CAPE, Excess CAPE Yield; laufender Monat vorläufig |
| FINRA (entfällt, E-42) | `www.finra.org/sites/default/files/2021-03/margin-statistics.xlsx` | `.xlsx`, Debit Balances in Mio. USD, neueste Zeile zuerst |
| Cboe VX (M4d) | Kontraktliste `www.cboe.com/us/futures/market_statistics/historical_data/product/list/VX/` (JSON), CSV je Kontrakt auf `cdn.cboe.com/data/us/futures/…/VX/VX_<Verfall>.csv` | Spalten u. a. Settle, Open Interest; Monats- und Wochenkontrakte |

- **Excel-Leser für M4c:** `xlrd` 2.0.2 (für `.xls` nötig) und `openpyxl` 3.1.5 mit `et_xmlfile` 2.0.0 sind reine Python-Wheels (`py3-none-any`). Die Auswahl wird in M4c entschieden.
- **Nutzungsbedingungen:**
  - EZB: Weiterverwendung frei mit der Quellenangabe „Source: ECB statistics.“ (Pflichthinweis in M6).
  - FINRA (Stand 09.11.2023): nur „own non-commercial personal or professional use“; untersagt sind „data mining, scraping or harvesting tools (including robots)“ und „stored for subsequent use“ ohne Zustimmung. Ein automatischer Abruf widerspräche `CLAUDE.md` (kein Scraping gegen AGB); die Klärung erfolgt in M4c.
  - Shiller: in der Datei nur ein Haftungsausschluss.
  - OFR: keine Einschränkung für eigene Daten genannt, nur ein Haftungsausschluss.
  - Fed-Board: „Unless otherwise indicated, information on Board's website is in the public domain“, Quellenangabe erbeten (Website Policies, geprüft 26.09.2026). Gilt für EBP und Z.1.
- **Margin Debt, Optionen (26.09.2026, zur Entscheidung vor M4c):**
  - FINRA-Nutzungsbedingungen (Stand 09.11.2023) untersagen neben Robots auch „stored for subsequent use“ und „develop or create a database of data using the FINRA Website“ ohne schriftliche Zustimmung. Damit wäre auch ein manueller Download mit Import in die Datenbank ohne Zustimmung unzulässig. Die Statistikseite sagt: „FINRA does not provide the data outside of this webpage and data feeds are not available.“ Zustimmung per Anfrage über `finra.org/contact-finra/permission-use-finra-copyrighted-material`, ohne Formular, Gebühr oder Frist.
  - Ersatz aus der Z.1-Statistik der Fed über FRED: `BOGZ1FL663067003Q` (Security Brokers and Dealers; Receivables Due from Customers, Margin Loans and Other Receivables), quartalsweise ab Q4 1945, Mio. USD, echte Vintages in ALFRED. Veröffentlichung etwa 10 Wochen nach Quartalsende (Q2 2026 am 11.09.2026). Einmaliger Vergleich mit der FINRA-Datei, Quartalsenden 1997 bis Q2 2026: Niveau 0,42- bis 1,52-mal FINRA (Median 0,63), Vorjahresveränderungen korrelieren mit 0,83, gleiches Vorzeichen in 101 von 114 Quartalen. Abweichungen in einzelnen Phasen, z. B. 2007-12 FINRA +17 %, Z.1 +3 %; 2022-06 FINRA −23 %, Z.1 −6 %.
  - Die Haushaltsreihe `BOGZ1FL153167005Q` (Margin Accounts at Brokers and Dealers) hat in ALFRED nur einen Stand (11.09.2026) und kommt deshalb nicht in Frage.

**Ergebnis M4a (26.09.2026, erledigt):**
- **Umgesetzt wie freigegeben:**
  - `fever/sources/ecb.py`, `ofr.py`, `fed.py`; gemeinsame CSV-Spaltenfunktion `csv_column` in `fever/sources/__init__.py`
  - Gruppenabruf (E-36): `update_group` in `fever/sources/update.py`, Worker plant je Gruppe
  - Katalogfelder `group`, ID-Regel E-35; Allowlist um `data-api.ecb.europa.eu`, `www.financialresearch.gov`, `www.federalreserve.gov`
  - 14 Reihen in `config/series.toml`; Fixtures aus gekürzten echten Antworten (nicht lizenziert)
- **Zusätzlich:** Sofort-Abruf als Kommando `python -m fever.sources.update` (vorher Einzeiler); Exit-Code 1, wenn eine Reihe ein Problem meldet.
- **Parameter (E-38):**

  | Reihen | Verzug | Uhrzeit ET | Beleg |
  |---|---|---|---|
  | `ecb_ciss` | 1 | 06:15 | Datei am Fr 25.09. um 09:00 UTC geändert, letzter Wert Do 24.09.; Einzelbeobachtung. Annahme: feste MEZ-Uhrzeit, daher auch in den Umstellungswochen passend |
  | `ecb_exr_usd`, `ecb_exr_jpy` | 0 | 11:15 | Datei am 25.09. um 13:57 UTC mit dem Wert desselben Tages; gegen 16:00 MEZ = 10:00 ET, in Umstellungswochen 11:00 ET |
  | `ofr_fsi` und 8 Teilindizes | 4 | 10:30 | „two business days prior“; Freitagswert erst am Dienstag; Datei am 25.09. um 10:00 EDT |
  | `fed_ebp`, `fed_gz_spread` | 38 | 10:15 | 4. Geschäftstag des Folgemonats nach 10:00 ET; Monatserster + 38 Tage deckt späte Fälle ab; Datei 06.08. um 10:00 EDT für Juli |

  Grenzen: CISS 0–1 (per Konstruktion), USD 0,3–5, JPY 20–800, OFR −50 bis 150, EBP −10 bis 30, GZ −10 bis 50. Toleranz überall nach E-10.
- **Belege:**
  - `pytest -q`: 214 passed (36 neu)
  - `python -m fever.sources.update` gegen `data-dev/`: Lauf 1 mit 14 neuen Reihen und 92 327 Zeilen, 0 Probleme; Lauf 2 ohne neue Zeilen. OFR und EBP je einmal geladen und archiviert
  - Gegenprobe mit 14 absichtlich eingebauten Fehlern, alle erkannt (drei erst nach drei zusätzlichen Tests): CSV-Leerzelle, CSV-Kopfzeile, fremde EZB-Reihe, leerer EZB-Wert, Monatserster, Rohdaten je Reihe statt je Gruppe, Erfolg ohne lesbare Reihe, Fehler einzelner Reihen nicht gemeldet, Gruppenplan, Präfixregel, doppelte Quellkennung, Worker je Reihe statt je Gruppe, jüngstes statt ältestes Gruppenmitglied, Allowlist ohne OFR
- **Nicht geprüft:** Abruf auf TrueNAS (nach dem Update, `docs/einrichtung.md`, Schritt 9); Veröffentlichungszeiten von CISS nur einmal beobachtet (Prüfung wie M3, Schritt 9).

**Ergebnis M4b (26.09.2026, erledigt):**
- **Umgesetzt wie freigegeben (E-39):**
  - `fever/sources/cftc.py`: Socrata-Abfrage mit festen Feldern (`$select`), Filter auf den Marktcode (`$where`), Sortierung und `$limit` 50 000. Eine Antwort mit 50 000 oder mehr Zeilen gilt als womöglich abgeschnitten und ist ein Fehler. Werte müssen ganze Zahlen sein; ein fehlendes Feld gilt als fehlender Wert
  - `source_id` im Format `<Marktcode>/<Feld>`, z. B. `1170E1/noncomm_positions_long_all`; Marktcode und Feld werden geprüft
  - Quelle `cftc` im Katalog, Allowlist um `publicreporting.cftc.gov`
  - 4 Reihen in der Gruppe `cftc_vx` (ein Abruf, eine Rohdatei); Fixture aus der gekürzten echten Antwort (gemeinfrei)
- **Befunde:**
  - Stichtag ist der Dienstag, Veröffentlichung am Freitag um 15:30 ET; in Wochen mit US-Feiertag verschiebt sich die Veröffentlichung, 2026 auf die Montage 22.06., 16.11., 30.11. und 28.12. (CFTC-Veröffentlichungsplan)
  - Historie ab 27.07.2004, 1114 Berichte. 10 Stichtage fallen auf Montag oder Mittwoch (Feiertagswochen). Lücken der Quelle: 2006 (98 Tage) und 12/2008 bis 06/2009 (168 Tage); Grund nicht geprüft
  - Der Feldname `noncomm_postions_spread_all` enthält einen Tippfehler der CFTC und wird so abgefragt
  - Nutzungsbedingungen: gemeinfrei, die CFTC bittet um Quellenangabe (Hinweis in M6)
- **Parameter (E-40):**

  | Reihe | CFTC-Feld | Historie (Kontrakte) |
  |---|---|---|
  | `cftc_vx_open_interest` | `open_interest_all` | 5 732 bis 704 831 |
  | `cftc_vx_noncomm_long` | `noncomm_positions_long_all` | 426 bis 258 691 |
  | `cftc_vx_noncomm_short` | `noncomm_positions_short_all` | 233 bis 353 649 |
  | `cftc_vx_noncomm_spread` | `noncomm_postions_spread_all` | 0 bis 236 674 |

  Alle wöchentlich, Verzug 3 (Dienstag → Freitag), Uhrzeit 15:45 ET (15 Minuten nach der Veröffentlichung), Toleranz nach E-10, Grenzen 0 bis 10 000 000 (fangen nur grobe Fehler wie Einheit oder Vorzeichen).
- **Belege:**
  - `pytest -q`: 231 passed (17 neu in `tests/test_sources_cftc.py`)
  - Gruppe `cftc_vx` gegen `data-dev/` mit echter API: Lauf 1 mit 4 × 1114 neuen Zeilen, geschätzter Stand des Stichtags 22.09.2026 = Fr 25.09.2026 19:45 UTC; Lauf 2 ohne neue Zeilen und ohne zweite Rohdatei
  - `python -m fever.sources.update` gegen `data-dev/`, zweimal: „Sofort-Abruf beendet: 41 Reihen, 0 mit Problemen“; Worker-Start meldet „41 Reihen in 29 Abrufgruppen“
  - Gegenprobe gegen die CFTC-Jahresdatei `deacot2026.zip` (anderer Vertriebsweg): 38 Stichtage 2026, keine Abweichung
  - Gegenprobe mit 11 absichtlich eingebauten Fehlern, alle erkannt: immer erstes Feld, Kürzungsschutz fehlt oder um eins zu spät, Marktcode oder Feld ungeprüft, fehlendes Feld nicht übersprungen, Dezimalwerte akzeptiert, ohne Datums- und Endlichkeitsprüfung, kein Marktfilter, Allowlist ohne CFTC, Quelle nicht registriert
- **Auf TrueNAS geprüft (26.09.2026, zusammen mit M4a):** Sofort-Abruf „41 Reihen, 0 mit Problemen“.
- **Nicht geprüft:** tatsächliche Ankunft des Freitagsberichts vor 15:45 ET (Rohdatenarchiv nach dem ersten Freitag prüfen, wie M3, Schritt 9).

**Ergebnis M4c (26.09.2026, erledigt):**
- **Umgesetzt wie freigegeben (E-43):**
  - `fever/sources/shiller.py`: Abruf in zwei Schritten. Die Download-Seite `shillerdata.com` wird geladen, darin muss genau ein Link auf `img1.wsimg.com/…/ie_data.xls` stehen; danach wird die Datei geladen. Einlesen mit `xlrd` 2.0.2 (E-41): Blatt „Data“, Kopfzeile = Zeile mit „Date“ in Spalte A, Spalte über den vollständigen Kopftext (`source_id`), Datum `JJJJ.MM` mit Oktober als `.1`, „NA“ und leere Zellen als fehlende Werte, Hinweiszeile am Ende übersprungen
  - 2 Reihen in der Gruppe `shiller` (`shiller_cape`, `shiller_ecy`) und die Z.1-Reihe `bogz1fl663067003q` über das vorhandene FRED-Modul (E-42); neue Frequenz `quarterly`
  - Allowlist um `shillerdata.com` und `img1.wsimg.com`; `xlrd==2.0.2` in `requirements.txt`
  - Fixtures: Shiller synthetisch (enthält S&P-Daten, E-27), erzeugt mit `tests/fixtures/shiller/make_ie_data.py` (braucht `xlwt`, keine Projektabhängigkeit); Z.1 als gekürzte echte Antwort (gemeinfrei)
- **Parameter (E-44):**

  | Reihe | Frequenz | Verzug | Uhrzeit ET | Toleranz | Grenzen | Beleg |
  |---|---|---|---|---|---|---|
  | `shiller_cape` | monatlich | 45 | 16:00 | 10 | 1 bis 100 | Historie 4,78 bis 44,20; Verzug = Monatsende plus rund zwei Wochen für unregelmäßige Uploads (nur ein Upload beobachtet: 02.09.2026, 13:52 ET) |
  | `shiller_ecy` | monatlich | 45 | 16:00 | 10 | −0,5 bis 0,5 | Historie −0,026 bis 0,235 (dezimal, 0,01 = 1 %) |
  | `bogz1fl663067003q` | quartalsweise | 175 | 13:15 | 10 (neuer Standard) | 0 bis 10 000 000 | Mio. USD, Historie 594 bis 742 321. Erstveröffentlichung 2019–2026 (ALFRED, 30 Quartale) 156 bis 192 Tage nach Quartalsbeginn, Median 161,5; regulärer Höchstwert 175, nur der Shutdown-Fall Q3 2025 lag bei 192 |

- **Befunde:**
  - Die Zeile des laufenden Monats ist vorläufig: Kurs und GS10 vom ersten Handelstag, CPI geschätzt (Hinweiszeile der Datei). Sie wird mit der Abrufzeit gespeichert und später revidiert; mit Verzug 45 zählt ein Monat im Score erst ab Mitte des Folgemonats.
  - Excess CAPE Yield laut Datei = 1/CAPE − (GS10 − annualisierte Inflation der letzten 10 Jahre); für alle 1749 Monate nachgerechnet (L-10).
  - Z.1 wird um 12:00 ET veröffentlicht (Fed; Datei `FRB_Z1_csv.zip` mit `Last-Modified` 11.09.2026 16:00 UTC). FRED übernahm das Update am 11.09.2026 um 12:52 ET. Nächster Termin: 10.12.2026.
  - **Strukturbruch in Z.1:** Laut Series Analyzer der Fed enthält die Reihe vor 2000:Q1 auch Forderungen an Nicht-Kunden (F830). Veränderungen gegenüber dem Vorjahr über diese Grenze sind verzerrt; relevant für Fenster und Backtest (L-10, Phase 2).
  - In der neuen Tabellenstruktur der Fed (L.130 heißt jetzt S125s3.s) und in `z1_csv_files.zip` fehlt die Reihe; sie steht nur noch im Gesamtpaket `FRB_Z1_csv.zip` und bei FRED.
- **Belege:**
  - `pytest -q`: 261 passed (30 neu)
  - Echte Abrufe gegen `data-dev/`: Shiller 2 × 1749 Zeilen ab 01.1881, Z.1 305 Zeilen ab Q4 1945; zweiter Lauf ohne neue Zeilen und ohne zweite Rohdatei. `python -m fever.sources.update`: „44 Reihen, 0 mit Problemen“; Worker-Start „44 Reihen in 31 Abrufgruppen“
  - Gegenprobe Shiller: Excess CAPE Yield aus CAPE, GS10 und CPI der archivierten Datei nachgerechnet, 1749 von 1749 Monaten, größte Abweichung 2,2·10⁻¹⁶
  - Gegenprobe Z.1: FRED gegen die Fed-Gesamtdatei `FRB_Z1_csv.zip`, 305 von 305 Quartalen identisch
  - Gegenprobe mit 17 absichtlich eingebauten Fehlern, alle erkannt (Link-Host, doppelte Links, HTML-Entities, Excel-Kennung, Kopfzeilensuche, Spalte per Teiltext, Leerzeichen, Monat abgeschnitten, Monatsprüfung, NA, Hinweiszeile, `checked()`, Allowlist, Registrierung, Frequenz, beide Verzüge)
  - Build-Probe (linux/amd64): 42 s, `xlrd` 2.0.2 im Image
- **Auf TrueNAS geprüft (26.09.2026):** Sofort-Abruf „44 Reihen, 0 mit Problemen“.
- **Nicht geprüft:**
  - In der Cloud-Umgebung brach der Proxy Verbindungen zu `shillerdata.com` zeitweise ab (`ws_closed_mid_exchange`, auch mit curl); ein zweiter Sofort-Abruf meldete deshalb nach drei Versuchen einen Fehler für die Gruppe `shiller`, sichtbar und ohne Datenverlust
  - Regelmäßigkeit und Uhrzeit der Shiller-Uploads (Verzug 45 unbelegt; Internet Archive aus der Cloud-Umgebung nicht erreichbar)

**Ergebnis M4d (26.09.2026, erledigt):**
- **Umgesetzt wie freigegeben (E-45, E-46):**
  - Neue Quelle `cfe` (Cboe Futures Exchange), `fever/sources/cfe.py`: Kontraktliste von `www.cboe.com` (JSON), dann die CSV je Monatskontrakt von `cdn.cboe.com`; Wochenkontrakte und Mini-VX bleiben außen vor. Ein Abruf wird als JSON-Bündel archiviert
  - 16 Reihen in der Gruppe `cfe_vx`: `cfe_vx1` bis `cfe_vx8` (Settlement) und `cfe_vx1_days` bis `cfe_vx8_days` (Kalendertage bis Verfall)
  - Rangregel: Rang n ist der n-te Monatskontrakt, der am Handelstag gelistet ist (erste Zeile seiner Datei an oder vor dem Tag) und danach verfällt. Am Verfallstag zählt der verfallende Kontrakt nicht mehr. Fehlt einem gelisteten Kontrakt die Zeile, bleibt sein Rang leer; spätere rücken nicht auf. Settlement 0 gilt als fehlend
  - `fetch` aller Quellmodule hat den optionalen Parameter `since` (jüngster gespeicherter Tag der Gruppe, Minimum über die Mitglieder). Nur `cfe` nutzt ihn: Erstabruf aller Monatskontrakte, danach nur Kontrakte mit Verfall ab `since` − 45 Tage; das Bündel nennt den ersten vollständig abgedeckten Tag
  - Allowlist um `www.cboe.com`; Fixtures: gekürzte echte Kontraktliste (keine Kurse), Kontraktdatei mit synthetischen Werten (E-27)
- **Parameter (E-46):** täglich, Verzug 0, 22:00 ET wie die Cboe-Indizes (unbelegt, Prüfung mit M3, Schritt 9), Toleranz 3 (E-10), Grenzen Settlement 1 bis 300, Restlaufzeit 1 bis 400 Tage.
- **Befunde:**
  - Kontraktdateien gibt es ab Verfall Januar 2013 (174 Monatskontrakte bis Juni 2027); ältere liefern „Access Denied“. Bis 17.05.2013 steht als Settlement 0; verwertbar ab 20.05.2013
  - An jedem der 3362 Handelstage seit 20.05.2013 gibt es mindestens 8 Monatskontrakte mit Settlement, ohne Lücke unter den vorderen Rängen. Settlement historisch 8,75 bis 72,63
  - Die Tages-Settlementdatei (`settlement/csv?dt=…`) liefert für unbekannte Daten (2013, 2008) stillschweigend die aktuellen Kurse; sie wird nicht verwendet
  - `robots.txt` von `www.cboe.com` sperrt nur `/book/` und `volume_reports`; Nutzung wie E-26
- **Belege:**
  - `pytest -q`: 292 passed (31 neu)
  - Echter Abruf gegen `data-dev/`: Erstabruf 175 Anfragen in 178 s, je Reihe 3362 Werte vom 20.05.2013 bis 25.09.2026; Folgeabruf 12 Anfragen in 12 s, keine neuen Zeilen. Rohdaten: 666 KB (Erstabruf), 26 KB (Folgeabruf). `python -m fever.sources.update`: 60 Reihen, davon Shiller mit Proxy-Abbruch der Cloud-Umgebung (siehe M4c); Worker-Start „60 Reihen in 32 Abrufgruppen“
  - Gegenprobe gegen die Tages-Settlementdatei vom 25.09.2026: Ränge 1 bis 8 und Restlaufzeiten identisch
  - Unabhängige Neuberechnung aus getrennt geladenen Kontraktdateien: 26 896 Werte (3362 Tage × 8 Ränge), keine Abweichung
  - Gegenprobe mit 18 absichtlich eingebauten Fehlern, alle erkannt (Verfallstag, Aufrücken, Listungsbeginn, Settlement 0, erster vollständiger Tag, laufender Tag, Wochenkontrakte, Kontraktbezeichnung, Tag nach Verfall, Mindestzahl, Fenster, vertauschte Werte, Rang 9, Kopfzeile, `since` fehlt oder vom jüngsten Mitglied, Allowlist, Registrierung)
- **Auf TrueNAS geprüft (26.09.2026):** Sofort-Abruf „60 Reihen, 0 mit Problemen“.
- **Nicht geprüft:** Uhrzeit, ab der Cboe den Handelstag in die Kontraktdateien schreibt (22:00 ET übernommen von den Indizes).

### M5 – Scoring (Schritte 1–6, Stufe 1)

**Voraussetzung:** L-1 bis L-12 entschieden (E-47 bis E-49, 26.09.2026); `scoring.toml` mit Startwerten aus Bericht 4.3 und den Entscheidungen; Freigabe erteilt 26.09.2026.

**Dateien:**
- `[indicator.*]` in `config/series.toml`: Transformation, Orientierung, Block bzw. Fallhöhe (E-13)
- `fever/scoring/` mit Perzentil, Transformationen, Veraltung, Blockmedian, Composite, Fallhöhe, Glättung, Matrixregeln mit Hysterese, Konfidenz, Diffusionsindex. Reine Funktionen mit Stichtag t, ohne Import aus `web/` oder `store/`.
- Migration der Score-Tabellen
- Neuberechnung im Worker bei neuen Daten oder geändertem Hash von `scoring.toml`

**Indikatoren (E-49):**

| Block | Indikator | Transformation | Stress bzw. Fallhöhe hoch, wenn | V-Score |
|---|---|---|---|---|
| Volatilität | `vix` | VIX-Niveau | hoch | 1 |
| | `vix_vix3m` | VIX/VIX3M | hoch | 2 |
| | `vvix` | VVIX-Niveau | hoch | 2 |
| | `vrp` | VIX − realisierte Vola des S&P 500 (21 Beobachtungen, annualisiert) | niedrig | 2 |
| Kredit/Funding | `ebp` | Excess Bond Premium | hoch | 4 |
| | `sofr_iorb` | SOFR − IORB | hoch | 2 |
| | `ofr_credit`, `ofr_funding` | OFR-FSI-Teilindizes | hoch | 2 |
| Makro/Finanzierungsbedingungen | `nfci`, `stlfsi4`, `ciss` | Niveau | hoch | 3, 2, 2 |
| | `sahm` | Sahm-Regel in Echtzeit | hoch | 2 |
| | `claims` | 4-Wochen-Schnitt / Minimum der letzten 52 Wochen − 1 | hoch | 3 |
| | `stock_bond_corr` | Korrelation über 63 Beobachtungen: S&P-500-Logrendite gegen −ΔDGS10 | hoch | 2 |
| | `usdjpy_change`, `usdjpy_vol` | USD/JPY aus EZB-Kursen: −(5-Tage-Logveränderung), annualisierte Vola der Logveränderungen über 21 Kurstage | hoch | 2 |
| Fallhöhe | `ecy` | Excess CAPE Yield | niedrig | 1 |
| | `margin_yoy` | Margin Debt (Z.1) ggü. Vorjahresquartal | hoch | 2 |
| | `vx_cot_short` | (Short − Long) der Non-Commercials / Open Interest | hoch | 2 |

**Pflichttests** (`CLAUDE.md`):
- Ergebnis für t identisch mit und ohne Beobachtungen nach t
- Perzentil mit Gleichständen gegen ein handgerechnetes Beispiel
- Veraltung, Toleranz, Konfidenz
- Matrixregeln genau auf der Schwelle, Hysterese
- Block ohne gültigen Indikator

**Sichtbare Platzhalter:** Block „Breite“ ohne Datenquelle (O-1), Block „Positionierung“ ohne Indikator bis Phase 2 (AAII), HY-OAS-Rot-Regel inaktiv (O-5). Alles erscheint in der Oberfläche, nicht nur im Code (M6/M7).

**Ergebnis M5 (26.09.2026, umgesetzt; auf TrueNAS ⏳):**
- **Umgesetzt wie entschieden (E-47 bis E-50):**
  - `config/scoring.toml`: alle Parameter (Perzentilfenster, Mindesthistorie, Transformationsfenster, Mindestzahl Blöcke und Fallhöhe-Komponenten, Halbwertszeiten, Ampelschwellen, Hysterese); jeder Parameter ist Pflicht, fehlende oder unbekannte sind ein Fehler
  - `[indicator.*]` in `config/series.toml`: 19 Indikatoren (16 Stress in 3 Blöcken, 3 Fallhöhe; Tabelle oben). Die Anzahl in E-49 lautete zunächst 15; richtig sind 16 (Volatilität 4, Kredit/Funding 4, Makro 8)
  - `fever/scoring/`: `transforms.py` (10 Transformationen), `percentile.py` (Mittelrang, Fenster, Mindesthistorie), `composite.py` (Status je Indikator und Tag, Blöcke, Composite, Fallhöhe, EWMA, Konfidenz, Diffusion, Ampelregeln mit Hysterese), `pipeline.py`. Keine Importe aus `store`, `web` oder `sources` (geprüft)
  - `fever/release.py`: geschätzte Veröffentlichung (E-14) aus `fever/sources/update.py` herausgelöst, damit das Scoring nichts aus dem Speicher importiert
  - Migration 0002 mit `indicator_score` und `composite_score`; `fever/store/scores.py`
  - `fever/score.py`: Scoring-Lauf mit `python -m fever.score`; der Worker rechnet am Ende eines Takts neu, wenn seit dem letzten Lauf Beobachtungen gespeichert wurden oder sich `scoring.toml` bzw. `series.toml` geändert haben (SHA-256). Läufe und Fehler stehen unter `scoring` in `source_status`
- **Randfälle, bestätigt am 26.09.2026 (E-51):**
  - EWMA: Fehlt ein Wert (z. B. Composite mit weniger als 3 Blöcken), fehlt auch der geglättete Wert, und die Glättung beginnt danach neu
  - Realisierte Vola (VRP, USD/JPY): Wurzel aus 252 × Mittel der quadrierten täglichen Logrenditen, ohne Mittelwertabzug (wie die Varianz hinter dem VIX)
  - VIX/VIX3M-Regel: zählt nur Werte vom Score-Tag selbst; ein Tag ohne Wert unterbricht die Serien, beendet eine aktive Regel aber nicht
  - Ampel ohne Composite: Die übrigen Regeln (VIX/VIX3M, Fallhöhe, Diffusion) gelten weiter; der fehlende Composite ist in der Oberfläche zu kennzeichnen (M6)
  - Gelb „Fallhöhe ≥ 80 bei Stress < 75“ ist als „Fallhöhe ≥ 80“ umgesetzt; bei Stress ≥ 75 greift ohnehin die Orange-Regel, das Ergebnis ist gleich
  - Veraltung: Frequenz in Tagen täglich 1, wöchentlich 7, monatlich 31, quartalsweise 92 (E-10, E-44)
- **Stand am 25.09.2026 (`data-dev/`, Abruf 26.09.2026):** Stress 37,8 (Volatilität 28, Kredit/Funding 70, Makro 32), Fallhöhe 79,9 (roh 82,2: Excess CAPE Yield 99,6, Margin Debt 91,3, VX-COT 55,7), Ampel Grün, Konfidenz 90 % (EBP veraltet, weil das September-Update der Fed fehlt), Diffusion 20 %
- **Plausibilität in bekannten Episoden** (Stress geglättet / Fallhöhe / Ampel): 10.10.2008 93,7 / 24,1 / Rot; 24.08.2015 41,9 / 57,1 / Rot (VIX/VIX3M); 05.02.2018 23,2 / 70,8 / Grün; 16.03.2020 58,5 / 57,9 / Rot (VIX/VIX3M); 30.06.2020 88,6 / 46,1 / Rot (Composite, Hysterese); 12.10.2022 81,4 / 63,1 / Orange; 05.08.2024 59,7 / 64,7 / Gelb; 08.04.2025 54,2 / 64,2 / Rot (VIX/VIX3M). Seit 1990: Grün 63 %, Gelb 20 %, Orange 9 %, Rot 8 % der Handelstage
- **Befunde zur Methode (keine Rechenfehler, Folgen der Entscheidungen):**
  - Schnelle Schocks erreicht der Composite spät (Halbwertszeit 10, Makro- und Kreditblock träge); am 05.02.2018 war die Ampel noch grün, Rot kam über die VIX/VIX3M-Regel erst nach drei Tagen
  - Langsame Indikatoren (Erstanträge ggü. Tief, Sahm, EBP) halten den Composite nach Krisen hoch: Ende Juni 2020 noch Rot, als die Märkte sich erholt hatten
- **Belege:**
  - `pytest -q`: 341 passed (50 neu in `tests/test_scoring.py`, `tests/test_score.py` und `tests/test_config.py`), darunter die Pflichttests aus `CLAUDE.md`: Look-ahead (synthetisch), Perzentil mit Gleichständen von Hand, Veraltung/Toleranz/Konfidenz, Regeln genau auf der Schwelle und Hysterese, Block ohne gültigen Indikator
  - Look-ahead auf echten Daten: für 10.10.2008, 16.03.2020, 05.08.2024 und 18.09.2026 identische Ergebnisse mit und ohne Beobachtungen nach dem Stichtag (19 Indikatoren und Composite)
  - Gegenprobe mit 36 absichtlich eingebauten Fehlern, alle erkannt (Perzentil, Orientierung, Veröffentlichung, Stichtag, Veraltung, Median, Mindestblöcke, Glättung, Fallhöhe, Konfidenz, Diffusion, Regeln, Hysterese, VIX-Regel, Transformationen, Auslöser der Neuberechnung, Worker)
  - Rechenzeit: 5,6 s für den ganzen Lauf mit 9281 Handelstagen (Rechnung 2,0 s), Entwicklungsumgebung
  - Migration mit dem gebauten Image als 568:568 auf einer Kopie des Backups vor der Migration: 0001 → 0002, danach `python -m fever.score` wie oben
- **Auf TrueNAS geprüft (26.09.2026):** Migration 0002 und `python -m fever.score`: „9281 Tage ab 02.01.1990, zuletzt 25.09.2026: Stress 37,8, Fallhöhe 79,9, Ampel Grün, Konfidenz 90,0 % (6,5 s)“, identisch mit der Entwicklungsumgebung.


**Risiko:** Rechenzeit auf dem Zielsystem (rollierende Perzentile über bis zu 10 Jahre je Indikator). Erst messen, dann optimieren.

### M6 – Web-Grundgerüst, Gestaltung, Aktualität, Datenstand

**Ziel:** Lauffähige Dash-App mit Designsystem, Chart-Standard, Tooltip- und Erklärseiten-Mechanik, Aktualitätsanzeige und Ansicht „Datenstand“.

**Dateien:**
- `fever/web/app.py`: Dash mit `serve_locally=True` (Standard), gunicorn mit 1–2 Prozessen
- `fever/web/db.py`: nur lesend
- `fever/web/health.py`, `fever/web/figures.py` (Chart-Fabrik), `fever/web/components.py` (Kennzahl-Kopf mit Info-Symbol, Aktualitäts-Badge), `fever/web/texts.py` (Laden der Texte und Erzeugen von Steckbrief und Schwellen)
- `fever/web/pages/`: Übersicht, Themen-Ansichten, Visualisierung, Datenstand, Erklärungen, `/kennzahl/<id>`
- `assets/`: `base.css` (Tokens hell/dunkel, Layout), `tooltip.css`, `print.css`, `fullscreen.js`, `theme.js`

**Schritte:** Abschnitt 7 umsetzen. Quellenhinweis „Source: ECB statistics.“ neben dem FRED-Hinweis. Dienst `web` in `compose.dockge.yaml` ergänzen (Port `0.0.0.0:${FEVER_WEB_PORT}` nach E-4, Anzahl der gunicorn-Prozesse 1–2 festlegen) mit Healthcheck. Pflichthinweis nach den FRED-Nutzungsbedingungen auf jeder Seite, z. B. in der Fußzeile: „This product uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis.“

**Tests:**
- Smoke-Test: App startet, `/_dash-layout` und Health-Endpunkt liefern 200
- das ausgelieferte HTML enthält keine externe URL (kein CDN)
- die Chart-Fabrik setzt den Standard aus 7.1: Config, Zeitraum-Buttons, Datenstand-Annotation, `uirevision`
- kein `dangerously_allow_html` im Code
- jede angezeigte Kennzahl hat einen Text (siehe M8)

**Sichtprüfung:** Playwright mit dem vorinstallierten Chromium in der Entwicklungsumgebung (kein Projekt-Requirement), Breiten 390 px und 1440 px, hell und dunkel, Druckvorschau. Screenshots bleiben außerhalb des Repos.

**Ergebnis M6 (26.09.2026, umgesetzt; auf TrueNAS ⏳):**
- **Umgesetzt wie entschieden (E-52 bis E-55):**
  - `fever/web/app.py`: Dash 4.4.1 mit Seiten (`use_pages`), nur lokale Ressourcen, Seitenrahmen mit Kopfzeile (Worker zuletzt aktiv, Scores berechnet, Seite aktualisiert), Banner „Worker ohne Lebenszeichen“ (Grenze wie der Healthcheck) und „Keine Verbindung zum Server“ (clientseitig nach mehr als zwei Intervallen ohne Antwort), Aktualisierung alle 5 Minuten, Fußzeile mit den Pflichthinweisen (FRED, EZB) und Quellen, `/health`
  - `fever/web/db.py` (nur lesend, `query_only`), `format.py` (Dezimalkomma, TT.MM.JJJJ, MEZ/MESZ, relatives Alter), `figures.py` (Chart-Fabrik nach 7.1), `components.py` (Kennzahl-Kopf mit CSS-Tooltip, Aktualität, Ampel, Perzentil-Chip, Chart-Karte mit Vollbild), `texts.py` (Textprüfung, Steckbrief und „Schwellen und Farben“ aus der Konfiguration), `views.py` (Seiteninhalte als testbare Funktionen)
  - Seiten: Übersicht (Ampel mit zutreffenden Regeln, Stress, Fallhöhe, Konfidenz, Verlauf Stress/Fallhöhe, sichtbare Platzhalter O-1, O-5, Phase 2), Datenstand (Worker, je Quelle, je Reihe mit „veraltet“ nach E-10), Erklärungen, Erklärseite `/kennzahl/<id>`
  - Texte für `traffic_light`, `stress`, `vulnerability`, `confidence`, `percentile`, `staleness` (inhaltliche Prüfung durch den Nutzer wie in M8); Indikatoren ohne Text werden nicht angezeigt
  - `assets/`: `base.css` (Farben hell/dunkel aus der Referenzpalette), `tooltip.css`, `print.css`, `theme.js` (Systemwechsel, vor dem Druck hell), `fullscreen.js`
  - Dienst `web` in `compose.dockge.yaml` (gunicorn, 1 Prozess mit 4 Threads, seit E-77 mit 1 Thread, Port `0.0.0.0:${FEVER_WEB_PORT}`, Healthcheck über `/health` mit der Standardbibliothek); das Dockerfile kopiert `assets/`
  - Veraltungsregel (E-10) als `is_stale` in `fever/release.py`, gemeinsam für Scoring und Oberfläche
- **Belege:**
  - `pytest -q`: 359 passed (18 neu in `tests/test_web.py` und `tests/test_compose.py`): Smoke-Test (`/`, Seiten, `/_dash-layout`, `/_dash-dependencies`, `/health`), `/health` 503 ohne Datenbank, keine externe URL im HTML, `query_only`, kein `dangerously_allow_html`, Chart-Standard, Textregeln, jede angezeigte Kennzahl hat einen Text, Formate
  - gunicorn gegen `data-dev/`: alle Seiten 200
  - Sichtprüfung mit Playwright und Chromium (390 px und 1440 px, hell und dunkel, fünf Seiten): keine Konsolenfehler, keine Anfrage an fremde Hosts, kein horizontales Scrollen; Druck aus dem Dunkelmodus hell ohne Navigation und Knöpfe; Tooltip per Fokus; Vollbild und ESC. Behoben nach der Sichtprüfung: Legende über den Zeitraum-Buttons, abgeschnittene Datierung, schräge Achsenbeschriftung bei 390 px
  - Build-Probe; Dienst `web` über `compose.dockge.yaml` als 568:568: „healthy“, `0.0.0.0:8003`, Seiten 200
  - Farben: Linienfarben mit dem Validator des Dataviz-Skills geprüft (hell und dunkel, alle Prüfungen bestanden)
- **Nicht geprüft:** echte Geräte (nur Chromium-Emulation); Perzentilbänder im Verlauf fehlen noch (brauchen gespeicherte Bänder, M7). Auf TrueNAS läuft das Dashboard seit 26.09.2026 (Rückmeldung des Nutzers).

**Nachtrag M6 (26.09.2026): Rezessionsbalken (E-56) und Korrekturen aus der Sichtprüfung**
- **Umgesetzt:**
  - `config/series.toml`: Reihe `usrec` (FRED `USREC`, monatlich, Verzug 31 Tage wie die übrigen Monatsreihen, Grenzen 0 bis 1); damit 61 Reihen in 33 Abrufgruppen. Kein `[indicator.*]`, also in keinem Score.
  - `fever/web/db.py`: `recessions()` fasst aufeinanderfolgende Monate mit Wert 1 zu Zeiträumen (Monatserster bis Monatsletzter) zusammen, je Beobachtung der neueste Stand.
  - `fever/web/figures.py`: graue Flächen (`layer: below`, eigene Stufe für hell und dunkel) nur im Datenbereich des Charts; Datierungszeile „Grau: US-Rezessionen nach NBER (über FRED)“; `views.py` übergibt die Zeiträume an alle Zeitreihen-Charts.
  - Konzeptseite `fever/web/texts/recessions.md` mit Steckbrief aus `series.toml`; Fußzeile nennt die NBER-Rezessionsdatierung.
- **Korrigiert (Fehler seit M6, bei dieser Sichtprüfung gefunden):**
  1. Nach einem Klick auf einen Zeitraum-Button fiel die Chart-Karte auf 0 px Höhe zusammen: `dcc.Graph` mit `responsive` setzt `height: 100%`, der Container hatte keine Höhe. Jetzt steckt der Graph in `.chart-box` mit 450 px, der Höhe, die Plotly vorher als Standard nutzte.
  2. Plotly.js 4.1.1 (in Plotly 7.1.0) zeigt standardmäßig den Modebar-Button „Share chart…“, der den Chart samt Daten nach einer Bestätigung zu Plotly Cloud hochlädt (Standard `plotlyServerURL`: `https://cloud.plotly.com/newchart`, geprüft im Quelltext von `plotly.min.js`). Das widerspricht „keine Weitergabe lizenzierter Daten“ und „der Browser spricht nur mit dem eigenen Server“. Abgeschaltet mit `showSendToCloud: False`; ein Test sichert es.
  3. Im Vollbild rutschten die Datierungszeilen aus dem Bild, weil ihr Abstand ein Anteil der Plot-Höhe war. Jetzt fester Abstand in Pixeln (`yshift`).
  4. Der Vollbild-Button verdeckte die Modebar-Buttons „Zoom in“, „Zoom out“ und „Reset axes“. Er steht jetzt in einer eigenen Zeile über dem Chart; im Vollbild füllt der Chart den Rest der Höhe.
- **Belege (Entwicklungsumgebung, 26.09.2026):**
  - `pytest -q`: 362 passed (neu: Rezessionszeiträume aus `USREC`, Flächen und Datierungszeile, Chart-Container mit Höhe; erweitert: `showSendToCloud`, Pixelabstand der Datierung).
  - Messung mit Playwright/Chromium, Seite Stress, 1440 px: Karte/Plot vor dem Fix nach „Max“ 26/0 px, danach 507/450 px; Vollbild 900 px, unterste Datierungszeile endet bei 853 px (390 × 844: 797 px); ESC stellt 507/450 px wieder her. Kein Modebar-Button unter dem Vollbild-Button (1440 und 390 px); kein „Share chart“ im DOM. Keine Konsolenfehler.
  - Screenshots 390 und 1440 px, hell und dunkel, dazu Druckmedien-Emulation: Flächen 1990/91, 2001, 2008/09 und 2020 hinter den Linien.
  - Scores gegen `data-dev/` neu berechnet: unverändert (Stress 37,8, Fallhöhe 79,9, Ampel Grün, Konfidenz 90,0 %); `/_dash-layout` und `/health` 200.
- **Nicht geprüft:** TrueNAS; der echte Druckdialog (nur Druckmedien-Emulation, dabei läuft `beforeprint` nicht).

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

**Nachtrag 27.09.2026: eine Version (E-67)**
- Übersicht B ist die Startseite `/` (Karten Ampel, Stress, Fallhöhe, Konfidenz, Diffusionsindex; Ampelmatrix; Hinweis zum neuesten Stand; Aktualisierung je Quelle); `/uebersicht-b` leitet mit 301 auf `/` um
- Entfernt: die alte Übersicht mit den Bereichen und Einzelreihen (M7a: Rahmen, Callbacks mit `MATCH`, Auf- und Zuklappen, Stile, Tests); geblieben sind die 22 Texte, „So fließt der Wert in den Bereich ein“ auf den Erklärseiten und die Korrektur „Historie ab“
- Navigation in einer Zeile: Übersicht, Signale, Breite, Positionierung, Makro, Fallhöhe, Visualisierung, Datenstand, Erklärungen
- Belege: `pytest -q` 388 passed; Seiten 200, `/uebersicht-b` 301; Browser 1440 px hell und 390 px dunkel ohne Konsolenfehler und ohne seitliches Scrollen

**Ergebnis M7, Teil 1 (27.09.2026, umgesetzt; auf TrueNAS ⏳): Übersicht B und Ansichten 2–6 (E-62, E-65)**
- **Umgesetzt:**
  - Zweite Navigationszeile „Ansichten“ (`fever/web/app.py`, `VIEWS`); die bisherige Übersicht bleibt Startseite (E-62)
  - Übersicht B (`/uebersicht-b`): Ampel, Konfidenz, Diffusionsindex; Ampelmatrix mit den Regeln für Stress und Fallhöhe aus `scoring.toml` als Flächen (opake Tönungen, die höchste Stufe liegt oben, Stufennamen im Chart), Spur der letzten 60 Handelstage und heutigem Punkt; Hinweis, dass VIX/VIX3M-Regel, Diffusionsregel und Hysterese nicht in den Flächen stehen; letzte Aktualisierung je Quelle
  - `/ansicht/signale`: VIX-Termstruktur als Kurve (Indizes auf nominaler Frist, VX-Futures auf Restlaufzeit), VIX/VIX3M mit violetter Backwardation, VIX, VRP, VVIX, SKEW, USD/JPY; Hinweis zu MOVE (W-6)
  - `/ansicht/breite`: ausdrücklich ohne Datenquelle (O-1)
  - `/ansicht/positionierung`: VX-COT mit Perzentil über 10 Jahre (Score) und 3 Jahre (Anzeige), Margin Debt; Hinweis AAII (Phase 2)
  - `/ansicht/makro`: NFCI, ANFCI, STLFSI4, OFR FSI mit Beiträgen der Kategorien und Regionen, CISS, HY-OAS, CCC − BB (am selben Beobachtungstag gebildet), EBP, SOFR − IORB, Zinskurve mit violetten Inversionsphasen (E-65), Sahm-Regel, Erstanträge; Lizenzhinweis bei den ICE-Reihen
  - `/ansicht/fallhoehe`: CAPE, Excess CAPE Yield, Margin Debt; Hinweis auf fehlende Konzentration und Margin Debt relativ zur Marktkapitalisierung
  - Anzeige-Kennzahlen (`texts.DISPLAYS`): `vix_term`, `skew`, `hy_oas`, `ccc_bb`, `anfci`, `ofr_fsi`, `yield_curve`, `cape`, nie in einem Score, mit Steckbrief aus `series.toml` und Link zur Ansicht; 9 neue Texte (die acht und `diffusion`)
  - Chart-Fabrik: Ampelmatrix (`matrix`), Termstruktur (`curve`), violette Phasen, Nulllinie, Endbeschriftungen ab drei Linien; die Linienfarben folgen der validierten Reihenfolge der Referenzpalette (fünf Farben hell und dunkel mit dem Validator geprüft; im hellen Modus drei Farben unter 3:1 Kontrast, deshalb Endbeschriftungen); gemeinsame Chart-Konfiguration und Datierungszeilen
  - Charts der Ansichten starten mit der ganzen Historie und beim ersten echten Wert: Plotly skaliert die y-Achse über alle Daten, ein Start mit 5 Jahren ließ NFCI, Sahm-Regel oder Erstanträge flach wirken
  - Kleine Werte mit mindestens zwei signifikanten Stellen (die Yen-Aufwertung zeigte „0,00“); Tooltips mit vier signifikanten Stellen
- **Belege (Entwicklungsumgebung, 27.09.2026):**
  - `pytest -q`: 386 passed; neu: Regionen der Matrix aus `scoring.toml` (geänderte Parameter verschieben die Flächen), Matrix-Standard und Beschriftungen, Übersicht B mit Spur der letzten 60 Tage, Navigation, alle Ansichten rendern und zeigen jede Anzeige-Kennzahl, Seiten 200, `runs`, CCC − BB nur an gemeinsamen Tagen, Inversionsflächen, Werteformat, Link der Anzeige-Seiten
  - Browser (Chromium, 1440 px hell, 390 px dunkel): alle Seiten ohne Konsolenfehler. Datenmenge je Seite: Signale 1,5 MB, Positionierung 1,0 MB, Makro 3,4 MB (14 Charts, rund 6 s), Fallhöhe 0,7 MB
- **Nicht geprüft:** TrueNAS; echte Geräte; Druck der neuen Seiten.

**Ergebnis M7, Teil 2 (27.09.2026, umgesetzt; auf TrueNAS ⏳): Perzentilbänder (E-64) und Ansicht 7 (E-63, E-66)**
- **Umgesetzt:**
  - Scoring: `window_quantiles()` in `fever/scoring/percentile.py` (10., 50. und 90. Perzentil der Rohwerte im selben Fenster wie das Perzentil, nur Beobachtungen bis t, lineare Interpolation, unter der Mindesthistorie leer); `IndicatorHistory.bands`, `IndicatorScore.band_p10/p50/p90`
  - Migration 0003: drei Spalten in `indicator_score`; `fever/store/tables.py` angepasst
  - `config/episodes.toml` (L-13, E-63): 13 Krisen des Berichts als Schlusskurs-Hoch bis -Tief des S&P 500 mit Quelle (1998 bis 2020: Yardeni, *Predicting the Markets*, Anhang 15.4; 2022, August 2024, April 2025: S&P Dow Jones Indices bzw. CNBC; 2026: Bericht Abschn. 3 und PBS, Sekundärquellen); nur Daten, keine Indexstände; Loader `crisis_episodes()` prüft Felder und Reihenfolge
  - Ansicht 7 (`/ansicht/visualisierung`) als statischer Rahmen, damit Schalter und Auswahl die Aktualisierung überstehen (Dash-`persistence`): Stress-Historie mit Krisenbalken oben (Hover nennt Krise und Daten) und Tabelle der Krisen mit Quellen; Regime-Zeitleiste der Ampel; Heatmap der Perzentile mit Schalter wöchentlich/ganze Historie (letzter Handelstag je Woche, nichts gemittelt) und täglich/2 Jahre (E-66), ungültige Werte bleiben leer; Perzentilbänder mit Auswahl des Indikators; Sparklines der letzten 12 Monate mit Wert, Perzentil, Stand und Abruf
  - Chart-Fabrik: `Band`, Krisenstreifen, `heatmap`, `regime`, `sparkline`; `PERCENTILE_RAMP` liegt jetzt in `figures.py`
- **Belege (Entwicklungsumgebung, 27.09.2026):**
  - `pytest -q`: 396 passed; neu: Bänder von Hand gerechnet (mit Fenster und Mindesthistorie), Bänder als Rohwerte bis in `IndicatorScore`; der Look-ahead-Pflichttest vergleicht ganze Zeilen und deckt die Bänder mit ab; Krisen-Konfiguration, Krisenstreifen, alle Teile der Ansicht 7, Wochen- und Tagesraster, leere Zellen, Bänder im Chart, Standard der neuen Chart-Arten, Rahmen mit `persistence`
  - Gegenprobe: Bänder aus dem ganzen Datensatz statt bis t → Look-ahead-Pflichttest und beide Handrechnungen rot
  - Migration: Probe an einer Backup-Kopie mit dem neu gebauten Image als 568:568 (0002 → 0003, `alembic current` 0003 (head)); Scoring danach 11,8 s statt 5,6 s, Werte unverändert (Stress 37,8, Fallhöhe 79,9, Ampel Grün, Konfidenz 90,0 %); alle gültigen Indikatoren haben Bänder
  - Build-Probe (Dockerfile unverändert; `config/episodes.toml` und die Migration sind im Image)
  - Browser (Chromium, 1440 px hell, 390 px dunkel): keine Konsolenfehler; Seitenaufruf 1,9 MB, Wechsel auf das Tagesraster 0,2 MB; der Schalter bleibt nach einer simulierten Aktualisierung auf „täglich“
- **Nicht geprüft:** TrueNAS; echte Geräte; Druck. Die Server-Zeit der Sparklines liegt bei rund 2 s, die der Ansicht Makro bei rund 3 s (gemessen, nicht optimiert; beschleunigt am 28.09.2026, Abschnitt „Ladezeiten der Seiten“).
- **Kleinere Schulden (behoben 28.09.2026 auf Anweisung):** Der Sofort-Abruf läuft nach einem unerwarteten Fehler einer Abrufgruppe weiter wie der Worker (Fehler im Datenstand, Exit-Code 1); `HEARTBEAT_MAX_AGE` steht in `fever/store/status.py`, das Web importiert den Worker nicht mehr; `estimated_release` wird nur noch aus `fever/release.py` importiert; Kopf von `requirements.txt` nennt linux/amd64. Offen bleibt als Schuld: Ansicht Makro rund 3 s, Sparklines rund 2 s Serverzeit (nicht optimiert, Nutzer 28.09.2026).
- **Technische Schuld (behoben 28.09.2026 auf Anweisung):** Eine neue Programmversion des Scorings löste keine Neuberechnung aus. Seitdem gehen `fever/config.py`, `fever/release.py`, `fever/score.py` und `fever/scoring/*.py` in den Fingerabdruck ein, der sonst `scoring.toml` und `series.toml` abdeckt (`score.config_hash`).

**Ergebnis M7a (26.09.2026, umgesetzt; auf TrueNAS ⏳): Bereiche und Einzelreihen (E-57 bis E-60)**
- **Umgesetzt:**
  - Übersicht: unter dem Verlauf von Stress und Fallhöhe die vier Bereiche als eigener, statischer Rahmen außerhalb des alle 5 Minuten ersetzten Inhalts, damit geöffnete Abschnitte offen bleiben. Kopf je Bereich: Bereichswert (Volatilität: Median und geglättet; Fallhöhe: ungeglättet und geglättet), Zahl der gültigen Indikatoren, Stand. Aufgeklappt: Verlauf des Bereichs und je Indikator eine Zeile mit Wert, Perzentil, Status und Stand; jede Zeile klappt einzeln auf zu Wert- und Perzentil-Chart und „So fließt der Wert in den Bereich ein“
  - `fever/web/pages/uebersicht.py`: Callbacks mit Mustern (`ALL` für die Kopfzeilen in einer Datenbankabfrage, `MATCH` für die Charts nur geöffneter Abschnitte); Auf- und Zuklappen im Browser (clientseitiger Callback setzt `hidden` und `aria-expanded` und löst ein `resize` aus, damit Plotly verdeckt gezeichnete Charts anpasst)
  - `fever/web/texts.py`: `contribution()` erzeugt die Schritte je Indikator aus der Konfiguration (Umrechnung, Perzentilfenster und Richtung, Mindesthistorie und Veraltung, Median im Bereich bzw. Mittel der Fallhöhe, Glättung, Stress, Diffusion, VIX/VIX3M-Regel, Konfidenzgewicht, Anzeigeperzentil); `views._role_today()` nennt den heutigen Anteil aus den gespeicherten Scores
  - 22 neue Texte (`fever/web/texts/`), dazu Erklärseiten aller 19 Indikatoren und der drei Blöcke; die Erklärseite eines Indikators enthält ebenfalls den Abschnitt „So fließt der Wert in den Bereich ein“
  - Hinweis unter jedem Verlauf (Übersicht, Bereiche, Erklärseiten): Je Beobachtung zählt der neueste Stand (Phase-1-Ausnahme aus `CLAUDE.md`, fehlte seit M6)
  - Startzeitraum (E-61): Charts der Bereiche und Einzelreihen zeigen zu Beginn die ganze Historie (`Chart.full_history`); geprüft im Browser: Bereich Kredit/Funding und EBP ab 1990 mit vier Rezessionsflächen
- **Korrigiert (Fehler seit M6):** „Historie ab“ im Steckbrief nahm bei Indikatoren aus mehreren Reihen das früheste Datum irgendeiner Reihe (VIX/VIX3M zeigte 1990, SOFR − IORB 2018). Jetzt `db.history_start()`: der erste Tag, an dem alle Reihen vorliegen (VIX/VIX3M 18.09.2009, SOFR − IORB 29.07.2021, VRP und Aktien-Anleihen-Korrelation 26.09.2016).
- **Belege (Entwicklungsumgebung, 26.09.2026):**
  - `pytest -q`: 375 passed; neu in `tests/test_web.py`: Startzeitraum (ganze Historie in den Bereichen, 5 Jahre auf den Erklärseiten), Rahmen mit genau den Indikatoren je Bereich (alle 19, alles zu Beginn geschlossen), Rahmen außerhalb des aktualisierten Inhalts und Callbacks registriert, Charts nur offen, Rezessionsflächen in Bereichs- und Indikator-Charts, Reihenfolge der Kopfzeilen, ohne Scores, Einflussschritte folgen der Konfiguration (geänderte Parameter ändern den Text), heutige Rolle, `history_start`, Erklärseite mit Einfluss, Hinweis zum neuesten Stand
  - Gegenprobe mit eingebauten Fehlern (`min` statt `max` in `history_start`, Bereich offen statt geschlossen, festes „10 Jahre“ im Text): jeweils ein Test rot
  - Browser (Chromium, 390 und 1440 px, hell und dunkel): Aufklappen von Bereich und Indikator, simulierte 5-Minuten-Aktualisierung (Abschnitte bleiben offen, 3 Charts bleiben), Zuklappen setzt `hidden`, Wiederaufklappen mit voller Chartbreite (328 bzw. 1218 px); keine Konsolenfehler. Datenmenge: Seitenaufruf 615 KB, Bereich Volatilität 536 KB, ein Indikator 447 KB
  - Scores unverändert (keine Änderung an Scoring, Schema, Dockerfile oder Compose)
- **Nicht geprüft:** TrueNAS; echte Geräte; der Druck geöffneter Bereiche (nur Bildschirmansicht geprüft).
- **Beobachtung:** Die Cboe-Datei des VIX3M beginnt am 18.09.2009; der Bericht nennt als Historienbeginn den 04.12.2007 (Abschn. 6.1). Folge: VIX/VIX3M hat zwei Jahre weniger Historie als im Bericht angenommen.

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

1. `pytest -q`, Build-Probe, Update auf TrueNAS nach `docs/einrichtung.md`.
2. Sichtprüfung aller Ansichten auf Smartphone und Desktop.
3. `docs/bedienung.md` und `docs/einrichtung.md` von ⏳ auf ✅, wo geprüft.
4. README-Status aktualisieren.

### M10 – Validierung (Bericht 4.3, Schritt 7; Ansicht 8 aus 6.3; E-89, E-93)

Plan vom 29.09.2026, vom Nutzer ohne Rückfrage freigegeben („Plan für M10 erstellen und ohne Freigabeaufforderung sofort ausführen“). Festlegungen, die der Bericht offenlässt, sind als eigene markiert (E-93) und stehen als Parameter in `config/scoring.toml`, `[validation]`.

**Ziel:** Prüfen, ob Ampel, Stress und Fallhöhe vergangene Einbrüche und VIX-Spitzen besser ankündigen als ein naiver VIX-Perzentil-Filter. Nur Auswertung: nichts davon wirkt auf die Scores zurück (`CLAUDE.md`: keine im Backtest optimierten Schwellen), und nichts ist eine Wahrscheinlichkeit für heute.

**Ereignisse** (Bericht 4.3, Schritt 7):
- (a) Rückgang des S&P 500 um mindestens 10 % vom laufenden Hoch, Beginn innerhalb der nächsten 63 Handelstage.
- (b) VIX-Schluss über 30 an einem der nächsten 21 Handelstage.
- (c) Bärenmarkt: Rückgang um mindestens 20 %, Beginn innerhalb der nächsten 63 Handelstage (Horizont eigene Festlegung; der Bericht nennt keinen).
- Rückgangsphasen mechanisch nach Lunde/Timmermann (2004) mit gleicher Schwelle in beide Richtungen: Eine Phase beginnt am Schlusskurs-Hoch, sobald der Kurs die Schwelle darunter schließt, und endet am Tief, sobald er von dort um dieselbe Schwelle steigt; das nächste Hoch zählt ab diesem Tief. Beginn = erster Handelstag nach dem Hoch. Kurse: `spx` (Cboe) ab 1975.
- Tage, deren Horizont über das Datenende oder in einen noch unbestätigten Rückgang reicht, bleiben ohne Ergebnis und fallen aus der Auswertung (Zensur am Ende).

**Signale:** Ampel mindestens Gelb, mindestens Orange und Rot (feste Regeln, nicht kalibriert); stetig Stress und Fallhöhe (geglättet), Ampelstufe und das VIX-Perzentil über 10 Jahre (gespeichert wie im Dashboard).

**Vergleiche:**
- VIX-Filter mit gleichem Alarmanteil je Ampelstufe, walk-forward: ab 2000 für jedes Jahr die Schwelle aus den Jahren davor, so dass der VIX-Filter dort so oft Alarm gab wie die Ampelstufe; ohne Ereignisse, also ohne Blick auf spätere Ergebnisse (Bericht: „ab 2000 jährlich neu kalibrieren, Schwellen nur mit Daten bis t“).
- VIX-Perzentil über der Markierung „erhöht“ (fest).
- „Immer Alarm“: die Basisrate (entspricht „immer investiert“ als Klassifikation).

**Metriken** (Auswertung ab 2000):
- AUC mit ROC-Kurve je stetigem Signal; Differenz Stress minus VIX-Perzentil mit Konfidenzintervall und Urteil (besser, nicht unterscheidbar, schlechter).
- Precision und Recall je Ampelstufe und VIX-Filter, Differenz der Precision Ampel minus VIX-Filter mit Konfidenzintervall.
- Ereignisse gewarnt (x von n) und Vorlauf je Ereignis: Handelstage vom ersten Alarm im Horizont vor dem Beginn bis zum Beginn; Vorlauf-Histogramm.
- Fehlalarme: Alarmphasen (Lücken bis 5 Handelstage zusammengefasst, eigene Festlegung) ohne Ereignis im Horizont, je Jahr und als Liste.
- Stabilität: AUC je Zeitraum (1993–1999 vor dem Walk-forward, 2000–2009, 2010–2019, ab 2020) und die jährlichen Schwellen des VIX-Filters. „Walk-forward-Stabilität der Gewichte“ entfällt: Die Blöcke sind gleich gewichtet, geschätzt wird nichts.
- Konfidenzintervalle per Block-Bootstrap (Bericht): Blöcke von 126 Handelstagen (doppelter Horizont), 1.000 Ziehungen, 90 %, fester Startwert (eigene Festlegungen).
- Entfällt in M10: Brier-Score (erst mit dem Logit in Phase 3) und der ökonomische Test mit Put-Absicherung (ThetaData, Phase 3; wäre zudem ein Handelssignal).

**Architektur:**
- `fever/validation.py`: reine Berechnung (numpy, pandas), importiert nichts aus `web/` oder `store/`.
- `fever/validate.py`: Lauf: Scores, VIX-Perzentil, S&P 500 und VIX aus der Datenbank lesen, rechnen, Bericht als JSON in der neuen Tabelle `validation_report` ersetzen (Migration 0004); Status unter „validation“ im Datenstand. Der Worker startet ihn nach dem Scoring, wenn neue Scores oder eine geänderte Validierung (Code oder `[validation]`) vorliegen; direkt mit `python -m fever.validate`.
- Oberfläche: Ansicht 8 „Validierung“ (`/ansicht/validierung`) mit Ereigniswahl, Kurzfazit, ROC-Kurve, Tabelle Precision/Recall, Vorlauf-Histogramm und Ereignisliste, Fehlalarm-Liste, Stabilität, Grenzen; Erklärseite „Validierung“.

**Risiken:** wenige unabhängige Ereignisse (weite Intervalle); überlappende Horizonte (deshalb Block-Bootstrap); Phase-1-Scores mit neuesten Vintages und geschätzten Veröffentlichungen, also nicht revisionsgenau; die Regeln des Berichts und die Entscheidungen E-80 bis E-91 entstanden mit Kenntnis dieser Historie, die Auswertung ist deshalb nicht streng out-of-sample; einige Sekunden mehr Worker-Laufzeit; Migration auf TrueNAS nötig.

**Tests:** Rückgangsphasen, Ereignisse und Zensur von Hand; AUC mit Gleichständen von Hand, gewichtete AUC gleich AUC auf wiederholten Tagen; Precision, Recall, Vorlauf und Fehlalarme von Hand; Walk-forward-Schwelle eines Jahres unverändert ohne spätere Daten; Bootstrap reproduzierbar; Migration und Tabellendefinition; Lauf speichert den Bericht, Worker startet ihn nur bei Bedarf; Ansicht mit und ohne Bericht, jede Figur gültig.

**Schritte:** Plan (dieser Abschnitt) → Parameter und Prüfung → Berechnung mit Tests → Migration, Speicher, Lauf, Worker → Oberfläche und Texte → Lauf auf `data-dev/`, Browser → Ergebnisse, Doku, Commit, Push.

**Umsetzung (29.09.2026):**
- `config/scoring.toml`, `[validation]`: elf Parameter, geprüft in `fever/config.py` (`validation_config`: Prozente unter 100, Jahreszahl, ganze Zahlen). Wie jede Änderung an `scoring.toml` oder `fever/config.py` löst das Update einen Scoring-Lauf aus, danach die Validierung; die Scores bleiben gleich (geprüft an einer Kopie von `data-dev/`: alle 9.281 Tage und 296.992 Indikatorwerte mit altem und neuem Stand identisch).
- `fever/validation.py` (reine Berechnung), `fever/validate.py` (Lauf, `python -m fever.validate`), `fever/store/validation.py`, Migration 0004 (`validation_report`, eine Zeile mit dem Bericht als JSON). Der Worker startet die Validierung nach dem Scoring, wenn die Scores neuer sind als der Bericht oder sich Code bzw. `scoring.toml` geändert haben (Fingerabdruck); Fehler stehen unter „validation“ im Datenstand. Laufzeit 2,6 s in der Entwicklungsumgebung.
- Ansicht 8 `/ansicht/validierung` (`fever/web/validation_view.py`): statischer Rahmen mit Ereigniswahl (`persistence`), Inhalt per Callback; Kurzfazit, Trennschärfe (ROC-Kurven, AUC mit Intervall), Treffer und Fehlalarme, Vorlauf-Histogramm (verpasst, drei Klassen, „≥ Horizont“) mit Ereignisliste, Fehlalarm-Listen, Stabilität je Zeitraum mit den Schwellen des VIX-Filters je Jahr, Grenzen. Der Bericht wird bei jedem Aufruf gelesen (klein, kein Lesepuffer: er entsteht Sekunden nach dem Scoring, ohne dass sich der Datenstand ändert). Fabriken `figures.roc` und `figures.bars`; Erklärseite `validation`.
- Tests: `tests/test_validation.py` (13) und in `tests/test_web.py` (6): Rückgänge genau auf der Schwelle, laufender Rückgang, Zensur am Ende, VIX-Ereignisse, AUC mit Gleichständen und Gewichten, ROC, Precision/Recall, Vorlauf, Alarmphasen, Bootstrap reproduzierbar, Walk-forward ohne spätere Jahre, Zeiträume nur mit Ereignis, konstruierte Historie mit bekanntem Ergebnis, Parameterprüfung, Lauf und Worker, Ansicht mit und ohne Bericht, ohne S&P-500-Kurse, jede Figur gültig.
- Migrationsprobe (Entwicklungsumgebung, 29.09.2026, gebautes Image als 568:568 auf einer Kopie mit Stand 0003): `fever.validate` vorher „Migration fehlt: Datenbank auf 0003, Programm erwartet 0004“; `fever.backup`, `alembic upgrade head` („Running upgrade 0003 -> 0004“), `alembic current` „0004 (head)“, `fever.score` 24 s, `fever.validate` 0,8 s. Ohne Reihe `spx` (vor ihrem ersten Abruf) meldet die Validierung für Rückgänge und Bärenmärkte „keine auswertbaren Tage“.
- Browser (Entwicklungsumgebung, 390 px hell und 1280 px dunkel): alle drei Ereignisse ohne Konsolenfehler, kein waagrechtes Scrollen; Legenden der Charts in eigenen Zeilen unter dem Titel, Achsentitel über den Datierungszeilen.

**Ergebnisse** (Entwicklungsdatenbank, Scores vom 29.09.2026, S&P 500 ab 02.01.1975 bis 28.09.2026, VIX bis 25.09.2026; Auswertung ab 03.01.2000; Intervalle 90 %; Momentaufnahme, die Ansicht zeigt den jeweils aktuellen Stand):

| Ereignis | Tage (mit Ereignis) | Ereignisse seit 1975 (mit ganzem Vorlauf ab 2000) | AUC Stress | AUC VIX-Perzentil | Unterschied | Urteil |
|---|---|---|---|---|---|---|
| Rückgang ab 10 %, Beginn in 63 Tagen | 6.630 bis 13.05.2026 (21 %) | 41 (22) | 0,67 (0,56–0,76) | 0,64 (0,54–0,73) | +0,03 (−0,05 bis +0,10) | nicht unterscheidbar |
| VIX über 30 in 21 Tagen | 6.736 bis 27.08.2026 (21 %) | 35 (29) | 0,81 (0,75–0,87) | 0,90 (0,86–0,93) | −0,08 (−0,13 bis −0,05) | schlechter |
| Bärenmarkt ab 20 %, Beginn in 63 Tagen | 6.630 bis 13.05.2026 (6 %) | 8 (5) | 0,60 (0,35–0,81) | 0,71 (0,54–0,85) | −0,12 (−0,26 bis −0,01) | schlechter |

AUC der übrigen Signale: Ampelstufe 0,68 / 0,80 / 0,65, Fallhöhe 0,55 / 0,41 / 0,56 (Rückgang / VIX / Bärenmarkt). Die Fallhöhe misst die mögliche Tiefe, nicht den Zeitpunkt; vor VIX-Spitzen war sie eher niedrig.

Precision je Stufe gegen den VIX-Filter mit dem Alarmanteil der Stufe (Prozent; Unterschied in Prozentpunkten mit Intervall):

| Stufe | Alarm an: Ampel / VIX-Filter | Rückgang | VIX über 30 | Bärenmarkt |
|---|---|---|---|---|
| mindestens Gelb | 44 / 47 % | 33 / 27: +6 (+3 bis +12), besser | 40 / 40: −1 (−5 bis +5), nicht unterscheidbar | 9 / 9: −1 (−1 bis +2), nicht unterscheidbar |
| mindestens Orange | 22 / 15 % | 40 / 34: +7 (−5 bis +16), nicht unterscheidbar | 53 / 81: −28 (−39 bis −17), schlechter | 12 / 10: +2 (−5 bis +6), nicht unterscheidbar |
| Rot | 12 / 8 % | 34 / 43: −9 (−24 bis +2), nicht unterscheidbar | 64 / 93: −29 (−41 bis −18), schlechter | 14 / 17: −3 (−12 bis +4), nicht unterscheidbar |

- Rückgänge (22 mit ganzem Vorlauf): gewarnt Gelb 19, Orange 14, Rot 14 (VIX-Filter 20, 14, 11); Vorlauf im Median 63, 63 und 50 Handelstage, das heißt meist war der Alarm schon zu Beginn des Vorlaufs an; Fehlalarm-Phasen je Jahr Ampel 0,9 / 0,9 / 1,0 gegen VIX-Filter 2,3 / 1,3 / 0,9. Von Gelb verpasst: die Rückgänge ab den Hochs vom 29.04.2011, 21.05.2015 und 19.02.2020 (Covid); VIX-Spitzen ab 04.08.2011 und 24.08.2015.
- Stabilität (AUC Stress / VIX-Perzentil, Rückgang): 1993–1999 0,66 / 0,82; 2000–2009 0,83 / 0,80; 2010–2019 0,43 / 0,43; 2020–2026 0,50 / 0,48. VIX über 30: 0,87 / 0,93; 0,85 / 0,92; 0,80 / 0,81; 0,65 / 0,87. Bärenmarkt: 2000–2009 0,69 / 0,78; 2020–2026 0,10 / 0,41 (Covid 2020 und 2022 aus ruhiger Lage).
- Schwellen des VIX-Filters (Perzentil): 2000 Gelb 44,7, Orange und Rot 99,2 (bis dahin kaum Orange); 2026 Gelb 55,1, Orange 86,0, Rot 92,0.
- Einordnung: Nach dem Maßstab des Berichts („Schlägt der Composite den naiven VIX-Filter nicht, ist er Ballast“) schlägt die Ampel den VIX-Filter in dieser Stichprobe nur bei der Precision von Gelb vor Rückgängen belastbar; vor VIX-Spitzen ist der VIX-Filter belastbar besser (erwartbar, er misst dieselbe Größe), bei Rückgängen und Bärenmärkten ist der Rest nicht unterscheidbar oder schlechter. Die Trennschärfe hängt stark am Jahrzehnt 2000–2009; seit 2010 liegen beide Signale vor Rückgängen nahe am Zufall. Nichts davon ändert Scores oder Parameter (`CLAUDE.md`); was daraus folgt (etwa Aggregation Stufe 2 in Phase 2 nur mit besserem Ergebnis hier, E-89), entscheidet der Nutzer.

### O-1: Recherche Ausweichquellen (28.09.2026, 10:36–11:30 UTC)

Anlass: Der Block „Breite“ und die Top-10-Konzentration haben keine Datenquelle. Geprüft: Indexanbieter, ETF-Emittenten, Kurs-APIs. Datenstand der FRED-Reihen: letzte Beobachtung 25.09.2026.

| Route | Befund | Ergebnis |
|---|---|---|
| MSCI (End-of-Day-Suche) | Terms of Use (Stand 15.07.2026) verbieten „unauthorized bots, scrapers … or any other unauthorized automated means“ und „populate a database with“ MSCI-Material | verworfen |
| FTSE Russell (LSEG) | Website-Bedingungen: Speichern nur „temporarily“; „You agree not to use … any bot, script, automation software …“, auch bei persönlicher Nutzung; Indexdaten sonst per Abo | verworfen |
| S&P DJI | lizenzpflichtig (`CLAUDE.md`), nicht weiter geprüft | verworfen |
| Nasdaq-Indizes über FRED | täglich, per CSV-Abruf geprüft; Status „Copyrighted: Pre-Approval Required“ wie `SP500` und `BAMLH0A0HYM2` (private Nutzung ohne Genehmigung) | gewählt (E-68) |
| ETF-NAV-Dateien von SSGA (xlsx ohne Login) | SPY, XLY, XLP, XLK, XLI, XLU ab 01.12.2003, KBE ab 15.11.2005, XSD ab 03.02.2006, KRE ab 19.06.2006, SPSM ab 08.07.2013; kein RSP, IWM, SMH. Bedingungen erlauben Kopien nur als „print-outs for your own personal use“; `openpyxl` oder eigener Parser nötig | verworfen (rechtlich unklar) |
| iShares | Download-Adresse lieferte HTML statt Datei | nicht verfolgt |
| Tiingo | Starter (0 USD): kein dauerhaftes Speichern („only transiently in volatile memory“); Power 30 USD/Monat erlaubt Speichern, nach Kündigung Löschpflicht einschließlich Backups (ToS vom 05.08.2026) | verworfen |
| IBKR | historische Daten über die API nur mit Level-1-Echtzeitabo und laufendem Gateway mit Login | Phase 3 |

Ersatzreihen auf FRED (Beginn der Reihe):

| Bericht 6.3 | Reihen | ab | Anmerkung |
|---|---|---|---|
| RSP/SPY | `NASDAQNQUS500LCE` / `NASDAQNQUS500LC` | 22.06.2017 / 11.01.2016 | 2.328 gemeinsame Tage; Verhältnis 0,79 (22.06.2017), 0,65 (31.12.2024), 0,60 (25.09.2026) |
| Small/Large | `NASDAQNQUSS` / `NASDAQNQUSL` | 16.05.2011 | Total-Return-Varianten `…ST`/`…LT` ab 17.05.2011 |
| SMH relativ | `NASDAQSOX` / `NASDAQNQUSB` | 02.09.2004 / 16.05.2011 | PHLX Semiconductor statt des SMH-Index |
| KRE | `NASDAQABAQ` / `NASDAQNQUSB` | 02.06.2008 / 16.05.2011 | ABA Community Bank |
| XLY/XLP | `NASDAQNQUSB40` / `NASDAQNQUSB45` | 22.09.2020 | ICB-Umstellung 2020; länger: Retail `NASDAQNQUSB4040` / Food, Beverage and Tobacco `NASDAQNQUSB4510` ab 23.05.2011 |

Ohne freie, regelkonforme Quelle (entschieden: Top-10 aus N-PORT, E-71; 50/200-Tage-Linie entfällt, E-72):
- **Top-10-Konzentration:** SEC EDGAR, Form N-PORT des SPDR S&P 500 ETF Trust (CIK 884394): quartalsweise, öffentlich rund 60 Tage nach Quartalsende, ab Stichtag 30.09.2019, alle Positionen mit Anteil (`pctVal`). Probe: Top-10-Positionen 21,59 % (30.09.2019), 36,42 % (30.06.2026); Alphabet steht mit zwei Aktiengattungen darin. SEC: „Information presented on sec.gov is considered public information and may be copied or further distributed … without the SEC's permission“; höchstens 10 Anfragen je Sekunde mit erklärtem User-Agent. SEC ist keine der Phase-1-Quellen in `CLAUDE.md`.
- **Anteil über der 50/200-Tage-Linie:** braucht Tageskurse aller Mitglieder mit historischen Mitgliederlisten. Frei und speicherbar nicht gefunden. Kostenpflichtig: EODHD „Fundamentals Data Feed“ 59,99 USD/Monat (Mitglieder ab April 2012; Speicherbedingungen nicht geprüft), Sharadar über Nasdaq Data Link (Mitglieder ab 1957, Kurse ab 1998; Preis erst nach Anmeldung sichtbar; Löschpflicht 30 Tage nach Ende), Norgate nur unter Windows. Mitglieder quartalsweise auch aus N-PORT, dann fehlen nur die Kurse.

**Umsetzung (28.09.2026, Freigabe des Nutzers am selben Tag):**
- Katalog: 9 Nasdaq-Reihen über FRED (Verzug 1 Tag, `release_time` 06:00: FRED aktualisiert sie gegen 23:45 New York am Beobachtungstag, `last_updated` aller neun geprüft) und `sec_spy_top10` (Quelle `sec`, quartalsweise, Verzug 62 Tage, `release_time` 18:00); 71 Reihen in 43 Abrufgruppen. Indikatoren: fünf im Block Breite (`relative_change`, Fenster 63 in `scoring.toml`, Orientierung „low“), `top10_concentration` in der Fallhöhe; 25 Indikatoren.
- `fever/sources/sec.py`: Einreichungsliste (`data.sec.gov`), je Stichtag die neueste Meldung (auch NPORT-P/A), XML aus dem Ordner der Meldung. Die Liste nennt als Dokument die gerenderte Ansicht `xslFormNPORT-P_X01/primary_doc.xml`; das XML liegt unter `primary_doc.xml` (geprüft). Nur Stammaktien (`assetCat` EC, `payoffProfile` Long), Aktiengattungen über den LEI zusammengefasst, ohne LEI über den Namen. Unter 100 Aktienpositionen ist ein Formatfehler. Nach dem Erstabruf wird je Abruf die Liste und die neueste Meldung gelesen (rund 450 KB).
- HTTP-Client: `data.sec.gov` und `www.sec.gov` mit 0,2 s Abstand; `get(..., user_agent=...)` für den SEC-Kontakt aus `FEVER_SEC_CONTACT` (Compose, optional).
- Probeabruf 28.09.2026 (Entwicklungsumgebung): 28 Stichtage von 30.09.2019 bis 30.06.2026, Top-10 je Emittent 22,8 % bis 40,7 % (30.06.2026: 37,9 %; je Wertpapierzeile wären es 36,4 %), Bündel 13,1 MB, 10 s.
- **Wirkung auf die Scores** (Entwicklungsdatenbank, gleicher Datenstand, 25.09.2026; Shiller ohne den Abruf vom 28.09.): Stress 37,8 → 42,8, Fallhöhe 79,9 → 80,6, Ampel Grün → **Gelb** (Fallhöhe über der Gelb-Schwelle), Konfidenz 90,0 → 92,3 %, Diffusion 20 → 30 %. Block Breite 95,3; Perzentile: gleich/kapital 95, klein/groß 96, Halbleiter 98, Regionalbanken 68, Zykliker 67, Top-10 80. Rückwirkend haben 267 von 9281 Tagen eine andere Ampel.
- **Befund zu den Krisen** (Einschätzung, keine Parameteränderung): Vor Feb. 2018, Q4 2018, März 2020 und Apr. 2025 stand der Block Breite schon zu Beginn der Episode hoch (78–90) und hob den Stress. Im Zinsjahr 2022 und in der Episode 2026 lag er niedrig (Tief 12.10.2022: 17), weil die großen Werte stärker fielen als die gleichgewichteten; der Stress-Composite sinkt dadurch, die Tage mit Orange oder Rot in 2022 gehen von 113 auf 3 zurück (Höchststand Stress 84,4 → 79,0). Das ist die Folge der gleich gewichteten Blöcke nach Bericht 4.3, kein Rechenfehler.
- Tests: 421 grün; SEC-Parser mit gekürzten echten Meldungen, `relative_change` von Hand gerechnet, Look-ahead-Pflichttest um `breadth_equal_weight` und `top10_concentration` erweitert.
- Sichtprüfung im Browser (Entwicklungsdatenbank): Ansicht Breite mit 10 Charts, Fallhöhe mit 5, keine Seitenfehler; `/health`, `/_dash-layout`, Erklärseiten 200.

### Ladezeiten der Seiten (28.09.2026, E-77, E-78)

Anlass: Nutzer, „Seiten laden sehr lange“. Gemessen in der Entwicklungsumgebung mit echten Daten (`data-dev/`, 72 Reihen, Scoring 9281 Tage, 294 230 Beobachtungen, 250 587 Indikator-Scores); TrueNAS rechnete das Scoring am 26.09.2026 etwa 15 % langsamer, die Werte sind also übertragbar. Methode: Abschnitt 10, Punkt 10.

**Ursachen** (Profil der Ansicht Makro, 5,4 s Server-Zeit):
- rund 75 %: `plotly.graph_objects` prüft und kopiert jede Figur, dazu die JSON-Umwandlung von rund 185 000 Datumsobjekten;
- die Konfiguration wurde je Seite rund 70-mal neu eingelesen (`series.toml`, 1183 Zeilen);
- Datenbank: Historien mit allen Spalten und Zeitstempeln, 20 ganze Reihen für die letzten Werte der Termstruktur, die Heatmap las alle 250 587 Scores;
- 4 gunicorn-Threads: parallele Callbacks bremsten sich über den GIL gegenseitig aus (E-77);
- 4,2 MB JSON je Aufruf der Ansicht Makro, ungepackt.

**Maßnahmen** (ohne neue Abhängigkeit, ohne Migration):
1. `fever/web/figures.py` baut einfache Dicts im plotly.js-Format; die Tests prüfen jede Figur mit `go.Figure`, und die Charts aller Seiten sind im Screenshot-Vergleich (hell/dunkel, 1280/390 px, 5 Seiten) pixelgleich mit vorher; Unterschiede nur in Uhrzeit- und Altersangaben.
2. `fever/config.py` baut die Kataloge einmal je Dateiinhalt (liest die Datei weiter bei jedem Aufruf, sieht also jede Änderung).
3. Schlanke Abfragen in `fever/web/db.py`: nur benötigte Spalten, `latest_pairs` ohne Zeitstempel, letzte Werte per `LIMIT 1`, Heatmap nur für die gezeigten Tage, Sparklines in einer Abfrage.
4. gunicorn mit einem Thread (E-77, `compose.dockge.yaml`).
5. gzip (Stufe 1) für JSON-Antworten ab 2 KB: Makro 4,2 → 1,0 MB, 32 ms.
6. Lesepuffer je Datenstand für die langen Lesezugriffe (E-78, `per_data_version`).

Scores unverändert: nach der Änderung an `fever/config.py` neu gerechnet, alle 9281 Tage und alle 250 587 Indikatorzeilen identisch (die Programmversion des Scorings ändert sich, der Worker rechnet auf TrueNAS nach dem Update einmal neu).

**Server-Zeit je Seite** (Aufbau plus JSON; nachher: erster Aufruf nach neuen Daten / erneuter Aufruf aus dem Puffer):

| Seite | vorher | nachher |
|---|---|---|
| Übersicht | 0,05 s | 0,06 / 0,004 s |
| Signale | 2,69 s | 0,64 / 0,08 s |
| Breite | 2,31 s | 0,55 / 0,09 s |
| Positionierung | 0,93 s | 0,29 / 0,04 s |
| Makro | 5,36 s | 1,15 / 0,21 s |
| Fallhöhe | 1,11 s | 0,38 / 0,05 s |
| Visualisierung (5 Callbacks) | 5,77 s | 0,55 / 0,10 s |
| Kennzahl VIX | 0,61 s | 0,10 / 0,03 s |
| Erklärungen | 0,35 s | 0,004 s |

**Im Browser** (Chromium, 1280 px, bis jeder Chart gezeichnet ist; enthält rund 0,5 s Warten auf Netzruhe):

| Seite | neuer Tab vorher | neuer Tab nachher | Klick in der Navigation vorher | nachher |
|---|---|---|---|---|
| Übersicht | 1,9 s | 1,4 s | 5,0 s | 0,3 s |
| Signale | 4,6 s | 1,7 s | 11,5 s | 0,7 s |
| Breite | 3,9 s | 1,8 s | 11,6 s | 0,6 s |
| Makro | 7,6 s | 2,4 s | 7,2–33,7 s | 1,3 s (erster Aufruf 2,3 s) |
| Visualisierung | 14,0 s | 2,2 s | 39,0 s | 1,5 s |
| Kennzahl VIX | 2,0 s | 1,6 s | – | – |

Die Navigationszeiten vorher schwanken stark, weil sich die Callbacks mehrerer Seiten über den GIL gegenseitig aufhielten. Smartphone-Näherung (CPU 4-fach gedrosselt, Navigation nachher): Makro 3,9–4,2 s (erster Aufruf 8,9 s), Signale 2,2 s, Visualisierung 4,4 s. Speicher des Web-Prozesses mit allen Ansichten im Puffer rund 230 MB (ohne Puffer rund 170 MB).

**Nicht umgesetzt** (gemessenes Potenzial, bei Bedarf einzeln entscheiden):
- Index auf `indicator_score (indicator_id, score_date)`: je Indikator 38 → 18 ms, Makro beim ersten Aufruf rund 0,2 s schneller; braucht Migration 0004.
- Eine Abfrage je Ansicht für alle Indikatoren: Makro beim ersten Aufruf rund 0,3 s schneller; Umbau der Ansichten.
- Zeichnen im Browser (Makro: 17 Charts mit je rund 9000 Punkten, rund 1,4 s, dazu 0,4 s für plotly.js beim ersten Chart): nur mit Änderungen an der Oberfläche zu verkürzen, etwa Charts erst beim Scrollen zeichnen (dann fehlen sie im Druck).
- Datum als Millisekunden statt ISO-Text: kein messbarer Gewinn.

### SEC-Kontakt im Container (28.09.2026)

Befund (Nutzer): `FEVER_SEC_CONTACT` steht in der `.env` des Dockge-Stacks und im Projektordner, trotzdem meldete der Sofort-Abruf um 18:48 MESZ „FEVER_SEC_CONTACT fehlt oder enthält keine E-Mail-Adresse“. Der Worker-Container sah also keinen gültigen Wert. Wahrscheinlichste Ursache: Die `compose.yaml` in Dockge ist noch die alte Kopie ohne die Worker-Zeile `FEVER_SEC_CONTACT: ${FEVER_SEC_CONTACT:-}` (E-32: Kopie von Hand), oder der Stack wurde nach der Änderung nur neu gestartet statt neu bereitgestellt; die `.env` im Projektordner liest der Stack nicht. Umsetzung: Die Meldung unterscheidet jetzt „kommt nicht im Container an“ (Zeile fehlt in `compose.yaml`), „im Container leer“ (Wert fehlt in der `.env` des Stacks) und „keine E-Mail-Adresse“, ohne den Wert zu nennen; der Worker warnt schon beim Start im Log; Prüfbefehl und Schritte in `docs/einrichtung.md`, Abschnitte 9 und 11. Geprüft im gebauten Image (alle drei Fälle und gesetzter Kontakt) und im Stack aus `compose.dockge.yaml`; auf TrueNAS ⏳.

### Entscheidungsrunde 29.09.2026 (E-80 bis E-92)

Anlass (Nutzer, 28./29.09.2026): Sahm-Regel als Rezessionssignal mit Vorwarnung, sichtbare Rolle je Wert, kürzere Mindesthistorie, Zinskurve prüfen, investiertes und investierbares Geld, alle Berechnungen gegen die Forschung prüfen, y-Achse beim Zoomen. Recherche und elf Auswahlfragen mit Belegen (Entscheidungsseite im Chat, 29.09.2026), Antworten F1 bis F11, HY-OAS-Nachfrage und Begrenzung der Sahm-Regel, FRED SP500: Abschnitt 2, E-80 bis E-92.

**Umsetzung:**
- Quellen: `spx` (Cboe), `iursa` (FRED, wöchentlich), sieben Z.1-Reihen für die Aktienquote und `mmmffaq027s` (Geldmarktfonds), alle über die bestehenden Parser. Verzug geprüft an den Erstveröffentlichungen in ALFRED (29.09.2026): IURSA 12 Tage bei 230 von 246 Wochen, Z.1 158 bis 169 Tage, einmal 192 (Shutdown 2025), also wie Margin Debt 175. Erstabruf in `data-dev/`: 13.043, 2.907 und je 305 Zeilen, keine verworfen. FRED `SP500` verlässt den Katalog (E-92); ihre gespeicherten Werte bleiben.
- Scoring: Transformationen `sos`, `equity_share` und `trend_gap`, Block `rule` für Indikatoren, die nur eine Ampelregel liest (`config.RULE_ONLY`), Regeln `yellow_sahm` und `orange_sahm_trend` (Sahm ≥ Schwelle, Orange nur mit S&P 500 unter der 200-Tage-Linie, E-91) und `yellow_sos` (Wert > Schwelle), alle ohne Hysterese und nur mit gültigem Wert (nicht veraltet, Mindesthistorie erfüllt). Indikatoren `sos`, `spx_trend`, `credit_spread_tight`, `equity_allocation`, `hy_oas`; VRP und Korrelation auf `spx`.
- Oberfläche: Rollen-Marken (`texts.roles`), Heatmap mit Quadraten und Rolle im Hover, Sahm, S&P-500-Trend und SOS mit violetten Flächen für die Tage aktiver Regel (aus den gespeicherten Ampelregeln), Hinweis auf das letzte Re-Steepening, Geldmarktfonds als Anzeige, y-Achse (`figures.fitted_range`, `assets/autoscale.js`).
- Tests: Pflichttests für die neuen Regeln genau auf der Schwelle und ohne Hysterese, Look-ahead-Test mit allen neuen Indikatoren (alle drei Wertregeln lösen dort aus), Rundung gegen Rechenrauschen, SOS, Trend und Aktienquote von Hand, Rollen, Re-Steepening, y-Bereich. 465 Tests grün.
- Browser (Entwicklungsumgebung, 29.09.2026, 1280 px hell und 390 px dunkel): alle Ansichten und neuen Erklärseiten ohne Fehler; beim Laden kein zusätzliches Neuzeichnen (Server- und Browserrechnung stimmen überein); nach „1 J“, „6 M“, „5 J“, „Max“, waagrechtem Zoom, Doppelklick und `Plotly.react` (wie die Aktualisierung) liegt der sichtbare Bereich mit höchstens 5 % Rand in der y-Achse; Perzentil-Charts bleiben bei 0–100.

**Vorher/Nachher der Ampel** (Entwicklungsdatenbank, 9.281 Handelstage 02.01.1990 bis 25.09.2026; vorher = Scores vom 28.09.2026; nachher = Stand mit E-91):

| Stufe | Tage vorher | Tage nachher (E-80, Sahm → Orange) | Tage nachher (mit E-91) |
|---|---|---|---|
| Grün | 5.835 | 4.635 | 4.635 |
| Gelb | 1.778 | 2.114 | 3.068 |
| Orange | 614 | 1.659 | 705 |
| Rot | 1.054 | 873 | 873 |

- Sahm-Regel nach E-80 (Orange, solange ≥ 0,5): 10.12.1990–06.01.1993, 09.07.2001–06.12.2002, 08.05.2008–07.07.2010, 08.05.2020–07.05.2021 und 07.08.2024–06.11.2024 (ohne Rezession); Orange bis weit in die Erholung (Tage mindestens Orange 1991 2 → 252, 1992 3 → 254, 2021 0 → 87). Deshalb begrenzt (E-91). Varianten, gezählt als Tage, an denen allein die Sahm-Regel Orange auslöst: unverändert 1.216; Orange 12 Monate, dann Gelb 725 (2020–21 und 2024 bleiben Orange); 6 Monate 349 (2001–02 nur einen Monat); nur im Abwärtstrend 262 (gewählt).
- Mit E-91 Orange über die Sahm-Regel: 10.12.1990–23.01.1991, 09.07.2001–06.12.2002 (mit kurzen Unterbrechungen), 08.05.2008–29.05.2009, 20.05.–07.07.2010, 08.–26.05.2020, dazu einzelne Tage 1991, 1992, 2009 und 2020 an der 200-Tage-Linie; sonst Gelb, 07.08.–06.11.2024 nur Gelb. Tage mindestens Orange je Jahr gegenüber vorher: 1991 2 → 35, 1992 3 → 14, 2002 168 → 234, 2009 162 → 146, 2010 20 → 33, 2020 92 → 87, 2021 0 → 0.
- SOS mindestens Gelb: 13.09.1990–15.04.1992, 05.04.2001–24.12.2002, 24.04.2008–28.04.2010, 09.04.2020–12.05.2021; kein Signal ohne Rezession, jeweils zwei Wochen bis gut drei Monate vor der Sahm-Regel.
- Weniger Orange 1998 (89 → 43), 1999 (94 → 0) und 2003 (77 → 0): VRP und Aktien-Anleihen-Korrelation zählen jetzt ab 1990 (E-83); Beispiel 15.10.1999: Block Volatilität 93,6 → 58,4 (VIX 93,6 und VRP 23,1).
- Fallhöhe-Gelb 2000 252 → 0 Tage (mittlere Fallhöhe 89,6 → 73,3), 1998 234 → 184: Die Baa-Spreads waren 1998 bis 2000 schon weit, die umgedrehte Komponente (E-85) senkt die Fallhöhe dieser Jahre. Mehr Fallhöhe-Gelb 2017 (0 → 120), 2018 (66 → 177), 2022 (0 → 131), 2025 (0 → 141) und 2026 (9 → 190).
- Heute (25.09.2026) unverändert Gelb über die Fallhöhe: Fallhöhe 80,6 → 84,8, Stress 36,6 → 36,8; Aktienquote 56,4 % (Perzentil 99), Kreditspread-Enge Perzentil 99,8, SOS −0,004, Sahm −0,07.
- Scoring-Lauf 22 s in der Entwicklungsumgebung (32 Indikatoren).

Die Nebenwirkung Sahm-Orange in Erholungen hat der Nutzer mit E-91 begrenzt; die Variante stützt sich auf eine veröffentlichte Regel (Livermore 2016) und wurde nicht an diesen Daten optimiert, die Auswertung oben ist aber dieselbe Stichprobe. Die Fallhöhe 2000 bleibt (Nutzer 29.09.2026: Begrenzung der Sahm-Regel statt Entfernen der Kreditspread-Enge). Ob die Regeln die Ampel verbessern, prüft M10 (E-89).

---

## 5. Fachliche Lücken (vor dem betroffenen Meilenstein per Auswahlfrage klären)

Nichts davon wird geraten. Die Vorschläge sind begründete Startpunkte, keine Entscheidungen.

| Nr. | Lücke | Betrifft | Vorschlag mit Begründung | Klären vor |
|---|---|---|---|---|
| L-1 | Perzentil bei Gleichständen; gehört xₜ zur Referenzmenge? | jeder Score | **Entschieden 26.09.2026 (E-47):** wie vorgeschlagen. Mittelrang: p = 100 · (Anzahl kleiner + ½ · Anzahl gleich) / n, Referenz = alle gültigen Werte im Fenster bis einschließlich t. Symmetrisch; Reihen mit vielen gleichen Werten (Sahm-Regel, SOFR−IORB) werden nicht systematisch verschoben | – |
| L-2 | Fenster für Reihen mit 5–10 Jahren Historie | jeder Score | **Entschieden 26.09.2026 (E-47):** wie vorgeschlagen. Rollierend höchstens 10 Jahre; solange weniger vorhanden ist (aber ≥ Mindesthistorie), alle vorhandenen Werte. Passt zu „expandierend mit mindestens 5 Jahren“ (Bericht 4.3) | – |
| L-3 | Worauf beziehen sich die Ampelschwellen („Stress-Composite ≥ 90. Perzentil“, „Fallhöhe ≥ 80“): auf den Wert selbst (Mittel der Blockperzentile, 0–100) oder auf einen erneut perzentilierten Composite? | Ampel | **Entschieden 26.09.2026 (E-47):** wie vorgeschlagen. Auf den Wert selbst. Der CISS aggregiert ebenfalls ohne zweites Ranking. Ein neu gerankter Composite läge per Konstruktion an rund 10 % aller Tage ≥ 90, auch in ruhigen Jahrzehnten. Folge: Rot über den Composite nur bei breitem Stress, schnelle Schocks fangen die Einzelregeln | – |
| L-4 | Composite, wenn Blöcke fehlen. In Phase 1 fehlt „Breite“ dauerhaft (O-1) | Stress, Ampel | **Entschieden 26.09.2026 (E-47):** wie vorgeschlagen. Mittel der vorhandenen Blöcke, mindestens 3 von 5, sonst kein Composite (sichtbar). Fehlende Blöcke werden in der Übersicht benannt und senken die Konfidenz | – |
| L-5 | Toleranz je Frequenz (ab wann „veraltet“) | Veraltung, Score | **Entschieden (E-10):** Toleranz 3 / 3 / 10 Kalendertage zusätzlich zur Frequenz, also veraltet nach 4 / 10 / 41 Tagen. Der ursprüngliche Vorschlag „täglich 4, wöchentlich 3, monatlich 10“ mischte Gesamtwert und Toleranz; die Entscheidungsfrage nannte die Gesamtwerte ausdrücklich | – |
| L-6 | Konfidenz „gewichtet mit dem historischen Vorlauf“: welche Gewichte? | Konfidenz | **Entschieden 26.09.2026 (E-48):** wie vorgeschlagen. V-Score aus Bericht Tabelle 2 (1–5) als Gewicht. Konfidenz = Summe der Gewichte aktueller, gültiger Indikatoren / Summe der Gewichte aller scorerelevanten Indikatoren. Tabelle 2 ist die einzige vorhandene Vorlaufbewertung; die Werte sind Einschätzungen und in `series.toml` sichtbar | – |
| L-7 | Hysterese für Regeln ohne Perzentilskala (VIX/VIX3M > 1 an 3 Tagen, Diffusionsindex ≥ 40 %) | Ampel | **Entschieden 26.09.2026 (E-48):** wie vorgeschlagen. VIX/VIX3M: Die Regel endet, wenn das Verhältnis an 3 Tagen in Folge < 1 liegt (spiegelbildlich). Diffusionsindex: 5 Prozentpunkte unter der Schwelle, analog zur Perzentil-Hysterese | – |
| L-8 | Glättung: welcher Block ist „schnell“, in welcher Reihenfolge wird geglättet, nutzt die Ampel geglättete Werte? | Stress, Ampel | **Entschieden 26.09.2026 (E-48):** wie vorgeschlagen. Schnell = Volatilität/Optionen (HWZ 3 auf den Blockscore). Composite HWZ 10. Die Ampel nutzt den geglätteten Composite, die Einzelregeln (VIX/VIX3M, HY-OAS) Rohwerte. Folge: Bei HWZ 10 wirkt ein Sprung erst nach 10 Handelstagen zur Hälfte, der Composite-Weg zu Rot ist also träge | – |
| L-9 | VX-COT-Perzentil über 3 Jahre (Bericht 6.3) vs. 10-Jahres-Fenster (4.3) | Positionierung | **Entschieden 26.09.2026 (E-49):** wie vorgeschlagen. Im Score das Standardfenster (4.3), in Ansicht 4 zusätzlich das 3-Jahres-Perzentil als Anzeige | – |
| L-10 | Transformationen ohne Definition: Erstanträge „Veränderung ggü. Tief“ (welches Fenster?), USD/JPY-Vola (Fenster), Re-Steepening-Flag (Definition), Aktien-Anleihen-Korrelation (Anleiherendite aus DGS10-Änderung?), COT-Maß und Orientierung, Excess CAPE Yield (Shiller-Spalte: 1/CAPE − (GS10 − 10-Jahres-Inflation), Ergebnis M4c), Margin Debt aus Z.1 quartalsweise (E-42): ggü. Vorjahr oder relativ zur Marktkapitalisierung aus Z.1; Strukturbruch vor 2000:Q1, VIX6M (nicht in 6.1, Endpoint prüfen) | Indikatoren | **Entschieden 26.09.2026 (E-49):** siehe Entscheidung. Je Indikator beim Anlegen in `series.toml` einzeln vorschlagen und fragen. Quelle für USD/JPY: E-17 | – |
| L-11 | Fallhöhe in Phase 1: Top-10-Konzentration (O-1), HY-OAS-Niveau (O-5) und AAII (Phase 2) fehlen | Fallhöhe | **Entschieden 26.09.2026 (E-49):** wie vorgeschlagen. Mittel der vorhandenen Komponenten (Excess CAPE Yield, Margin Debt ggü. Vorjahr, VX-COT-Short-Vol), mindestens 2; Fehlende sichtbar. Ergänzt: Top-10-Konzentration (E-71), Kreditspread-Enge mit BAA10Y statt HY-OAS (E-85), Aktienquote der Anleger (E-86); AAII fehlt weiter | – |
| L-12 | Diffusionsindex: welche Einzelreihen zählen? | Ampel (Gelb) | **Entschieden 26.09.2026 (E-48):** wie vorgeschlagen. Nur Stress-Indikatoren mit gültigem, aktuellem Wert und ausreichender Historie. Fallhöhe-Indikatoren nicht, sonst ginge Fallhöhe doppelt in „Gelb“ ein | – |
| L-13 | Krisenmarken in der Composite-Historie: genaue Zeiträume | Anzeige | **Entschieden 27.09.2026 (E-63):** Schlusskurs-Hoch bis -Tief des S&P 500 je Episode, recherchiert mit Quelle, in `config/episodes.toml` (Anzeige, kein Score) | – |

---

## 6. Widersprüche und Inkonsistenzen

| Nr. | Befund | Umgang |
|---|---|---|
| W-1 | Der Nutzerwunsch nennt drei Farben (Grün, Gelb, Rot), die Ampel des Berichts hat vier Stufen (mit Orange) | Vier Stufen bleiben; die Erklärseite „Ampel“ erklärt alle vier |
| W-2 | VX-COT-Fenster 3 Jahre (6.3) vs. 10 Jahre (4.3) | L-9 |
| W-3 | Bericht 4.3, Schritt 4 nennt Fallhöhe-Komponenten, die in Phase 1 größtenteils fehlen | L-11 |
| W-4 | Die Rot-Regel „HY-OAS-Anstieg über 20 Tage ≥ 95. Perzentil“ braucht HY-OAS im Score; O-5 schließt das bis zur Entscheidung aus | Bis 28.09.2026 inaktiv. Seit E-75 aktiv mit BAA10Y statt HY-OAS: Perzentil der 20-Tage-Veränderung ≥ `red_credit_change`. Messung (Entwicklungsdatenbank, 25.09.2026): Kreditblock 69,8 → 5,1 (Baa-Spread 1,39 Prozentpunkte, Perzentil 0,2), Stress 42,8 → 36,6, Ampel bleibt Gelb; rückwirkend 716 von 9281 Tagen mit anderer Ampel, Kredit-Regel an 568 Tagen aktiv, u. a. Tief 1998 Gelb → Rot, Beginn 2000 Orange → Rot, Tief 2011 Grün → Gelb |
| W-5 | `CLAUDE.md`: Fehler „werden geloggt, nicht gespeichert, und erscheinen im Datenstand“. Die Web-Oberfläche kann Worker-Logs nicht lesen | Entschieden (E-9): Fehlerhafte Werte werden nie gespeichert. Der letzte Fehler je Quelle (Zeit und Meldung) steht in `source_status`, ohne Historie |
| W-6 | Bericht 6.3, Ansicht 2 nennt MOVE (ICE-Lizenz, nicht in Phase 1) und VIX6M (nicht in Tabelle 6.1) | MOVE entfällt in Phase 1; VIX6M als Rohreihe in M2 Teil B (E-20), VX-Futures in M4 (E-18) |
| W-7 | Der Migrationsablauf in `CLAUDE.md` (stop → Backup → upgrade → up) gilt „auch bei der Ersteinrichtung“; dann gibt es aber nichts zu stoppen oder zu sichern | Die Einrichtungsanleitung lässt Stop und Backup bei der Ersteinrichtung aus; `fever.backup` meldet eine fehlende Datenbank klar |
| W-8 | Bericht 6.1: VIX3M-Historie ab 04.12.2007. Die Cboe-CSV beginnt erst am 18.09.2009 (geprüft 26.09.2026) | Archiviert wird, was die CSV liefert; für das 10-Jahres-Fenster folgenlos |
| W-9 | `CLAUDE.md` verlangt gekürzte echte Antworten als Fixtures, verbietet aber die Weitergabe lizenzierter Daten; das Repository ist öffentlich | E-27: Format echt, Werte lizenzierter Quellen synthetisch |
| W-10 | `CLAUDE.md` verlangte FINRA Margin Debt als Download ohne Login und verbietet zugleich Scraping gegen Nutzungsbedingungen; FINRA untersagt Speichern und Datenbanken ohne schriftliche Zustimmung | E-42: Margin Debt aus Fed Z.1 über FRED; `CLAUDE.md` angepasst |
| W-11 | FRED Terms of Use (abgerufen 28.09.2026): „You may not, without the Bank's prior written consent: … (p) Store, cache, or archive any portion of … FRED® Content; … or incorporate any FRED® Content in any database“; für die API ohne Zustimmungsvorbehalt „(l) Use the FRED® API in connection with storing, caching, or archiving …“. Die allgemeine Lizenz erlaubt dagegen, eine Kopie „solely for your personal, non-commercial use“ herunterzuladen. Der Worker speichert alle FRED-Reihen, auch das ICE-Archiv; derselbe Maßstab wie bei FINRA (W-10) trifft hier den Kern des Projekts. Ob die Klauseln bei der Prüfung in M2 schon bestanden, ließ sich nicht klären (Webarchiv: 429) | E-69: Zustimmung anfragen, O-7; Zustimmung erhalten 28.09.2026 (E-79) |

---

## 7. Technische Leitlinien der Oberfläche

Kurzfassung als Regel für KI-Sitzungen: `.claude/rules/oberflaeche.md`. Hier stehen Details und Begründungen.

### 7.1 Chart-Standard (gilt für jeden Chart)

- **Eine Fabrikfunktion** in `fever/web/figures.py` erzeugt Figure und Config. Die Figure ist seit 28.09.2026 ein einfaches Dict im plotly.js-Format mit Datum als ISO-Text (Ladezeit, siehe „Ladezeiten der Seiten“ in Abschnitt 4); die Tests prüfen jede mit `plotly.graph_objects`. Kein Chart wird an ihr vorbei gebaut, damit Standard und Test an einer Stelle hängen.
- **Zoom und Verschieben:** Plotly-Standard (Rahmen aufziehen, Verschieben über die Modebar, Doppelklick setzt zurück). `scrollZoom` aus, weil sonst das Scrollen der Seite auf dem Smartphone im Chart hängen bleibt.
- **Zeitraum-Buttons (E-2):** `xaxis.rangeselector` mit „1 M“, „6 M“, „1 J“, „5 J“, „Max“. Kein Rangeslider; er kostet auf dem Smartphone zu viel Höhe.
- **Bildexport:** Modebar-Button „Download als PNG“ über `toImageButtonOptions` (`format="png"`, `scale=2`, Dateiname `<kennzahl>_<TT-MM-JJJJ>`), `displaylogo=False`. `showSendToCloud=False`: Plotly.js 4 zeigt sonst „Share chart…“ und lädt damit Chart und Daten zu Plotly Cloud hoch. Die Bilderzeugung läuft im Browser, ohne Server-Bibliothek; geprüft am Quelltext von Dash 4.4.1 (`dcc.Graph`, Prop `config`).
- **Datenstand im Bild:** Titel, Quelle, letztes Beobachtungsdatum und Abrufzeitpunkt stehen als Annotation *im* Chart, mit festem Pixelabstand unter der Achse. Ein exportiertes oder ausgedrucktes Bild darf nie zeitlos wirken.
- **Rezessionsbalken (E-56):** US-Rezessionen aus FRED `USREC` als graue Flächen hinter den Linien in allen Zeitreihen-Charts, mit Hinweiszeile in der Datierung. Nur Anzeige.
- **Vollbild (E-2):** ein Button je Chart-Karte, in eigener Zeile über dem Chart (über der Modebar verdeckte er deren Buttons), der die Karte per CSS-Klasse als Overlay über den ganzen Bildschirm legt (`position: fixed; inset: 0`); Plotly passt sich über `responsive` an. Der Graph steckt in `.chart-box` mit fester Höhe, im Vollbild füllt die Box den Rest der Karte. Bewusst ohne Fullscreen-API, damit das Verhalten nicht vom Browser abhängt. ESC oder Button schließt.
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
- **Übersichtsseite „Erklärungen“:** alle Kennzahlen nach Block gruppiert, dazu die Konzeptseiten „Perzentil“, „Ampel“, „Konfidenz“, „Veraltung“, „Rezessionsbalken“ (E-56).
- **Einfluss je Indikator (E-57):** erzeugter Abschnitt „So fließt der Wert in den Bereich ein“ auf der Erklärseite und in der Übersicht: die heutige Rolle aus den gespeicherten Scores, dann die Schritte aus `series.toml` und `scoring.toml`. Keine Zahl davon steht im Code.

### 7.3 Aktualität

- **Je Wert:** Beobachtungsdatum, Abrufzeitpunkt (Europe/Berlin mit Zonenkürzel MEZ/MESZ) und relatives Alter („vor 3 Std.“).
- **Veraltet** (älter als Frequenz plus Toleranz): ausgegraut und schraffiert, dazu das Wort „veraltet“. Nie nur über Farbe.
- **Kopfzeile auf jeder Seite:** letzte erfolgreiche Worker-Aktualisierung und Zeitpunkt der letzten Seitenaktualisierung.
- **Worker-Banner:** Ist der Heartbeat überfällig (dieselbe Grenze wie der Healthcheck), erscheint ein roter Hinweis „Worker ohne Lebenszeichen seit …, Werte werden nicht aktualisiert“.
- **Seiten-Aktualisierung (E-7):** `dcc.Interval` alle 5 Minuten liest Daten und Status neu.
- **Verbindungs-Wächter:** Ist der Server nicht erreichbar, schlagen die Interval-Callbacks fehl und die Seite zeigt still alte Werte. Deshalb merkt sich ein Clientside-Callback die Browserzeit der letzten erfolgreichen Antwort. Ein zweiter Clientside-Timer blendet nach mehr als 2 Intervallen ohne Antwort ein Banner ein: „Keine Verbindung zum Server – angezeigte Werte vom …“. Es wird die Browserzeit verglichen, nicht die Serverzeit, damit abweichende Uhren keine Rolle spielen.
- **Uhrzeit des Servers:** Die Veraltungslogik hängt an der Systemzeit. Die Einrichtungsanleitung prüft die NTP-Synchronisation.

### 7.4 Gestaltung

- **Grundsatz:** ruhig, konsistent, lesbar; Zahlen stehen im Vordergrund. Keine Animationen, keine Tachometer-Spielereien, keine 3D-Charts.
- **Farbschema (E-5):** CSS-Variablen in `assets/base.css`, hell und dunkel über `prefers-color-scheme`. Zwei Plotly-Templates (`fever_light`, `fever_dark`; `figures.TEMPLATES`, in jede Figur eingebettet). `assets/theme.js` erkennt das Schema und meldet Wechsel über `matchMedia(...).addEventListener("change", …)` an einen `dcc.Store`; die Figure-Callbacks lesen ihn.
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
| Verzögerter Start des Workers | ICE-Historie geht tageweise verloren | M0–M3 zuerst, früh in Betrieb |
| Dash 4 / Plotly 7 sind neuer als das Trainingswissen vieler KI-Modelle | erfundene oder veraltete Signaturen | Signaturen im installierten Paket nachsehen; bei Unsicherheit sagen |
| Unverifizierte Endpoints (OFR, EBP, CISS, TFF-IDs, VIX6M) | Quelle fällt aus oder liefert anderes Format | real abrufen vor dem Parser (M2/M4), Fixture, sichtbarer Fehler |
| Rechenzeit rollierender Perzentile | langsame Neuberechnung | gemessen in M5: 5,6 s je vollständigem Lauf (Entwicklungsumgebung); auf TrueNAS messen |
| Lesepuffer im Web-Prozess (E-78) | ein Chart zeigt nach neuen Daten noch den alten Stand | Datenstand aus größter rowid von `observation` (nur Anfügen, Trigger) und `computed_at` der Scores; jede Änderung verwirft den ganzen Puffer; Tests `test_long_reads_are_kept_until_the_worker_stores_new_data` |
| Druck von dunklen Charts | unlesbare PDFs | Prüfung in M6, Fallback `beforeprint` |
| Kein Passwort im Heimnetz (E-3) | jedes Gerät im WLAN sieht das Dashboard | akzeptiert; die Daten sind öffentliche Marktdaten ohne Kontobezug |
| Docker-Portfreigaben umgehen Host-Firewallregeln (E-4) | Firewall-Regeln greifen nicht für den Web-Port | in `docs/einrichtung.md` dokumentiert; keine Portweiterleitung im Router |
| Speicherklausel der Cboe-Nutzungsbedingungen (E-26) | Cboe könnte das private Archiv beanstanden | nur private Nutzung, keine Weitergabe, ein Abruf je Datei und Tag; bei Beanstandung Cboe-Reihen aus dem Katalog nehmen |
| Veröffentlichungszeiten teils nur einmal beobachtet (E-23) | geschätzte Vintages der Rückfüllung um Stunden verschoben | Prüfung aus dem Rohdatenarchiv in M3 (Schritt 9) |
| Datenordner im Git-Arbeitsverzeichnis (E-28) | `git clean -fdx` löscht Datenbank und Backups zugleich | Warnung in `docs/einrichtung.md` und `CLAUDE.md`; optional TrueNAS-Snapshots des Datasets `data` |
| Shiller-Download über wechselnden Link (E-43) | Umbau der Seite oder neuer Dateiname stoppt CAPE und Excess CAPE Yield | sichtbarer Fehler im Datenstand; Parser in `fever/sources/shiller.py` anpassen |
| Betrieb direkt vom Entwicklungsbranch (E-30) | ein ungeprüfter Push landet beim nächsten Update im Betrieb | nur geprüften Stand pushen; Update nur auf Anweisung in `docs/einrichtung.md` |
| Rezessionsregeln ohne Hysterese (E-80, E-91) | Sahm-Gelb hält bis weit in Erholungen an; an der 200-Tage-Linie wechselt Orange/Gelb öfter | Wirkung dokumentiert (Abschnitt 4, „Entscheidungsrunde 29.09.2026“); M10 prüft die Ampel als Ganzes, nicht jede Regel einzeln |
| Validierung auf derselben Stichprobe (M10, E-93) | Ergebnisse überschätzen die Güte; Versuchung, Schwellen nachzuziehen | Nur Auswertung ohne Rückwirkung; Parameter nur auf Anweisung (`CLAUDE.md`); Grenzen in der Ansicht und auf der Erklärseite |
| y-Achsen-Skript nutzt Plotly-Interna (`_fullLayout`, E-88) | nach einem Plotly-Update passt sich die y-Achse nicht mehr an (Daten bleiben richtig) | nach jedem Update von Dash/Plotly Zoom im Browser prüfen (Abschnitt 10) |

---

## 9. Übergabe an die nächste Sitzung

- **Stand (29.09.2026):**
  - M0 bis M8 erledigt; Entscheidungsrunde 29.09.2026 umgesetzt und in der Entwicklungsumgebung geprüft (E-80 bis E-92; Abschnitt 4, „Entscheidungsrunde 29.09.2026“, mit Vorher/Nachher der Ampel).
  - M10 (Validierung, E-89, E-93) umgesetzt und in der Entwicklungsumgebung geprüft: Berechnung, Migration 0004, Worker, Ansicht 8, Erklärseite; Ergebnisse in Abschnitt 4, M10. Migrationsprobe 0003 → 0004 mit dem gebauten Image bestanden. 484 Tests grün.
  - Auf TrueNAS beides noch nicht eingespielt. Ob TrueNAS schon vom Branch `claude-raramo` läuft (E-76), ist nicht bestätigt.
  - `data-dev/` steht auf 0004, mit Scores und Validierungsbericht vom 29.09.2026.
  - Entscheidungen bis E-93; die Festlegungen der Validierung (E-93) hat der Nutzer nach Vorlage der Ergebnisse bestätigt.
- **Nächster Schritt:**
  1. TrueNAS: falls noch nicht geschehen, Update „schnellere Seiten und Branch `claude-raramo`“, dann „Entscheidungsrunde 29.09.2026 und Validierung (M10)“ (`docs/einrichtung.md`, Abschnitt 9): Probe der Migration an einer Backup-Kopie, Stack stoppen, Backup, `alembic upgrade head` (0004), „Deploy“, Sofort-Abruf, `fever.score`, `fever.validate`.
  2. Nutzer: Ergebnisse von M10 in der Ansicht „Validierung“ ansehen; Folgerungen (etwa für Aggregation Stufe 2 in Phase 2, E-89) entscheidet der Nutzer.
  3. Nach einigen Werktagen: Veröffentlichungszeiten aus dem Rohdatenarchiv prüfen (M3, Schritt 9); für `iursa` und die Z.1-Reihen neu.
  4. M9 (Abnahme Phase 1).
- **Hinweise:**
  - Betrieb läuft direkt von `claude-raramo` (E-76): nur geprüften Stand pushen.
  - Das Repository ist öffentlich: keine Werte lizenzierter Quellen in Fixtures oder Doku (E-27).
  - **Netzwerk der Cloud-Entwicklungsumgebung** (nur KI-Sitzungen): erreichbar am 26.09.2026 waren `api.stlouisfed.org`, `cdn-api.cboe.com`, `data-api.ecb.europa.eu`, `www.financialresearch.gov`, `www.federalreserve.gov`, `publicreporting.cftc.gov`, `www.finra.org`, `shillerdata.com` (über den Proxy zeitweise abgebrochen), `img1.wsimg.com`, `www.cboe.com`, `cdn.cboe.com`; nicht erreichbar `www.econ.yale.edu`, `web.archive.org`. Am 28.09.2026 zusätzlich erreichbar: `fred.stlouisfed.org` (CSV ohne Schlüssel), `www.ssga.com`, `www.sec.gov`, `data.sec.gov`, `indexes.nasdaq.com`; `archive.org` antwortete mit 429. Für SEC-Probeabrufe in der Cloud nur einen Platzhalterkontakt (`…@example.org`) setzen, nie die Adresse des Nutzers. Am 28.09.2026 abends lief der Sofort-Abruf aller 72 Reihen in der Cloud ohne Probleme.
  - **FRED-Schlüssel:** in der Cloud-Umgebung als `FRED_API_KEY` gesetzt (26.09.2026, nur Länge geprüft). Nie im Chat und nie im Repo; die `.env` wird nie gelesen.
- **Offene Entscheidungen des Nutzers:** O-6 (Phase 2); die Optionen unter „Nicht umgesetzt“ (Ladezeiten), falls die Seiten auf TrueNAS noch zu langsam sind.
- **Befehle:** `pytest -q` (Python 3.14 mit `requirements-dev.txt`), Build-Probe, Compose-Prüfung und Ladezeit-Messung siehe Abschnitt 10; Betrieb auf TrueNAS in `docs/einrichtung.md`, Abschnitt 12.

---

## 10. Entwicklungsumgebung (für KI-Sitzungen in der Cloud)

Stand 25.09.2026, erprobt in der Claude-Code-Cloud-Umgebung. Die Umgebung ist ein flüchtiger Container: Docker-Daemon und Hilfs-Images sind nach einem Neustart weg.

1. **Docker-Daemon starten** (CLI und `dockerd` sind installiert, laufen aber nicht):
   ```bash
   nohup dockerd > /tmp/dockerd.log 2>&1 &
   ```
2. **arm64-Emulation:** entfällt seit E-21 (Zielsystem x86_64 wie die Entwicklungsumgebung).
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
   Antwortet Docker Hub mit „429 Too Many Requests“ (anonyme Abrufe gedrosselt, so am 26.09.2026), das Basis-Image über den Spiegel holen und umbenennen: `docker pull mirror.gcr.io/library/python:3.14-slim-trixie && docker tag mirror.gcr.io/library/python:3.14-slim-trixie python:3.14-slim-trixie`.
5. **Build-Probe** (seit E-21 für x86_64, ohne Emulation; ausgeführt am 26.09.2026, 42 s): Kopie des Dockerfiles mit den zwei Zertifikatszeilen nach `FROM`, sonst unverändert:
   ```bash
   sed '/^FROM /a COPY --from=proxyca ca-bundle.crt /tmp/proxy-ca.crt\nENV PIP_CERT=/tmp/proxy-ca.crt' \
     Dockerfile > <scratch>/Dockerfile.probe
   docker buildx build -f <scratch>/Dockerfile.probe \
     --build-context proxyca=/root/.ccr --network host \
     --build-arg HTTPS_PROXY --build-arg HTTP_PROXY --load -t fever:local .
   ```
6. **Compose prüfen ohne `.env`** (die echte `.env` wird nie gelesen): eine Testdatei mit Platzhaltern im Scratchpad anlegen (`FEVER_DATA_DIR` auf einen Ordner mit Eigentümer 568:568) und `env -u FRED_API_KEY -u FEVER_SEC_CONTACT docker compose -f compose.dockge.yaml --env-file <scratch>/probe.env -p fever-probe config` aufrufen. **Immer mit `env -u …`:** Compose nimmt gesetzte Umgebungsvariablen vor der `--env-file`, und `config` gibt sie im Klartext aus; so geriet am 28.09.2026 der FRED-Schlüssel der Cloud-Umgebung in eine Befehlsausgabe (nicht ins Repository); mit `up -d`, `logs worker`, `stop` und `down` läuft der Stack wie in Dockge. Die Bau-Datei: `docker compose -f docker-compose.yml config`.
7. **Echte Abrufe in Containern** (Teil B): Proxy-Variablen, Zertifikat und Schlüssel durchreichen, ohne ihn anzuzeigen:
   ```bash
   docker run --rm --network host -e HTTPS_PROXY -e HTTP_PROXY -e FRED_API_KEY -e PYTHONPATH=/src \
     -e FEVER_DATA=/src/data-dev -e REQUESTS_CA_BUNDLE=/ca.crt -v /root/.ccr/ca-bundle.crt:/ca.crt:ro \
     -v "$PWD":/src fever-devtest python …
   ```
   `data-dev/` vorher anlegen und migrieren: `mkdir -p data-dev && docker run --rm -e FEVER_DATA=/src/data-dev -v "$PWD":/src fever-devtest alembic upgrade head`.
   `requests` nutzt sonst sein eigenes Zertifikatsbündel und scheitert am Proxy. Große Antworten erst in eine Datei schreiben und nur Anfang und Ende ansehen (`CLAUDE.md`).
8. **Nach einem Neustart der Cloud-Umgebung** sind Docker-Daemon und Hilfs-Images weg. Die Schritte 1 und 4 wiederholen. Der Daemon stoppte am 26.09.2026 auch zwischendurch ohne Neustart der Umgebung („Cannot connect to the Docker daemon“); dann nur Schritt 1.
9. **Abhängigkeiten ändern:** im Container (linux/amd64) mit `pip install --only-binary=:all: -r <direkte Pakete>` auflösen, `pip freeze` übernehmen, direkte Pakete mit Zweckkommentar oben in `requirements.txt`, transitive darunter.
10. **Ladezeiten messen** (28.09.2026; Skripte liegen nicht im Repository, Node gehört nicht zum Projekt):
    - Daten: `data-dev/` wie in Punkt 7 anlegen, alle Reihen holen (`python -m fever.sources.update` mit `FEVER_SEC_CONTACT=… …@example.org`, rund 4 Minuten), dann `python -m fever.score`.
    - Server: im Hilfs-Image `fever.web.app` importieren, dann je Seite die Funktion aus `fever/web/views.py` aufrufen und mit `dash._utils.to_json` umwandeln, jeweils zweimal (erster Aufruf, Aufruf aus dem Lesepuffer); Profil mit `cProfile`.
    - Browser: gunicorn wie in `compose.dockge.yaml` im Hilfs-Image mit `--network host` gegen `data-dev/` starten; Playwright aus der globalen Node-Installation der Cloud-Umgebung (`require('/opt/node22/lib/node_modules/playwright')`, Chromium unter `/opt/pw-browsers`); Zeit vom Aufruf bzw. Klick in der Navigation, bis jedes `.dash-graph` ein `.main-svg` enthält. Drosselung über CDP: `Emulation.setCPUThrottlingRate` (Smartphone-Näherung 4) und `Network.emulateNetworkConditions`.
    - Vergleich mit dem alten Stand: `git worktree add <scratch>/before <commit>` und dort einen zweiten gunicorn auf anderem Port.
11. **y-Achse prüfen** (E-88; nach jedem Update von Dash oder Plotly, 29.09.2026 erprobt): gunicorn wie in Punkt 10, dann mit Playwright eine Ansicht laden, `Plotly.relayout` per Init-Skript zählen (erwartet 0 beim Laden), je Zeitraum-Knopf „1 J“, „6 M“, „5 J“, „Max“, waagrechtem Ziehen, Doppelklick und `Plotly.react(gd, gd.data, gd.layout)` den sichtbaren Wertebereich mit `gd._fullLayout.yaxis.range` vergleichen (enthalten, höchstens rund 5 % Rand). Das Graph-Element ist `#<id> .js-plotly-plot`, nicht das Element mit der Id selbst.
