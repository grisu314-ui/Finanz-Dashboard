# Dokumentation (gilt immer)

Die Doku hat zwei Zielgruppen: eine KI, die das Projekt später fortsetzt, und den Nutzer als Anwender. Eine Änderung ist erst fertig, wenn die betroffene Doku im selben Commit stimmt.

| Datei | Für | Inhalt | Pflegen bei |
|---|---|---|---|
| `README.md` | alle | Einstieg, Status, Wegweiser | Statuswechsel eines Meilensteins |
| `docs/umsetzungsplan.md` | KI, Nutzer | Meilensteine und Stand, Entscheidungen, fachliche Lücken, Übergabe | jeder Sitzung, jeder Entscheidung |
| `docs/einrichtung.md` | Nutzer | Einrichtung, Update, Backup/Wiederherstellung, Fehlersuche | Änderungen an Dockerfile, Compose, `.env`, Migrationen, Befehlen |
| `docs/bedienung.md` | Nutzer | Dashboard lesen und bedienen | Oberflächenänderungen |
| `docs/leitfaden-erklaertexte.md` | KI, Textautor | Vorlage und Regeln für Kennzahl-Texte | Änderungen am Textformat |
| `fever/web/texts/*.md` | Nutzer (in der App) | Kurzinfo und Erklärseite je Kennzahl | neuen oder geänderten Kennzahlen |

- Jeder Einrichtungsschritt ist ein kopierbarer Befehl mit erwarteter Ausgabe. Braucht ein Schritt ein Secret, einen Schlüssel oder einen Hash, steht der Befehl zum Erzeugen daneben, nie der Wert.
- Markierung je Abschnitt: ✅ geprüft (mit Datum und Ort: Entwicklungsrechner oder Pi) oder ⏳ geplant bzw. ungeprüft. Nichts als geprüft markieren, was nicht ausgeführt wurde.
- Anwender-Doku schreibt keine Parameterwerte aus `scoring.toml` ab, sondern verweist auf die Erklärseiten der App.
- Neue oder geänderte Befehle auch in `CLAUDE.md` unter „Befehle“ eintragen.
- Am Ende jeder Sitzung in `docs/umsetzungsplan.md` den Status (Abschnitt 1) und die Übergabe (Abschnitt 9) aktualisieren.
