# Iteration 83 – Read-only Event Provider

## Änderung

I83 implementiert ausschließlich den nach I78, I81 und I82 autorisierten dünnen read-only Event-Provider. CP-03, CP-08 und alle eingefrorenen Schreib-Slices bleiben unverändert.

## Umsetzung

`AuditEventReadProvider` erhält eine geliehene SQLite-Connection und liest ausschließlich `audit_events`. Die Projektion bleibt exakt beim bereits entschiedenen Vertrag:

- `occurred_at` → `EventItem.time_label` unverändert als Text,
- konstantes `·` → `EventItem.symbol`,
- `summary` → `EventItem.text`.

Die Reihenfolge ist `occurred_at DESC, id DESC`. Der zweite Schlüssel macht gleiche Zeitstempel deterministisch. Nichtpositive Limits liefern leer; positive Limits werden hart auf 100 begrenzt. Der Provider schließt die geliehene Connection niemals.

## Freeze-Schutz

Unverändert: CP-03/CP-08, Schema/Migrationen, `storage/sqlite/audit.py`, Operation Journal, Repositories, Domain/Application-Core, TUI-Runtime/View-Models, Writer und Starter.

## Prüfstrategie

Fokussiert werden Projektion/Reihenfolge, neutrales Symbol, nichtpositive und übergroße Limits sowie fehlende Close-Ownership geprüft. Zusätzlich gelten Manifest-, Scope- und Governance-Gates. Keine Full-Suite, Browser- oder visuellen Tests, da deren Trigger nicht betroffen sind.

## Verbleibendes Risiko

Der Provider ist absichtlich noch nicht in einen produktiven TUI-Composition-Root verdrahtet. Ein späterer Root muss weiterhin genau eine read-only Connection besitzen und Writer-Lifecycle getrennt halten.

## Nächster Schritt

I83 gaten und einfrieren. Danach I84 ausschließlich den TUI-Composition-Root gegen `TuiCatalogReadAdapter`, `DatabaseReadinessHealthProvider`, `AuditEventReadProvider` und I78-Ownership erneut inventarisieren.
