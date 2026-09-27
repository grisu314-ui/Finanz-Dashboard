# CISS Euroraum

## Kurzinfo
Systemischer Stress im Finanzsystem des Euroraums laut EZB (Composite Indicator of Systemic Stress, täglich, 0 bis 1). Hoch = mehr Stress.

## Was die Kennzahl misst
Der CISS der Europäischen Zentralbank fasst Stressmaße aus fünf Marktsegmenten zusammen: Devisen-, Aktien-, Geld- und Anleihemarkt sowie Finanzintermediäre. Die Besonderheit ist die Zusammenfassung nach der Portfoliotheorie: Die zeitlich wechselnden Korrelationen zwischen den Segmenten gehen ein, sodass gleichzeitiger Stress in mehreren Märkten stärker zählt als Stress in einem einzelnen (Holló, Kremer, Lo Duca, ECB Working Paper 1426, 2012). Der Wert liegt zwischen 0 und 1. Das Dashboard nutzt die tägliche Reihe mit dem Schlüssel SS_CIN; die ältere Reihe SS_CI endete am 02.05.2025 (Bericht, Abschn. 6.1).

## Warum sie für Marktstress oder Fallhöhe zählt
Der CISS ergänzt die US-lastigen Indizes um den Euroraum und damit um einen Teil der globalen Sicht. Der Bericht führt ihn als globalen Kernindikator mit kurz- bis mittelfristigem Horizont und guter Evidenz (docs/recherche.md, Abschn. 2). Seine Methode ist zugleich das Vorbild für die korrelationsgewichtete Stufe 2 des Composites, die für Phase 2 geplant ist (Abschn. 4.3, Schritt 3).

## So liest du sie
- Ein hohes Perzentil heißt: Der Stress im Euroraum ist hoch und betrifft wahrscheinlich mehrere Märkte zugleich.
- Steigt der CISS ohne die US-Indizes, liegt der Stress eher in Europa.

## Grenzen und Fallstricke
- Europäischer Schwerpunkt: Für den US-Aktienmarkt ist er ein indirektes Signal.
- Einschätzung: Durch die Korrelationsgewichtung kann der CISS in einer Krise sprunghaft steigen, auch wenn einzelne Teilmaße nur mäßig zulegen.
- Die Reihe erscheint mit einem Tag Verzug.

## Quellen
- Holló, Kremer, Lo Duca: CISS – a composite indicator of systemic stress in the financial system, ECB Working Paper Nr. 1426, März 2012 (Kurzfassung über SSRN und das ECB-Verzeichnis, abgerufen 26.09.2026)
- docs/recherche.md, Abschnitte 2, 4.3 und 6.1 (Stand 25.09.2026)
- Source: ECB statistics.
