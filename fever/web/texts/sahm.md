# Sahm-Regel (Echtzeit)

## Kurzinfo
Anstieg der US-Arbeitslosenquote (Dreimonatsschnitt) über ihr Tief der letzten zwölf Monate, in Prozentpunkten, mit damals verfügbaren Daten. Hoch = mehr Stress.

## Was die Kennzahl misst
Die Sahm-Regel nach Claudia Sahm vergleicht den gleitenden Dreimonatsdurchschnitt der US-Arbeitslosenquote (U3) mit dem niedrigsten dieser Durchschnitte aus den vorangegangenen zwölf Monaten. Die Echtzeit-Variante auf FRED nutzt die Arbeitslosenquoten so, wie sie im jeweiligen Monat verfügbar waren (FRED, Reihe SAHMREALTIME). Der Indikator nimmt diesen Wert unverändert.

## Warum sie für Marktstress oder Fallhöhe zählt
Steigt die Arbeitslosigkeit vom Tief aus spürbar, verstärkt sie sich meist selbst: Weniger Beschäftigte konsumieren weniger, Unternehmen stellen weniger ein. Laut FRED signalisiert die Regel den Beginn einer Rezession, wenn der Anstieg 0,50 Prozentpunkte oder mehr erreicht (FRED, ebenda). Diese Schwelle ist eine Konvention aus der Literatur und geht nicht in den Score ein; dort zählt nur das Perzentil. Der Bericht führt die Echtzeit-Sahm-Regel als Kernindikator mit mittelfristigem Horizont und guter Evidenz (docs/recherche.md, Abschn. 2). Weil FRED die damals verfügbaren Daten verwendet, entspricht die Reihe weitgehend dem, was man zum jeweiligen Zeitpunkt wissen konnte; der Bericht nennt sie „schon Echtzeit“ (Abschn. 4.3, Schritt 6).

## So liest du sie
- Ein hohes Perzentil heißt: Die Arbeitslosigkeit steigt ungewöhnlich deutlich von ihrem jüngsten Tief.
- Die Regel reagiert langsam und eher bestätigend; ein Anstieg über mehrere Monate ist das eigentliche Signal.
- Zusammen mit den Erstanträgen lesen: Diese sind wöchentlich und reagieren früher.

## Grenzen und Fallstricke
- Monatlich und spät: Der Wert kommt erst mit dem Arbeitsmarktbericht des Folgemonats (Bericht, Abschn. 6.1).
- Viele Monate haben denselben niedrigen Wert; das Perzentil springt dadurch in groben Stufen.
- Einschätzung: Eine steigende Arbeitslosenquote durch mehr Arbeitssuchende, etwa durch Zuwanderung, kann die Regel auslösen, ohne dass Stellen wegfallen.

## Quellen
- FRED, St. Louis Fed: Reihe SAHMREALTIME, Notes, abgerufen 26.09.2026
- docs/recherche.md, Abschnitte 2, 4.3 und 6.1 (Stand 25.09.2026)
