# Margin Debt (Z.1) ggü. Vorjahr

## Kurzinfo
Veränderung der Margin-Kredite von US-Brokern an Kunden gegenüber dem Vorjahresquartal (Fed-Statistik Z.1). Hoch = schnell wachsender Hebel; mehr Fallhöhe.

## Was die Kennzahl misst
Die Reihe stammt aus den Financial Accounts of the United States (Z.1) der Federal Reserve: Forderungen der Wertpapierhändler und Broker an Kunden, also Margin-Kredite und andere Forderungen, in Millionen US-Dollar, quartalsweise zum Quartalsende (FRED, Reihe BOGZ1FL663067003Q). Margin-Kredite sind Kredite, mit denen Anleger Wertpapiere auf Pump kaufen. Der Indikator ist die Veränderung gegenüber dem Wert ein Jahr zuvor.

## Warum sie für Marktstress oder Fallhöhe zählt
Wächst der Hebel schnell, steigt die Fallhöhe: Fallen die Kurse, müssen Anleger Sicherheiten nachschießen oder verkaufen, und das kann einen Rückgang beschleunigen. Der Bericht nennt Margin Debt gegenüber dem Vorjahr als Komponente der Fallhöhe (docs/recherche.md, Abschn. 4.3, Schritt 4), bewertet sie aber schwach: wenig Evidenz, kaum Vorlauf, großer Verzug (Abschn. 2). Das Projekt nutzt die Fed-Statistik statt der FINRA-Daten, weil deren Nutzungsbedingungen das Speichern untersagen (Entscheidung E-42).

## So liest du sie
- Ein hohes Perzentil heißt: Der Hebel wächst ungewöhnlich schnell.
- Einschätzung: Schnell wachsende Margin-Kredite gehen oft mit steigenden Kursen einher; die Reihe zeigt Übertreibung eher, als dass sie den Wendepunkt bestimmt.

## Grenzen und Fallstricke
- Sehr später Wert: quartalsweise und mit mehreren Monaten Verzug; er ist oft über ein halbes Jahr alt.
- Die Fed überarbeitet die Z.1-Daten mit jeder Quartalsausgabe, teils auch strukturell (FRED, ebenda).
- Vor 2000 enthält die Reihe auch Forderungen an Nicht-Kunden; es gibt dort einen Strukturbruch (docs/umsetzungsplan.md, Ergebnis M4c).
- Die Reihe misst den Betrag, nicht den Hebel im Verhältnis zur Marktkapitalisierung, den der Bericht als Alternative nennt (Abschn. 4.3, Schritt 4).

## Quellen
- FRED, St. Louis Fed: Reihe BOGZ1FL663067003Q (Z.1 Financial Accounts of the United States), Notes, abgerufen 26.09.2026
- docs/recherche.md, Abschnitte 2 und 4.3 (Stand 25.09.2026)
- docs/umsetzungsplan.md, Entscheidungen E-42 und E-49, Ergebnis M4c (26.09.2026)
