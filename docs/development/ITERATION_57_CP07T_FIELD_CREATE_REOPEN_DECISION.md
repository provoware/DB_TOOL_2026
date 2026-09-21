# Iteration 57 – CP-07T Feldanlage Reopen-Entscheidung

## Zweck

I57 trifft ausschließlich die formale Reopen-Entscheidung für CP-07T nach den eingefrorenen I55- und I56-Verträgen.

Es wird **kein Runtime-Code** geändert.

## Entscheidung

**JA – CP-07T darf für genau einen minimalen Entry-Field-Create-Flow in I58 eng reopened werden.**

Diese Freigabe gilt ausschließlich für:

- den bereits eingefrorenen `EntryFieldWriteAdapter`;
- exakt einen ausgewählten Entry;
- exakt einen Feldnamen;
- exakt einen explizit ausgewählten freigegebenen `FieldType`;
- genau einen Adapter-Write;
- anschließenden Read-Port-Refresh nur für diesen Entry;
- deterministisches Fokus-/Cancel-/Fehlerverhalten.

Alle anderen CP-07T-Schreibpfade bleiben eingefroren.

## Freigegebene FieldTypes

I58 darf ausschließlich folgende Typen anbieten:

- `TEXT`
- `LONG_TEXT`
- `INTEGER`
- `DECIMAL`
- `DATE`
- `DATETIME`
- `BOOLEAN`

## Weiterhin gesperrte Typen

### MONEY

Bleibt gesperrt, weil der aktuelle I54-Adapter keinen `currency_code` transportiert.

### SINGLE_CHOICE / MULTI_CHOICE

Bleiben gesperrt, weil Options-Writes weiterhin geschlossen sind und eine Felddefinition ohne Optionen für Laien unvollständig wäre.

## Verbindlicher I58-Flow

1. Nutzer wählt einen Entry.
2. Feld-Create wird gestartet.
3. Die aktuelle `entry_id` wird sofort erfasst und bleibt bis Erfolg/Cancel/Fehler stabil.
4. Ein erlaubter `FieldType` wird explizit gewählt.
5. Der Feldname wird eingegeben.
6. Exakt ein Aufruf:
   `EntryFieldWriteAdapter.create_entry_field(captured_entry_id, name, captured_field_type)`
7. Bei Erfolg:
   - nur `TuiDataPort.fields(captured_entry_id)` neu lesen;
   - keine direkte `FieldDefinition` in die UI injizieren;
   - Entry-Auswahl erhalten;
   - Feldliste aktualisieren;
   - Fokus deterministisch auf Feldliste, sofern nicht leer.
8. Bei Fehler:
   - kein Refresh;
   - kein zweiter Write;
   - Parent-ID und FieldType bleiben erhalten;
   - Fokus bleibt im aktiven Create-Control.
9. Bei Escape:
   - kein Write;
   - Name, FieldType und Parent-ID löschen;
   - Fokus zurück auf den ursprünglichen Entry.

## Minimaler Runtime-State

I58 darf höchstens ergänzen:

- optionalen `EntryFieldWriteAdapter`;
- `_field_create_entry_id: str | None`;
- `_field_create_type: FieldType | None`;
- minimale transiente Controls für Typauswahl und Feldname.

Keine Repository-, SQL-, Storage- oder CatalogService-Abhängigkeit darf in die Runtime gelangen.

## Read-only-Kompatibilität

Die Konstruktion ohne `EntryFieldWriteAdapter` muss vollständig funktionieren.

Wenn kein Field-Writer injiziert ist:

- Feldanlage nicht verfügbar;
- keine Änderung an bestehender Navigation;
- keine Änderung an Kategorie-/Entry-Create;
- keine neue Abhängigkeit.

## FieldType-Auswahl

Die Auswahl muss keyboard-only bedienbar und deterministisch sein.

I57 schreibt keine konkrete Widget-Klasse vor. Zulässig ist die kleinste Textual-Lösung, die:

- nur die sieben erlaubten Typen anbietet;
- nicht frei editierbar ist;
- direkt auf `FieldType` abbildet;
- Escape sauber unterstützt;
- Fokus nicht verliert.

Eine neue allgemeine Text-/Capability-Registry ist dafür nicht erforderlich.

## Pflichtregressionen für I58

Mindestens:

- read-only Konstruktion unverändert;
- ohne Field-Writer kein Create;
- ohne ausgewählten Entry kein Write;
- Parent-ID beim Start eingefroren;
- sichtbarer Entry-Index darf während Eingabe wechseln, ohne Parent zu ändern;
- nur sieben erlaubte Typen auswählbar;
- exakt ein Adapter-Write;
- übergebener `FieldType` identisch;
- Erfolg refresht nur `fields(captured_entry_id)`;
- keine Category-/Entry-Reloads durch Erfolg;
- Fehler refresht nichts;
- Fehler hält Parent/Typ/Fokus;
- Escape schreibt nichts und löscht transienten State;
- bestehende Kategorie-/Entry-Create-Tests bleiben grün;
- Navigation/Fokusregressionen bleiben grün;
- MONEY/Choice nicht auswählbar;
- Runtime weiterhin ohne Storage-/SQL-Importe.

## Text-/Wartbarkeitsgrenze

I56 erlaubt später gemeinsame `FieldType`-Labels, sobald TUI und Web sie real gemeinsam benötigen.

Für I58 gilt jedoch:

**Kein zusätzlicher Textkatalog-Refactor neben der Feldanlage.**

Die erste Implementierung darf lokale, klar begrenzte Labels verwenden. Eine Zentralisierung gehört frühestens in I59.

## Freeze-Grenzen

Weiterhin geschlossen:

- CP-03;
- CP-06;
- SQLite/Storage;
- `CatalogService`;
- Domain-Modelle;
- Kategorie-Felder;
- Feldwerte;
- Choice-Optionen;
- `MONEY`;
- `SINGLE_CHOICE`;
- `MULTI_CHOICE`;
- allgemeine Registry-/Plugin-Infrastruktur.

## Ergebnis

Der Reopen ist fachlich ausreichend abgesichert.

**I58 darf CP-07T genau für die minimale Entry-Feldanlage reopen.**

Keine weitere TUI-Schreibfunktion wird dadurch freigegeben.
