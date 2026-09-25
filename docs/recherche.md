# Fieberthermometer für US- und globale Aktienmärkte: Indikator-Recherche, Ranking, Risiko-Composite und Dashboard-Spezifikation (Stand 25.09.2026)

Ein brauchbares "Fieberthermometer" ist machbar, aber als Regime- und Risikosteuerungsinstrument, nicht als Crash-Timer: Die besten, kostenlos per API beschaffbaren Größen (VIX-Termstruktur, Variance Risk Premium, High-Yield-Spreads, Financial-Conditions-Indizes, Zinskurve, Arbeitsmarkt-Trigger) messen zuverlässig, *ob* Stress herrscht, sagen aber empirisch nur schwach voraus, *wann* ein Einbruch kommt. Die Forschung (Goyal/Welch 2008, aktualisiert 2024) zeigt, dass die meisten publizierten Renditeprädiktoren out-of-sample versagen. Deshalb empfehle ich zwei getrennte Anzeigen, "akuter Stress" und "Fallhöhe", statt einer multiplizierten FMEA-Risikoprioritätszahl, und dazu ein Validierungsmodul, das jede Signalbehauptung gegen die eigene Historie prüft.

## TL;DR

- **Kernaussage:** Rund 22 Indikatoren in fünf Ebenen reichen: schnelle Markt- und Optionssignale, Marktbreite, Sentiment und Positionierung, Makro und Liquidität, Bewertung als Fallhöhe. Die meisten sind über FRED, Cboe-CSV, CFTC-Socrata, OFR und das EZB-Datenportal kostenlos verfügbar. Eine wichtige Einschränkung ist verifiziert: Laut Hinweis der St. Louis Fed auf FRED gilt für die ICE-BofA-Spreadreihen "Starting in April 2026, this series will only include 3 years of observations".
- **Composite:** Eine RPZ nach dem Muster Bedeutung × Auftreten × Entdeckung ist methodisch schwach, und die AIAG-VDA-FMEA (2019) hat sie in der Automobilpraxis selbst durch die Aufgabenpriorität (Action Priority, AP) ersetzt. Besser ist ein perzentil-normierter, blockweise gemittelter Stress-Composite (optional mit korrelationsgewichteter Aggregation wie beim CISS der EZB). Dazu kommt eine separate Fallhöhe-Achse. Beides wird in einer AP-artigen Matrix mit Regeln kombiniert, nicht per Multiplikation.
- **Aktuelle Lage (24./25.09.2026):** Der akute Stress ist niedrig: VIX 15,67 zum Schluss am 24.09., VIX/VIX3M 0,81 in Contango, HY-OAS 2,68–2,73 %, NFCI −0,564, STLFSI4 −0,79. Die Fallhöhe ist dagegen sehr hoch: Shiller-CAPE rund 40,6–41,3 und damit im 98,8. Perzentil seit 1881, Margin Debt laut Advisor Perspectives (FINRA-Daten, veröffentlicht 17.09.2026) 1,45 Bio. USD (+37,2 % ggü. Vorjahr). Hinzu kommen ein Zinsschock (10-jährige Rendite 5,17 %, nahe 19-Jahres-Hoch; 66 % Wahrscheinlichkeit einer Fed-Zinserhöhung im Oktober) und schwache Breite (nur 29,2 % der S&P-500-Titel über dem 50-Tage-Durchschnitt). Meine Einschätzung: Ampel "Gelb", also erhöhte Verwundbarkeit ohne akuten Auslöser; Absicherungen sind relativ günstig.

## Kurzfazit: wichtigste Erkenntnisse und ehrliche Grenzen

**Recherchiert:**
1. **Die Vorhersagbarkeit von Renditen ist schwach.** Goyal/Welch (2008, Review of Financial Studies) fanden, dass die gängigen Prädiktoren der Aktienrisikoprämie "predicted poorly both in-sample (IS) and out-of-sample (OOS) for 30 years" und einem Anleger mit Echtzeitinformation kein profitables Market Timing ermöglicht hätten. Die Aktualisierung von Goyal/Welch/Zafirov (2024, RFS 37(11), 3490–3557) prüfte 29 neue Variablen aus 26 Papieren mit Stand Ende 2021. Mehr als ein Drittel ist schon in-sample nicht mehr signifikant, und von den übrigen schneidet die Hälfte out-of-sample schlecht ab.
2. **Crash-Wahrscheinlichkeit ist eher vorhersagbar als die Durchschnittsrendite.** Greenwood/Shleifer/You ("Bubbles for Fama", JFE 2019) zeigen: Scharfe Kursanstiege von Branchen (100 % in zwei Jahren) sagen keine niedrigen Durchschnittsrenditen voraus, erhöhen aber die Wahrscheinlichkeit eines Crashs (≥ 40 % Drawdown innerhalb von zwei Jahren) deutlich. Steigt die Überrendite gegenüber dem Markt von 50 % auf 100 %, klettert diese Wahrscheinlichkeit von 20 % auf 53 %. Von 40 US-Episoden crashten 21. Für ein Dashboard folgt daraus: Tail-Wahrscheinlichkeiten modellieren, nicht die Renditehöhe.
3. **Stress-Indizes der Zentralbanken erkennen Stress, prognostizieren ihn aber nur begrenzt.** Der OFR FSI identifiziert Stressepisoden laut OFR-Arbeitspapier in einem Logit-Rahmen gut und geht der Chicago-Fed-Aktivität (CFNAI) im Granger-Sinn voraus. Er ist aber primär ein gleichlaufender Marktstress-Schnappschuss.

**Eigene Einschätzung:**
- Der realistische Nutzen liegt in drei Bereichen: Regime-Erkennung (ruhig, erhöhte Anfälligkeit, akuter Stress), Positionsgröße und Short-Vol-Exposure sowie die Frage, wann Absicherungen relativ billig sind. Präzises Crash-Timing ist nicht erreichbar.
- Die gefährlichsten Einbrüche der jüngsten Zeit waren exogene Schocks mit kurzer Vorlaufzeit: Covid 2020, der Yen-Carry-Unwind im August 2024, der Zollschock im April 2025 und der Iran-Krieg ab Ende Februar 2026. Hier helfen vor allem schnelle Optionsmarktsignale, die Fallhöhe (wie weit kann es fallen) und vorausschauend eingekaufte Konvexität, nicht Makro-Vorlaufindikatoren.

## 1. Kriterienset (verbessert gegenüber "Aussagekraft, Beschaffbarkeit, Schnelligkeit")

| Kürzel | Kriterium | Gewicht | Begründung |
|---|---|---|---|
| E | Evidenz und Wirkmechanismus (peer-reviewed, Out-of-Sample, plausibler ökonomischer Kanal) | 25 % | Wichtigster Schutz gegen Data-Mining und das Goyal/Welch-Problem |
| V | Vorlauf vor Drawdowns (Tage/Wochen/Monate) und Stabilität des Vorlaufs | 15 % | Ein Signal ohne stabilen Vorlauf ist nur Beschreibung |
| B | Beschaffbarkeit: Kosten, offizielle API, Lizenz, Zuverlässigkeit | 15 % | Voraussetzung für ein MVP ohne Scraping |
| A | Aktualität: Frequenz plus Veröffentlichungsverzug | 10 % | Für einen Optionshändler zählen Tage |
| H | Länge der Historie (≥ 20 Jahre mit mehreren Krisen ideal) | 10 % | Nötig für Perzentile und Backtest |
| I | Inkrementelle Information (geringe Redundanz) | 15 % | Verhindert Doppelzählung desselben Faktors |
| O | Relevanz für Optionshorizonte (1 Tag bis 6 Monate) und Hedging-Entscheidungen | 10 % | Zielgruppe |

Zusätzlich markiert werden, aber nicht gewichtet: Revisionsanfälligkeit (Point-in-Time nötig?), Wartungsaufwand und Strukturbruchrisiko (QE, 0DTE, Passivierung).

## 2. Ranking-Tabelle (Scores 1–5; Gesamt = gewichteter Score × 20, Skala 0–100)

*Alle Scores sind eigene Einschätzung auf Basis der Recherche. Horizont: K = kurzfristig (Tage bis 4 Wochen), M = mittelfristig (1–6 Monate), L = langfristig (über 1 Jahr).*

| # | Indikator | E | V | B | A | H | I | O | Gesamt | Horizont | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | VIX/VIX3M (plus VIX9D/VIX) | 4 | 2 | 5 | 5 | 4 | 4 | 5 | 81 | K | Kern |
| 2 | HY-OAS (plus CCC-minus-BB-Differenz) | 5 | 3 | 3 | 5 | 3 | 4 | 4 | 79 | K/M | Kern |
| 3 | Variance Risk Premium (VIX minus realisierte 21-Tage-Vola) | 3 | 2 | 5 | 5 | 5 | 4 | 5 | 78 | K | Kern |
| 4 | Aktien-Anleihen-Korrelation (63 Tage, SPY vs. 10-jährige Treasuries) | 3 | 2 | 5 | 5 | 5 | 4 | 4 | 76 | K/M | Kern |
| 5 | NFCI / ANFCI | 4 | 3 | 5 | 3 | 5 | 3 | 3 | 75 | M | Kern |
| 6 | Erstanträge (4-Wochen-Durchschnitt, Veränderung ggü. Tief) | 4 | 3 | 5 | 4 | 5 | 3 | 2 | 75 | M | Kern |
| 7 | VIX-Niveau (Perzentil) | 4 | 1 | 5 | 5 | 5 | 2 | 5 | 74 | K | Kern |
| 8 | 10y−3m-Spread plus Re-Steepening-Flag | 3 | 3 | 5 | 5 | 5 | 4 | 1 | 73 | L | Kern |
| 9 | RSP/SPY (Equal- vs. Cap-Weight) | 3 | 3 | 5 | 5 | 4 | 3 | 3 | 72 | M | Kern |
| 10 | Dollar breit / USD/JPY (5-Tage-Veränderung, Vola) | 3 | 2 | 5 | 5 | 4 | 4 | 3 | 72 | K | Kern |
| 11 | VVIX | 3 | 2 | 5 | 5 | 3 | 3 | 5 | 71 | K | Kern |
| 12 | ECB CISS (Euroraum) | 4 | 2 | 4 | 4 | 5 | 3 | 2 | 69 | K/M | Kern (global) |
| 13 | Excess Bond Premium (Fed) | 4 | 4 | 4 | 1 | 5 | 3 | 1 | 67 | M/L | Kern |
| 14 | OFR FSI (inkl. Regionen) | 4 | 2 | 4 | 4 | 4 | 2 | 3 | 66 | K | Kern (global) |
| 15 | Anteil über 200-/50-Tage-Linie (selbst berechnet) | 3 | 3 | 2 | 5 | 3 | 4 | 4 | 66 | M | Kern |
| 16 | Sahm-Regel in Echtzeit | 4 | 2 | 5 | 2 | 5 | 3 | 1 | 66 | M | Kern |
| 17 | Absorption Ratio / Turbulence (selbst berechnet) | 3 | 2 | 4 | 5 | 4 | 3 | 3 | 66 | K/M | Nice to have |
| 18 | STLFSI4 | 4 | 2 | 5 | 3 | 4 | 2 | 2 | 65 | M | Kern (Redundanz-Check) |
| 19 | SOFR − IORB (Repo-Stress) | 3 | 2 | 5 | 5 | 1 | 4 | 2 | 64 | K | Kern |
| 20 | Shiller-CAPE / Excess CAPE Yield | 4 | 1 | 4 | 2 | 5 | 4 | 1 | 63 | L | Kern (Fallhöhe) |
| 21 | MOVE | 3 | 2 | 2 | 5 | 4 | 4 | 3 | 63 | K | Nice to have (lizenzpflichtig) |
| 22 | Cboe SKEW | 2 | 1 | 5 | 5 | 5 | 3 | 3 | 63 | K | Nice to have |
| 23 | CFTC COT (VX-, ES-Futures) | 2 | 2 | 5 | 3 | 4 | 3 | 3 | 60 | M | Kern (Positionierung) |
| 24 | AAII Bull-Bear-Spread | 2 | 2 | 3 | 4 | 5 | 3 | 2 | 56 | K/M | Kern (Kontraindikator) |
| 25 | Dealer-GEX (aus ThetaData) | 2 | 1 | 3 | 5 | 2 | 3 | 5 | 55 | K | Nice to have |
| 26 | Put/Call-Ratios | 2 | 1 | 3 | 5 | 4 | 2 | 3 | 52 | K | Nice to have |
| 27 | FINRA Margin Debt (ggü. Vorjahr, relativ zur Marktkapitalisierung) | 2 | 2 | 3 | 1 | 4 | 2 | 1 | 43 | L | Kern (Fallhöhe, Kontext) |

**Verworfen bzw. nicht im Composite, jeweils mit Begründung (eigene Einschätzung):**
- **Hindenburg Omen:** viele Fehlalarme, willkürliche Schwellen, kein ökonomischer Mechanismus. Höchstens als Kuriosität.
- **CNN Fear & Greed:** Ein Aggregat aus Größen, die ohnehin im Set sind (Put/Call, Junk-Bond-Nachfrage, Breite, VIX); Doppelzählung, keine offizielle API.
- **Buffett-Indikator, Tobin's Q:** stark redundant mit dem CAPE, zusätzlich revisionsanfällig (Z.1, BIP).
- **"Net Liquidity" (Fed-Bilanz − TGA − RRP):** populär, aber überwiegend Scheinkorrelation mit Trendlaufzeiten. Keine robuste Out-of-Sample-Evidenz gefunden; allenfalls als Kontextpanel.
- **Rezessionswahrscheinlichkeit der NY Fed:** keine eigene Information, da eine monotone Transformation des 10y−3m-Spreads. Nur als Übersetzung anzeigen.
- **LPPLS / Financial Crisis Observatory:** interessant, aber die Parameterschätzung ist instabil und schwer out-of-sample validierbar. Nur als optionales Forschungspanel.
- **Citi Economic Surprise, Goldman-/Bloomberg-FCI, EPFR:** kostenpflichtig. Freie Ersatzgrößen sind NFCI/ANFCI (statt GS-FCI) und für Überraschungen eine selbst gebaute Abweichung von Konsens bzw. Nowcast (z. B. GDPNow-Revisionen).

## 3. Was die Episoden lehren (Evidenz zum Vorlauf)

**Recherchierte Episoden 2026:**
- **Iran-Krieg:** Die Kämpfe begannen mit US-israelischen Angriffen am 28.02.2026. Der S&P 500 lag laut Ed Yardeni (Yardeni Research, zitiert von Fortune am 30.03.2026) 8,7 % unter seinem Rekordhoch vom 27.01.; das IO Fund beziffert den Rückgang bis zum Tief am 30.03. auf 9,7 %. Der VIX erreichte laut CNBC (Live-Updates vom 07.04.2026) am 27.03.2026 sein Hoch mit 31,65 intraday und schloss an diesem Tag bei 31,05. Die Straße von Hormus war faktisch geschlossen, der Ölpreis stieg innerhalb von zwei Wochen um über 40 % (Fortune, 14.03.2026). Nach der Waffenruhe vom 07.04. stand der S&P 500 laut 24/7 Wall St. am 16.04.2026 auf Rekordhoch; die von StockCram genannten rund 11 % Anstieg binnen neun Tagen sind nicht primär belegt.
- **29.07.2026:** Der Dow fiel um 1.153 Punkte (−2,19 %), der S&P 500 um 1,52 %. Auslöser waren eine falkenhafte Fed mit drei Gegenstimmen zugunsten einer Zinserhöhung, schwache SK-Hynix-Zahlen und ein iranischer Angriff (Chamberlin Financial, Sekundärquelle).
- **September 2026:** Die 10-jährige Rendite liegt "near 19-year highs", die Wahrscheinlichkeit einer Oktober-Zinserhöhung laut CME FedWatch bei 66 % (Schwab, 25.09.2026, 9:13 ET).

**Einschätzung zu den historischen Episoden (nicht einzeln in dieser Recherche nachgeprüft; vor Verwendung im Backtest mit Daten belegen):**
- **Kreditgetriebene Abschwünge (2000–02, 2007–09):** HY-Spreads, Excess Bond Premium, Zinskurve und Arbeitsmarkt liefen Monate voraus. Die Zinskurve invertierte lange vorher; der Bärenmarkt setzte typischerweise *nach* dem Re-Steepening ein.
- **Liquiditäts- und Positionierungsschocks (1987, 1998, Februar 2018, August 2024):** Makro-Vorlauf gleich null. Nur Optionsmarkt (Termstruktur, VVIX, Short-Vol-Positionierung im VX-COT) und Funding-Signale (Carry, Cross-Currency-Basis) zeigten Tage vorher Anspannung.
- **Exogene Schocks (März 2020, April 2025, März 2026):** kein verlässlicher Vorlauf. Nützlich sind Fallhöhe und bereits gekaufte Konvexität.
- **2022 (Inflations- und Zinsregime):** Die Aktien-Anleihen-Korrelation drehte positiv, klassische Stressindizes blieben moderat. Genau dieses Regime ähnelt der aktuellen Lage mit steigenden Renditen und Zinserhöhungserwartungen.

**Konsequenz:** Ein Composite braucht einen schnellen Block für Schocks, einen Kredit- und Makroblock für langsame Abschwünge und eine Fallhöhe-Achse, und diese Blöcke dürfen nicht zu einer Zahl verschmolzen werden.

## 4. Zusammengesetzter Risiko-Indikator

### 4.1 FMEA-Analogie: ehrliche Prüfung

- **AP statt RPZ:** Laut MetricMech hat das gemeinsame AIAG-VDA-FMEA-Handbuch (1. Auflage, 2019) die RPZ durch die Aufgabenpriorität (Action Priority, AP) ersetzt. Die AP stuft jede Fehlerart anhand einer definierten Tabelle aller 1.000 Kombinationen aus Bedeutung, Auftreten und Entdeckung als Hoch/Mittel/Niedrig ein, wobei die Bedeutung dominiert. Das Handbuch selbst habe ich nicht eingesehen; die Quellen sind Beratungs- und Softwareseiten, die übereinstimmend berichten.
- **Bekannte Schwäche:** Sie wird dort am Beispiel S=10/O=2/D=2 (RPZ 40) gegenüber S=3/O=5/D=4 (RPZ 60) illustriert: Der katastrophale Fall erhält die niedrigere Zahl.
- **Übertragung auf Märkte (eigene Bewertung):**
  - *Bedeutung = Fallhöhe:* sinnvoll.
  - *Auftreten = aktueller Stress:* sinnvoll.
  - *Entdeckung = Früherkennbarkeit:* konzeptionell fehlplatziert. Sie ist keine Eigenschaft des Marktzustands, sondern des Messinstruments, also Vorlauf und Datenverzug. Sie gehört in die Gewichtung bzw. in einen Konfidenzwert, nicht in das Risikoprodukt.
  - *Multiplikation ordinaler Skalen:* mathematisch unzulässig. Gleiche Produkte können völlig verschiedene Lagen bedeuten, etwa hohe Bewertung ohne Stress (2021) und niedrige Bewertung mit akutem Stress (März 2009).
- **Fazit:** Die RPZ nicht übertragen, die AP-Idee schon. Eine zweidimensionale Matrix aus Stress und Fallhöhe mit expliziten Regeln, bei denen der akute Stress dominiert.

### 4.2 Vergleich der Aggregationsmethoden

| Methode | Vorbild | Vorteil | Nachteil | Empfehlung |
|---|---|---|---|---|
| z-Score-Mittel | NFCI (105 Messgrößen, Mittel 0, Standardabweichung 1 seit 1971) | einfach, transparent | empfindlich für Ausreißer und Nicht-Normalität | nur mit Winsorisierung |
| Perzentil-Composite | – | robust, einheitliche Skala 0–100 | verliert Information über Extreme | **Basis** |
| PCA | STLFSI4 (18 Wochenreihen) | extrahiert den gemeinsamen Faktor | Gewichte driften, Vollstichprobe erzeugt Look-ahead | nur expandierend schätzen |
| Dynamisches Faktormodell | OFR FSI (33 Variablen, 5 Kategorien, 3 Regionen) | verarbeitet unterschiedliche Historienlängen | aufwendig | extern übernehmen statt nachbauen |
| Portfolio-/Korrelationsaggregation | ECB CISS | Stress zählt stärker, wenn Segmente gleichzeitig brennen | Korrelationsschätzung verrauscht | **Option für Stufe 2** |
| Diffusionsindex | – | intuitiv ("wie viele auf Rot") | ignoriert Intensität | **ergänzend anzeigen** |
| Logit/Probit auf Drawdown-Ereignisse | Estrella/Mishkin-Probit der NY Fed | liefert kalibrierte Wahrscheinlichkeiten | wenige Ereignisse, Overfitting | **Stufe 3, streng walk-forward** |
| Markov-Regime-Switching | Chauvet/Piger-Rezessionswahrscheinlichkeit | Regime statt Punktprognose | Regime werden rückwirkend geglättet ("smoothed") | nur gefilterte (Echtzeit-)Wahrscheinlichkeiten nutzen |
| Machine Learning | – | nichtlinear | bei rund 10–15 unabhängigen Crash-Ereignissen seit 1990 fast garantiert overfittet | nicht im MVP |

Das Probit der NY Fed laut Estrella/Mishkin (1998) lautet P(Rezession in 12 Monaten) = Φ(−0,5333 − 0,6629 × Spread10y−3m) (Central Bank Watch, Sekundärquelle).

### 4.3 Konkrete Empfehlung

**Schritt 1: Normierung (jede Einzelreihe x)**
- Vorzeichen so ausrichten, dass hoch = Stress (z. B. RSP/SPY-Momentum und Breite invertieren).
- Transformation je Typ: Niveaus (VIX, OAS), Veränderungen (20-Tage-Veränderung des OAS, 5-Tage-Veränderung von USD/JPY) oder Verhältnisse (VIX/VIX3M).
- Perzentil pₜ = Rang von xₜ in der Vergangenheit bis t, ohne Werte nach t. Fenster: expandierend mit mindestens 5 Jahren Vorlauf. Zusätzlich rollierend über 10 Jahre (≈ 2.520 Handelstage), um Strukturbrüche abzufedern (QE-Ära, 0DTE, Passivierung). Anzeigen würde ich beide; in den Composite geht das 10-Jahres-Fenster.
- Ausnahme HY-OAS: Wegen der Drei-Jahres-Grenze auf FRED muss die Historie ab sofort **lokal archiviert** werden. Ältere Daten sind lizenzrechtlich nur direkt von ICE nutzbar ("Reproduction … prohibited except with the prior written permission of ICE Data Indices").

**Schritt 2: Blockbildung gegen Doppelzählung**
- Fünf Blöcke: Volatilität/Optionen, Kredit/Funding, Makro/Financial Conditions, Breite/Internals, Positionierung/Sentiment.
- Innerhalb eines Blocks wird gemittelt: Blockscore = Median der Perzentile, damit die Mehrheit zählt und nicht ein Ausreißer.
- Zwischen den Blöcken bekommen zunächst alle das gleiche Gewicht. Eigene Einschätzung: Gleichgewichtung ist out-of-sample meist robuster als optimierte Gewichte, weil die Schätzfehler bei so wenigen Ereignissen dominieren.

**Schritt 3: Stress-Composite**
- Stufe 1: S = Mittel der fünf Blockscores.
- Stufe 2 (CISS-artig): S = √(sᵀ Cₜ s)/‖s‖ mit s = Vektor der Blockscores und Cₜ = EWMA-Korrelationsmatrix (Halbwertszeit 60 Tage). Gleichzeitiger Stress in mehreren Blöcken wird so verstärkt, isolierter Stress gedämpft.
- Glättung: EWMA mit Halbwertszeit 3 Tagen für den schnellen Block, 10 Tagen für den Composite.
- Fehlende bzw. verzögerte Daten: Letzten verfügbaren Wert *zum Veröffentlichungszeitpunkt* verwenden (siehe Schritt 6).

**Schritt 4: Fallhöhe-Score (getrennt)**
- Perzentile von Excess CAPE Yield (invertiert), Margin Debt relativ zur Marktkapitalisierung bzw. ggü. Vorjahr, Top-10-Konzentration, HY-OAS-Niveau (sehr eng = Selbstgefälligkeit), AAII-Extreme, Short-Vol-Positionierung.
- Gemittelt; Halbwertszeit 20 Tage.

**Schritt 5: AP-artige Ampelmatrix (Regeln statt Produkt)**
- **Rot:** Stress-Composite ≥ 90. Perzentil, oder VIX/VIX3M > 1 an 3 Tagen in Folge, oder HY-OAS-Anstieg über 20 Tage im ≥ 95. Perzentil.
- **Orange:** Stress ≥ 75 und Fallhöhe ≥ 80, oder Stress ≥ 80.
- **Gelb:** Fallhöhe ≥ 80 bei Stress < 75, oder Diffusionsindex ≥ 40 % der Einzelreihen über dem 80. Perzentil.
- **Grün:** sonst.
- Hysterese: Eine Stufe wird erst verlassen, wenn der Wert 5 Perzentilpunkte unter der Schwelle liegt. Das verhindert Flattern.
- Zusätzlich angezeigt wird ein Konfidenzwert: Anteil der Einzelreihen mit aktuellen Daten, gewichtet mit dem historischen Vorlauf. Hier lebt die "Entdeckung" der FMEA sinnvoll weiter.

**Schritt 6: Look-ahead-Bias vermeiden**
- Jede Reihe mit Veröffentlichungszeitstempel speichern, nicht nur mit Beobachtungsdatum:
  - NFCI erscheint mittwochs 8:30 ET für die Woche bis zum Vorfreitag.
  - COT erscheint freitags 15:30 ET mit Daten vom Dienstag.
  - FINRA Margin Debt erscheint in der dritten Woche des Folgemonats, 4–7 Wochen Verzug.
  - OFR FSI hat zwei Geschäftstage Verzug.
- Makroreihen (Erstanträge, Arbeitslosenquote) als Vintages über ALFRED ziehen. Das SAHMREALTIME-Konzept von FRED ist schon Echtzeit.
- Keine Vollstichproben-Standardisierung. NFCI und STLFSI4 werden selbst rückwirkend neu geschätzt; ALFRED führt Vintages von STLFSI4.

**Schritt 7: Validierung (Backtest-Modul)**
- Ereignisse:
  - (a) S&P-500-Drawdown ≥ 10 % vom laufenden Hoch, beginnend innerhalb der nächsten 63 Handelstage.
  - (b) VIX-Schluss > 30 innerhalb von 21 Tagen.
  - (c) Bärenmarkt ≥ 20 %.
- Walk-forward: ab 2000 jährlich neu kalibrieren, Schwellen nur mit Daten bis t.
- Metriken:
  - AUC/ROC
  - Precision/Recall je Ampelstufe
  - Fehlalarme pro Jahr
  - mittlere Vorlaufzeit bis zum Ereignisbeginn
  - Brier-Score für Logit-Wahrscheinlichkeiten
  - ökonomischer Test: Hedge-Kosten vs. vermiedener Drawdown bei regelbasierter Put-Absicherung, simuliert mit ThetaData-Historie
- Benchmark: naiver VIX-Perzentil-Filter und "immer investiert". Wenn der Composite den naiven VIX-Filter nicht schlägt, ist er Ballast.
- Ehrliche Erwartung: Die Anzahl unabhängiger Ereignisse ist klein. Konfidenzintervalle per Block-Bootstrap angeben.

**Wofür realistisch nützlich (Einschätzung):**
- Regime-Klassifikation
- Skalierung von Short-Vol-Positionen und Gesamtdelta
- Entscheidung, wann Tail-Hedges billig und nötig sind: hohe Fallhöhe und niedriger VIX, also genau jetzt
- Stop-Disziplin bei Rot

**Wofür nicht:** Tagesgenaues Top-Picking, Timing exogener Schocks, Renditeprognosen.

## 5. Aktuelle Lage (Realitätscheck, Stand 25.09.2026)

| Indikator | Wert | Zeitstempel der Quelle | Quelle | Einordnung |
|---|---|---|---|---|
| VIX | 15,67 (+0,49) | Schluss 24.09.2026, 15:15:01 CDT | Yahoo Finance / Cboe | 52-Wochen-Spanne 13,38–35,30; niedrig |
| VIX (vorbörslich) | 15,22 | 25.09.2026, 9:13 ET | Schwab Market Update | – |
| Realisierte 30-Tage-Vola S&P 500 | 10,71 (VIX 15,18) | Schluss 23.09.2026 | StreetStats | VRP ≈ +4,5 Punkte: Optionen relativ teuer ggü. realisierter Vola, absolut aber billig |
| VIX/VIX3M | 0,8069 (14,21/17,61), Contango Tag 116 | Schluss 22.09.2026 | thetrading.tools | Backwardation seit 2010 an nur 8 % der Tage |
| VVIX / SKEW | 86,2 / 144,1 | Schluss 02.09.2026 (Bericht vom 03.09.) | robomacro (Sekundärquelle) | SKEW erhöht: Tail-Nachfrage vorhanden; *veraltet, aktualisieren* |
| MOVE | 95,45 (realisiert 85,00) | Stand um den 24.09.2026, genaues Datum unklar | StreetStats | Anleihevola deutlich über der Aktienvola; passt zum Zinsschock |
| HY-OAS | 2,68 % | Beobachtung 18.09.2026, aktualisiert 21.09., 9:16 CDT | ALFRED/FRED | Sehr eng; Allzeithoch 19,88 (Dez. 2008), März 2020 10,87 |
| HY-OAS / IG-OAS | 2,68 % / 0,77 % | 22.09.2026 | StreetStats (ICE-Daten) | historisch eng |
| HY-OAS | 2,73 % | 23.09.2026 | govspending.org (Sekundärquelle) | leichter Anstieg |
| 10y−3m (T10Y3M) | 0,92 Pp. | um den 23.09.2026 (FRED-Reihe bis 24.09.) | MacroRadar/FRED | nicht invertiert |
| Treasury-Kurve | 2J 4,90 %, 10J 5,12 %, 30J 5,40 % | 23.09.2026 | StreetStats (US Treasury) | 10y−2y ≈ +22 bp |
| 10-jährige Rendite | 5,17 % | 25.09.2026, 9:13 ET | Schwab | "near 19-year highs" |
| NY-Fed-Rezessionswahrscheinlichkeit (12 Monate) | 13,88 % | Daten bis Aug. 2026, Stand 06.09.2026 | EconomicGreenfield (Sekundärquelle der NY Fed) | niedrig |
| NFCI | −0,564 | Woche bis 04.09.2026 | Equibles (FRED-Spiegel) | lockere Bedingungen; FRED hat Daten bis 18.09., den Wert habe ich nicht extrahiert |
| STLFSI4 | −0,7884 | Woche bis 04.09.2026 | Equibles (FRED-Spiegel) | unterdurchschnittlicher Stress |
| OFR FSI | −2,289 | 10.09.2026 (Datumsformat vermutlich MM-TT) | CEIC (Sekundärquelle) | deutlich unter dem Mittel (−1,49); Höchstwert 10,27 im März 2020 |
| ECB CISS (Euroraum) | ≈ 0,03 (Monatsmittel September) | Seite aktualisiert 24.09.2026 | Eco3min (abgeleitet, Sekundärquelle) | unter dem Durchschnitt von 0,16 |
| Sahm-Regel (Echtzeit) | −0,07 Pp. | August 2026, aktualisiert 04.09.2026, 8:39 CDT | FRED SAHMREALTIME | weit unter der Auslöseschwelle 0,50 |
| GDPNow Q3 | 5,1 % | 24.09.2026 | Schwab (Atlanta Fed) | starkes Wachstum, "good is bad" für Zinsen |
| AAII | Bullen 32,7 / Neutral 19,2 / Bären 48,1; Spread −15,4 | Woche bis 23.09.2026 | AAII | Vorwoche Bullen 28,8 % = niedrigster Wert seit rund einem Jahr (Bloomberg: 16-Monats-Tief); kontraindikativ eher positiv |
| Breite | 29,2 % über der 50-Tage-Linie, Index-Perzentil 13 | 23.09.2026 | StreetStats (Snippet) | schwache kurzfristige Breite; S&P 500 bei 7.708,55 aber über der 200-Tage-Linie (7.196,56) |
| Shiller-CAPE | 40,6 (98,8. Perzentil seit 1881, vorläufig) | September 2026 | thetrading.tools (Shiller-Daten) | nur 20 Monate jemals höher (1999/2000/2026); GuruFocus nennt 41,29 per 01.09.; Rekord 44,2 |
| FINRA Margin Debt | 1,45 Bio. USD (+2,6 % ggü. Vormonat, +37,2 % ggü. Vorjahr) | August 2026, veröffentlicht 17.09.2026 | Advisor Perspectives (FINRA-Daten) | Rekordbereich, starkes Wachstum |
| Fed-Pfad | 66 % Wahrscheinlichkeit einer Zinserhöhung im Oktober | 25.09.2026 früh | CME FedWatch via Schwab | Zinserhöhungszyklus |
| Öl WTI / Gold / DXY | 92,54 USD / 4.335,70 USD / 100,98 | 25.09.2026, 9:13 ET | Schwab | – |

**Datenkonflikte und unbestätigte Punkte:**
- Central Bank Watch behauptet, der 3m10y-Spread sei "negative again" und die Rezessionswahrscheinlichkeit liege über 30 %. Das widerspricht den FRED-nahen Werten (T10Y3M ≈ +0,92) und der NY-Fed-Zahl von 13,9 %; vermutlich ist die Seite veraltet. Ich folge FRED und NY Fed.
- Die Angaben zum Fed-Vorsitz ("Fed Chair Warsh") und zum Neustart des Zinserhöhungszyklus stammen aus einem Substack-Marktbericht und sind hier nicht primär verifiziert. Die Zinserhöhungserwartung selbst ist über CME FedWatch/Schwab belegt.
- Die CAPE-Werte weichen je nach Anbieter ab (40,6 vs. 41,29): unterschiedliche Stichtage und vorläufige Gewinndaten.

**Was das Gesamtbild signalisiert (eigene Einschätzung):**
- Nach Ebenen:
  - Schnelle Signale: grün.
  - Kredit: grün, und zwar "zu grün".
  - Makro: grün, mit starkem Wachstum.
  - Breite: gelb.
  - Sentiment: bärisch, kontraindikativ leicht positiv.
  - Fallhöhe: tiefrot.
- Das Hauptrisiko ist kein Kreditunfall, sondern ein **Zins- und Bewertungsschock** wie 2022: Die 10-jährige Rendite liegt bei 5,17 % mit steigender Tendenz, der CAPE bei rund 40 und die Aktien-Anleihen-Korrelation dürfte positiv sein (vor Verwendung selbst berechnen). Die Kombination aus MOVE bei rund 95 und VIX bei rund 15 zeigt, dass der Anleihemarkt mehr Unsicherheit einpreist als der Aktienmarkt.
- Matrix-Ergebnis: **Gelb** (Fallhöhe ≥ 80, Stress < 75).
- Konsequenz für einen Optionshändler: Tail-Absicherung und Put-Spreads sind bei VIX-Perzentilen im unteren Bereich vergleichsweise günstig. Aggressives Short-Vol-Exposure ist bei dieser Fallhöhe schlecht bezahlt. Ein Übergang zu Orange oder Rot würde vor allem durch VIX/VIX3M > 1, einen Sprung der HY-OAS über ~3,5 % oder eine Zinsauktion bzw. einen Renditesprung mit gleichzeitig fallenden Aktien angezeigt.

## 6. Dashboard-Spezifikation

### 6.1 Datenquellen-Matrix (MVP = kostenlos und per API)

*Verifiziert = in dieser Recherche bestätigt; (*) = ID aus dem FRED- bzw. Anbieterkatalog, vor der Implementierung per API-Metadatenabruf prüfen.*

| Indikator | Quelle / Endpoint | Serien-ID / Ticker | Kosten | Frequenz / Verzug | Historie ab | Lizenz / Hinweis |
|---|---|---|---|---|---|---|
| VIX, VIX3M, VIX9D, VVIX, SKEW | Cboe CSV `cdn.cboe.com/api/global/us_indices/daily_prices/{SYMBOL}_History.csv` | VIX, VIX3M (verifiziert), VIX9D, VVIX, SKEW (*) | frei | täglich, Schlusskurs | VIX3M ab 04.12.2007 | Cboe-Nutzungsbedingungen; FRED VIXCLS als Fallback ("Reprinted with permission") |
| VX-Futures-Termstruktur | Cboe CFE Historical Data (CSV je Kontrakt) oder IBKR | VX | frei / IBKR-Abo | täglich / live | 2004 | – |
| HY-, IG-, BBB-, CCC-OAS | FRED API | BAMLH0A0HYM2, BAMLC0A0CM, BAMLC0A4CBBB, BAMLH0A3HYC, BAMLH0A1HYBB (alle verifiziert) | frei | täglich, rund 1 Tag Verzug | **nur 3 Jahre seit April 2026** | ICE-Copyright; lokal archivieren, keine Weitergabe |
| NFCI, ANFCI, Subindizes | FRED API | NFCI, NFCILEVERAGE (verifiziert), ANFCI (*) | frei | wöchentlich, Mi 8:30 ET | 1971 | Zitierpflicht |
| STLFSI4 | FRED / ALFRED | STLFSI4 (verifiziert) | frei | wöchentlich | 1993 | Vintages in ALFRED |
| OFR FSI | financialresearch.gov (Button "Download all data") | – | frei | täglich, 2 Geschäftstage Verzug | 2000 | Die OFR-REST-API (`data.financialresearch.gov/v1`) deckt nachweislich den Short-term Funding Monitor ab; für den FSI **nicht belegt**. Download-URL vor der Implementierung prüfen |
| ECB CISS | ECB Data Portal SDMX `data-api.ecb.europa.eu/service/data/CISS/D.U2.Z0Z.4F.EC.SS_CIN.IDX` | SS_CIN (neu); SS_CI endete am 02.05.2025 | frei | täglich (Vortag) | 1999 | Endpoint nicht live getestet; DBnomics als Spiegel |
| 10y−3m, 10y−2y | FRED | T10Y3M (verifiziert, ab 1982), T10Y2Y (*) | frei | täglich | 1982 / 1976 | – |
| Sahm-Regel in Echtzeit | FRED | SAHMREALTIME (verifiziert) | frei | monatlich (Arbeitsmarktbericht) | 1959 | nächste Veröffentlichung 02.10.2026 |
| Erstanträge | FRED / ALFRED | ICSA, IC4WSA (*) | frei | wöchentlich, Do | 1967 | revisionsanfällig: ALFRED |
| Realzins, Term Premium | FRED | DFII10, THREEFYTP10 (Kim-Wright) (*) | frei | täglich | 2003 / 1990 | ACM-Prämie direkt von der NY Fed |
| Dollar, SOFR, IORB | FRED | DTWEXBGS, SOFR, IORB (*) | frei | täglich | 2006 / 2018 / 2021 | – |
| Excess Bond Premium | Federal Reserve (FEDS Notes, CSV) | EBP | frei | monatlich | 1973 | Download-URL prüfen |
| COT (ES, VX) | CFTC Socrata `publicreporting.cftc.gov/resource/{id}.json` | Legacy ab 15.01.1986; TFF ab 13.06.2006; Disaggregated Combined `kh3c-gbw2`, Futures Only `72hh-3qpy`; TFF-IDs (*) | frei, keine Registrierung | wöchentlich, Fr 15:30 ET (Daten vom Dienstag) | 1986/2006 | `$limit` bis 50.000 pro Abfrage |
| AAII | aaii.com (Excel-Historie) | – | teils mitgliederpflichtig | wöchentlich, Do | 1987 | **optional**, Scraping bzw. manuell |
| Margin Debt | FINRA Margin Statistics | – | frei (Excel) | monatlich, 3. Woche des Folgemonats | 1997 | **optional**, halbautomatisch |
| Shiller-CAPE | Shiller-Datensatz (ie_data.xls) | – | frei | monatlich, jüngste Werte vorläufig | 1881 | **optional**, Datei-Download |
| RSP/SPY, IWM, XLY/XLP, SMH, KRE, EEM, ACWI, HYG/LQD | IBKR TWS/Gateway API (`reqHistoricalData`) | Ticker | im Marktdaten-Abo | live / täglich | je nach ETF | eigenes Abo; Yahoo nur als inoffizieller Fallback |
| Breite (% > 50/200-Tage-Linie) | selbst berechnet aus Kursen der Indexmitglieder (IBKR) | – | Abo | täglich | abhängig von Point-in-Time-Mitgliederlisten | **Survivorship-Bias**, falls aktuelle Mitgliederliste verwendet wird |
| VRP, Skew, Termstruktur, GEX | ThetaData | SPX-/SPY-Optionen | Options Value 40 USD, Standard 80 USD, Pro 160 USD pro Monat (4/8/12 Jahre Historie) | intraday / täglich | 4–12 Jahre | Privatlizenz "no redistribution or business use"; Indexdaten (SPX-Underlying) brauchen ein separates Index-Abo |
| V2X, Nikkei VI, MOVE | IBKR / ICE | V2X, JNIV, MOVE | Abo bzw. ICE-Lizenz | live | – | **optional** |

### 6.2 Architektur (eigene Empfehlung für TrueNAS)

- **Ingestion:** Python-Pakete je Quelle (FRED, Cboe, CFTC, OFR, ECB, IBKR, ThetaData). Scheduler: *Prefect* (UI, Retries, Logs) oder schlanker *APScheduler/cron* im Container. Jeder Abruf schreibt Rohdaten unverändert mit `observation_date`, `published_at` und `retrieved_at`.
- **Speicher:**
  - **DuckDB + Parquet** (Bronze → Silber → Gold) ist die empfohlene Hauptlösung: spaltenorientiert, dateibasiert, ideal für Perzentil-Rechnungen und Backtests mit Numba/Pandas.
  - **Postgres/TimescaleDB** nur, wenn mehrere Dienste gleichzeitig schreiben oder Grafana direkt abfragen soll.
- **Rechenschicht:** Perzentile, Blockscores, CISS-Aggregation und Ampelregeln als reine Funktionen mit Stichtag t (erzwingt Point-in-Time).
- **Frontend:**
  - **Dash (Plotly)** für das interaktive Dashboard: Callbacks, Heatmaps, Crossfilter, produktionsfähiger als Streamlit.
  - **Streamlit** für schnelle Forschungsseiten (Backtest-Ansicht).
  - **Grafana** optional für Betriebsmonitoring (Datenfrische, Pipeline-Fehler) und Alerting.
- **Alerts:** ntfy (selbst gehostet), Telegram oder E-Mail bei Ampelwechsel, Einzelreihen-Perzentil ≥ 95, VIX/VIX3M > 1 und bei **Datenveraltung**. Das Veralten wird oft vergessen, etwa beim Wegfall der ICE-Historie.
- **Deployment:** Docker Compose auf TrueNAS SCALE, Reverse Proxy mit Authentifizierung. IBKR Gateway in eigenem Container mit Neustart-Logik.

### 6.3 Ebenen und Ansichten

1. **Übersicht:** Ampelmatrix aus Stress (x) und Fallhöhe (y) mit aktuellem Punkt und 60-Tage-Spur; Konfidenzwert; letzte Aktualisierung je Quelle.
2. **Schnelle Marktsignale:** VIX-Termstruktur-Kurve (9D/30D/3M/6M plus VX-Futures), VIX/VIX3M-Historie mit Backwardation-Schattierung, VRP, VVIX, SKEW, MOVE, USD/JPY.
3. **Marktbreite:** RSP/SPY, % > 50/200-Tage-Linie, Zykliker/Defensive, Small/Large, SMH relativ, KRE.
4. **Sentiment und Positionierung:** AAII-Spread, VX-COT der Non-Commercials (Perzentil über 3 Jahre), Margin Debt ggü. Vorjahr.
5. **Makro und Liquidität:** NFCI/ANFCI, STLFSI4, OFR FSI mit Regionen- und Kategoriezerlegung, CISS, HY-OAS plus CCC−BB, EBP, SOFR−IORB, Zinskurve mit Re-Steepening-Marker, Sahm-Regel, Erstanträge.
6. **Fallhöhe:** CAPE bzw. Excess CAPE Yield, Konzentration, Margin Debt relativ zur Marktkapitalisierung.
7. **Visualisierung:**
   - Heatmap (Indikatoren × Zeit, Perzentilfarben)
   - Perzentil-Bänder (10/50/90) je Reihe
   - Sparklines mit Zeitstempel
   - Composite-Historie mit markierten Krisen (1998, 2000–02, 2007–09, 2011, 2015/16, Feb. 2018, Q4 2018, März 2020, 2022, Aug. 2024, Apr. 2025, Feb.–Apr. 2026)
   - Regime-Zeitleiste
8. **Backtest und Validierung:**
   - Ereigniswahl
   - ROC-Kurve
   - Precision/Recall je Schwelle
   - Vorlauf-Histogramm
   - Fehlalarm-Liste
   - Walk-forward-Stabilität der Gewichte
   - Vergleich mit dem naiven VIX-Filter

### 6.4 MVP und Erweiterungen

- **MVP (kostenlos, API-stabil):** Cboe-CSV (VIX-Familie), FRED (OAS, NFCI/ANFCI, STLFSI4, Zinskurve, SAHMREALTIME, Erstanträge, Dollar, SOFR/IORB), CFTC Socrata (COT), ECB SDMX (CISS), OFR-Download (FSI); dazu ETF-Kurse über das vorhandene IBKR-Abo.
- **Erweiterung 1 (vorhandene Abos):** ThetaData für VRP, Skew, Termstruktur, GEX und den Backtest von Put-Absicherungen; IBKR für V2X, Nikkei VI und VX-Futures live.
- **Erweiterung 2 (Scraping bzw. manuell, klar markiert):** AAII, FINRA Margin Debt, Shiller-CAPE, Konzentration im S&P 500.
- **Erweiterung 3 (kostenpflichtig):** vollständige ICE-OAS-Historie, MOVE, iTraxx/CDX, EPFR, Citi-Surprise.

## Caveats

- **Sekundärquellen:** Mehrere aktuelle Werte (NFCI, STLFSI4, OFR FSI, CISS, VVIX/SKEW, Breite, NY-Fed-Wahrscheinlichkeit) stammen aus Spiegelseiten, weil die Primärseiten Werte per JavaScript laden oder den Abruf blockierten. Vor produktiver Nutzung direkt per API gegenprüfen. VVIX und SKEW sind drei Wochen alt.
- **FMEA-Handbuch:** Den Ersatz der RPZ durch die AP im AIAG-VDA-Handbuch 2019 habe ich über übereinstimmende Praxisquellen bestätigt, nicht über das Handbuch selbst.
- **Historische Episoden:** Die Aussagen zu den Episoden vor 2026 sowie die Einzel-Scores sind eigene Einschätzungen. Sie müssen im Validierungsmodul mit echten Daten belegt werden.
- **Nicht verifizierte Lizenzen und Kosten:** Lizenzbedingungen der Cboe-CSV-Nutzung, IBKR-Abokosten für Cboe-Indizes und V2X sowie die Serien-IDs mit (*) habe ich nicht verifiziert.
- **Grundsätzliche Grenze:** Jedes Composite ist an wenigen unabhängigen Krisen kalibriert. Strukturbrüche (0DTE, Passivierung, Fed-Put vs. Inflationsregime) können historische Beziehungen außer Kraft setzen. Das aktuelle Umfeld mit steigenden Zinsen und niedrigem Kreditstress ist genau so ein Regime, in dem kreditlastige Indikatoren zu spät anschlagen.
