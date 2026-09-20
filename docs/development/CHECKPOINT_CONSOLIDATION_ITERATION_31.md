# Iteration 31 – CP-07T Read-only Checkpoint Consolidation

## Zweck

Iteration 31 löst den nach Iteration 30 verbliebenen CP-07T-Scope auf. Sie ist bewusst ein reiner Konsolidierungs- und Regressionsschritt. Es wird keine neue Produktfunktion eingeführt.

## Befund aus `main`

Der aktuelle `main` steht auf `abb9a4732f26b6794500c6bd094544c912972357`.

Der in Iteration 22 freigegebene CP-07T-Scope verlangte ausschließlich:

- Textual-Runtime inventarisieren und anbinden,
- Kategorie-, Eintrag- und Feld-Lesepfade validieren,
- Tastatur-/Fokusführung validieren,
- repräsentative 80×24- und große Viewport-Gates,
- keinen direkten SQL-Zugriff,
- keinen neuen Schreibpfad,
- keine Änderung geschützter Freeze-Bereiche.

Diese Anforderungen sind durch Iterationen 24 bis 30 bereits funktional abgedeckt:

- I24: minimale read-only Textual-Shell, 80×24 / 160×40, Fokus-/Tastatur-Smoke, No-SQL-Guard,
- I25: Kategorie → Einträge + Visual Evidence,
- I26: Eintrag → Felder,
- I27: keyboard-stabile Leerzustände für Einträge/Felder,
- I28: Null-Kategorien-Startzustand,
- I29: manueller Kategorie-Refresh,
- I30: Auswahl-Erhalt per stabiler Kategorie-ID + Visual Evidence.

Damit existiert innerhalb des explizit freigegebenen CP-07T-Scopes kein weiterer noch offener Funktionsblock.

## Nicht als I31-Feature ableiten

`TuiDataPort.health()` und `TuiDataPort.recent_events()` existieren als Vertrag, wurden aber weder in Iteration 22 als freizugebende CP-07T-Funktion genannt noch durch Iteration 23 als nächster Runtime-Block ausgewählt.

Sie jetzt automatisch als I31-Funktion zu implementieren wäre ein neuer Produkt-Scope ohne Masterplan-Freigabe und ist daher ausdrücklich ausgeschlossen.

## Konsolidierter CP-07T-Teilstand

Nach erfolgreichem I31-Gate gilt als CP-07T-Read-only-Checkpoint konsolidiert:

- injizierter `TuiDataPort` als einzige Runtime-Datengrenze,
- Kategorie → Eintrag → Felder read-only,
- stabile gerenderte IDs für Kategorie-/Eintragsnavigation,
- keyboard-stabile Leerzustände,
- Null-Kategorien-Zustand,
- manueller Kategorie-Refresh,
- Erhalt der gewählten Kategorie per stabiler ID, sofern sie weiter existiert,
- deterministischer Fallback bei entfernter oder leerer Kategorie-Liste,
- Layout-Klassifizierung für 80×24 und 160×40,
- dokumentierte Visual Evidence aus I25 und I30,
- kein direkter Storage-/SQLite-/SQL-Zugriff aus der Runtime,
- keine Mutation.

## Non-Goals

Nicht Bestandteil von Iteration 31 sind:

- `health()` oder `recent_events()` in der TUI,
- neue Navigationsebenen,
- automatisches Polling oder Hintergrund-Refresh,
- neue Produktfeatures,
- CP-03 Schema V1 oder Migrationen,
- CP-06 / Frozen Core,
- SQLite-Repositories,
- CP-07H Browserpfad,
- CRUD, Schreiben, Papierkorb, Restore oder Undo,
- Theme-/Responsive-Umbauten,
- Dependency- oder CI-Umbauten.

## Harte Freeze-Grenzen

Unverändert und geschlossen bleiben:

- CP-03 Schema V1,
- Schema und Migrationen,
- CP-06 / Frozen Core,
- SQLite-Repository-Schicht,
- CP-07H read-only Browserpfad.

Der durch I31 konsolidierte CP-07T-Read-only-Teilstand darf danach ebenfalls nur über einen neu dokumentierten Scope verändert werden.

## Exit-Gates

1. Compile ausschließlich `src/provoware_db/tui/runtime.py` und `tests/tui/test_runtime_shell.py`.
2. Bestehende gezielte CP-07T-Runtime-Regression erfolgreich:
   - 80×24 compact,
   - 160×40 wide,
   - Kategorie → Eintrag → Felder,
   - stabile Kategorie-/Eintragsidentität,
   - Leerzustände,
   - Null-Kategorien-Zustand,
   - manueller Refresh,
   - Auswahl-Erhalt/Fallback.
3. No-SQL-/No-Storage-Guard unverändert grün.
4. Repository-/Governance-Gates grün.
5. Keine ungeplante Datei und keine Freeze-Verletzung.
6. Kein Full-Suite-Lauf ohne konkreten Trigger.
7. Kein neuer Screenshot, da I31 weder fünfte Iteration noch visuelle Änderung ist.

## Exit-Kriterium

Nur wenn alle ausgelösten Gates grün sind, gilt CP-07T als konsolidierter read-only Checkpoint. Bei Rot wird ausschließlich der erste reproduzierbare Befund im direkt betroffenen Scope untersucht.

## Nächster Schritt nach I31

Erst nach erfolgreicher Konsolidierung den nächsten noch offenen Masterplan-Checkpoint gegen den dann aktuellen `main` auflösen. Es darf kein neues Feature allein aus ungenutzten Port-Methoden oder vorhandenen Modellklassen abgeleitet werden.
