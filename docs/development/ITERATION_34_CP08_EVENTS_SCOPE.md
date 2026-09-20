# Iteration 34 – CP-08 Read-only Event Surface Scope

## Zweck

Iteration 34 ist ausschließlich eine Planungs- und Scope-Iteration nach dem eingefrorenen I33-Health-Block. Es wird kein Produktcode verändert.

## Ausgangslage

`main` steht zu Beginn auf `6b6bc5a93e38ffbc4ea91a66c71f6099676a9c9c` (Iteration 33). I32 hat `recent_events()` ausdrücklich aus dem ersten CP-08-Block ausgeschlossen und für Ereignis/Audit eine separate Scope-Freigabe verlangt.

Der bestehende `TuiDataPort` enthält bereits den read-only Vertrag `recent_events(limit: int = 10) -> Sequence[EventItem]`. `EventItem` besitzt nur `time_label`, `symbol` und `text`. Diese Iteration erfindet weder neue Ereignisdaten noch öffnet sie Audit-Persistenz.

## Verantwortungsgrenze

Der nächste funktionale Slice darf ausschließlich vorhandene `EventItem`-Daten aus dem bereits injizierten `TuiDataPort` darstellen. Die TUI ist Konsument, nicht Erzeuger, Persistierer oder Interpreter von Auditdaten.

Nicht autorisiert sind Änderungen an `storage/sqlite/audit.py`, Operation Journal, Repositories, Schema, Migrationen, Catalog Service oder anderen Providern. Ebenso wird keine Aussage darüber eingeführt, ob `recent_events()` vollständige, revisionssichere oder persistierte Auditdaten repräsentiert.

## Kleinster späterer Funktionsblock

Nach grün eingefrorenem I34-Scope darf auf einem frischen Branch genau ein kleiner Funktionsblock entstehen:

- `recent_events(limit=10)` genau einmal read-only beim TUI-Start lesen,
- höchstens die zehn gelieferten `EventItem` in einer nicht fokussierbaren Ereignisfläche darstellen,
- leere Ereignisliste mit ruhigem read-only Leerzustand darstellen,
- Kategorie→Eintrag→Feld-Navigation und I33-Health-Anzeige unverändert lassen,
- keine neue Navigationsebene erzeugen,
- kein Polling, kein Hintergrund-Refresh und keine zeitgesteuerte Aktualisierung einführen.

## Begrenzter REOPEN

Für den späteren Funktionsblock dürfen ausschließlich diese Produkt-/Testbereiche begrenzt geöffnet werden:

- `src/provoware_db/tui/runtime.py`: read-only Ereignisdarstellung,
- `tests/tui/test_runtime_shell.py`: direkt zugehörige Ereignis-, Leerzustands-, Layout- und Fokusregressionen.

`src/provoware_db/tui/view_models.py` bleibt unverändert, solange der vorhandene `EventItem`-/`recent_events()`-Vertrag ausreicht.

## Non-Goals

Ausdrücklich ausgeschlossen sind:

- CP-03 Schema V1 oder Migrationen,
- CP-06 / Frozen Core,
- SQLite-Audit-, Journal- oder Repository-Änderungen,
- neue SQL-Zugriffe,
- neue Service-/Repository-Adapter,
- Ereignisse schreiben, löschen, quittieren oder filtern,
- CRUD-/Write-Pfade,
- Autosave,
- Polling oder Hintergrund-Refresh,
- Browser-/CP-07H-Änderungen,
- Theme-/Responsive-Redesign,
- Dependency-/CI-Umbauten.

## Exit-Gates für I34

1. Ausschließlich dieses Scope-Dokument und das I34-Manifest geändert.
2. Kein Produktcode geändert.
3. Repository-Foundation grün.
4. Governance grün.
5. Kein Full-Suite-, Browser- oder TUI-Test ohne Produktänderung.
6. Kein Screenshot.

## Exit-Gates für den späteren Funktionsblock

1. Compile ausschließlich direkt betroffene TUI-Dateien.
2. Gezielte Ereignisdarstellung und Leerzustand testen.
3. Bestehende Health-, Kategorie→Eintrag→Feld-, Leerzustands-, Refresh- und Fokusregressionen bleiben grün.
4. 80×24 und 160×40 bleiben ohne Überlagerung und Fokusverlust bedienbar.
5. Ereignisfläche ist nicht fokussierbar und verändert keine Tastaturnavigation.
6. `recent_events(limit=10)` wird nur read-only konsumiert; kein direkter Storage-/SQLite-/SQL-Zugriff.
7. Kein Schreibpfad, Polling oder Hintergrund-Refresh.
8. Keine Änderung geschützter Core-/Repository-/Browser-Bereiche.
9. Kein Full Suite ohne neuen Trigger.
10. Visuelle Evidence nur, wenn der geplante Screenshot-Meilenstein oder ein konkreter Layoutbefund sie verlangt.

## Verbleibendes Risiko

Die semantische Herkunft und Vollständigkeit der gelieferten Ereignisse bleibt absichtlich außerhalb dieses UI-Scope. Sollte der spätere Funktionsblock einen Provider- oder Audit-Persistenzmangel sichtbar machen, ist dafür ein eigener REOPEN-Befund erforderlich; er darf nicht nebenbei in der TUI-Iteration behoben werden.

## Nächster Schritt

I34 ausschließlich gaten und einfrieren. Erst danach darf auf einem frischen Branch der oben definierte minimale read-only Ereignis-Slice umgesetzt werden.
