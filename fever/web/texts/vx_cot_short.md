# VX-Futures: Netto-Short der Spekulanten

## Kurzinfo
Netto-Short-Position der nicht kommerziellen Händler in VIX-Futures im Verhältnis zum Open Interest (CFTC, wöchentlich). Hoch = viel Wette auf Ruhe; mehr Fallhöhe.

## Was die Kennzahl misst
Die CFTC veröffentlicht jede Woche die Commitments of Traders: wer welche Positionen in US-Terminkontrakten hält. Im Legacy-Bericht sind Händler kommerziell, wenn sie Futures zur Absicherung nutzen; alle übrigen meldepflichtigen Händler gelten als nicht kommerziell, meist Spekulanten. Das Open Interest ist die Zahl aller offenen, noch nicht glattgestellten Kontrakte (CFTC, Explanatory Notes). Der Indikator ist die Zahl der Short- minus Long-Kontrakte der nicht kommerziellen Händler in VIX-Futures, geteilt durch das Open Interest.

## Warum sie für Marktstress oder Fallhöhe zählt
Wer VIX-Futures verkauft, setzt auf anhaltend niedrige Volatilität. Ist diese Wette verbreitet, kann ein plötzlicher Anstieg der Volatilität erzwungene Käufe auslösen und den Anstieg verstärken. Der Bericht nennt die Short-Volatilitäts-Positionierung im VX-COT als eines der Signale, die bei Positionierungsschocks wie im Februar 2018 Tage vorher Anspannung zeigten (docs/recherche.md, Abschn. 3; dort als Einschätzung gekennzeichnet), und als Komponente der Fallhöhe (Abschn. 4.3, Schritt 4). Das Projekt ordnet sie deshalb der Fallhöhe zu, nicht dem Stress (Entscheidung E-49).

## So liest du sie
- Ein hohes Perzentil heißt: Die Spekulanten sind im Verhältnis zum Markt ungewöhnlich stark short, also auf Ruhe positioniert.
- Hohe Werte bedeuten keine unmittelbare Gefahr, sondern eine Verstärkung, falls ein Schock kommt.
- Neben dem Perzentil über das lange Fenster zeigt die Erklärseite ein zweites über einen kürzeren Zeitraum, nur zur Anzeige (Entscheidung E-49).

## Grenzen und Fallstricke
- Verzug: Die Daten beziehen sich auf den Dienstag und erscheinen am Freitag (Bericht, Abschn. 4.3, Schritt 6).
- Die Einteilung in kommerziell und nicht kommerziell folgt den Meldungen der Händler und passt bei VIX-Futures nicht immer zur tatsächlichen Absicht (Einschätzung).
- Short-Volatilität wird auch über Optionen und börsengehandelte Produkte aufgebaut, die der Bericht nicht erfasst (Einschätzung).
- Der Bericht bewertet die Evidenz für COT-Daten als schwach (Abschn. 2).

## Quellen
- Commodity Futures Trading Commission: Explanatory Notes, Commitments of Traders, abgerufen 26.09.2026
- docs/recherche.md, Abschnitte 2, 3 und 4.3 (Stand 25.09.2026)
- docs/umsetzungsplan.md, Entscheidung E-49 (26.09.2026)
