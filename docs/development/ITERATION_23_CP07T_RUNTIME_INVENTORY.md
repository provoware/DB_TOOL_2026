# Iteration 23 – CP-07T Runtime Inventory

## Zweck

Nur-Lese-Inventur des in Iteration 22 freigegebenen CP-07T-Bereichs. Diese Iteration verändert keinen Produktcode.

## Reproduzierbarer Befund

Der aktuelle `src/provoware_db/tui/`-Baum enthält ausschließlich UI-Policies und View-Model-Verträge:

- `accessibility.py`
- `contrast.py`
- `layout_policy.py`
- `themes.py`
- `view_models.py`
- `__init__.py`

Es existiert derzeit keine Textual-App-/Screen-/Widget-Runtime, kein TUI-Startskript und keine Snapshot-Infrastruktur. Die vorhandenen TUI-Tests prüfen nur Accessibility-, Layout- sowie Theme-/Kontrast-Policies.

Damit kann ein Snapshot-/Fokus-Smoke noch nicht sinnvoll ausgeführt werden. Ein Versuch, Snapshot-Tests ohne Runtime einzuführen, würde Testinfrastruktur für nicht vorhandenes Produktverhalten bauen.

## Architekturgrenze

`TuiDataPort` ist bereits als Nur-Lese-Vertrag vorhanden (`categories`, `entries`, `fields`, `health`, `recent_events`). Der kleinste sichere nächste Produktblock kann daher oberhalb dieses Ports bleiben. Direkter SQL-/Repository-Zugriff aus der TUI ist nicht erforderlich und bleibt verboten.

## Freeze-Nachweis

Unverändert bleiben:

- CP-03 Schema V1 und Migrationen,
- CP-06 / Frozen Core,
- SQLite-Repositories,
- CP-07H Browserpfad,
- Schreib-, CRUD-, Papierkorb-, Restore- und Undo-Pfade.

## Kleinster nächster CP-07T-Block

Eine minimale read-only Textual-Runtime als Shell, die ausschließlich einen injizierten `TuiDataPort` konsumiert und zunächst Kategorie-Navigation plus stabile Layout-Klassifizierung bereitstellt. Erst für diese reale Runtime werden gezielte 80×24- und große-Viewport-Smokes/Snapshots sowie Fokus-/Tastaturtests gerechtfertigt.

Nicht Teil dieses nächsten Blocks: Datenbank-Bootstrap, neue SQL-Zugriffe, Mutationen, vollständige Drei-Stufen-Funktionalität oder kosmetische Theme-Arbeit.

## Exit-Gate dieser Inventur

- nur diese Inventurdokumentation geändert,
- Repository-/Governance-Gates grün,
- kein Produktcode geändert,
- nächster Block eindeutig aus einem reproduzierbaren Ist-Befund abgeleitet.

## Nächster Schritt

Nach grünem Gate diese Inventur einfrieren. Danach auf einem frischen Branch ausschließlich die minimale read-only Textual-Shell gegen `TuiDataPort` implementieren und nur deren direkt betroffene Compile-, Layout- und Tastatur/Fokus-Gates ausführen.
