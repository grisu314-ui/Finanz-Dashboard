# Bedienung: das Dashboard lesen

Stand: 29.09.2026 · Für: dich als Anwender · Status: ⏳ **Zielbild, teilweise umgesetzt.** Seit M6 gibt es Seitenrahmen, Übersicht (Ampel, Stress, Fallhöhe, Konfidenz), Datenstand, Erklärungen und Erklärseiten; die Themen-Ansichten folgen in M7, die übrigen Texte in M8 (`docs/umsetzungsplan.md`). Dieser Text wird bei der Abnahme (M9) gegen die fertige App geprüft und dann auf ✅ gesetzt.

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
| Orange | deutlicher Stress, vor allem zusammen mit hoher Fallhöhe, oder ein ausgelöstes Rezessionssignal (Sahm-Regel), während der S&P 500 unter seiner 200-Tage-Linie liegt |
| Rot | akuter, breiter Stress oder ein schnelles Warnsignal (z. B. Volatilitätskurve invertiert) |

Gelb gibt es außerdem bei einem Rezessionssignal vom Arbeitsmarkt ohne Abwärtstrend (SOS-Indikator, Sahm-Regel). Die Rezessionsregeln gelten, solange ihre Werte die Schwellen erfüllen, und bleiben nach Rezessionen oft bis in die Erholung hinein aktiv (Erklärseite „Ampel“).

- **Hysterese:** Eine Stufe wird erst verlassen, wenn der Wert klar unter die Schwelle fällt. Das verhindert tägliches Hin- und Herspringen.
- **Konfidenz:** Anteil der Kennzahlen mit aktuellen Daten, gewichtet nach ihrem historischen Vorlauf. Niedrige Konfidenz heißt: Die Ampel steht auf dünner Datenbasis.
- In Phase 1 fehlen einzelne Bausteine sichtbar, z. B. der Block „Positionierung/Sentiment“ (Phase 2), im Block „Breite“ der Anteil der Aktien über ihrer 50/200-Tage-Linie (E-72); die Kreditspread-Regel und die Kreditspread-Enge in der Fallhöhe nutzen vorerst Moody's Baa statt HY-OAS (E-75, E-85). Die App zeigt das an, statt Lücken zu verstecken.

## 3. Einzelkennzahlen lesen

- **Perzentil:** Anteil der vergangenen Tage im Vergleichsfenster, an denen der Wert niedriger war. „Perzentil 85“ heißt: höher als an etwa 85 % der Vergleichstage. Gerechnet wird nur mit Daten, die am jeweiligen Tag schon veröffentlicht waren.
- **Orientierung:** Bei jeder Kennzahl bedeutet ein hohes Perzentil mehr Stress bzw. mehr Fallhöhe. Wo die Rohgröße andersherum läuft (z. B. Marktbreite), ist sie bereits umgedreht; der Steckbrief sagt es.
- **Farben:** Einzelkennzahlen haben eine neutrale Farbskala nach Perzentil und ab einer festen Schwelle die Markierung **„erhöht“**. Ampelfarben gibt es nur für die Gesamtampel (Entscheidung E-1).
- **Marken neben dem Namen** sagen, wo der Wert zählt (E-81): blau **„Stress · Bereich“** (etwa „Stress · Kredit“), violett **„Fallhöhe“**, grau **„nur Anzeige“** (geht in keinen Score ein), umrandet **„Ampelregel“** (eine Regel der Ampel liest den Wert selbst, z. B. Sahm-Regel oder VIX/VIX3M). Zählt ein Wert doppelt, trägt er zwei Marken: Der Kreditspread Baa ist weit gleich Stress, eng gleich Fallhöhe.
- **Unter Mindesthistorie:** Kennzahlen mit zu kurzer Historie werden angezeigt, zählen aber noch nicht zum Score. Sie sind entsprechend markiert.

## 4. Kurzinfo und Erklärseite

- **ⓘ neben einer Kennzahl:** Maus darüber (Smartphone: antippen) zeigt eine Kurzinfo, was die Kennzahl repräsentiert.
- **Name der Kennzahl anklicken** öffnet die Erklärseite mit:
  - aktuellem Stand und Verlauf
  - ausführlicher Erklärung (was sie misst, warum sie zählt, wie man sie liest, Grenzen)
  - Steckbrief (Quelle, Frequenz, Verzug, Historie)
  - bei Indikatoren „So fließt der Wert in den Bereich ein“: welche Rolle der Wert heute spielt und wie er Schritt für Schritt in den Bereich und in Stress bzw. Fallhöhe eingeht
  - „Schwellen und Farben“: ab wann „erhöht“ bzw. welche Ampelregel gilt
  - Quellen
- Die Seite „Erklärungen“ listet alle Kennzahlen nach Block, dazu die Konzepte Perzentil, Ampel, Konfidenz, Veraltung und Rezessionsbalken.

## 5. Aktualität: Wie alt ist, was ich sehe?

- Jeder Wert zeigt **Beobachtungsdatum**, **Abrufzeitpunkt** (deutsche Zeit mit MEZ/MESZ) und das **Alter** („vor 3 Std.“).
- **Veraltet:** Ist ein Wert älter, als seine Veröffentlichungsfrequenz plus Toleranz erlaubt, erscheint er ausgegraut, schraffiert und mit dem Wort „veraltet“. Veraltete Werte zählen nicht zum Score und senken die Konfidenz.
- **Handelsfreie Tage** (Wochenende, US-Feiertage) sind normal und kein Fehler.
- **Die offene Seite aktualisiert sich alle 5 Minuten** selbst; dein Zoom bleibt dabei erhalten.
- **Banner:**
  - „Migration fehlt“: Nach einem Update wurde die Datenbank nicht auf den neuen Stand gebracht; der Datenabruf ruht, bis die Migration nachgeholt ist (`docs/einrichtung.md`, Fehlersuche).
  - „Worker ohne Lebenszeichen“: Der Datenabruf auf dem Server steht, alle Werte werden nicht mehr aktualisiert.
  - „Keine Verbindung zum Server“: Die Seite erreicht den Server nicht mehr; was du siehst, ist der Stand von der angegebenen Uhrzeit.
- Ansicht **„Datenstand“**: je Quelle letzter erfolgreicher Abruf, letzter Versuch, letzter Fehler.

## 6. Charts bedienen

| Aktion | So geht es |
|---|---|
| Zoomen | mit der Maus einen Rahmen aufziehen; auf dem Smartphone mit dem Finger ziehen. Waagrecht gezogen passt sich die y-Achse an: der kleinste sichtbare Wert unten, der größte oben (E-88). Ziehst du selbst einen Rahmen in der Höhe, bleibt deine Höhe bis zum nächsten Zeitraum-Knopf |
| Verschieben | in der Leiste oben rechts im Chart „Pan“ wählen, dann ziehen |
| Zurücksetzen | Doppelklick bzw. Doppeltippen in den Chart |
| Zeitraum | Buttons „1 M“, „6 M“, „1 J“, „5 J“, „Max“ über dem Chart; die y-Achse passt sich dem gewählten Zeitraum an. Perzentile, Stress, Fallhöhe und Ampelstufe behalten ihre feste Skala |
| Werte ablesen | Maus über die Linie bzw. antippen |
| Bild speichern | Kamera-Symbol in der Chart-Leiste lädt ein PNG herunter; Titel, Quelle und Datenstand sind im Bild enthalten |
| Vollbild | Button „Vollbild“ oben rechts über dem Chart; ESC oder „Schließen“ beendet es |
| Graue Flächen | US-Rezessionen nach der NBER-Datierung, wie in den FRED-Grafiken; nur zur Orientierung, kein Teil eines Scores. Erklärung: Seite „Erklärungen“ → „Rezessionsbalken“ |
| Violette Flächen | markierte Phasen: Backwardation (VIX/VIX3M), Inversion der Zinskurve, Tage mit aktiver Ampelregel (Sahm-Regel, S&P 500 unter der 200-Tage-Linie, SOS-Indikator); die Zeile unter dem Chart sagt, was gemeint ist |
| Ganze Ansicht als PDF | Browser → Drucken → „Als PDF speichern“; die Druckansicht ist hell und ohne Bedienelemente |

Das Scrollrad zoomt bewusst nicht, damit die Seite auf dem Smartphone scrollbar bleibt.

**Lizenzhinweis:** Charts mit ICE-BofA-Spreads (HY-OAS u. a.) nur für dich selbst verwenden, nicht veröffentlichen oder weitergeben.

## 7. Ansichten

1. **Übersicht** (Startseite): Ampel mit den zutreffenden Regeln, Stress und Fallhöhe (geglättet, dazu ungeglättet), Konfidenz und Diffusionsindex; die Ampelmatrix (Stress nach rechts, Fallhöhe nach oben; die farbigen Flächen zeigen, welche Ampelstufe die Regeln aus Stress und Fallhöhe ergeben; die Linie ist die Spur der letzten 60 Handelstage) und die letzte Aktualisierung je Quelle. Die Einzelregeln (Rot über VIX/VIX3M und den Anstieg des Kreditspreads, Orange über die Sahm-Regel im Abwärtstrend, Gelb über Sahm-Regel, SOS-Indikator und Diffusionsindex) stehen nicht in den Flächen; die Ampel kann deshalb höher stehen, als der Punkt vermuten lässt. Auf dem Smartphone lesbar.
2. **Signale:** VIX-Termstruktur (heute), VIX/VIX3M mit violett markierter Backwardation, VIX, VRP, VVIX, SKEW, USD/JPY.
3. **Breite:** fünf Verhältnisse von Nasdaq-Indizes als relative Stärke (gleich- gegen kapitalgewichtet, kleine gegen große Werte, Halbleiter und Regionalbanken gegen den Gesamtmarkt, Zykliker gegen Defensive), je mit Wert und Perzentil; ein niedriger Wert heißt, die breite bzw. zyklische Seite fällt zurück. Der Anteil über der 50/200-Tage-Linie fehlt (keine freie Quelle). Nasdaq-Daten nur für dich selbst verwenden.
4. **Positionierung:** Positionierung am VIX-Futures-Markt (COT) mit Perzentil über 10 und 3 Jahre, Margin Debt; AAII folgt in Phase 2.
5. **Makro:** Financial-Conditions- und Stressindizes, OFR FSI nach Kategorien und Regionen, Kreditspread Baa (Niveau und Anstieg) und HY-OAS-Niveau (im Score; das HY-OAS-Perzentil misst sich vorerst nur an den Jahren seit 2023), CCC − BB (nur Anzeige), Zinskurve mit violett markierter Inversion und dem Datum des letzten Re-Steepening, Sahm-Regel, Abstand des S&P 500 zu seiner 200-Tage-Linie und SOS-Indikator mit violett markierten Tagen aktiver Ampelregel, Erstanträge.
6. **Fallhöhe:** CAPE, Excess CAPE Yield, Aktienquote der Anleger (Anteil der Aktien am Finanzvermögen aus Aktien, Anleihen und Krediten, quartalsweise aus der Fed-Statistik Z.1), Geldmarktfonds im Verhältnis zu Aktien (nur Anzeige), Kreditspread Baa: Enge, Margin Debt, Top-10-Konzentration (Anteil der zehn größten Unternehmen im SPDR S&P 500 ETF, quartalsweise aus den Meldungen an die SEC, rund zwei Monate verzögert).
7. **Visualisierung:**
   - *Stress-Historie mit Krisen:* die dunklen Balken oben markieren Krisen vom Hoch bis zum Tief des S&P 500; Maus darüber nennt Krise und Daten, die Tabelle darunter die Quellen.
   - *Regime-Zeitleiste:* die Ampelstufe an jedem Handelstag.
   - *Heatmap:* jede Zeile ein Indikator, die Farbe sein Perzentil (dunkler = höher); der Schalter wechselt zwischen wöchentlich über die ganze Historie und täglich für die letzten zwei Jahre. Leere Stellen: an diesem Tag nicht gültig (veraltet oder zu kurze Historie). Die farbigen Quadrate vor dem Namen sind die Marken (blau Stress, violett Fallhöhe, grau Ampelregel); Maus darüber nennt auch den Bereich.
   - *Perzentilbänder:* für den gewählten Indikator der Wert, der Bereich zwischen dem 10. und 90. Perzentil seines Vergleichsfensters (hellblau) und der Median (gestrichelt). Liegt der Wert über dem Band, ist er ungewöhnlich hoch.
   - *Sparklines:* alle Indikatoren der letzten 12 Monate auf einen Blick, mit Wert, Perzentil und Stand.
8. **Datenstand** und **Erklärungen.**

In den Ansichten starten die Verläufe mit der ganzen Historie; Grau sind US-Rezessionen. Die Marke „nur Anzeige“ steht bei Reihen, die nicht in Stress oder Fallhöhe eingehen.

Hinweis zur Historie: Für vergangene Tage zählt je Beobachtung der neueste veröffentlichte Stand (auch nach späteren Revisionen). Die historische Kurve kann deshalb etwas anders aussehen als das, was man an dem jeweiligen Tag gesehen hätte. Die revisionsgenaue Rückrechnung ist für Phase 2 geplant. Unter jedem Verlauf steht dazu ein kurzer Hinweis.
