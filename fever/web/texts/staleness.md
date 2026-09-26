# Veraltung

## Kurzinfo
Ein Wert gilt als veraltet, wenn seit seiner erwarteten Veröffentlichung mehr Zeit vergangen ist, als seine Frequenz plus Toleranz erlaubt. Veraltete Werte zählen nicht.

## Was die Kennzahl misst
Jede Reihe hat eine Frequenz (täglich, wöchentlich, monatlich, quartalsweise), einen üblichen Veröffentlichungsverzug und eine Toleranz. Ab dem Beobachtungsdatum plus Verzug läuft die Uhr; überschreitet das Alter die Frequenz plus Toleranz, ist der Wert veraltet. Handelsfreie Tage und Feiertage sind damit kein Fehler.

## Warum sie für Marktstress oder Fallhöhe zählt
Ein veralteter Wert, der wie ein aktueller aussieht, ist der gravierendste Fehler dieser Anwendung (CLAUDE.md, Anzeige und Datenaktualität). Der Bericht verlangt, fehlende Daten nicht zu schätzen, sondern den letzten zum Veröffentlichungszeitpunkt bekannten Wert nur begrenzt weiterzuverwenden (docs/recherche.md, Abschn. 4.3, Schritte 3 und 6).

## So liest du sie
- Veraltete Werte sind ausgegraut, schraffiert und mit dem Wort „veraltet“ markiert.
- Sie fallen aus ihrem Block heraus und senken die Konfidenz.
- Der Datenstand zeigt je Reihe die letzte Beobachtung und den Status; je Quelle den letzten Erfolg und Fehler.

## Grenzen und Fallstricke
- Verspätet sich eine Quelle regulär (etwa bei einer Behördenschließung), erscheint ihr Wert veraltet, obwohl nichts kaputt ist.
- Die Grenze hängt an der Systemzeit des Servers; eine falsch gestellte Uhr verfälscht die Anzeige (docs/einrichtung.md).

## Quellen
- CLAUDE.md, Abschnitte „Fachliche Korrektheit“ und „Anzeige und Datenaktualität“
- docs/recherche.md, Abschnitt 4.3 (Stand 25.09.2026)
- docs/umsetzungsplan.md, Entscheidungen E-10 und E-44 (26.09.2026)
