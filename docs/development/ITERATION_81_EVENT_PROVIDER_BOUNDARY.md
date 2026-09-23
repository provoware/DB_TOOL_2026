# Iteration 81 – Event Provider Boundary

## Änderung

I81 setzt die I80-Inventur als reine Decision-Iteration fort. Es wird kein Produktcode verändert und insbesondere CP-03/CP-08 nicht wieder geöffnet.

## Befund

Der bestehende `TuiDataPort` verlangt `recent_events(limit) -> Sequence[EventItem]`. `EventItem` besitzt ausschließlich `time_label`, `symbol` und `text`. Die TUI konsumiert diese Daten beim Start als Snapshot und erzeugt oder interpretiert keine Auditdaten.

Im bestehenden SQLite-Schema ist `audit_events` die einzige klar passende persistierte Ereignisquelle. Sie besitzt `occurred_at`, `action`, `entity_type`, `summary` und weitere Auditfelder; `ix_audit_events_time` unterstützt eine zeitlich absteigende Lesesicht. `AuditWriter` schreibt diese bestehende Quelle, stellt aber absichtlich keinen Read-Provider bereit.

Damit sind zwei Projektionen ohne neue Persistenzsemantik naheliegend:

- `occurred_at` → `EventItem.time_label`,
- `summary` → `EventItem.text`.

Für `EventItem.symbol` existiert dagegen im geprüften Vertrag keine autorisierte fachliche Projektion. Weder CP-08 noch I71 legen fest, ob das Symbol aus `action`, `entity_type`, Actor-Daten oder einem konstanten neutralen Zeichen entstehen soll. Eine solche Zuordnung jetzt im Adapter zu erfinden würde die Event-Semantik nebenbei erweitern.

## Entscheidung

**`AUDIT_EVENT_SOURCE_IDENTIFIED_SYMBOL_PROJECTION_UNRESOLVED`**

Ein produktiver Event-Provider wird in I81 nicht implementiert.

Die bestehende Tabelle `audit_events` wird als geeignete read-only Quellkandidatin bestätigt, aber erst eine separate minimale Entscheidung zur Symbolprojektion darf den Adapter freigeben. Diese Entscheidung darf weder Schema noch `AuditWriter`, Operation Journal oder bestehende CP-08-TUI-Darstellung verändern.

## Zulässiger nächster Vertrag

Der nächste Decision-Slice soll ausschließlich festlegen, wie ein persistiertes Audit-Ereignis auf `EventItem.symbol` projiziert wird. Bevorzugt ist die semantisch kleinste Lösung; insbesondere darf kein neues Ereignis-Taxonomie-System entstehen.

Erst nach dieser Entscheidung darf ein dünner Provider erwogen werden, der:

- eine vom äußeren Owner geliehene read-only Connection nutzt,
- `audit_events` ausschließlich liest,
- `occurred_at DESC` und ein hart begrenztes `limit` verwendet,
- exakt `EventItem` projiziert,
- keine Connection schließt,
- weder Audit- noch Journaldaten schreibt oder verändert.

## Freeze-Schutz

Unverändert bleiben CP-03, CP-08, Schema/Migrationen, `storage/sqlite/audit.py`, Operation Journal, Repositories, Domain/Application-Core, TUI-Runtime, Writer, Starter und alle eingefrorenen CP-09-Slices.

## Prüfstrategie

Da I81 ausschließlich Dokumentation und Manifest ergänzt, sind nur Governance-, Manifest- und Scope-Gates gerechtfertigt. Produkt-, TUI-, Browser-, Storage- und Full-Suite-Tests werden nicht künstlich ausgelöst.

## Verbleibendes Risiko

Bis die Symbolprojektion festgelegt ist, bleibt der produktive `EventReadPort` bewusst unverdrahtet. Dadurch bleibt auch der vollständige TUI-Composition-Root blockiert, ohne eingefrorene Bereiche zu gefährden.

## Nächster Schritt

I81 gaten und einfrieren. Danach separat die minimale `EventItem.symbol`-Projektion entscheiden; erst anschließend einen Event-Provider prüfen.