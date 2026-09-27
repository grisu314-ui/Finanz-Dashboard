# Variance Risk Premium

## Kurzinfo
VIX minus die tatsächlich gemessene Schwankung des S&P 500 der letzten Wochen. Niedrig oder negativ = die reale Schwankung holt die erwartete ein; mehr Stress.

## Was die Kennzahl misst
Die Variance Risk Premium (VRP) ist hier die Differenz zwischen dem VIX, also der erwarteten Schwankung, und der realisierten Volatilität des S&P 500: Das ist die Schwankung, die die täglichen Kursänderungen des Index in einem kurzen zurückliegenden Fenster tatsächlich hatten, auf ein Jahr gerechnet. Die genaue Berechnung und das Fenster stehen unten im Steckbrief. Im Normalfall ist der VIX höher als die realisierte Schwankung, weil Anleger für Absicherung eine Prämie zahlen.

## Warum sie für Marktstress oder Fallhöhe zählt
Bollerslev, Tauchen und Zhou (2009) zeigen, dass die Differenz zwischen erwarteter und realisierter Schwankung einen Teil der späteren Aktienrenditen erklärt, am stärksten über etwa ein Quartal. Der Bericht führt die VRP als Kernindikator mit kurzem Horizont (docs/recherche.md, Abschn. 2). Für das Dashboard zählt die Richtung: Schrumpft die Prämie oder wird sie negativ, schwankt der Markt bereits stärker, als die Optionspreise erwartet haben. Deshalb gilt hier niedrig = mehr Stress (Entscheidung E-49).

## So liest du sie
- Die Orientierung ist umgedreht: Ein hohes Perzentil entsteht bei niedriger oder negativer Prämie.
- Eine negative Prämie tritt typischerweise mitten in einem Ausverkauf auf, wenn die realisierten Kursausschläge sprunghaft steigen (Einschätzung).
- Zusammen mit dem VIX-Niveau lesen: Hoher VIX bei hoher Prämie ist Angst vor dem, was kommt; hoher VIX bei negativer Prämie ist Stress, der schon da ist.

## Grenzen und Fallstricke
- Die Prämie ist verrauscht: Einzelne große Tagesbewegungen verschieben die realisierte Schwankung stark.
- Der S&P 500 kommt von FRED und reicht dort nur rund zehn Jahre zurück (offener Punkt O-1 in CLAUDE.md); die VRP hat deshalb eine deutlich kürzere Historie als der VIX (Beginn im Steckbrief).
- Die Studie misst Varianzen und Renditen über Monate; dieses Dashboard nutzt nur die Richtung als Stresssignal, keine Renditeprognose.
- Die S&P-500-Daten von FRED unterliegen der Lizenz von S&P Dow Jones Indices: nur privat, keine Weitergabe.

## Quellen
- Bollerslev, Tauchen, Zhou: Expected Stock Returns and Variance Risk Premia, Review of Financial Studies 22(11), 2009, S. 4463–4492 (Angaben und Kurzfassung über RePEc, abgerufen 26.09.2026)
- docs/recherche.md, Abschnitt 2 (Stand 25.09.2026)
- docs/umsetzungsplan.md, Entscheidungen E-49 und E-51 (26.09.2026)
