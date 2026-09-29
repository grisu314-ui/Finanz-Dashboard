# Ampel

## Kurzinfo
Gesamtlage in vier Stufen aus Stress, Fallhöhe und schnellen Warnsignalen: Grün, Gelb, Orange, Rot. Höhere Stufe = angespanntere Lage. Keine Prognose.

## Was die Kennzahl misst
Die Ampel fasst die Lage des US- und des globalen Aktienmarkts in einer von vier Stufen zusammen. Sie folgt festen Regeln statt einer Formel: Jede Regel prüft den geglätteten Stress, die Fallhöhe, den Diffusionsindex, das Verhältnis VIX zu VIX3M (Volatilitätserwartung für 30 Tage zu der für drei Monate), den Anstieg des Kreditspreads Baa oder eines von zwei Rezessionssignalen vom US-Arbeitsmarkt: die Sahm-Regel und den SOS-Indikator. Es gilt die höchste Stufe, deren Regel zutrifft. Welche Regeln das sind und ab welchen Werten sie greifen, steht unten unter „Schwellen und Farben“; die Werte kommen direkt aus der Konfiguration.

## Warum sie für Marktstress oder Fallhöhe zählt
Stress und Fallhöhe beschreiben verschiedene Dinge: akute Anspannung und Verwundbarkeit. Der Bericht empfiehlt, sie nicht zu multiplizieren, sondern über Regeln zu kombinieren, weil sonst eine hohe Bewertung ohne Stress und akuter Stress bei niedriger Bewertung ununterscheidbar würden (docs/recherche.md, Abschn. 4.3, Schritte 4 und 5). Zusätzliche Einzelregeln fangen schnelle Schocks, die ein geglätteter Composite erst spät zeigt.

## So liest du sie
- **Grün:** keine der Regeln trifft zu.
- **Gelb:** erhöhte Verwundbarkeit ohne akuten Auslöser, viele Einzelwerte gleichzeitig auffällig, oder eine frühe Rezessionswarnung vom Arbeitsmarkt (SOS-Indikator).
- **Orange:** deutlicher Stress, besonders zusammen mit hoher Fallhöhe, oder ein ausgelöstes Rezessionssignal (Sahm-Regel).
- **Rot:** breiter akuter Stress oder ein schnelles Warnsignal wie eine invertierte Volatilitätskurve.

Unter der Ampel steht, welche Regeln gerade zutreffen. Eine Stufe wird erst verlassen, wenn der Wert deutlich unter die Schwelle fällt (Hysterese); das verhindert tägliches Hin- und Herspringen (Abschn. 4.3, Schritt 5). Lies die Ampel immer zusammen mit der Konfidenz.

## Grenzen und Fallstricke
- Die Ampel ist eine Regime- und Risikoanzeige, keine Crash-Prognose und kein Handelssignal (Bericht, Kurzfazit).
- Der Composite ist geglättet und reagiert auf schnelle Schocks spät; die VIX/VIX3M-Regel gleicht das nur teilweise aus.
- In Phase 1 fehlt der Block Positionierung, im Block Breite der Anteil über der 50/200-Tage-Linie (E-72), und die Regel über den Anstieg der Kreditspreads nutzt vorerst Moody's Baa statt des HY-OAS (E-75). Die Ampel stützt sich deshalb auf weniger oder andere Bausteine als im Bericht vorgesehen.
- Fehlt der Stress-Composite, entscheiden die übrigen Regeln (Entscheidung E-51).
- Die Rezessionsregeln gelten, solange ihr Wert die Schwelle erfüllt, ohne Hysterese (Entscheidung E-80). Beide Größen bleiben nach dem Beginn einer Rezession oft bis weit in die Erholung hinein erhöht. Eigene Auswertung (29.09.2026): Die Sahm-Regel hielt die Ampel mindestens auf Orange von 12/1990 bis 01/1993, 07/2001 bis 12/2002, 05/2008 bis 07/2010 und 05/2020 bis 05/2021, dazu 08/2024 bis 11/2024 ohne Rezession.
- Einschätzung: Die Schwellen sind Startwerte aus dem Bericht und nicht an Krisen optimiert; das ist Absicht, um Überanpassung zu vermeiden (Abschn. 4.3, Schritt 7).

## Quellen
- docs/recherche.md, Kurzfazit und Abschnitt 4.3 (Stand 25.09.2026)
- docs/umsetzungsplan.md, Entscheidungen E-47 bis E-51 (26.09.2026) und E-80 (29.09.2026)
