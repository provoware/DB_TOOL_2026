# I171 – Vertrag für die Zahlenbereichsregel

## Ziel und Status

I171 präzisiert ausschließlich den nächsten Regeltyp `number_range` auf Basis
des gemeinsamen I166-Regelmodells. **PLAN/CONTRACT ONLY:** Es entsteht weder
Runtime-Code noch eine produktiv aktive Regel. TODO-Fortschritt und Roadmap-
Status bleiben unverändert.

## Schritt 1 – Deterministische Regeldefinition

Eine Zahlenbereichsregel ergänzt die gemeinsamen Bestandteile um
`parameters.min` und `parameters.max`. Jeder Parameter ist entweder eine
endliche JSON-Zahl oder `null`; `null` bedeutet eine offene Grenze. Mindestens
eine Grenze muss gesetzt sein. Sind beide gesetzt, muss `min <= max` gelten.
`NaN`, Unendlichkeit, Zahlen als Zeichenketten, zusätzliche Parameter und
boolesche Werte sind ungültig.

Der temporäre Vorschauwert ist entweder eine endliche Zahl oder eine
Zeichenkette im kanonischen Dezimalformat `-?(0|[1-9][0-9]*)(\.[0-9]+)?`.
Vorzeichen, führende oder folgende Leerzeichen und lokalisierte Dezimaltrennzeichen
werden nicht stillschweigend normalisiert. Ein leerer oder syntaktisch ungültiger
Wert ist `not_evaluable`, nicht `violated`.

Die Grenzen sind einschließlich: Ein Wert erfüllt die Regel genau dann, wenn er
jede gesetzte Unter- und Obergrenze erreicht oder innerhalb davon liegt.

### Ergebnis und Reason-Codes

- `satisfied` / `number_in_range`: „Der Testwert liegt im erlaubten Zahlenbereich.“
- `violated` / `number_below_min`: „Der Testwert muss mindestens {min} sein.“
- `violated` / `number_above_max`: „Der Testwert darf höchstens {max} sein.“
- `not_evaluable` / `invalid_number_value`: „Gib eine gültige Zahl ohne Leerzeichen ein.“
- `not_evaluable` / `invalid_number_range`: „Der Zahlenbereich ist ungültig. Prüfe Unter- und Obergrenze.“

Die Darstellungsprojektion nennt Problem, betroffenes Draft-Feld und Behebung.
Sie zeigt Feldbezeichnung und formatierte Grenzen, verwendet aber weiterhin die
stabile Feld-ID für die Zuordnung. Interne Exceptions werden nicht angezeigt.

### Invarianten

1. Preview und eine später separat freigegebene Aktivierung verwenden denselben reinen Auswerter.
2. `not_evaluable` gilt nie als erfüllt und erlaubt keine Aktivierung.
3. Die Auswertung hängt weder von Browser-Locale noch von Feldlabel oder Klickreihenfolge ab.
4. Beide Grenzen sind inklusiv; es gibt in diesem Slice keine exklusiven Grenzen oder Schrittweite.
5. Der Vertrag liest oder schreibt weder Datensätze noch `validation_json`, Schema oder Repository.

**Zwischen-Gate:** Parameter, Eingabeformat, Randwerte, Ergebniszustände und
Fehlerprojektion sind vollständig entscheidbar; ungültige Zustände scheitern
geschlossen. Schritt 1 ist GRÜN.

## Schritt 2 – Kleinster späterer Preview-Slice

Der kleinste Implementierungsslice ist browserlokal und beschränkt sich auf
**genau ein vorhandenes Draft-Zahlenfeld mit genau einer gesetzten Grenze**.
Regeldefinition und Testwert bleiben flüchtig. Der Slice muss Untergrenze,
Obergrenze, exakten Grenzwert, Über-/Unterschreitung und ungültige Eingabe
gezielt prüfen. Eine zweite gleichzeitig gesetzte Grenze folgt erst nach grüner
Abnahme dieses Basisslices.

Eine spätere sichtbare UI-Änderung benötigt ein eigenes Chromium-/Accessibility-
Gate und darf die I170-Testausnahme nicht wiederverwenden. Es gibt keinen
Speichern-, Aktivieren-, Submit-, Netzwerk-, LocalStorage- oder SessionStorage-
Pfad.

## Geschlossene Bereiche

- produktive Aktivierung und Validierung gespeicherter Datensätze,
- zwei gleichzeitig gesetzte Grenzen, exklusive Grenzen, Schrittweite und Einheiten,
- lokalisierte Zahlenformate, Datum, Dateitypen und weitere Regelarten,
- `validation_json`, Schema, Repository, Migration und Dependencies,
- CP-03 und CP-06.

## Laienhilfe-Delta

Eine Zahlenbereichsregel ist wie ein Türsteher für Zahlen: Eine spätere Vorschau
zeigt nur, ob ein Testwert eine festgelegte Unter- oder Obergrenze einhält. Sie
speichert weder die Regel noch den Testwert und verändert keine vorhandenen Daten.

## Gate

- fokussierten I171-Vertragstest ausführen,
- Manifest V2 und versiegelten Scope prüfen,
- Single-Source-Preflight ausführen,
- keine Produkt-, UI-, Browser- oder Storage-Tests, weil Runtime und Rendering unverändert bleiben.
