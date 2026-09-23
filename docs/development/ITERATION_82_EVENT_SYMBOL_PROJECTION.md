# Iteration 82 – Event Symbol Projection

## Änderung

I82 löst ausschließlich die in I81 isolierte `EventItem.symbol`-Grenze. Es wird kein Produktcode verändert und kein eingefrorener Checkpoint wieder geöffnet.

## Befund

Der eingefrorene CP-08-Vertrag behandelt die TUI ausschließlich als Konsument bereits projizierter `EventItem`-Daten. `EventItem` besitzt `time_label`, `symbol` und `text`; die TUI darf Auditdaten weder erzeugen noch fachlich interpretieren.

Die bestehende CP-08-Ereignisregression verwendet bereits das neutrale Zeichen `·` als `EventItem.symbol`. Dieses Zeichen transportiert keine Aussage über `action`, `entity_type`, Actor, Erfolg, Fehler oder Priorität. Damit kann es als reine Präsentationsmarke verwendet werden, ohne eine neue Audit-Taxonomie oder Domain-Semantik einzuführen.

Eine dynamische Ableitung aus `audit_events.action`, `entity_type` oder anderen Auditfeldern wäre dagegen eine neue fachliche Klassifikation und bleibt ausdrücklich außerhalb dieses Scopes.

## Entscheidung

**`EVENT_SYMBOL_NEUTRAL_CONSTANT_DOT_AUTHORIZED`**

Ein späterer dünner read-only Event-Provider darf für jedes gelesene Audit-Ereignis exakt

`symbol = "·"`

projizieren.

Das Zeichen ist ausschließlich eine neutrale visuelle Markierung. Es darf nicht als Status-, Typ-, Schweregrad- oder Aktionsklassifikation dokumentiert oder ausgewertet werden.

Damit ist die in I81 verbliebene Projektionslücke geschlossen:

- `occurred_at` → `EventItem.time_label`,
- konstantes `·` → `EventItem.symbol`,
- `summary` → `EventItem.text`.

## Autorisierte spätere Provider-Grenze

Nach grünem I82-Gate darf separat geprüft und gegebenenfalls implementiert werden, ob ein dünner Provider bereits vollständig aus den vorhandenen Seams ableitbar ist. Er darf nur:

- die vom äußeren Owner geliehene read-only SQLite-Connection verwenden,
- `audit_events` lesen,
- die neuesten Datensätze deterministisch begrenzen,
- exakt `EventItem` projizieren,
- das neutrale konstante `·` verwenden,
- die Connection niemals schließen,
- keinerlei Audit-, Journal- oder andere Daten verändern.

## Freeze-Schutz

Unverändert bleiben CP-03, CP-08, Schema/Migrationen, `storage/sqlite/audit.py`, Operation Journal, Repositories, Domain/Application-Core, TUI-Runtime, View-Models, Writer, Starter und alle eingefrorenen CP-09-Slices.

## Prüfstrategie

Da I82 ausschließlich Dokumentation und Manifest ergänzt, sind nur Manifest-, Scope- und Governance-Gates gerechtfertigt. Produkt-, TUI-, Browser-, Storage- und Full-Suite-Tests werden nicht künstlich ausgelöst.

## Verbleibendes Risiko

Die Symbolsemantik ist jetzt absichtlich minimal und stabil, der produktive Event-Provider ist aber noch nicht implementiert. Die spätere SQL-Lesereihenfolge, Limit-Behandlung und Zeitdarstellung müssen im Provider-Slice gegen das bestehende Schema geprüft werden; sie dürfen nicht in I82 vorweggenommen werden.

## Nächster Schritt

I82 gaten und einfrieren. Erst danach den kleinsten read-only Event-Provider gegen I78 + I81 + I82 inventarisieren und nur bei vollständig vorhandenen Seams implementieren.