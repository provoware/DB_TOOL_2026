# Iteration 87 – Read-only Catalog Provider

## Änderung

I87 ergänzt ausschließlich einen dünnen `CatalogReadProvider` für den bestehenden `CatalogReadPort`. Er arbeitet auf einer geliehenen SQLite-Connection und konstruiert nur `CategoryRepository`, `EntryRepository` und `FieldRepository`.

## Nachvollziehbare Basis

I87 stützt sich nicht auf einen separaten I86-Checkpoint. Die fachliche Basis ist direkt versioniert und überprüfbar: I85 hat die Writer-Kopplung des `CatalogService` als Blocker isoliert; I87 vergleicht anschließend die drei benötigten Read-Operationen unmittelbar mit den bereits vorhandenen `CatalogService`-Methoden und den bestehenden Repository-Reads.

## Semantik

Die drei Reads bleiben identisch zur vorhandenen `CatalogService`-Lesesemantik:

- `list_categories()` delegiert an `CategoryRepository.list_active()`.
- `list_entries(category_id)` prüft zuerst die aktive Kategorie und liefert bei fehlender oder gelöschter Kategorie `[]`.
- `list_fields_with_values(entry_id)` erhält die bestehende `DOM-101`-Fehlermeldung, Feldreihenfolge und Wertprojektion.

Der Provider besitzt die Connection nicht und stellt deshalb bewusst kein `close()` bereit.

## Freeze-Schutz

Keine Änderung an CP-03 oder anderen eingefrorenen Checkpoints, Schema/Migrationen, Repositories, `CatalogService`, TUI-Runtime/View-Models, Health/Event-Providern, Writern oder Starter.

## Prüfstrategie

Nur fokussierte, dependency-freie Paritätstests für die drei Reads, `DOM-101` und fehlende Close-Ownership. Der Test wird wie vom Targeted-Gate vorgesehen direkt mit Python ausgeführt und benötigt kein zusätzliches `pytest`-Paket. Keine unnötige Vollsuite oder Browser-/Visual-Tests.

## Verbleibendes Risiko

Der Provider ist noch nicht produktiv verdrahtet. Ein späterer Composition-Root muss weiterhin genau eine read-only Connection besitzen und Writer-Lifecycle strikt getrennt halten.

## Nächster Schritt

Nach grünem I87-Gate den minimalen read-only TUI-Composition-Root erneut inventarisieren. Erst bei lückenlosen Seams implementieren.
