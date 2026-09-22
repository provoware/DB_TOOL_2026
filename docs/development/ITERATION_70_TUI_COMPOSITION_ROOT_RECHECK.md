# Iteration 70 – TUI Composition Root Recheck

## Änderung

I70 prüft die in I65 vertagte Composition-Root-Entscheidung erneut gegen den aktuellen `main` nach I67 und I69.

Der damalige unmittelbare Blocker ist beseitigt: Mit `TuiCatalogReadAdapter` existiert jetzt eine produktive Projektion von `CatalogService` auf Kategorie, Entry und Feld/Wert. Der Adapter erwartet Health und Events jedoch weiterhin bewusst als getrennt injizierte Read-Quellen.

## Schritt 1 – Recheck

### Jetzt vorhanden

- produktiver `TuiCatalogReadAdapter` für Kategorie → Entry → Feld/Wert;
- bestehende TUI-ViewModels und `TuiDataPort`;
- schmale Category-, Entry-, EntryField- und Scalar-Value-Write-Seams;
- bestehende `ProvowareDbTui`-Constructor-Seams;
- Web-Startup als read-only Lifecycle-Präzedenzfall.

### Noch nicht eindeutig produktiv geklärt

1. **Health-Quelle:** Der TUI-Read-Adapter definiert nur `HealthReadPort`; er besitzt und erzeugt keine produktive Quelle.
2. **Event-Quelle:** Gleiches gilt für `EventReadPort` und `recent_events(limit)`.
3. **Schreibfähiger Lifecycle:** Der Web-Startup öffnet `main.db` ausdrücklich read-only und baut den `CatalogService` dafür partiell auf. Dieses Muster kann nicht unverändert für die bereits vorhandenen TUI-Write-Seams übernommen werden.
4. **Ownership/Close:** Für einen schreibfähigen TUI-Start muss eindeutig feststehen, wer Main-/State-Verbindungen und deren Close-Reihenfolge besitzt. Das darf nicht implizit im Starter erfunden werden.

## Entscheidung

**NEGATIV – der produktive Composition Root ist noch nicht der kleinste sichere Implementierungsblock.**

Die Lage ist gegenüber I65 deutlich enger: Nicht mehr die fachliche Read-Projektion blockiert, sondern ausschließlich die produktive Ownership der Health-/Event-Quellen und der bereits benötigte schreibfähige Lifecycle.

Ein Starter-Patch würde diese Entscheidungen gleichzeitig mit Runtime-Wiring treffen und wäre damit wieder breiter als eine atomare Iteration.

## Schritt 2

Da die Voraussetzung „produktive Quellen vollständig und eindeutig geklärt“ nicht erfüllt ist:

**STEP 2 = NO_WIRING_CONTRACT_REQUIRED**

Es wird kein Starter, kein Composition Root und kein künstlicher Status-Commit erzeugt. Nach grünem Scope-Gate ist I70 abgeschlossen.

## Freeze-Schutz

Unverändert bleiben CP-03, Schema/Migrationen, Storage/Repositories, eingefrorene CP-09-Slices, TUI-Runtime, Writer, `CatalogService`, Web-Startup und CI.

## Nächster sicherer Scope

Vor einem erneuten Composition-Root-Versuch ist separat und read-only zu inventarisieren, welche **bereits vorhandenen** Quellen Health und Events produktiv liefern können und welcher bestehende Lifecycle die Writer tragen kann. Nur wenn diese Inventur eine eindeutige bestehende Ownership ergibt, darf danach ein minimaler Wiring-Vertrag entstehen. Fehlt eine Quelle tatsächlich, muss sie als eigener kleiner Vertrag behandelt werden – nicht als Nebenprodukt des Starters.

## Exit-Gates

1. I69 beseitigt den alten Read-Adapter-Blocker nachweisbar.
2. Die verbleibenden Lifecycle-/Source-Fragen sind exakt eingegrenzt.
3. Keine eingefrorene Schicht wird geöffnet.
4. Manifest-/Write-Scope bleibt auf zwei I70-Dateien begrenzt.
5. Schritt 2 endet ohne Write als `NO_WIRING_CONTRACT_REQUIRED`.
