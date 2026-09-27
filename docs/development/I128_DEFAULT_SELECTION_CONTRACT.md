# I128 – defaultSelection-Vertrag für den temporären Browser-Draft

## Status

**PLAN/CONTRACT ONLY.** Dieser Vertrag öffnet weder Persistenz noch einen produktiven Schreibpfad. Er definiert ausschließlich den später erlaubten browserlokalen Draft-Scope.

## Ziel

Choice-Felder sollen später einen optionalen Standard-Auswahlzustand erhalten, ohne Labels als Identität zu missbrauchen, ohne beim Typwechsel Daten still umzuschreiben und ohne bereits ausgewählte Optionen unbemerkt zu entfernen.

## Zustandsvertrag

- `defaultSelection` gehört ausschließlich zu Draft-Elementen vom Typ `field`.
- Der Wert referenziert **stabile `draft-option-*`-IDs**, niemals Option-Labels.
- `single_choice`: null oder exakt eine vorhandene Option-ID.
- `multi_choice`: null oder eine geordnete, duplikatfreie Liste vorhandener Option-IDs.
- Für Nicht-Choice-Datentypen ist `defaultSelection` inaktiv und wird nicht in der Preview ausgewertet.
- Ein temporärer Typwechsel darf den gespeicherten Draft-Zustand nicht still löschen.

## Mutationsregeln

1. Eine Auswahl darf erst übernommen werden, wenn alle referenzierten Option-IDs existieren.
2. Mehrfachauswahl enthält keine Duplikate.
3. Die sichtbare Reihenfolge einer Mehrfachauswahl folgt der aktuellen Optionsreihenfolge, nicht der Klickreihenfolge.
4. Reorder einer Option erhält die Auswahl über ihre stabile ID.
5. Eine aktuell ausgewählte Option darf nicht still entfernt werden. Entfernen wird blockiert, bis die Option aus `defaultSelection` gelöst wurde.
6. Wechsel `multi_choice -> single_choice` wird blockiert, solange mehr als eine Default-Option gewählt ist.
7. Wechsel von Choice zu Nicht-Choice lässt `defaultSelection` dormant bestehen; Preview und Eingabesteuerung ignorieren ihn.
8. Rückwechsel zu Choice reaktiviert den Zustand nur, wenn alle referenzierten IDs weiterhin gültig sind.

## Preview-Vertrag

Die Preview zeigt nur aktiven Choice-Zustand:

- keine Auswahl: `Standardauswahl: keine`
- Einfachauswahl: Label der referenzierten Option
- Mehrfachauswahl: Labels in aktueller Optionsreihenfolge

Die Preview darf keine interne Draft-ID sichtbar machen.

## Accessibility-Vertrag

- Steuerung nur per nativen fokussierbaren Controls.
- Zugänglicher Name enthält Feldlabel und Zweck `Standardauswahl`.
- Statusmeldungen erklären Übernahme oder Blockierung.
- Fokus kehrt nach erfolgreicher oder blockierter Aktion deterministisch zur Default-Auswahlsteuerung zurück.
- Bedienung bleibt in schmaler Darstellung ohne horizontalen Zwang erreichbar.

## Nicht-Scope

- keine Speicherung in `MaskTemplate`, `MaskFieldSpec` oder `MaskTemplateStore`
- keine JSON-Schema-Erweiterung
- keine SQLite-/Repository-Änderung
- keine produktive Anwendung eines Standardwerts auf Datensätze
- kein CP-03-/CP-06-Reopen
- keine Migration

## Implementierungsreihenfolge für eine spätere eigene Iteration

1. browserlokalen Draft-Zustand und reine Validierungsfunktionen ergänzen;
2. single_choice-Steuerung + Preview + Fokusvertrag;
3. multi_choice-Steuerung + Duplikat-/Reihenfolgevertrag;
4. Remove-/Type-Switch-Guards;
5. gezielte Browser- und Accessibility-Evidence.

Erst nach separatem grünen Gate darf eine Persistenzabbildung überhaupt geplant werden.
