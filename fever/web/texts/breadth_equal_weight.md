# Gleich- gegen kapitalgewichtet

## Kurzinfo
Relative Stärke der 500 größten US-Aktien mit gleichem Gewicht gegenüber denselben nach Börsenwert gewichtet. Niedrig = wenige Schwergewichte tragen den Markt, mehr Stress.

## Was die Kennzahl misst
Zwei Indizes von Nasdaq mit denselben Aktien: Der Nasdaq US 500 Large Cap Index gewichtet die 500 größten US-Werte nach ihrem frei handelbaren Börsenwert, der Nasdaq US 500 Large Cap Equal Weight Index gibt jedem dieser Werte das gleiche Gewicht (Nasdaq Global Indexes, Indexbeschreibung NQUS500LCE). Der Indikator ist die relative Stärke: die Veränderung des Verhältnisses gleichgewichtet zu kapitalgewichtet über ein festes Fenster von Handelstagen (Steckbrief unten). Er ersetzt das Verhältnis der ETFs RSP und SPY aus dem Bericht, für das es keine speicherbare freie Kursquelle gibt (Entscheidung E-68).

## Warum sie für Marktstress oder Fallhöhe zählt
Der Bericht führt RSP/SPY als Kernindikator des Blocks Breite mit mittlerem Horizont von einem bis sechs Monaten (docs/recherche.md, Abschn. 2, Rang 9) und verlangt, das Momentum so zu drehen, dass hoch mehr Stress bedeutet (Abschn. 4.3, Schritt 1). Einschätzung: Steigt der Markt nur noch dank weniger großer Werte, während die Mehrheit zurückbleibt, ist der Aufschwung schmal und anfälliger; das zeigt sich als fallendes Verhältnis.

## So liest du sie
- Ein hohes Perzentil heißt: Die gleichgewichtete Variante bleibt ungewöhnlich stark hinter der kapitalgewichteten zurück.
- Die Kennzahl misst eine Veränderung, kein Niveau; sie schlägt aus, wenn sich die Breite verschlechtert, und beruhigt sich, wenn der Abstand stabil bleibt.
- Zusammen mit den übrigen Verhältnissen des Blocks lesen: Fallen mehrere gleichzeitig, ist die Schwäche breit.

## Grenzen und Fallstricke
- Kurze Historie: Die gleichgewichtete Reihe beginnt am 22.06.2017; das Perzentilfenster ist bis 2027 kürzer als die vorgesehenen zehn Jahre.
- Andere Indexfamilie als im Bericht: Nasdaq US 500 statt S&P 500; Verlauf und Niveau weichen etwas ab.
- Kursindizes ohne Dividenden; der Unterschied über wenige Monate ist klein.
- Einzelne Handelstage fehlen in einer der beiden Reihen; gerechnet wird nur auf Tagen mit beiden Werten.
- Lizenz Nasdaq, Inc. über FRED: nur private Nutzung, keine Weitergabe.

## Quellen
- Nasdaq Global Indexes: Nasdaq US 500 Large Cap Equal Weight Index (NQUS500LCE), Indexbeschreibung, abgerufen 28.09.2026
- FRED, St. Louis Fed: Reihen NASDAQNQUS500LCE und NASDAQNQUS500LC, abgerufen 28.09.2026
- docs/recherche.md, Abschnitte 2, 4.3 und 6.3 (Stand 25.09.2026)
- docs/umsetzungsplan.md, Entscheidungen E-68 und E-74 (28.09.2026)
