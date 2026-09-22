# Iteration 67 – Entry Scalar Value Write Adapter

## Schritt 1 – Einordnung

Der in I64 vorbereitete Scalar-Value-Adaptervertrag bleibt nach I65 unverändert ausführbar.

I65 blockiert einen produktiven TUI-Composition-Root, weil der produktive `TuiDataPort` noch fehlt. Diese Blockade betrifft jedoch nicht die isolierte Write-Seam: `EntryScalarValueWriteAdapter` benötigt weder Runtime-Wiring noch Read-Adapter, Datenbanköffnung, Health/Event-Projektion oder UI-Parsing.

**Entscheidung: FREI FÜR DEN DÜNNEN ADAPTER.**

## Schritt 2 – Minimaler Implementierungsumfang

Erlaubt sind ausschließlich:

- `EntryScalarValueWriteService` Protocol;
- `EntryScalarValueWriteAdapter`;
- fokussierte Contract-Tests.

Der Adapter delegiert exakt einmal an `set_scalar_value(entry_id, field_id, value)`, verändert keine Eingabe, fängt keine Domainfehler ab und gibt exakt das `ScalarValue`-Objekt des Services zurück.

## Harte Grenzen

Nicht Bestandteil von I67 sind TUI Runtime, Composition Root, `TuiDataPort`, Eingabewidgets, Parsing, Choice-Writes, MONEY-UI, Kategorie-Felder, CatalogService-, Domain-, Repository-, Storage- oder Schemaänderungen.

## Triggerbasierte Prüfungen

Gezielt erforderlich:

1. Compile von Adapter und neuem Test;
2. neuer Scalar-Adapter-Contract-Test;
3. bestehender Entry-Field-Adapter-Test als lokale Regression;
4. Manifest-/Scope-Gate.

Keine Volltests, Browser-, Runtime- oder Datenbanktests, weil diese Bereiche nicht verändert werden.
