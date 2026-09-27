# Rezessionsbalken

## Kurzinfo
Graue Flächen in den Verlaufs-Charts: Zeiträume von US-Rezessionen nach der NBER-Datierung, wie in FRED-Grafiken. Nur Anzeige, kein Teil eines Scores.

## Was die Kennzahl misst
Die Flächen zeigen die US-Rezessionen nach der Datierung des National Bureau of Economic Research (NBER), eines privaten Forschungsinstituts. Grundlage ist die FRED-Reihe USREC: Sie ist für jeden Monat 1, wenn er zu einer Rezession gehört, sonst 0. FRED legt dabei die Trough-Methode an: Eine Rezession beginnt im Monat nach dem Konjunkturhoch und endet mit dem Monat des Tiefs. Genauso schattiert FRED seine eigenen Grafiken (FRED, Reihe USREC, abgerufen 26.09.2026).

## Warum sie für Marktstress oder Fallhöhe zählt
Viele Stressmaße steigen in Rezessionen, manche laufen ihnen voraus, andere hinken nach. Die Flächen machen dieses Zusammenspiel im Verlauf sichtbar: etwa, ob ein Indikator vor einer Rezession anzog oder erst mittendrin. Der Bericht unterscheidet genau diese Vorlauf-Horizonte (docs/recherche.md, Abschn. 2 und 3).

## So liest du sie
- Eine graue Fläche markiert einen Rezessionszeitraum, nicht einen Börseneinbruch; beides fällt oft, aber nicht immer zusammen.
- Vergleiche, wo die Linie eines Indikators relativ zum Beginn der Fläche steigt.
- In kurzen Zeiträumen (1 Monat, 6 Monate) ist oft keine Fläche zu sehen.

## Grenzen und Fallstricke
- Das NBER legt Hoch und Tief erst Monate später fest. Eine laufende Rezession erscheint deshalb nie sofort; am rechten Rand steht immer „keine Rezession“, bis das NBER entschieden hat. Die Flächen sind Rückschau und kein Signal.
- Die Datierung ist monatlich; Beginn und Ende auf den Monatsersten bzw. Monatsletzten sind eine Konvention von FRED.
- Sie betrifft nur die USA; Rezessionen im Euroraum oder in Asien sind nicht markiert.

## Quellen
- FRED, St. Louis Fed: NBER based Recession Indicators for the United States from the Period following the Peak through the Trough (USREC), abgerufen 26.09.2026
- FRED, St. Louis Fed: Recession Indicators Series, abgerufen 26.09.2026
- docs/recherche.md, Abschnitte 2 und 3 (Stand 25.09.2026)
