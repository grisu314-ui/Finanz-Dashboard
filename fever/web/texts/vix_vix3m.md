# VIX/VIX3M

## Kurzinfo
Erwartete Schwankung des S&P 500 über 30 Tage geteilt durch die über drei Monate (Termstruktur). Hoch = kurzfristige Angst übersteigt die längerfristige, mehr Stress.

## Was die Kennzahl misst
Der Indikator teilt den VIX (erwartete Schwankung des S&P 500 für 30 Tage) durch den VIX3M, das entsprechende Maß für drei Monate. Beide berechnet Cboe aus Optionspreisen auf den S&P 500. Cboe vergleicht diese Termstruktur der erwarteten Volatilität mit der Zinsstrukturkurve am Anleihemarkt (Cboe, VIX Term Structure). Normalerweise ist die längere Frist teurer; das heißt Contango, das Verhältnis liegt dann unter eins. Liegt die kurze Frist darüber, spricht man von Backwardation.

## Warum sie für Marktstress oder Fallhöhe zählt
Der Bericht setzt VIX/VIX3M an die Spitze seiner Rangliste: gute Evidenz, sehr aktuell, lange Historie und hohe Relevanz für Optionshorizonte, allerdings mit kurzem Vorlauf (docs/recherche.md, Abschn. 2, Rang 1, Horizont kurzfristig). Eine umgedrehte Termstruktur zeigt, dass der Markt für die nächsten Wochen mehr Unruhe erwartet als für die nächsten Monate, typisch für akuten Stress. Darum gibt es zusätzlich eine eigene Rot-Regel der Ampel für mehrere Tage Backwardation (Abschn. 4.3, Schritt 5; die Regel steht unten).

## So liest du sie
- Ein hohes Perzentil heißt: Die kurze Frist ist im Verhältnis ungewöhnlich teuer.
- Backwardation hält meist nur Tage bis wenige Wochen; eine Rückkehr in Contango zeigt, dass der akute Druck nachlässt.
- Zusammen mit dem VIX-Niveau lesen: Ein hoher VIX mit Contango ist erhöhte, aber geordnete Unruhe.

## Grenzen und Fallstricke
- Kurzer Vorlauf: Die Termstruktur dreht meist erst mit dem Stress selbst (Bericht, Abschn. 2, Spalte V).
- Die Cboe-Datei des VIX3M reicht weniger weit zurück als die des VIX; das Verhältnis gibt es erst ab ihrem Beginn (im Steckbrief), die Perzentile stützen sich daher auf weniger Jahre.
- Cboe-Daten dürfen nur privat und nicht kommerziell genutzt werden.

## Quellen
- Cboe: VIX Term Structure (cboe.com), abgerufen 26.09.2026
- docs/recherche.md, Abschnitte 2 und 4.3 (Stand 25.09.2026)
