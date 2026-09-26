# Ampel

## Kurzinfo
Gesamtlage in vier Stufen aus Stress, Fallhöhe und schnellen Warnsignalen: Grün, Gelb, Orange, Rot. Höhere Stufe = angespanntere Lage. Keine Prognose.

## Was die Kennzahl misst
Die Ampel fasst die Lage des US- und des globalen Aktienmarkts in einer von vier Stufen zusammen. Sie folgt festen Regeln statt einer Formel: Jede Regel prüft den geglätteten Stress, die Fallhöhe, den Diffusionsindex oder das Verhältnis VIX zu VIX3M (Volatilitätserwartung für 30 Tage zu der für drei Monate). Es gilt die höchste Stufe, deren Regel zutrifft. Welche Regeln das sind und ab welchen Werten sie greifen, steht unten unter „Schwellen und Farben“; die Werte kommen direkt aus der Konfiguration.

## Warum sie für Marktstress oder Fallhöhe zählt
Stress und Fallhöhe beschreiben verschiedene Dinge: akute Anspannung und Verwundbarkeit. Der Bericht empfiehlt, sie nicht zu multiplizieren, sondern über Regeln zu kombinieren, weil sonst eine hohe Bewertung ohne Stress und akuter Stress bei niedriger Bewertung ununterscheidbar würden (docs/recherche.md, Abschn. 4.3, Schritte 4 und 5). Zusätzliche Einzelregeln fangen schnelle Schocks, die ein geglätteter Composite erst spät zeigt.

## So liest du sie
- **Grün:** keine der Regeln trifft zu.
- **Gelb:** erhöhte Verwundbarkeit ohne akuten Auslöser, oder viele Einzelwerte gleichzeitig auffällig.
- **Orange:** deutlicher Stress, besonders zusammen mit hoher Fallhöhe.
- **Rot:** breiter akuter Stress oder ein schnelles Warnsignal wie eine invertierte Volatilitätskurve.

Unter der Ampel steht, welche Regeln gerade zutreffen. Eine Stufe wird erst verlassen, wenn der Wert deutlich unter die Schwelle fällt (Hysterese); das verhindert tägliches Hin- und Herspringen (Abschn. 4.3, Schritt 5). Lies die Ampel immer zusammen mit der Konfidenz.

## Grenzen und Fallstricke
- Die Ampel ist eine Regime- und Risikoanzeige, keine Crash-Prognose und kein Handelssignal (Bericht, Kurzfazit).
- Der Composite ist geglättet und reagiert auf schnelle Schocks spät; die VIX/VIX3M-Regel gleicht das nur teilweise aus.
- In Phase 1 fehlen die Blöcke Breite und Positionierung, und die Regel über den Anstieg des HY-OAS (Risikoaufschlag von Hochzinsanleihen) ist inaktiv (O-1, O-5). Die Ampel stützt sich deshalb auf weniger Bausteine als im Bericht vorgesehen.
- Fehlt der Stress-Composite, entscheiden die übrigen Regeln (Entscheidung E-51).
- Einschätzung: Die Schwellen sind Startwerte aus dem Bericht und nicht an Krisen optimiert; das ist Absicht, um Überanpassung zu vermeiden (Abschn. 4.3, Schritt 7).

## Quellen
- docs/recherche.md, Kurzfazit und Abschnitt 4.3 (Stand 25.09.2026)
- docs/umsetzungsplan.md, Entscheidungen E-47 bis E-51 (26.09.2026)
