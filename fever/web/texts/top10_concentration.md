# Top-10-Konzentration

## Kurzinfo
Anteil der zehn größten Unternehmen am Vermögen des SPDR S&P 500 ETF (je Unternehmen, quartalsweise). Hoch = der Markt hängt an wenigen Werten, mehr Fallhöhe.

## Was die Kennzahl misst
Der SPDR S&P 500 ETF Trust bildet den S&P 500 nach und meldet der US-Börsenaufsicht SEC zu jedem Quartalsende alle Positionen mit ihrem Anteil am Fondsvermögen (Formular N-PORT). Aus der Meldung werden die Aktienpositionen genommen; mehrere Aktiengattungen desselben Unternehmens, erkannt an seiner Kennung LEI (Legal Entity Identifier), zählen zusammen. Die Kennzahl ist die Summe der Anteile der zehn größten Unternehmen (Entscheidung E-74).

## Warum sie für Marktstress oder Fallhöhe zählt
Der Bericht nennt die Top-10-Konzentration als Komponente der Fallhöhe (docs/recherche.md, Abschn. 4.3, Schritt 4, und Abschn. 6.3, Ansicht 6). Einschätzung: Je mehr ein Index an wenigen Werten hängt, desto stärker schlägt ein Rückschlag bei diesen Werten auf den ganzen Markt durch, und desto weniger schützt die Streuung über viele Titel.

## So liest du sie
- Ein hohes Perzentil heißt: Die zehn größten Werte haben ein ungewöhnlich hohes Gewicht.
- Die Kennzahl ändert sich langsam und nur viermal im Jahr; sie beschreibt einen Zustand, keinen Auslöser.
- Zusammen mit dem Verhältnis gleich- zu kapitalgewichtet im Block Breite lesen: Das zeigt die Richtung, diese Kennzahl das erreichte Ausmaß.

## Grenzen und Fallstricke
- Großer Verzug: Die SEC veröffentlicht die Meldung rund zwei Monate nach dem Quartalsende; der Wert ist oft über drei Monate alt.
- Kurze Historie: öffentliche Meldungen ab dem Stichtag 30.09.2019; das Perzentilfenster umfasst anfangs nur wenige Jahre.
- Es sind die Gewichte des Fonds, nicht des Index selbst; Abweichungen durch Barmittel und Zeitpunkte sind klein, aber vorhanden.
- Die Zählweise je Unternehmen ergibt einen etwas höheren Wert als Übersichten, die jede Aktiengattung einzeln zählen.

## Quellen
- SEC EDGAR: N-PORT-Meldungen des SPDR S&P 500 ETF Trust (CIK 884394), abgerufen 28.09.2026
- SEC: Privacy and Website Policies (Nutzung öffentlicher Informationen von sec.gov), abgerufen 28.09.2026
- docs/recherche.md, Abschnitte 4.3 und 6.3 (Stand 25.09.2026)
- docs/umsetzungsplan.md, Entscheidungen E-71 und E-74 (28.09.2026)
