# I163 – Browserlokale Mehrfachauswahl

## Ziel

Den offenen Punkt **C · Datenarbeit → Mehrfachauswahl** als rein browserlokalen, flüchtigen Read-only-Slice umsetzen. Die Auswahl dient ausschließlich als sichere Grundlage für eine spätere Preview von Massenaktionen.

## Umsetzung

- Einträge erhalten eine eigene Auswahl-Checkbox.
- Die Auswahl wird ausschließlich im aktuellen DOM gehalten.
- Ein sichtbarer Zähler meldet `N ausgewählt`.
- `Auswahl aufheben` löscht alle gesetzten Checkboxen.
- Der ausgewählte Zeilenzustand wird visuell hervorgehoben.
- Tastaturfokus bleibt sichtbar.
- Navigation und Mehrfachauswahl bleiben getrennte Bedienelemente.

## Flüchtigkeitsvertrag

I163 speichert **nichts**:

- kein LocalStorage,
- kein SessionStorage,
- keine Cookies,
- kein Serverrequest,
- keine DB-/Repository-Mutation,
- keine Audit-Events.

Reload oder Navigation setzt die Auswahl deshalb absichtlich zurück.

## Sicherheitsgrenze

I163 führt **keine Massenaktion** aus. Die Auswahl ist nur eine temporäre Browsermenge.

Insbesondere nicht enthalten:

- Löschen/Verschieben/Bearbeiten mehrerer Einträge,
- persistierte Auswahl,
- serverseitige Auswahlzustände,
- neue POST-/Write-Routen,
- Repository-/Schemaänderungen.

## Accessibility

- Checkboxen besitzen eindeutige zugängliche Beschriftungen.
- Auswahlzustand ist nicht nur farblich sichtbar.
- Der Zähler verwendet `aria-live=polite`.
- Fokusrahmen bleibt kontrastreich.
- Auswahl kann vollständig per Tastatur bedient und zurückgesetzt werden.

## Ergebnis

Mit I163 existiert eine sichere browserlokale Auswahlbasis. Erst ein separater Folgeslice darf daraus eine **Preview für Massenaktionen** ableiten; produktive Massenwrites bleiben weiterhin geschlossen.
