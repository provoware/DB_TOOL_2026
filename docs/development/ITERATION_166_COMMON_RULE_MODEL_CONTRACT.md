# Iteration 166 – Vertrag für das gemeinsame Regelmodell

## Ziel und Status

I166 schließt ausschließlich `D · gemeinsames Regelmodell planen` und bestimmt danach den kleinsten temporären Regel-Preview-Slice. **PLAN/CONTRACT ONLY:** Es entsteht weder Runtime-Code noch eine produktiv aktive Regel.

## Schritt 1 – Gemeinsames Regelmodell

### Minimale Regeldefinition

Jede spätere Draft-Regel besitzt genau diese gemeinsamen Bestandteile:

- `id`: stabile, innerhalb des Drafts eindeutige `draft-rule-*`-ID,
- `kind`: diskriminierte Regelart, zunächst ausschließlich `required`,
- `targetFieldId`: stabile ID genau eines vorhandenen Draft-Felds,
- `enabled`: expliziter Aktivstatus innerhalb der temporären Preview,
- `parameters`: von `kind` abhängiges Objekt; für `required` exakt leer.

Labels sind Anzeige, nie Identität. Unbekannte Regelarten, fehlende Ziel-Felder, unzulässige Parameter oder Nicht-Feld-Ziele erzeugen kein stilles Fallback.

### Gemeinsames Auswertungsergebnis

Ein reiner Auswerter erhält Regel, Felddefinition und temporären Vorschauwert. Er liefert deterministisch:

- `satisfied`: Regel ist erfüllt,
- `violated`: Regel ist verletzt,
- `not_evaluable`: Regel oder Ziel ist strukturell ungültig.

Das Ergebnis trägt Regel-ID, Ziel-Feld-ID und einen stabilen Reason-Code. Erst die Darstellungsprojektion übersetzt den Reason-Code in einen laienverständlichen Text mit **Problem**, **Fundstelle** und **Behebung**. Interne Exceptions oder IDs werden nicht als normale Fehlermeldung angezeigt.

### Invarianten

1. Preview und eine später separat freigegebene Aktivierung verwenden denselben Auswerter.
2. Regeln werden in stabiler Draft-Reihenfolge ausgewertet; Ergebnisse werden nicht von Klickreihenfolge oder Labels abgeleitet.
3. `enabled = false` bedeutet: nicht auswerten und keinen Fehler anzeigen; die Definition bleibt im Draft erhalten.
4. `not_evaluable` darf niemals als `satisfied` gelten oder eine Aktivierung erlauben.
5. Änderung von Feld-ID oder Regelart ist eine explizite Draft-Mutation, keine automatische Reparatur.
6. I166 bildet keine Regel auf `validation_json`, Schema, Repository oder Datensätze ab.

**Zwischen-Gate:** Definition, Ergebnis und Fehlerprojektion sind für `required` vollständig entscheidbar; unbekannte oder ungültige Zustände scheitern geschlossen. Schritt 1 ist GRÜN.

## Schritt 2 – Kleinster temporärer Preview-Slice

Der nächste Slice ist ausschließlich `required` für **genau ein browserlokales Draft-Feld**:

- Eingabe: aktuelles Draft-Feld und ein temporärer Vorschauwert.
- Leer: kein Wert oder eine ausschließlich aus Leerraum bestehende Zeichenfolge.
- Nicht leer: mindestens ein Nicht-Leerraum-Zeichen.
- `satisfied`: „Pflichtwert vorhanden.“
- `violated`: „Dieses Feld ist ein Pflichtfeld. Gib einen Wert ein.“
- `not_evaluable`: ruhiger Schutzstatus; keine Aktivierung und keine Behauptung, der Wert sei gültig.

Diese Auswahl ist minimal, weil sie keine Parameter, zweite Feldreferenz, Datums-/Zahleninterpretation, Dateimetadaten oder Repository-Abfrage benötigt. Bestehendes produktives `is_required` wird weder gelesen noch verändert; die Preview arbeitet ausschließlich mit einem neuen flüchtigen Draft-Regelzustand.

### Spätere Akzeptanzkriterien

1. Regel und Vorschauwert bleiben bei Reload und Navigation nicht erhalten.
2. Es gibt keinen Speichern-, Aktivieren-, Submit- oder Netzwerkpfad.
3. Statusänderungen sind per Tastatur bedienbar und mit `aria-live=polite` verständlich angekündigt.
4. Leerer, Leerraum-, gefüllter und strukturell ungültiger Zustand werden gezielt getestet.
5. UI und Test beweisen, dass keine Local-/SessionStorage-Nutzung und keine SQLite-Änderung erfolgt.

## Geschlossene Bereiche

- Zahlenbereich, Datum, Dateitypen, Eindeutigkeit, Sichtbarkeit und Feldabhängigkeiten,
- produktive Regelaktivierung und Validierung gespeicherter Datensätze,
- `validation_json`, Schema, Repository, Migration und Dependencies,
- „zuletzt verwendet“, gespeicherte Ansichten und ausführende Massenaktionen,
- CP-03 und CP-06.

## Laienhilfe-Delta

Eine Regel wird künftig wie eine kleine Prüfanweisung beschrieben: **Welche Prüfung? Für welches Feld? Ist sie für die Vorschau eingeschaltet?** Die erste geplante Vorschau prüft nur, ob ein Pflichtfeld leer ist. Sie zeigt einen verständlichen Hinweis, speichert aber weder die Regel noch den eingegebenen Wert und verändert keine vorhandenen Daten.

## Gate

- Manifest-, Scope- und Dokumentkonsistenz prüfen.
- Fortschritt exakt um den abgeschlossenen Planungspunkt auf 40/132 erhöhen.
- Single-Source-Preflight ausführen.
- Keine Produkt-, UI- oder Storage-Tests, weil I166 keinen Runtime-Pfad ändert.
