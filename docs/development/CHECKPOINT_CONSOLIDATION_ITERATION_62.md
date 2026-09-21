# Iteration 62 – CP-09 Entry-Field-Create Audit und Freeze

## Zweck

I62 konsolidiert ausschließlich den in I47–I61 aufgebauten **Entry-Field-Create-Slice** von CP-09.

Die Iteration besteht aus genau zwei Schritten:

1. vollständiger Audit des freigegebenen Vertrags und seiner Regressionen;
2. formaler Freeze nur dann, wenn Schritt 1 vollständig grün ist.

I62 führt keine neue Produktfunktion ein.

## Audit-Grenze

Gegenstand des Audits ist ausschließlich:

- `CatalogService.create_entry_field(...)` als vorhandener Application-Service-Vertrag;
- `EntryFieldWriteAdapter` als dünne TUI-Schreibgrenze;
- unveränderte `FieldType`-Übergabe;
- unveränderte `FieldDefinition`-Rückgabe;
- stabile erfasste `entry_id`;
- genau ein Write pro Submit;
- Read-Port-Refresh über `TuiDataPort.fields(entry_id)`;
- Fehler-/Cancel-/Fokusvertrag;
- die sieben freigegebenen Create-Typen;
- Ausschluss von `MONEY`, `SINGLE_CHOICE`, `MULTI_CHOICE`;
- gemeinsame FieldType-Labels ohne Änderung der TUI-Sicherheitsmenge;
- automatisierte Keyboard-/Layout-Evidence aus I61.

## Audit I47–I61

### I47 – Scope

Der kleinste nächste Write-Scope wurde korrekt als `create_entry_field()` auf Entry-Ebene gewählt.

Nicht freigegeben wurden:

- Kategorie-Felder;
- Values;
- Choice-Optionen.

**Audit:** konsistent.

### I48 / I53 – Adapter- und Rückgabegrenze

`FieldRow` wurde bewusst nicht als Create-Result missbraucht.

Der spätere Adapter gibt die vorhandene `FieldDefinition` unverändert zurück.

**Audit:** konsistent; keine doppelte Ergebnisabstraktion.

### I54 – Adapter-Seam

`EntryFieldWriteAdapter` delegiert exakt einmal an den injizierten Service.

Der Adapter:

- führt keine Repository-/SQL-Operation aus;
- verändert `FieldType` nicht;
- gibt dieselbe `FieldDefinition` zurück;
- lässt DOM-104/DOM-202 unverändert passieren.

**Audit:** konsistent.

### I55 / I57 – Integrations- und Reopen-Grenze

Die Runtime darf nur mit stabil erfasster Parent-ID arbeiten.

Erlaubte Create-Typen:

- TEXT
- LONG_TEXT
- INTEGER
- DECIMAL
- DATE
- DATETIME
- BOOLEAN

Weiterhin gesperrt:

- MONEY;
- SINGLE_CHOICE;
- MULTI_CHOICE.

**Audit:** konsistent.

### I58 – TUI-Feldanlage

Der Runtime-Flow erfüllt den freigegebenen Vertrag:

`Entry wählen → F → Typ wählen → Name → Enter`

Nachweise:

- ohne Field-Writer kein Write;
- ohne ausgewählten Entry kein Write;
- Parent-ID wird vor der Eingabe erfasst;
- Änderung des sichtbaren Entry-Index verändert den Parent nicht;
- exakt ein Adapter-Write;
- Erfolg refresht nur die Felder des erfassten Entries;
- Fehler refresht nichts;
- Fehler behält Parent/Typ/Fokus;
- Escape schreibt nichts und löscht transienten State;
- Erfolg fokussiert die Feldliste.

**Audit:** konsistent.

### I60 – gemeinsame FieldType-Bezeichnungen

Web und TUI verwenden dieselbe kleine Labelquelle.

Die TUI-Sicherheitsmenge der sieben Create-Typen bleibt separat und explizit.

**Audit:** konsistent; Wartbarkeit verbessert ohne Policy-Kopplung.

### I61 – Accessibility-/Keyboard-Evidence

Automatisierte Layout-Stress-Evidence:

- 100 % Proxy: 160×40;
- 150 % Proxy: 107×27;
- 200 % Proxy: 80×20.

Bei allen drei Stufen:

- Keyboard-Pfad vollständig;
- Typauswahl fokussiert;
- sieben Typen vorhanden;
- genau ein Write;
- finaler Fokus auf Feldliste;
- kein nachgewiesener Layout-Blocker.

Die Evidence ersetzt ausdrücklich keine subjektive menschliche Wahrnehmungsabnahme.

**Audit:** technisch grün.

## Realer Wiring-Scope

Das Repository besitzt aktuell keinen allgemeinen produktiven CP-07T-Launcher, der Writer selbst verdrahtet.

Dieser Umstand ist **kein offener Vertrag innerhalb I47–I61**, weil der freigegebene Slice ausdrücklich die injizierbare Runtime-/Adapter-Grenze und deren Verhalten abdeckt.

Ein zukünftiger Launcher-/Composition-Root ist ein separater Produkt-Scope und darf nicht rückwirkend in diesen Freeze hineingezogen werden.

## Harte Non-Goals

Nicht Bestandteil dieses Freeze:

- Kategorie-Feldanlage;
- Field Values;
- Choice-Optionen;
- MONEY mit `currency_code`;
- SINGLE_CHOICE / MULTI_CHOICE Create;
- allgemeiner TUI-Launcher / Composition Root;
- Autosave;
- Undo;
- Restore;
- Crash-Recovery;
- neue Repository-/Storage-Verträge;
- neue Domain-/Schemaänderungen.

## Schritt-1 Exit-Gates

Der Audit darf nur als vollständig grün gelten, wenn folgende fokussierte Regressionen bestehen:

1. `EntryFieldWriteAdapter`-Vertrag;
2. TUI-Feld-Create-Vertrag;
3. Accessibility-/Keyboard-Evidence;
4. gemeinsamer FieldType-Label-Vertrag;
5. bestehender Entry-Create-Vertrag als direkte TUI-Nachbarregression;
6. bestehender Runtime-Shell-Vertrag;
7. Manifest-/Scope-Gate.

## Audit-Ergebnis vor Zwischen-Gate

Aus der statischen Vertragsprüfung ergibt sich **kein belegter offener Restvertrag** innerhalb des I47–I61-Slices.

Der formale Freeze darf dennoch erst nach vollständig grünem Schritt-1-Zwischen-Gate erfolgen.

## Schritt 2

Bei grünem Zwischen-Gate wird dieser Slice formal auf **FROZEN** gesetzt.

Jede spätere Änderung an:

- `EntryFieldWriteAdapter`-Semantik;
- Parent-Capture;
- Create-Typmenge;
- Write-Anzahl;
- Refresh-Verhalten;
- Fehler-/Cancel-/Fokusvertrag

benötigt danach einen expliziten **REOPEN** mit Begründung, Impact-Analyse und direkt betroffenen Regressionen.

Wenn der Zwischen-Gate einen reproduzierbaren Vertragsfehler zeigt, wird stattdessen ausschließlich genau dieser eine Restvertrag geschlossen.
