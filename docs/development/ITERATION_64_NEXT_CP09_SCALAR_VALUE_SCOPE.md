# Iteration 64 – Nächster CP-09-Scope nach eingefrorener Entry-Feldanlage

## Zweck

I64 bestimmt nach dem Freeze **FROZEN_CP09_ENTRY_FIELD_CREATE** ausschließlich read-only den nächsten fachlich sinnvollen CP-09-Scope.

Die Iteration besteht aus zwei Schritten:

1. nächsten Scope aus Zielbild, vorhandenen Serviceverträgen und Freeze-Grenzen bestimmen;
2. nur den kleinsten daraus zwingend folgenden Vertrag formal vorbereiten.

I64 implementiert **keinen Produktcode**.

## Ausgangslage

Bereits eingefroren:

- Kategorie anlegen;
- Eintrag anlegen;
- Entry-spezifisches Feld anlegen;
- sieben einfache FieldTypes in der TUI-Feldanlage;
- stabile Parent-ID;
- genau ein Write;
- Read-Port-Refresh;
- Fehler-/Cancel-/Fokusvertrag.

Weiter offen sind unter anderem:

- Scalar Field Values schreiben;
- Choice-Optionen anlegen;
- Single-/Multi-Choice-Werte schreiben;
- Kategorie-Felder;
- MONEY-spezifische Anlage;
- Update-/Trash-/Restore-/Undo-Oberflächen;
- produktiver Composition Root / Starter.

## Bewertete Kandidaten

### A – Kategorie-Feldanlage

`CatalogService.create_category_field(...)` existiert bereits und teilt den internen `_create_field(...)`-Pfad mit Entry-Feldern.

Trotzdem ist dieser Scope **breiter** als der eingefrorene Entry-Feld-Slice:

- ein Kategorie-Feld wirkt auf mehrere Einträge;
- UI-Provenienz und Refresh-Semantik unterscheiden sich;
- es entsteht noch kein zusätzlicher Nutzen beim tatsächlichen Befüllen eines bereits angelegten Entry-Felds.

**Nicht als nächster kleinster Scope gewählt.**

### B – Choice-Optionen / Choice-Werte

Vorhandene Verträge:

- `add_field_option(field_id, label, ...)`
- `set_single_choice(entry_id, field_id, option_id)`
- `set_multi_choice(entry_id, field_id, option_ids)`

Dieser Block benötigt mindestens zwei gekoppelte Semantiken:

1. Optionsdefinition;
2. Auswahlwert.

Damit ist er größer als ein einzelner Scalar-Value-Vertrag.

**Nicht als nächster kleinster Scope gewählt.**

### C – MONEY

`FieldDefinition` verlangt für MONEY zusätzlich `currency_code`.

Die derzeit eingefrorene TUI-Feldanlage bietet MONEY bewusst nicht an.

Ein MONEY-Value-Scope würde damit eine noch nicht freigegebene Definitionssemantik voraussetzen oder vorhandene externe Daten annehmen.

**Nicht als nächster kleinster Scope gewählt.**

### D – Update / Trash / Restore / Undo

Diese Verträge existieren bereits im Application Service, greifen aber in Revisionen, Lifecycle, Restore oder Audit-Inversion ein.

Sie sind fachlich und risikoseitig deutlich breiter als ein einzelner Feldwert-Write.

**Nicht als nächster kleinster Scope gewählt.**

### E – Scalar Field Value Write

Vorhandener Servicevertrag:

`CatalogService.set_scalar_value(entry_id, field_id, value) -> ScalarValue`

Der Vertrag:

- benutzt bereits die bestehende Entry-/Field-Identität;
- validiert den Feldtyp über `ScalarValue.from_input(...)`;
- blockiert Choice-Typen;
- prüft, ob das Feld auf den Entry anwendbar ist;
- schreibt über den bestehenden `CoordinatedWriter`;
- erzeugt Audit `field_value.set`;
- besitzt Postconditions;
- verändert weder Schema noch Repository-Vertrag.

Die Read-Seite ist bereits vorhanden:

- `list_fields_with_values(entry_id)`;
- `get_field_value(entry_id, field_id)`;
- TUI-`FieldRow` enthält `id`, `field_type` und `value`;
- Web zeigt Scalar Values bereits read-only an.

Damit schließt dieser Scope als kleinster nächster Schritt direkt die Lücke:

**Feld definieren → Feldwert setzen → vorhandenen Wert wieder lesen**

## Entscheidung Schritt 1

**Der nächste CP-09-Scope ist: Entry Scalar Field Value Write.**

Er umfasst zunächst ausschließlich den vorhandenen `set_scalar_value(...)`-Vertrag.

## Harte Grenzen

Nicht Bestandteil dieses Scopes:

- Choice-Optionen;
- SINGLE_CHOICE-Writes;
- MULTI_CHOICE-Writes;
- Kategorie-Feldanlage;
- MONEY-Feldanlage;
- Update / Trash / Restore / Undo;
- TUI-Runtime-Integration;
- neuer Composition Root;
- neue Domain-/Repository-/SQLite-Verträge;
- Schemaänderungen.

## Typgrenze

Der spätere erste UI-Verbraucher darf nur die bereits freigegebenen sieben einfachen Feldtypen berücksichtigen:

- TEXT
- LONG_TEXT
- INTEGER
- DECIMAL
- DATE
- DATETIME
- BOOLEAN

Wichtig:

Der schmale Adaptervertrag selbst soll **keine Feldtyp-Logik duplizieren**. Die Domain-/Servicevalidierung bleibt autoritativ.

MONEY und Choice bleiben auf UI-/Scope-Ebene geschlossen.

## Warum jetzt Wert statt Starter?

Ein produktiver TUI-Composition-Root ist ein Integrations-/Startthema und wird separat in I65 bewertet.

I64 soll den fachlichen CP-09-Pfad bestimmen. Der nächste fachliche Vertrag ist der Scalar Value Write; die Frage, wie Services/Adapter produktiv verdrahtet werden, bleibt davon getrennt.

## Schritt-1 Exit-Kriterium

Schritt 1 ist grün, wenn:

1. der Scope ausschließlich aus vorhandenen Verträgen abgeleitet ist;
2. kein Frozen-Core-Reopen erforderlich ist;
3. Choice/MONEY/Kategorie-Feld/Lifecycle getrennt bleiben;
4. kein Produktcode geändert wurde;
5. Manifest und Scope-Gate grün sind.

Erst danach darf Schritt 2 den minimalen Adaptervertrag formalisieren.
