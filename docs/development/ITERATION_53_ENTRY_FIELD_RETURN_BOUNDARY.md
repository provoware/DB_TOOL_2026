# Iteration 53 – EntryFieldWriteAdapter Rückgabegrenze

## Zweck

I53 ist ausschließlich eine read-only Vertragsentscheidung nach dem eingefrorenen I48 und der Governance-Härtung I49–I52.

Es wird **kein Produktcode** verändert.

## Entscheidungsfrage

Der spätere `EntryFieldWriteAdapter` benötigt eine minimale Rückgabegrenze.

Zur Auswahl standen:

1. direkte Rückgabe der bestehenden `FieldDefinition`;
2. ein neues minimales Create-Result-Modell;
3. Mapping auf bestehendes `FieldRow`.

## Entscheidung

**Der spätere Adapter gibt zunächst die vom `CatalogService.create_entry_field()` erzeugte `FieldDefinition` unverändert zurück.**

I53 autorisiert ausschließlich diese Adaptergrenze. Es autorisiert noch keine TUI-Nutzung dieses Domain-Objekts.

## Begründung

### Warum kein neues Create-Result?

Aktuell existiert noch kein freigegebener TUI-Verbraucher für das Ergebnis der Feldanlage.

Ein zusätzliches Modell würde deshalb heute nur bereits vorhandene Informationen kopieren, zum Beispiel:

- Feld-ID;
- Name;
- `FieldType`;
- Owner/`entry_id`;
- Required-Status.

Damit entstünde eine neue Abstraktion ohne konkreten Verbraucher. Das widerspricht der bestehenden Codesparsamkeitsregel.

Wenn eine spätere Runtime-Integration tatsächlich ein eigenes stabiles Präsentationsobjekt benötigt, muss dies in einer eigenen Scope-Entscheidung begründet werden.

### Warum kein FieldRow?

`FieldRow` ist bereits ein Präsentationsmodell für die bestehende Feldansicht und enthält unter anderem:

- `value`;
- `field_type` als Darstellungswert;
- `required`;
- `help_text`.

Eine frisch erzeugte Felddefinition besitzt noch keinen Feldwert.

Ein Mapping auf `FieldRow` würde deshalb vorzeitig Value- und Darstellungssemantik festlegen. Diese Semantik bleibt weiterhin geschlossen.

### Warum FieldDefinition direkt?

`CatalogService.create_entry_field()` gibt bereits genau eine validierte `FieldDefinition` zurück.

Die unveränderte Rückgabe hat für die schmale Adapter-Seam folgende Vorteile:

- kein neues Datenmodell;
- kein Informationsverlust;
- keine String-Konvertierung für `FieldType`;
- kein Mapping-Code;
- bestehende Domain-/Validation-Fehler bleiben unverändert;
- I54 kann mit einem sehr kleinen delegierenden Adapter auskommen.

## Begrenzung der Kopplung

Die direkte `FieldDefinition`-Rückgabe gilt ausschließlich für die **Adapter-Seam**.

Sie bedeutet ausdrücklich **nicht**, dass:

- `ProvowareDbTui` künftig Domain-Objekte direkt darstellen soll;
- `FieldRow` ersetzt wird;
- die Runtime `FieldDefinition` direkt speichern oder rendern darf;
- Value-/Choice-Logik freigegeben ist.

Die Präsentationsgrenze bleibt Aufgabe einer späteren Integrationsentscheidung.

## Vertrag für I54

Eine spätere I54-Funktionsiteration darf ausschließlich einen dünnen Vertrag implementieren, sinngemäß:

- Eingabe: `entry_id: str`
- Eingabe: `name: str`
- Eingabe: `field_type: FieldType`
- genau eine Delegation an `create_entry_field(...)`
- Rückgabe: exakt die erzeugte `FieldDefinition`
- keine String-Heuristik;
- kein Repository-/SQL-Zugriff;
- keine Fehlerumklassifizierung;
- keine TUI-/Runtime-Integration.

Optionale Feldparameter aus `CatalogService.create_entry_field(..., **kwargs)` werden durch I53 **nicht automatisch** freigegeben. I54 soll zunächst nur die drei zwingenden Eingaben exponieren.

## Freeze-Grenzen

Geschlossen bleiben:

- CP-03;
- CP-06;
- SQLite/Storage;
- `CatalogService`;
- Domain-Modelle;
- CP-07T Runtime;
- `FieldRow`;
- Kategorie-Feldanlage;
- Field Values;
- Choice-Optionen;
- Single-/Multi-Choice-Writes;
- Autosave/Undo/Recovery;
- Text-/Helper-/Capability-Registry.

## Ergebnis

Die minimale sichere Rückgabegrenze ist:

**`FieldDefinition` unverändert zurückgeben.**

Ein separates Create-Result wäre zum aktuellen Zeitpunkt unnötige Duplikation.

## Nächster Schritt nach Freeze

Nach vollständig grün eingefrorenem I53 darf I54 ausschließlich die dünne `EntryFieldWriteAdapter`-Seam implementieren. Noch keine TUI-Integration und keine Value-/Choice-Writes.
