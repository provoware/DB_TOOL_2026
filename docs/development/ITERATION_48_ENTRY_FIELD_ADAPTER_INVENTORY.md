# Iteration 48 – EntryFieldWriteAdapter / FieldType Inventur

## Zweck

I48 ist ausschließlich eine read-only Vertrags- und Adapterinventur nach dem eingefrorenen I47. Es wird kein Produktcode verändert.

## Ausgangslage

I47 hat als nächsten einzelnen CP-09-Vertrag ausschließlich `CatalogService.create_entry_field(entry_id, name, field_type, ...)` freigegeben.

Weiterhin geschlossen bleiben:

- TUI-Anbindung,
- Kategorie-Felder,
- Feldwerte,
- Choice-Optionen,
- Value-Writes,
- CP-03,
- CP-06,
- SQLite/Storage,
- CatalogService,
- CP-07T,
- CP-08.

## Befund: dünne Adaptergrenze ist technisch möglich

Die bestehende Datei `tui/write_adapter.py` folgt bereits einem klaren Muster:

- kleines Protocol nur für den benötigten Application-Service-Vertrag;
- genau ein delegierender Adapter;
- keine direkte Repository-/SQL-Nutzung;
- Domainfehler werden nicht umklassifiziert;
- Präsentationsmapping bleibt lokal am Adapter.

Dasselbe Muster ist für einen späteren `EntryFieldWriteAdapter` grundsätzlich möglich, ohne `CatalogService`, Domain, Repository oder SQLite zu verändern.

Ein geeigneter späterer Service-Protocol-Vertrag kann semantisch auf genau Folgendes begrenzt werden:

- `entry_id: str`
- `name: str`
- `field_type: FieldType`
- Rückgabe: bestehende `FieldDefinition`

I48 implementiert dieses Protocol jedoch noch nicht.

## FieldType-Grenze

`FieldType` ist bereits ein `StrEnum` im Domain-Modell und besitzt die stabilen Werte:

- `text`
- `long_text`
- `integer`
- `decimal`
- `money`
- `date`
- `datetime`
- `boolean`
- `single_choice`
- `multi_choice`

Für die Adaptergrenze ist deshalb **keine neue Typ-Abstraktion** nötig.

Die sichere Regel für eine spätere Implementierung lautet:

1. Der Adapter akzeptiert **`FieldType` selbst**, nicht beliebige Strings.
2. Es findet im Adapter **keine String-zu-Enum-Heuristik** und kein Fallback statt.
3. Der Adapter reicht denselben `FieldType` unverändert an `CatalogService.create_entry_field()` weiter.
4. Validierung unbekannter Eingaben gehört vor die Adaptergrenze bzw. in eine separat freigegebene UI-/Controller-Schicht.
5. Choice-spezifische Folgeschritte werden durch die reine Felddefinition **nicht** automatisch freigegeben.

Damit bleibt der Transport verlustfrei und typstabil.

## Rückgabegrenze

Hier besteht die wichtigste offene Designgrenze.

Die vorhandenen Adapter für Kategorie und Eintrag können jeweils auf `NavItem` abbilden, weil beide Objekte unmittelbar Navigationsknoten darstellen.

Für Felder existiert dagegen `FieldRow`. Dieses Modell enthält bereits:

- `value`
- `field_type`
- `required`
- `help_text`

Ein frisch erzeugtes `FieldDefinition` besitzt jedoch **noch keinen Feldwert**. Ein direktes Mapping auf `FieldRow` würde deshalb bereits eine Präsentations-/Value-Semantik festlegen, die I48 ausdrücklich nicht freigibt.

Folgerung:

**I48 autorisiert noch keinen Rückgabemapper auf `FieldRow`.**

Eine spätere Adapterimplementation soll zunächst entweder:

- die erzeugte `FieldDefinition` unverändert zurückgeben, **oder**
- in einer separaten Scope-Iteration ein minimales create-spezifisches Präsentationsmodell begründen.

Welche Variante gewählt wird, wird erst in der Folgeiteration entschieden.

## Fehlerverhalten

Der bestehende `CatalogService.create_entry_field()` besitzt bereits relevante Fehlerverträge, unter anderem:

- fehlender/inaktiver Parent-Eintrag → `DOM-104`;
- doppelter aktiver Feldname am selben Owner → `DOM-202`;
- Domain-/Validation-Fehler aus `FieldDefinition.new(...)`.

Ein späterer Adapter darf diese Fehler nicht verschlucken, umbenennen oder in Erfolgswerte umwandeln.

## Freeze-Grenzen / Non-Goals

I48 ändert ausdrücklich nicht:

- `src/provoware_db/tui/write_adapter.py`;
- `src/provoware_db/tui/view_models.py`;
- `CatalogService`;
- Domain-Modelle;
- Repository-/SQLite-Code;
- Runtime/CP-07T;
- Feldlisten-Refresh;
- FieldType-Auswahl in der UI;
- Kategorie-Felddefinitionen;
- Field-Values;
- Choice-Optionen;
- `set_scalar_value()`;
- Single-/Multi-Choice-Writes;
- Trash/Restore/Undo/Autosave/Recovery.

## Exit-Gates

1. Ausschließlich I48-Manifest und dieses Inventurdokument sind geändert.
2. Kein Produktcode ist geändert.
3. Kein Frozen-Core- oder Runtime-Pfad ist geändert.
4. Repository Foundation ist grün.
5. Agent Governance ist grün.
6. Targeted Iteration validiert nur Manifest/Scope.
7. Keine Full-Suite-, Browser-, TUI- oder Visual-Tests ohne Produktänderung.
8. Erst nach grünem Freeze darf eine Folgeiteration entscheiden, ob der dünne Adapter direkt `FieldDefinition` zurückgibt oder ein eigenes minimales Create-Result-Modell benötigt.

## Ergebnis

Die Adaptergrenze ist **technisch möglich**, ohne einen REOPEN von `CatalogService`, Domain, Repository, SQLite oder CP-07T.

`FieldType` kann verlustfrei als bestehender Domain-Enum transportiert werden.

Die einzige noch offene Vertragsentscheidung ist die Rückgabeform des späteren Adapters. Diese wird bewusst nicht mit `FieldRow` vorweggenommen.

## Nächster Schritt nach Freeze

Nach vollständig grün eingefrorenem I48: ausschließlich die minimale Rückgabegrenze für einen späteren `EntryFieldWriteAdapter` entscheiden. Erst wenn diese klar ist, darf eine Funktionsiteration genau diesen Adapter implementieren. Noch keine TUI-Integration und keine Value-Writes.
