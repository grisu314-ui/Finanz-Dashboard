# Stress

## Kurzinfo
Akuter Marktstress als Mittel der Themenblöcke, jeweils als Perzentil gegenüber den letzten Jahren (0–100). Hoch = mehr Stress als üblich.

## Was die Kennzahl misst
Jeder Stress-Indikator wird zuerst in ein Perzentil übersetzt: An wie vielen Tagen im Vergleichsfenster war der Wert niedriger? Die Indikatoren sind in Blöcke gruppiert (Volatilität/Optionen, Kredit/Funding, Makro/Finanzierungsbedingungen, Breite, Positionierung). Je Block zählt der Median der gültigen Indikatoren, der Stress ist das Mittel der vorhandenen Blöcke. Der schnelle Volatilitätsblock wird vorher leicht geglättet, der Stress selbst noch einmal stärker. Die Einzelheiten stehen im Steckbrief.

## Warum sie für Marktstress oder Fallhöhe zählt
Einzelne Stresssignale widersprechen sich oft oder messen dasselbe mehrfach. Der Bericht empfiehlt deshalb Perzentile statt Rohwerten, damit Größen mit unterschiedlichen Einheiten vergleichbar werden, und Blöcke mit Median, damit ein Ausreißer nicht die Mehrheit überstimmt (docs/recherche.md, Abschn. 4.3, Schritte 1 bis 3). Gleiche Gewichte zwischen den Blöcken gelten laut Bericht außerhalb der Stichprobe meist als robuster als optimierte Gewichte (Abschn. 4.2 und 4.3).

## So liest du sie
- Ein hoher Wert heißt: Die Indikatoren stehen breit über ihren üblichen Niveaus der letzten Jahre.
- Ein Wert um die Mitte ist normal, auch wenn einzelne Indikatoren erhöht sind.
- Schau bei einem Anstieg, welcher Block ihn trägt: Volatilität reagiert in Tagen, Makro und Kredit eher in Wochen.
- Der geglättete Wert zählt für die Ampel; der ungeglättete zeigt die Richtung früher, schwankt aber stärker.

## Grenzen und Fallstricke
- Perzentile sind relativ: Ein ruhiges Jahrzehnt im Fenster lässt mittlere Anspannung hoch aussehen und umgekehrt.
- Die Glättung verzögert: Schnelle Schocks erscheinen erst nach einigen Tagen voll im Wert.
- Langsame Makro- und Kreditreihen halten den Stress nach Krisen länger hoch, als die Märkte es zeigen.
- In Phase 1 fehlen die Blöcke Breite (keine Kursquelle, O-1) und Positionierung (erst Phase 2).
- Revisionen: In Phase 1 zählt je Beobachtung der neueste Stand; frühere Werte können sich dadurch leicht ändern (CLAUDE.md, fachliche Korrektheit).

## Quellen
- docs/recherche.md, Abschnitte 4.2 und 4.3 (Stand 25.09.2026)
- docs/umsetzungsplan.md, Entscheidungen E-47 bis E-49 (26.09.2026)
