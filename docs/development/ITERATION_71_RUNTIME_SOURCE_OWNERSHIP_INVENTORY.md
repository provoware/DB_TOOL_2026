# Iteration 71 – Runtime Source/Ownership Inventory

## Änderung

I71 setzt den I70-Entscheid ausschließlich read-only fort. Ziel ist nicht, einen Starter zu bauen, sondern die noch offenen produktiven Quellen und deren Ownership zu belegen.

## Schritt 1 – Inventar

### Catalog-Read

`TuiCatalogReadAdapter` besitzt eine klare fachliche Quelle: `CatalogReadPort`. Kategorie, Entry und Feld/Wert sind damit bereits produktiv projizierbar.

### Health

Der Adapter definiert `HealthReadPort.health()`, erhält die Quelle aber ausschließlich per Konstruktor-Injektion. Im geprüften produktiven TUI-Pfad ist keine eindeutige konkrete Health-Provider-Ownership belegt.

### Events

Analog definiert der Adapter `EventReadPort.recent_events(limit)`, ohne die Quelle zu erzeugen oder zu besitzen. Auch hier ist im geprüften produktiven Pfad keine eindeutige Provider-Ownership belegt.

### TUI-Runtime

`ProvowareDbTui` konsumiert ein fertiges `TuiDataPort` und optionale Writer. Die Runtime liest Health und Events beim Aufbau über den injizierten Data-Port, erzeugt aber weder deren Quellen noch Datenbankverbindungen. Das ist eine saubere Consumer-Grenze und soll erhalten bleiben.

### Schreibfähiger Connection-Lifecycle

I70 hat bereits festgestellt, dass der Web-Startup als read-only Präzedenzfall nicht unverändert für die vorhandenen TUI-Write-Seams taugt. Die jetzige Inventur liefert keinen Grund, Connection-Ownership oder Close-Reihenfolge im TUI-Starter neu zu erfinden oder dafür eingefrorene Persistenz zu öffnen.

## Zwischen-Gate-Entscheidung

Die Consumer-Seams sind klar, die produktive Provider-/Lifecycle-Ownership aber noch nicht eindeutig belegt.

**Schritt 2 = NO_WIRING_CONTRACT_REQUIRED.**

Es wird deshalb weder ein Composition Root noch ein Health/Event-Provider noch ein Connection-Lifecycle-Vertrag implementiert.

## Freeze-Schutz

Unverändert bleiben insbesondere CP-03, Schema/Migrationen, Storage/Repositories, Domain/Application-Core, bestehende TUI-Runtime und alle eingefrorenen CP-09-Slices.

## Exit-Kriterium

I71 ist abgeschlossen, wenn der Scope-Gate bestätigt, dass ausschließlich diese Inventur dokumentiert wurde. Der nächste sichere Schritt muss die kleinste noch offene Provider- oder Lifecycle-Grenze separat entscheiden, statt mehrere Ownership-Fragen in einem Starter zu bündeln.
