# Bedienung: das Dashboard lesen

Stand: 26.09.2026 · Für: dich als Anwender · Status: ⏳ **Zielbild, teilweise umgesetzt.** Seit M6 gibt es Seitenrahmen, Übersicht (Ampel, Stress, Fallhöhe, Konfidenz), Datenstand, Erklärungen und Erklärseiten; die Themen-Ansichten folgen in M7, die übrigen Texte in M8 (`docs/umsetzungsplan.md`). Dieser Text wird bei der Abnahme (M9) gegen die fertige App geprüft und dann auf ✅ gesetzt.

Die genauen Schwellenwerte stehen bewusst nicht hier, sondern in der App auf den Erklärseiten (z. B. „Ampel“). Die Seiten werden aus der Konfiguration erzeugt und sind deshalb immer aktuell.

---

## 1. Was das Dashboard ist und was nicht

- Es zeigt, **wie angespannt** der US- und der globale Aktienmarkt gerade sind (akuter Stress) und **wie tief** es fallen könnte, wenn etwas passiert (Fallhöhe).
- Es ist **keine Crash-Prognose**, gibt **keine Kauf- oder Verkaufssignale** und sagt **keine Renditen** voraus. Die Forschung zeigt, dass sich das Wann eines Einbruchs kaum vorhersagen lässt (Bericht, Kurzfazit).
- Es nutzt nur öffentliche Marktdaten, keine Kontodaten.

## 2. Die zwei Achsen und die Ampel

- **Stress** (0–100): Wie ungewöhnlich angespannt sind die Märkte heute, gemessen an den letzten Jahren? Er setzt sich aus Themenblöcken zusammen (Volatilität/Optionen, Kredit/Funding, Makro/Financial Conditions, Breite, Positionierung/Sentiment).
- **Fallhöhe** (0–100): Wie verwundbar ist der Markt, etwa durch hohe Bewertung oder hohe Hebel? Sie ändert sich langsam.
- Beide Werte werden **nie multipliziert**. Eine hohe Bewertung ohne Stress ist eine andere Lage als akuter Stress bei niedriger Bewertung.
- **Ampel** mit vier Stufen:

| Stufe | Bedeutung (qualitativ) |
|---|---|
| Grün | keine auffällige Lage |
| Gelb | erhöhte Verwundbarkeit ohne akuten Auslöser, oder viele Einzelwerte gleichzeitig erhöht |
| Orange | deutlicher Stress, vor allem zusammen mit hoher Fallhöhe |
| Rot | akuter, breiter Stress oder ein schnelles Warnsignal (z. B. Volatilitätskurve invertiert) |

- **Hysterese:** Eine Stufe wird erst verlassen, wenn der Wert klar unter die Schwelle fällt. Das verhindert tägliches Hin- und Herspringen.
- **Konfidenz:** Anteil der Kennzahlen mit aktuellen Daten, gewichtet nach ihrem historischen Vorlauf. Niedrige Konfidenz heißt: Die Ampel steht auf dünner Datenbasis.
- In Phase 1 fehlen einzelne Bausteine sichtbar, z. B. der Block „Breite“ (keine Kursquelle, O-1) und die HY-OAS-Regel (O-5). Die App zeigt das an, statt Lücken zu verstecken.

## 3. Einzelkennzahlen lesen

- **Perzentil:** Anteil der vergangenen Tage im Vergleichsfenster, an denen der Wert niedriger war. „Perzentil 85“ heißt: höher als an etwa 85 % der Vergleichstage. Gerechnet wird nur mit Daten, die am jeweiligen Tag schon veröffentlicht waren.
- **Orientierung:** Bei jeder Kennzahl bedeutet ein hohes Perzentil mehr Stress bzw. mehr Fallhöhe. Wo die Rohgröße andersherum läuft (z. B. Marktbreite), ist sie bereits umgedreht; der Steckbrief sagt es.
- **Farben:** Einzelkennzahlen haben eine neutrale Farbskala nach Perzentil und ab einer festen Schwelle die Markierung **„erhöht“**. Ampelfarben gibt es nur für die Gesamtampel (Entscheidung E-1).
- **Unter Mindesthistorie:** Kennzahlen mit zu kurzer Historie werden angezeigt, zählen aber noch nicht zum Score. Sie sind entsprechend markiert.

## 4. Kurzinfo und Erklärseite

- **ⓘ neben einer Kennzahl:** Maus darüber (Smartphone: antippen) zeigt eine Kurzinfo, was die Kennzahl repräsentiert.
- **Name der Kennzahl anklicken** öffnet die Erklärseite mit:
  - aktuellem Stand und Verlauf
  - ausführlicher Erklärung (was sie misst, warum sie zählt, wie man sie liest, Grenzen)
  - Steckbrief (Quelle, Frequenz, Verzug, Historie)
  - „Schwellen und Farben“: ab wann „erhöht“ bzw. welche Ampelregel gilt
  - Quellen
- Die Seite „Erklärungen“ listet alle Kennzahlen nach Block, dazu die Konzepte Perzentil, Ampel, Konfidenz, Veraltung und Rezessionsbalken.

## 5. Aktualität: Wie alt ist, was ich sehe?

- Jeder Wert zeigt **Beobachtungsdatum**, **Abrufzeitpunkt** (deutsche Zeit mit MEZ/MESZ) und das **Alter** („vor 3 Std.“).
- **Veraltet:** Ist ein Wert älter, als seine Veröffentlichungsfrequenz plus Toleranz erlaubt, erscheint er ausgegraut, schraffiert und mit dem Wort „veraltet“. Veraltete Werte zählen nicht zum Score und senken die Konfidenz.
- **Handelsfreie Tage** (Wochenende, US-Feiertage) sind normal und kein Fehler.
- **Die offene Seite aktualisiert sich alle 5 Minuten** selbst; dein Zoom bleibt dabei erhalten.
- **Banner:**
  - „Worker ohne Lebenszeichen“: Der Datenabruf auf dem Server steht, alle Werte werden nicht mehr aktualisiert.
  - „Keine Verbindung zum Server“: Die Seite erreicht den Server nicht mehr; was du siehst, ist der Stand von der angegebenen Uhrzeit.
- Ansicht **„Datenstand“**: je Quelle letzter erfolgreicher Abruf, letzter Versuch, letzter Fehler.

## 6. Charts bedienen

| Aktion | So geht es |
|---|---|
| Zoomen | mit der Maus einen Rahmen aufziehen; auf dem Smartphone mit dem Finger ziehen |
| Verschieben | in der Leiste oben rechts im Chart „Pan“ wählen, dann ziehen |
| Zurücksetzen | Doppelklick bzw. Doppeltippen in den Chart |
| Zeitraum | Buttons „1 M“, „6 M“, „1 J“, „5 J“, „Max“ über dem Chart |
| Werte ablesen | Maus über die Linie bzw. antippen |
| Bild speichern | Kamera-Symbol in der Chart-Leiste lädt ein PNG herunter; Titel, Quelle und Datenstand sind im Bild enthalten |
| Vollbild | Button „Vollbild“ oben rechts über dem Chart; ESC oder „Schließen“ beendet es |
| Graue Flächen | US-Rezessionen nach der NBER-Datierung, wie in den FRED-Grafiken; nur zur Orientierung, kein Teil eines Scores. Erklärung: Seite „Erklärungen“ → „Rezessionsbalken“ |
| Ganze Ansicht als PDF | Browser → Drucken → „Als PDF speichern“; die Druckansicht ist hell und ohne Bedienelemente |

Das Scrollrad zoomt bewusst nicht, damit die Seite auf dem Smartphone scrollbar bleibt.

**Lizenzhinweis:** Charts mit ICE-BofA-Spreads (HY-OAS u. a.) nur für dich selbst verwenden, nicht veröffentlichen oder weitergeben.

## 7. Ansichten

1. **Übersicht:** Ampel, Stress-Fallhöhe-Matrix mit 60-Tage-Spur, Konfidenz, Aktualität je Quelle. Auf dem Smartphone lesbar.
2. **Schnelle Marktsignale:** VIX-Termstruktur, VIX/VIX3M, VRP, VVIX, SKEW, USD/JPY.
3. **Marktbreite:** in Phase 1 ohne Datenquelle (O-1); die Ansicht sagt das.
4. **Sentiment und Positionierung:** Positionierung am VIX-Futures-Markt (COT), Margin Debt.
5. **Makro und Liquidität:** Financial-Conditions-Indizes, Stressindizes, Kreditspreads, Zinskurve, Arbeitsmarkt.
6. **Fallhöhe:** Bewertung (CAPE), Margin Debt.
7. **Visualisierung:** Heatmap aller Kennzahlen über die Zeit, Perzentilbänder, Composite-Historie mit markierten Krisen, Regime-Zeitleiste.
8. **Datenstand** und **Erklärungen.**

Hinweis zur Historie: Für vergangene Tage zählt je Beobachtung der neueste veröffentlichte Stand (auch nach späteren Revisionen). Die historische Kurve kann deshalb etwas anders aussehen als das, was man an dem jeweiligen Tag gesehen hätte. Die revisionsgenaue Rückrechnung ist für Phase 2 geplant.
