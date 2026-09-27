# Cboe SKEW

## Kurzinfo
Vom Optionsmarkt eingepreistes Risiko extremer Kursausschläge des S&P 500 über 30 Tage (Cboe SKEW). Um 100 = kaum Extremrisiko; höher = mehr. Nur Anzeige.

## Was die Kennzahl misst
Der SKEW misst laut Cboe das wahrgenommene Extremrisiko („tail risk“) des S&P 500. Grundlage ist der Marktpreis der Schiefe der 30-Tage-Rendite, berechnet aus einem Portfolio von S&P-500-Optionen, das eine Wette auf die Schiefe nachbildet. Cboe rechnet diesen Preis S in den Index um: SKEW = 100 − 10 × S. Der SKEW steigt also, je negativer die eingepreiste Schiefe ist, je mehr Gewicht also starke Kursverluste bekommen (Cboe, The CBOE SKEW Index, 2010).

## Warum sie für Marktstress oder Fallhöhe zählt
Der VIX misst die Breite der erwarteten Schwankung, aber nicht ihre Form. Die Renditen des S&P 500 haben laut Cboe mehr Ausreißer als eine Normalverteilung und eine negative Schiefe; der SKEW soll diesen Teil des Risikos sichtbar machen (Cboe, ebenda). Der Bericht führt ihn nur als „Nice to have“: Evidenz und Vorlauf sind schwach (docs/recherche.md, Abschn. 2). Er geht deshalb nicht in den Score ein (Entscheidung E-49).

## So liest du sie
- Ein hoher SKEW heißt: Absicherungen gegen starke Kursverluste sind im Verhältnis teuer.
- Einschätzung: Ein hoher SKEW bei niedrigem VIX ist häufig; er zeigt Vorsicht, nicht Panik. In akuten Einbrüchen fällt der SKEW oft, weil dann alle Optionen teurer werden.

## Grenzen und Fallstricke
- Kein Frühwarnsignal: Der Bericht gibt ihm für Evidenz und Vorlauf niedrige Noten (Abschn. 2).
- Cboe hat die Berechnung seit der Einführung angepasst; lange Vergleiche sind mit Vorsicht zu lesen (Einschätzung).
- Cboe-Daten dürfen nur privat und nicht kommerziell genutzt werden.

## Quellen
- Cboe: The CBOE SKEW Index (Whitepaper, 2010; cdn.cboe.com), abgerufen 27.09.2026
- docs/recherche.md, Abschnitt 2 (Stand 25.09.2026)
- docs/umsetzungsplan.md, Entscheidung E-49 (26.09.2026)
