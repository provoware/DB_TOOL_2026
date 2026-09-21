# Iteration 36 – CP-08 Read-only Status Consolidation

## Zweck

Iteration 36 ist ausschließlich eine Konsolidierungs- und Scope-Iteration nach dem eingefrorenen I35-Stand. Es wird kein Produktcode verändert und kein neuer Funktionsblock freigegeben.

## Ausgangslage

Der Ausgangs-`main` steht auf `9a3eb58db20ab5291df9eef6a83b43959b03ce3d`.

CP-08 wurde in kleinen, getrennten Schritten aufgebaut:

- I32: Read-only Status Foundation geplant und begrenzt freigegeben.
- I33: `TuiDataPort.health()` einmalig lesend in der Textual-Runtime dargestellt.
- I34: Ereignisoberfläche separat geplant und begrenzt freigegeben.
- I35: `TuiDataPort.recent_events(limit=10)` einmalig lesend dargestellt und mit 160×40-Evidence abgenommen.

Damit sind die zwei bereits vorhandenen read-only Statusverträge des `TuiDataPort` in der Oberfläche angekommen. Ein weiterer CP-08-Produktblock wäre ohne neue fachliche Freigabe erfunden.

## Gewählter nächster Schritt

**CP-08 Read-only Status Foundation konsolidieren und einfrieren.**

I36 dokumentiert nur die erreichte Grenze. Sie autorisiert weder CP-09 noch Autosave, Polling, Audit-Persistenz, CRUD, Undo, Restore oder neue Datenquellen.

## Konsolidierter CP-08-Umfang

Zum eingefrorenen CP-08-Stand gehören ausschließlich:

- einmaliger read-only `health()`-Snapshot beim Start,
- nicht fokussierbare Health-/Ampeldarstellung,
- einmaliger read-only `recent_events(limit=10)`-Snapshot beim Start,
- maximal zehn dargestellte Ereignisse,
- expliziter Ereignis-Leerzustand,
- unveränderte Kategorie → Eintrag → Feld-Navigation,
- bestehende Layout-/Fokusgrenzen und I35-Visual-Evidence.

## Freeze-Grenzen

Nach erfolgreichem I36-Gate gilt CP-08 als geschlossen. Änderungen daran benötigen künftig einen expliziten REOPEN mit Begründung, Impact-Analyse und direkt betroffener Regression.

Unverändert geschützt bleiben insbesondere:

- CP-03 / Schema V1 / Migrationen,
- CP-06 / Domain-/Repository-Kern,
- SQLite-Repositories und Audit-Persistenz,
- CP-07H Browserpfad,
- CP-07T Navigationssemantik,
- CRUD-/Write-Pfade.

## Non-Goals

I36 führt ausdrücklich **nicht** ein:

- Autosave,
- Polling oder Hintergrund-Refresh,
- neue Health- oder Event-Datenquellen,
- Audit-Persistenz oder Änderungen an `storage/sqlite/audit.py`,
- Papierkorb/Restore/Undo,
- CRUD oder sonstige Schreibpfade,
- CP-09-Produktcode,
- neue UI-Navigation,
- Theme-/Layout-Redesign,
- Dependency- oder CI-Änderungen.

## Exit-Gates

1. Ausschließlich dieses Konsolidierungsdokument und das I36-Manifest sind geändert.
2. Kein Produktcode ist geändert.
3. CP-03, CP-06 und alle übrigen Frozen-Bereiche sind unverändert.
4. Repository Foundation ist grün.
5. Agent Governance ist grün.
6. Targeted Iteration prüft ausschließlich den dokumentarischen Scope; kein Full-Suite-, Browser-, Repository- oder TUI-Produktregressionstest ohne Produktänderung.
7. Kein Screenshot: I35 besitzt bereits die aktuelle 160×40-Evidence.
8. Bei komplett grünem Gate wird I36 squash-gemergt und CP-08 als konsolidiert/frozen behandelt.

## Risiko

Das Projektziel enthält weitere Funktionen wie Autosave, Papierkorb/Restore, Undo, Audit und Crash-Recovery. Deren Reihenfolge und Architekturgrenzen sind nach CP-08 noch nicht verbindlich aufgelöst. I36 darf diese Lücke nicht durch stillschweigende Implementierung schließen.

## Nächster Schritt nach Freeze

Erst nach grün eingefrorenem I36 wird auf einem frischen Branch ausschließlich der nächste noch offene Checkpoint aus Projektziel, vorhandenen Verträgen und Freeze-Grenzen aufgelöst. Diese Folgeiteration ist zunächst wieder Planung; Produktcode bleibt gesperrt, bis Scope, Non-Goals und Exit-Gates eindeutig feststehen.
