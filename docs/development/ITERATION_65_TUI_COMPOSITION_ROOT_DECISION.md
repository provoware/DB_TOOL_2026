# Iteration 65 – TUI Composition Root / Starter Decision

## Zweck

I65 klärt ausschließlich, ob ein produktiver TUI-Composition-Root bzw. Starter **jetzt** der nächste sinnvolle Integrationsblock ist.

Die Iteration besteht aus zwei Schritten:

1. read-only Architektur- und Wiring-Inventur;
2. nur bei positiver Entscheidung: minimalen portablen Wiring-Vertrag festlegen.

Es wird kein Starter implementiert.

## Schritt 1 – Read-only Inventur

### Vorhandene TUI-Bausteine

Die TUI besitzt:

- `ProvowareDbTui`;
- `TuiDataPort` als Protocol;
- `CategoryWriteAdapter`;
- `EntryWriteAdapter`;
- `EntryFieldWriteAdapter`;
- getestete read-only Kategorie-/Entry-/Field-Navigation;
- getestete schmale Create-Pfade.

### Fehlender produktiver Read-Adapter

Im produktiven TUI-Paket existiert **kein** konkreter Adapter, der einen realen `CatalogService` in `TuiDataPort` projiziert.

Insbesondere fehlt eine produktive Implementierung für:

- `categories() -> Sequence[NavItem]`;
- `entries(category_id) -> Sequence[NavItem]`;
- `fields(entry_id) -> Sequence[FieldRow]`;
- `health() -> Sequence[HealthItem]`;
- `recent_events(limit) -> Sequence[EventItem]`.

Die bisherigen TUI-Tests verwenden gezielt Test-Fakes.

### Vergleich mit CP-07H Web

Die Web-Seite besitzt bereits einen echten Startup-/Composition-Pfad:

- `build_readonly_runtime(main_db)`;
- read-only SQLite-Verbindung;
- Schema-Guard;
- konkrete Repository-Projektion;
- `CatalogService`-Instanz;
- kontrolliertes Close;
- CLI-Start.

Damit ist der Web-Pfad produktiv verdrahtbar.

Die TUI besitzt keinen äquivalenten produktiven Read-/Startup-Pfad.

### Warum ein TUI-Starter jetzt zu breit wäre

Ein Composition Root müsste aktuell gleichzeitig entscheiden oder implementieren:

1. Main-DB öffnen und validieren;
2. State-DB für schreibfähige `CatalogService`-Instanz öffnen;
3. `app_session_id` erzeugen;
4. `app_version` festlegen;
5. produktiven `TuiDataPort` erzeugen;
6. Health/Event-Projektion erzeugen;
7. Category-/Entry-/Field-Writer injizieren;
8. Lifecycle/Close-Verhalten definieren;
9. CLI-/Startargumente definieren.

Das wäre kein reiner Wiring-Schritt mehr, sondern mehrere neue Architekturverträge auf einmal.

## Entscheidung

**NEGATIV – ein produktiver TUI-Composition-Root/Starter ist jetzt noch nicht der nächste sinnvolle Integrationsblock.**

Der unmittelbare Blocker ist nicht SQLite oder die Write-Adapter-Schicht, sondern der fehlende **produktive TUI Read Adapter**.

## Nächste Voraussetzung

Vor einem produktiven TUI-Composition-Root muss separat geklärt werden:

**`CatalogService/read-side sources → TuiDataPort`**

als produktiver, read-only Adaptervertrag.

Der kleinste sinnvolle Vorvertrag muss mindestens festlegen:

- Kategorien → `NavItem`;
- Einträge → `NavItem`;
- Felder + Werte → `FieldRow`;
- Health-/Event-Quelle ohne SQL in der UI;
- keine Write-Semantik;
- keine Runtime-Änderung.

## Verhältnis zu I64 Scalar Value

I64 hat den nächsten fachlichen CP-09-Vertrag als Scalar Value Write vorbereitet.

Diese fachliche Reihenfolge bleibt gültig.

Die fehlende TUI-Composition verhindert **nicht** die Implementierung eines dünnen Scalar-Value-Adapters als isolierte Seam.

Sie verhindert lediglich eine seriöse **produktive TUI-Verdrahtung**, solange der Read-Port nicht produktiv implementiert ist.

## Schritt 2

Die Bedingung für Schritt 2 lautet ausdrücklich: **nur bei positiver Composition-Root-Entscheidung**.

Da Schritt 1 negativ ausfällt:

**STEP 2 = NO_CONTRACT_REQUIRED**

Es wird kein Wiring-Vertrag erfunden und kein zweiter Repository-Commit benötigt, sofern der Schritt-1-Gate grün ist.

Das entspricht der I63-Regel für einen `NO_FIX_REQUIRED`-/No-Write-Folgeschritt.

## Harte Non-Goals

I65 verändert nicht:

- TUI Runtime;
- Write Adapter;
- CatalogService;
- Domain;
- Repository/SQLite;
- Schema;
- Web Startup;
- Scalar Value Adapter;
- start.sh;
- Dependencies;
- CI.

## Exit-Kriterium

I65 ist abgeschlossen, wenn:

1. der fehlende produktive `TuiDataPort` als konkreter Wiring-Blocker belegt ist;
2. kein bestehender produktiver TUI Read Adapter übersehen wurde;
3. Composition Root deshalb nachvollziehbar vertagt wird;
4. Schritt 2 ohne zusätzlichen Commit als nicht anwendbar abgeschlossen wird;
5. Manifest-/Scope-Gate grün ist.

## Ergebnis

Der nächste sinnvolle Integrationsschritt ist **nicht** der Starter selbst.

Zuerst muss ein kleiner, produktiver **TUI Read Adapter** inventarisiert und vertraglich festgelegt werden. Erst danach ist ein Composition Root codesparsam und testbar.
