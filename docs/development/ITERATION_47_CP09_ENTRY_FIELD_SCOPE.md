# Iteration 47 – CP-09 Entry-Field Scope

## Zweck

I47 ist ausschließlich eine read-only Post-I46-/CP-09-Scope-Auflösung. Es wird kein Produktcode verändert und kein eingefrorener Bereich geöffnet.

## Ausgangslage

Nach I46 sind genau zwei CP-09-Schreibpfade bis zur TUI freigegeben und wieder eingefroren:

1. Kategorie anlegen.
2. Eintrag in einer ausgewählten Kategorie anlegen.

Das Zielbild des Projekts beschreibt die Hierarchie **Kategorien → Einträge → frei definierbare Felder**. Field-/Value-Writes waren bis einschließlich I46 ausdrücklich geschlossen.

## Vertragsinventur

Der bestehende `CatalogService` stellt zwei öffentliche Felddefinitions-Verträge bereit:

- `create_category_field(category_id, name, field_type, ...)`
- `create_entry_field(entry_id, name, field_type, ...)`

Beide delegieren in den bereits vorhandenen `_create_field(...)`-Pfad und verwenden den bestehenden `CoordinatedWriter`.

Für den Entry-spezifischen Vertrag gilt bereits:

- Scope ist fest `FieldScope.ENTRY`;
- `entry_id` ist der Owner;
- ein fehlender/inaktiver Eintrag wird über den bestehenden `DOM-104`-NotFound-Vertrag abgewiesen;
- doppelte aktive Feldnamen am selben Owner werden über `DOM-202` abgefangen;
- die Felddefinition wird über das bestehende Repository gespeichert;
- Audit-Evidence `field_definition.create` wird erzeugt;
- transaktionale und committed Postconditions prüfen Felddefinition und Audit-Evidence;
- es ist keine Schema-, Repository- oder SQLite-Änderung nötig.

Der bestehende Read-Pfad `list_fields(entry_id)` liefert die für einen Eintrag sichtbaren Felddefinitionen. Damit liegt die notwendige Parent-Provenienz für einen späteren dünnen Write-Adapter grundsätzlich beim aktuell ausgewählten Eintrag.

## Nächster einzelner CP-09-Use-Case

**Eine Felddefinition ausschließlich für den aktuell ausgewählten Eintrag über `CatalogService.create_entry_field()` anlegen.**

Dieser Vertrag ist der kleinste logisch folgende Schritt, weil er:

- direkt der bereits freigegebenen Hierarchie Kategorie → Eintrag → Feld folgt;
- nur einen konkreten Eintrag betrifft;
- enger ist als ein Kategorie-Feld, das für mehrere Einträge sichtbar werden kann;
- noch keinen Feldwert schreibt;
- noch keine Choice-Optionen, Single-/Multi-Choice-Werte oder sonstige Value-Persistenz benötigt.

I47 autorisiert ausdrücklich **noch keine Implementierung** dieses Use-Cases.

## Bewusste Nicht-Entscheidungen

I47 legt noch nicht fest:

- wie die TUI den Feldnamen erfasst;
- wie `FieldType` ausgewählt wird;
- ob eine spätere erste UI-Integration alle vorhandenen Feldtypen oder nur einen separat freigegebenen Teil exponiert;
- wie Fokus und Feldlisten-Refresh nach einem Write erfolgen;
- ob dafür ein erneuter enger CP-07T-REOPEN nötig wird.

Diese Punkte gehören in getrennte Folgeiterationen. Insbesondere darf aus dem Vorhandensein der Feldtypen nicht automatisch eine neue UI oder ein Value-Editor abgeleitet werden.

## Freeze-Grenzen / Non-Goals

Unverändert geschlossen bleiben:

- CP-03 / Schema V1 / Migrationen;
- CP-06 Domain-/Repository-Kern;
- `storage/sqlite/**` einschließlich Audit, Journal, Unit of Work und Coordinator;
- `CatalogService` und sein bestehender Felddefinitionsvertrag;
- CP-07T Runtime-/Navigations-/Layoutpfad;
- CP-07H;
- CP-08 Health-/Event-Surface;
- Kategorie-Felddefinitionen;
- Feldwerte und `set_scalar_value()`;
- Choice-Optionen und Choice-Writes;
- Update-/Trash-/Restore-/Undo-Pfade;
- Autosave und Crash-Recovery;
- Theme/Layout/Dependencies/CI.

Jede Änderung an diesen Bereichen benötigt einen eigenen begründeten REOPEN.

## Exit-Gates

1. Ausschließlich I47-Manifest und dieses Scope-Dokument sind geändert.
2. Kein Produktcode ist geändert.
3. Kein Frozen-Core- oder Runtime-Pfad ist geändert.
4. Repository Foundation ist grün.
5. Agent Governance ist grün.
6. Targeted Iteration validiert nur Manifest/Scope.
7. Kein Full-Suite-, Browser-, TUI- oder visueller Test ohne Produktänderung.
8. Erst nach grünem Freeze von I47 darf eine Folgeiteration ausschließlich eine dünne `EntryFieldWriteAdapter`-Seam gegen `CatalogService.create_entry_field()` inventarisieren bzw. freigeben.

## Verbleibendes Risiko

`create_entry_field()` benötigt neben einer stabilen `entry_id` zwingend einen `FieldType`. Die Domain kennt mehrere Typen, darunter Text, Zahl, Datum, Boolean und Choice. Diese Typvielfalt macht die spätere UI-Integration deutlich komplexer als Kategorie- oder Entry-Erstellung.

Deshalb ist der sichere nächste Schritt nach I47 **nicht** sofort ein TUI-Dialog, sondern zunächst ausschließlich die Adapter-/Typgrenzen-Inventur.

## Nächster Schritt nach Freeze

Nach vollständig grün eingefrorenem I47: ausschließlich prüfen, ob ein dünner `EntryFieldWriteAdapter` ohne Änderung an `CatalogService`, Domain, Repository, SQLite oder Runtime möglich ist und wie `FieldType` an dieser Adaptergrenze explizit und verlustfrei transportiert wird.
