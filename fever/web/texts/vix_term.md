# VIX-Termstruktur

## Kurzinfo
Erwartete Schwankung des S&P 500 über verschiedene Fristen: VIX-Indizes von 9 Tagen bis 6 Monaten und VIX-Futures nach Restlaufzeit. Nur Anzeige.

## Was die Kennzahl misst
Die Kurve zeigt nebeneinander, welche Schwankung der Optionsmarkt für unterschiedliche Fristen erwartet: den VIX9D (9 Tage), den VIX (30 Tage), den VIX3M (3 Monate) und den VIX6M (6 Monate), alle von Cboe aus Optionspreisen auf den S&P 500 berechnet. Dazu kommen die Schlusskurse (Settlements) der monatlichen VIX-Futures der Cboe Futures Exchange, geordnet nach den Kalendertagen bis zu ihrem Verfall. Cboe vergleicht diese Termstruktur mit der Zinsstrukturkurve am Anleihemarkt (Cboe, VIX Term Structure). Die Indizes stehen auf ihrer nominalen Frist, die Futures auf ihrer tatsächlichen Restlaufzeit.

## Warum sie für Marktstress oder Fallhöhe zählt
In ruhigen Zeiten steigt die Kurve mit der Frist an (Contango): Für die fernere Zukunft wird mehr Unsicherheit eingepreist. In akutem Stress kippt sie (Backwardation), weil die nächsten Tage am unsichersten erscheinen. Der Bericht setzt das Verhältnis VIX/VIX3M an die Spitze seiner Rangliste und nennt die ganze Kurve als Teil der Ansicht „Schnelle Marktsignale“ (docs/recherche.md, Abschn. 2 und 6.3). In den Score geht nur VIX/VIX3M ein; die Kurve selbst ist Anzeige (Entscheidung E-49).

## So liest du sie
- Steigende Kurve von links nach rechts: normale Lage.
- Liegt das linke Ende höher als das rechte, erwartet der Markt kurzfristig mehr Unruhe als später: typisch für akuten Stress.
- Die Futures zeigen, wie der Markt den VIX zu den Verfallsterminen handelt; sie können von den Indizes abweichen.

## Grenzen und Fallstricke
- Die Fristen der Indizes sind nominal; die Futures verfallen an festen Terminen, ihre Restlaufzeit ändert sich täglich.
- Am Verfallstag zählt der verfallende Kontrakt nicht mehr (Entscheidung E-46).
- Cboe-Daten dürfen nur privat und nicht kommerziell genutzt werden.

## Quellen
- Cboe: VIX Term Structure (cboe.com), abgerufen 26.09.2026
- docs/recherche.md, Abschnitte 2 und 6.3 (Stand 25.09.2026)
- docs/umsetzungsplan.md, Entscheidungen E-45, E-46 und E-49 (26.09.2026)
