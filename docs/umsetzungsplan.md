# Umsetzungsplan Phase 1 – Fieberthermometer

Stand: 26.09.2026 · Status: **M0 bis M2, M4 und M5 erledigt (M5 noch nicht auf TrueNAS), M3: Worker läuft auf TrueNAS mit 60 Reihen** · Nächster Schritt: M5 auf TrueNAS einspielen (mit Migration 0002), M6 planen; M3 abschließen nach den ersten Werktags-Abrufen (Abschnitt 9)

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
| M3 | Worker und erste Inbetriebnahme auf TrueNAS mit Dockge (ICE-Archiv startet) | ◐ läuft auf TrueNAS seit 26.09.2026, ICE-Archiv ab Beobachtung 26.09.2023; offen: erste Werktags-Abrufe, Schritt 9 | M2, Angaben zu TrueNAS | erteilt 26.09.2026 |
| M4 | Weitere Quellen: CFTC, EZB (CISS, USD/JPY-Kreuzkurs), OFR, EBP, Shiller-CAPE, Margin Debt (Z.1, E-42), VX-Futures | ☑ 26.09.2026 (M4a bis M4d, E-37) | M3 | M4a bis M4d erteilt 26.09.2026 |
| M5 | Indikatoren (`[indicator.*]`), Scoring Schritte 1–6, Aggregation Stufe 1 | ☑ 26.09.2026 (auf TrueNAS ⏳) | M4, L-1 bis L-12 | erteilt 26.09.2026 |
| M6 | Web-Grundgerüst, Gestaltung, Aktualität, Datenstand | ☐ | M1 (Lesen), M3 (Heartbeat) | ja |
| M7 | Ansichten 1–7 | ☐ | M5, M6, L-13 | ja |
| M8 | Erklärtexte je Kennzahl | ☐ | parallel zu M6/M7 | ja (Texte prüfen) |
| M9 | Abnahme Phase 1 | ☐ | M0–M8 | – |

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
- **Technische Schuld (nicht behoben):** Der HTTP-Client verwirft bei HTTP-Fehlern den Antworttext. FREDs eigene Fehlermeldung (etwa bei HTTP 400 für eine eingestellte Reihe) erscheint deshalb weder im Log noch im Datenstand.

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
- **Offen bis ☑:** erster Werktag mit Abrufen nach dem Abrufplan (Montag, 28.09.2026), dann Prüfung der Veröffentlichungszeiten aus dem Rohdatenarchiv (Schritt 9).

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
- **Annahmen ohne eigene Entscheidung (bitte bestätigen oder ändern):**
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
- **Nicht geprüft:** Migration und Scoring auf TrueNAS; Rechenzeit dort.


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

1. `pytest -q`, Build-Probe, Update auf TrueNAS nach `docs/einrichtung.md`.
2. Sichtprüfung aller Ansichten auf Smartphone und Desktop.
3. `docs/bedienung.md` und `docs/einrichtung.md` von ⏳ auf ✅, wo geprüft.
4. README-Status aktualisieren.

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
| L-11 | Fallhöhe in Phase 1: Top-10-Konzentration (O-1), HY-OAS-Niveau (O-5) und AAII (Phase 2) fehlen | Fallhöhe | **Entschieden 26.09.2026 (E-49):** wie vorgeschlagen. Mittel der vorhandenen Komponenten (Excess CAPE Yield, Margin Debt ggü. Vorjahr, VX-COT-Short-Vol), mindestens 2; Fehlende sichtbar | – |
| L-12 | Diffusionsindex: welche Einzelreihen zählen? | Ampel (Gelb) | **Entschieden 26.09.2026 (E-48):** wie vorgeschlagen. Nur Stress-Indikatoren mit gültigem, aktuellem Wert und ausreichender Historie. Fallhöhe-Indikatoren nicht, sonst ginge Fallhöhe doppelt in „Gelb“ ein | – |
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
| W-6 | Bericht 6.3, Ansicht 2 nennt MOVE (ICE-Lizenz, nicht in Phase 1) und VIX6M (nicht in Tabelle 6.1) | MOVE entfällt in Phase 1; VIX6M als Rohreihe in M2 Teil B (E-20), VX-Futures in M4 (E-18) |
| W-7 | Der Migrationsablauf in `CLAUDE.md` (stop → Backup → upgrade → up) gilt „auch bei der Ersteinrichtung“; dann gibt es aber nichts zu stoppen oder zu sichern | Die Einrichtungsanleitung lässt Stop und Backup bei der Ersteinrichtung aus; `fever.backup` meldet eine fehlende Datenbank klar |
| W-8 | Bericht 6.1: VIX3M-Historie ab 04.12.2007. Die Cboe-CSV beginnt erst am 18.09.2009 (geprüft 26.09.2026) | Archiviert wird, was die CSV liefert; für das 10-Jahres-Fenster folgenlos |
| W-9 | `CLAUDE.md` verlangt gekürzte echte Antworten als Fixtures, verbietet aber die Weitergabe lizenzierter Daten; das Repository ist öffentlich | E-27: Format echt, Werte lizenzierter Quellen synthetisch |
| W-10 | `CLAUDE.md` verlangte FINRA Margin Debt als Download ohne Login und verbietet zugleich Scraping gegen Nutzungsbedingungen; FINRA untersagt Speichern und Datenbanken ohne schriftliche Zustimmung | E-42: Margin Debt aus Fed Z.1 über FRED; `CLAUDE.md` angepasst |

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
- **Verbindungs-Wächter:** Ist der Server nicht erreichbar, schlagen die Interval-Callbacks fehl und die Seite zeigt still alte Werte. Deshalb merkt sich ein Clientside-Callback die Browserzeit der letzten erfolgreichen Antwort. Ein zweiter Clientside-Timer blendet nach mehr als 2 Intervallen ohne Antwort ein Banner ein: „Keine Verbindung zum Server – angezeigte Werte vom …“. Es wird die Browserzeit verglichen, nicht die Serverzeit, damit abweichende Uhren keine Rolle spielen.
- **Uhrzeit des Servers:** Die Veraltungslogik hängt an der Systemzeit. Die Einrichtungsanleitung prüft die NTP-Synchronisation.

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
| Verzögerter Start des Workers | ICE-Historie geht tageweise verloren | M0–M3 zuerst, früh in Betrieb |
| Dash 4 / Plotly 7 sind neuer als das Trainingswissen vieler KI-Modelle | erfundene oder veraltete Signaturen | Signaturen im installierten Paket nachsehen; bei Unsicherheit sagen |
| Unverifizierte Endpoints (OFR, EBP, CISS, TFF-IDs, VIX6M) | Quelle fällt aus oder liefert anderes Format | real abrufen vor dem Parser (M2/M4), Fixture, sichtbarer Fehler |
| Rechenzeit rollierender Perzentile | langsame Neuberechnung | gemessen in M5: 5,6 s je vollständigem Lauf (Entwicklungsumgebung); auf TrueNAS messen |
| Druck von dunklen Charts | unlesbare PDFs | Prüfung in M6, Fallback `beforeprint` |
| Kein Passwort im Heimnetz (E-3) | jedes Gerät im WLAN sieht das Dashboard | akzeptiert; die Daten sind öffentliche Marktdaten ohne Kontobezug |
| Docker-Portfreigaben umgehen Host-Firewallregeln (E-4) | Firewall-Regeln greifen nicht für den Web-Port | in `docs/einrichtung.md` dokumentiert; keine Portweiterleitung im Router |
| Speicherklausel der Cboe-Nutzungsbedingungen (E-26) | Cboe könnte das private Archiv beanstanden | nur private Nutzung, keine Weitergabe, ein Abruf je Datei und Tag; bei Beanstandung Cboe-Reihen aus dem Katalog nehmen |
| Veröffentlichungszeiten teils nur einmal beobachtet (E-23) | geschätzte Vintages der Rückfüllung um Stunden verschoben | Prüfung aus dem Rohdatenarchiv in M3 (Schritt 9) |
| Datenordner im Git-Arbeitsverzeichnis (E-28) | `git clean -fdx` löscht Datenbank und Backups zugleich | Warnung in `docs/einrichtung.md` und `CLAUDE.md`; optional TrueNAS-Snapshots des Datasets `data` |
| Shiller-Download über wechselnden Link (E-43) | Umbau der Seite oder neuer Dateiname stoppt CAPE und Excess CAPE Yield | sichtbarer Fehler im Datenstand; Parser in `fever/sources/shiller.py` anpassen |
| Betrieb direkt vom Entwicklungsbranch (E-30) | ein ungeprüfter Push landet beim nächsten Update im Betrieb | nur geprüften Stand pushen; Update nur auf Anweisung in `docs/einrichtung.md` |

---

## 9. Übergabe an die nächste Sitzung

- **Stand (26.09.2026):**
  - M0 bis M2 erledigt, M3 umgesetzt (178 Tests grün): Worker mit Abrufplan (E-31), Heartbeat, täglichem Backup und Healthcheck; Compose-Dateien und Einrichtungsanleitung für TrueNAS mit Dockge.
  - Entscheidungen bis E-50; M4 vollständig (60 Reihen in 32 Abrufgruppen, auf TrueNAS seit 26.09.2026: „60 Reihen, 0 mit Problemen“).
  - M5 umgesetzt: 19 Indikatoren, Scoring nach Bericht 4.3 Schritte 1–6, Migration 0002, Scoring-Lauf im Worker und als `python -m fever.score`; 341 Tests grün. Noch nicht auf TrueNAS eingespielt.
  - Worker läuft auf TrueNAS seit Samstag, 26.09.2026 („healthy“). Erstabruf aller 23 Reihen am 26.09.2026 per Sofort-Abruf; das ICE-Archiv beginnt mit dem 26.09.2023. Planmäßige Abrufe ab Montag, 28.09.
- **Nächster Schritt:**
  1. M5 auf TrueNAS einspielen (Migration 0002): `docs/einrichtung.md`, Schritt 9, zuerst die Probe an einer Backup-Kopie; danach `python -m fever.score` und die Rechenzeit notieren.
  2. Nach den ersten Werktags-Abrufen: Log und Zeilenzahlen je Reihe prüfen (Nutzer schickt Ausgaben); dann M3 abschließen (geplant in der Woche ab 28.09.2026).
  3. Die Annahmen unter „Ergebnis M5“ vom Nutzer bestätigen lassen (EWMA-Neustart, Vola ohne Mittelwertabzug, VIX/VIX3M-Regel bei fehlendem Wert, Ampel ohne Composite).
  4. M6 planen (Web-Grundgerüst, Gestaltung, Aktualität, Datenstand); `scoring` in `source_status` im Datenstand als eigene Zeile benennen.
  5. Nach einigen Werktagen: Veröffentlichungszeiten aus dem Rohdatenarchiv prüfen (M3, Schritt 9), Cboe-Verhalten während der US-Handelszeit (Indizes und VX-Kontraktdateien), CFTC nach dem ersten Freitag, Shiller nach dem Oktober-Upload.
- **Hinweise:**
  - Betrieb läuft direkt von `claude-testing` (E-30): nur geprüften Stand pushen.
  - Das Repository ist öffentlich: keine Werte lizenzierter Quellen in Fixtures oder Doku (E-27).
  - **Netzwerk der Cloud-Entwicklungsumgebung** (nur KI-Sitzungen): erreichbar am 26.09.2026 waren `api.stlouisfed.org`, `cdn-api.cboe.com`, `data-api.ecb.europa.eu`, `www.financialresearch.gov`, `www.federalreserve.gov`, `publicreporting.cftc.gov`, `www.finra.org`, `shillerdata.com` (über den Proxy zeitweise abgebrochen), `img1.wsimg.com`, `www.cboe.com`, `cdn.cboe.com`; nicht erreichbar `www.econ.yale.edu`, `web.archive.org`.
  - **FRED-Schlüssel:** in der Cloud-Umgebung als `FRED_API_KEY` gesetzt (26.09.2026, nur Länge geprüft). Nie im Chat und nie im Repo; die `.env` wird nie gelesen.
- **Offene Entscheidungen des Nutzers:** O-1, O-5, O-6 (`CLAUDE.md`), L-13 (Abschnitt 5, vor M7), Bestätigung der M5-Annahmen.
- **Befehle:** `pytest -q` (Python 3.14 mit `requirements-dev.txt`), Build-Probe und Compose-Prüfung siehe Abschnitt 10; Betrieb auf TrueNAS in `docs/einrichtung.md`, Abschnitt 12.

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
6. **Compose prüfen ohne `.env`** (die echte `.env` wird nie gelesen): eine Testdatei mit Platzhaltern im Scratchpad anlegen (`FEVER_DATA_DIR` auf einen Ordner mit Eigentümer 568:568) und `docker compose -f compose.dockge.yaml --env-file <scratch>/probe.env -p fever-probe config` aufrufen; mit `up -d`, `logs worker`, `stop` und `down` läuft der Stack wie in Dockge. Die Bau-Datei: `docker compose -f docker-compose.yml config`.
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
