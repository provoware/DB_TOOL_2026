# Iteration 32 – CP-08 Read-only Status Foundation Scope

## Zweck

Iteration 32 ist ausschließlich eine Masterplan-/Scope-Auflösung nach dem in Iteration 31 eingefrorenen CP-07T-Checkpoint. Es wird kein Produktcode verändert.

## Ausgangslage

Der aktuelle `main` steht auf `16da88c914e04232e9fc05afe7e166ce9e04b7d8`.

Im Repository existiert nach CP-07 kein bereits dokumentierter CP-08/CP-09-Checkpoint. Gleichzeitig nennt das verbindliche Projektziel in `README.md` ausdrücklich:

- ein Autosave-/Statuskonzept,
- nachvollziehbare GRÜN/GELB/ROT-Selbstvalidierung.

Der bestehende read-only Vertrag `TuiDataPort` enthält dafür bereits `health()`. Die ebenfalls vorhandene Methode `recent_events()` passt dagegen zum getrennt genannten Audit-/Ereignisbereich.

Damit kann der nächste Checkpoint nicht aus einer vorhandenen CP-08-Datei gelesen werden; er muss in dieser Planungsiteration explizit und eng autorisiert werden.

## Gewählter nächster Checkpoint

**CP-08 – Read-only Status Foundation**

Ziel ist ausschließlich eine lesende Statusdarstellung oberhalb des bereits injizierten `TuiDataPort`. Der erste Funktionsblock darf nur vorhandene `HealthItem`-Daten aus `TuiDataPort.health()` darstellen.

Diese Scope-Freigabe ist keine Autorisierung für neue Datenquellen, SQL, Repository-Änderungen oder Mutationen.

## Kleinster späterer Funktionsblock

Nach grün eingefrorenem I32-Scope darf auf einem frischen Branch genau ein kleiner I33-Block entstehen:

- `health()` genau einmal read-only aus dem injizierten `TuiDataPort` lesen,
- Health-Daten als nicht fokussierbare Statusdarstellung in der bestehenden Textual-Runtime anzeigen,
- vorhandene Kategorie-/Eintrag-/Feld-Navigation unverändert lassen,
- keine neue Navigationsebene erzeugen,
- 80×24 und 160×40 auf Überlagerung/Fokus regressionsprüfen,
- No-SQL-/No-Storage-/No-Write-Grenzen unverändert beweisen.

## Begründung für `health()`

Die Freigabe stützt sich auf zwei bereits vorhandene Artefakte:

1. Das Projektziel fordert Statuskonzept und GRÜN/GELB/ROT-Selbstvalidierung.
2. Der UI-Port besitzt bereits den read-only Vertrag `health() -> Sequence[HealthItem]`.

Damit wird keine neue Domänenfunktion erfunden; es wird nur eine bereits geplante Produktanforderung mit einem bereits vorhandenen UI-Vertrag verbunden.

## Einordnung von `recent_events()`

`recent_events()` wird **nicht** in den ersten CP-08-Block aufgenommen.

Grund:

- Das Projektziel nennt Audit separat.
- `EventItem` / `recent_events()` gehören fachlich eher zur Ereignis-/Auditdarstellung.
- Eine gleichzeitige Einführung von Status und Ereignissen würde zwei Verantwortungen vermischen.
- Es existiert noch keine explizit freigegebene Ereignis-/Audit-UI-Scopegrenze.

Eine spätere Freigabe muss separat geplant werden.

## Begrenzter REOPEN

CP-07T bleibt als Checkpoint eingefroren. Für den späteren I33-Funktionsblock wird ausschließlich folgende begrenzte Erweiterung autorisiert:

- `src/provoware_db/tui/runtime.py`: nur zusätzliche read-only Health-Darstellung,
- `tests/tui/test_runtime_shell.py`: nur direkt zugehörige Health- und Layout-/Fokus-Regressionen.

Bestehende CP-07T-Navigation darf nicht semantisch verändert werden.

Dies ist **kein** REOPEN von CP-06/Frozen Core, Schema, SQLite-Repositories oder CP-07H.

## Non-Goals

Ausdrücklich ausgeschlossen sind:

- `recent_events()` / Auditdarstellung,
- Autosave-Implementierung,
- automatisches Polling,
- Hintergrund-Refresh,
- CRUD-/Schreibfunktionen,
- Papierkorb/Restore/Undo,
- CP-03 Schema V1 oder Migrationen,
- CP-06 / Frozen Core,
- SQLite-Repositories,
- CP-07H Browserpfad,
- neue SQL-Zugriffe,
- neue Service-/Repository-Adapter,
- Theme-/Responsive-Redesign,
- Dependency-/CI-Umbauten.

## Freeze-Grenzen

Geschlossen bleiben:

- CP-03 und Schema/Migrationen,
- CP-06 / Frozen Core,
- SQLite-Repository-Schicht,
- CP-07H,
- bestehende CP-07T Navigationssemantik,
- CRUD-/Write-Pfade.

## Exit-Gates für I32

1. Ausschließlich Scope-Dokument und I32-Manifest geändert.
2. Kein Produktcode geändert.
3. Repository-Foundation grün.
4. Governance grün.
5. Kein Full-Suite-, Browser- oder TUI-Test ohne Produktänderung.
6. Kein Screenshot.

## Exit-Gates für den späteren I33-Funktionsblock

1. Compile ausschließlich direkt betroffene TUI-Dateien.
2. Gezielt neue Health-Darstellung testen.
3. Bestehende Kategorie→Eintrag→Feld-, Leerzustands-, Refresh- und Fokusregression weiter grün.
4. 80×24 und 160×40 stabil.
5. Health-Darstellung ist nicht fokussierbar und verändert keine Tastaturnavigation.
6. Kein direkter Storage-/SQLite-/SQL-Zugriff.
7. Kein Schreibpfad.
8. Keine Änderung geschützter Core-/Repository-/Browser-Bereiche.
9. Kein Full Suite ohne neuen Trigger.
10. Kein Screenshot in I33, sofern kein konkreter visueller Layoutbefund entsteht; I35 bleibt der reguläre nächste Screenshot-Meilenstein.

## Nächster Schritt

I32 ausschließlich gaten und einfrieren. Erst danach auf neuem Branch den oben definierten kleinsten I33-Health-Block implementieren.
