# Iteration 85 – TUI Composition Read Boundary

## Änderung

I85 korrigiert ausschließlich die I84-Integrationsannahme vor einem produktiven Composition-Root. Es wird kein Produktcode geändert.

## Befund

Die drei TUI-seitigen Read-Bausteine sind vorhanden: `TuiCatalogReadAdapter`, `DatabaseReadinessHealthProvider` und `AuditEventReadProvider`. Der Catalog-Port kann jedoch nicht über den vorhandenen `CatalogService` in einen strikt read-only Composition-Root verdrahtet werden.

`CatalogService.__init__` verlangt neben `main_con` zwingend `state_con`, `main_db_path`, `app_session_id` und `app_version` und konstruiert dabei `AuditWriter` sowie `CoordinatedWriter`. Damit würde seine bloße Konstruktion die in I78 festgelegte read-only Ownership-Grenze überschreiten und Writer-Lifecycle in den Root ziehen.

## Entscheidung

`READONLY_TUI_COMPOSITION_ROOT_BLOCKED_BY_CATALOG_SERVICE_WRITE_COUPLING`.

Ein I85-Composition-Root wird deshalb ausdrücklich **nicht** implementiert. Die sichere nächste Grenze ist ein eigener dünner `CatalogReadPort`-Provider über die bereits vorhandenen read-fähigen Repositories. Er darf nur die drei vom TUI benötigten Methoden bereitstellen:

- `list_categories()`
- `list_entries(category_id)`
- `list_fields_with_values(entry_id)`

Dabei muss die bestehende Read-Semantik des `CatalogService` erhalten bleiben, ohne `AuditWriter`, `CoordinatedWriter`, State-DB oder neue SQL-Semantik einzuführen.

## Freeze-Schutz

Unverändert bleiben CP-03 und alle anderen eingefrorenen Checkpoints, Schema/Migrationen, Storage-Writer, `CatalogService`, Repositories, TUI-Runtime/View-Models, Event-/Health-Provider und Starter.

## Prüfstrategie

Da I85 ausschließlich eine Integrationsgrenze dokumentiert, werden keine Produkt-/Volltests ausgelöst. Das Gate prüft Manifest, Scope und Governance. Die entscheidende Regression ist hier die Vermeidung eines unzulässigen Writer-Lifecycles im read-only Root.

## Verbleibendes Risiko

Die Feldwertprojektion muss in einem späteren Read-Provider exakt die bestehende `CatalogService.list_fields_with_values()`-Semantik bewahren. Eine Kopie oder Neuinterpretation von Schreiblogik ist nicht zulässig.

## Nächster Schritt

I85 gaten und einfrieren. Danach I86 ausschließlich den minimalen read-only Catalog-Provider gegen die vorhandenen Repository-Read-Methoden inventarisieren und nur bei semantischer Deckung implementieren.
