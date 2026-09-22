# Iteration 68 – produktiver TUI Read Adapter

## Zweck

I68 inventarisiert ausschließlich den in I65 belegten Blocker `CatalogService/read-side sources → TuiDataPort` und begrenzt danach den kleinsten produktiven Read-Adapter-Vertrag. Es wird noch kein Adapter und kein Composition Root implementiert.

## Schritt 1 – Read-only Inventur

`TuiDataPort` verlangt genau fünf Read-Operationen: `categories()`, `entries(category_id)`, `fields(entry_id)`, `health()` und `recent_events(limit)`.

Im produktiven TUI-Paket existiert weiterhin keine konkrete Implementierung dieses Protocols. `ProvowareDbTui` erhält den Port ausschließlich per Konstruktor und führt selbst kein SQL aus. Damit bleibt der in I65 festgestellte Blocker unverändert und klar isoliert.

### Bereits vorhandene Datenquellen

Für den fachlichen Navigationspfad sind keine neuen Repository- oder SQL-Verträge nötig:

- Kategorien: `CatalogService.list_categories()` → `NavItem`;
- Einträge: `CatalogService.list_entries(category_id)` → `NavItem`;
- Felder plus Werte: `CatalogService.list_fields_with_values(entry_id)` → `FieldRow`.

Der Web-Adapter belegt bereits, dass diese Application-Read-Verträge ausreichen, um Kategorien, Einträge sowie Feldwerte ohne SQL in der UI zu projizieren. Die TUI darf diese Projektion fachlich nachbilden, aber nicht aus `provoware_db.web` importieren.

### Health und Events

`CatalogService` besitzt keinen Health-/Event-Read-Vertrag. Diese beiden Quellen werden deshalb in I68 ausdrücklich **nicht** künstlich in `CatalogService` aufgenommen und auch nicht per SQL in den TUI-Adapter eingebaut.

Der spätere konkrete Adapter soll zwei schmale, injizierte Read-Quellen erhalten:

- `HealthReadPort` mit einer read-only Health-Projektion;
- `EventReadPort` mit `recent_events(limit)`.

Die konkrete produktive Erzeugung dieser Quellen gehört erst in den späteren Composition Root. Bestehende eingefrorene CP-08-Semantik wird dadurch nicht geöffnet.

## Zwischen-Gate

Die Inventur ergibt einen kleinen Adapter ohne neue Datenbank- oder Domain-Semantik. Der Schritt-2-Vertrag darf deshalb vorbereitet werden. CP-03, CP-08, Runtime und Writer bleiben außerhalb des Write-Scope.

## Schritt 2 – minimaler Adaptervertrag

Der spätere `TuiCatalogReadAdapter` soll ausschließlich:

1. einen `CatalogService`-kompatiblen Read-Port entgegennehmen;
2. Kategorien in `NavItem` projizieren;
3. Einträge in `NavItem` projizieren;
4. Felder und bereits gelesene Werte in `FieldRow` projizieren;
5. Health über eine injizierte Read-Quelle in `HealthItem` projizieren bzw. bereits projizierte Items durchreichen;
6. Events über eine injizierte Read-Quelle begrenzt als `EventItem` liefern.

### Harte Grenzen

Der Adapter darf nicht:

- SQL ausführen;
- Connections öffnen oder schließen;
- `CatalogService` konstruieren;
- Write-Adapter kennen oder aufrufen;
- Runtime-/Widget-Zustand verändern;
- Web-Adapter oder Web-ViewModels importieren;
- neue Health-/Event-Semantik definieren;
- CP-03, Schema oder Migrationen verändern.

Die Werteformatierung soll TUI-eigen bleiben oder später über eine neutrale gemeinsame Projektion extrahiert werden, falls echte Duplikation messbar entsteht. Für I68 wird keine vorzeitige Shared-Abstraktion eingeführt.

## Entscheidung

**READ_ADAPTER_CONTRACT_READY**

Der nächste Produktblock kann ein einzelner `TuiCatalogReadAdapter` plus fokussierte Contract-Tests sein. Composition Root und Starter bleiben bis zu dessen erfolgreicher Implementierung gesperrt.

## Exit-Kriterium

I68 ist abgeschlossen, wenn:

1. der fehlende konkrete `TuiDataPort` erneut belegt ist;
2. Kategorie → Entry → Feld/Wert vollständig auf vorhandene Application-Reads abgebildet ist;
3. Health/Event als getrennte Read-Quellen begrenzt sind;
4. kein SQL-, Runtime-, Writer-, CP-03- oder CP-08-Reopen entsteht;
5. Manifest-/Scope-Gate grün ist.
