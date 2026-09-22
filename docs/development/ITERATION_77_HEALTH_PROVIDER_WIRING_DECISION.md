# Iteration 77 – Health Provider Wiring Decision

## Änderung

I77 prüft ausschließlich read-only, ob der in I74 definierte Database-Readiness-Vertrag und die in I76 autorisierte binäre Health-Projektion über eine bereits vorhandene Connection-/Factory-Seam als dünner `HealthReadPort`-Provider produktiv verdrahtet werden können.

## Befund

`src/provoware_db/storage/sqlite/connection.py` stellt mit `open_connection(path, read_only=True)` eine allgemeine technische Connection-Factory bereit. Diese Factory definiert jedoch keine TUI-spezifische Ownership, Lebensdauer oder Close-Reihenfolge.

Der vorhandene Web-Startup besitzt einen klaren read-only Lifecycle: `build_readonly_runtime()` öffnet und validiert die Connection, `ReadOnlyWebRuntime` hält sie und `close()` schließt sie. Dieser Lifecycle gehört dem Web-Pfad und ist kein bereits autorisierter TUI-Composition-Root.

I71 hat für den produktiven TUI-Pfad ausdrücklich festgestellt, dass `ProvowareDbTui` ein fertiges `TuiDataPort` konsumiert, selbst aber weder Datenbankverbindungen noch Health-Quellen erzeugt oder besitzt. Eine eindeutige produktive Health-Provider-/Connection-Ownership war dort nicht belegt. Seitdem wurde keine solche TUI-Ownership eingeführt.

## Entscheidung

Die technische Factory-Seam ist vorhanden, aber die für einen produktiven TUI-Provider notwendige Ownership ist weiterhin nicht eindeutig autorisiert.

**`NO_PROVIDER_WIRING_AUTHORIZED`**

I77 implementiert deshalb keinen `HealthReadPort`-Provider und übernimmt den Web-Lifecycle nicht stillschweigend in die TUI.

## Freeze-Schutz

Unverändert bleiben CP-03, CP-08, Schema/Migrationen, Storage-Implementierung, Repositories, Application-Core, TUI-Runtime, Events, Writer-Lifecycle und alle eingefrorenen CP-09-Slices. `open_connection()` und der Web-Startup werden nur gelesen.

## Prüfungen

- `open_connection(..., read_only=True)` als technische Factory-Seam bestätigt.
- Web-spezifische Connection-Ownership und Close-Reihenfolge bestätigt.
- I71-TUI-Consumer-Grenze gegen den aktuellen `main` erneut geprüft.
- Keine produktive TUI-Connection-/Provider-Ownership gefunden.
- Manifest-V2- und Write-Scope-Gates sind für genau diesen scope-only Schritt vorgesehen.

## Verbleibendes Risiko

Die Health-Semantik ist autorisiert, aber ohne explizite TUI-Connection-Ownership könnte ein Provider eine zweite Connection, unklare Lebensdauer oder konkurrierende Close-Verantwortung einführen.

## Nächster sicherer Schritt

Nach grünem I77-Gate separat entscheiden, ob ein minimaler read-only TUI-Connection-Ownership-Vertrag autorisiert werden darf. Erst danach darf ein Provider implementiert werden. Events, Writer-Lifecycle, Starter und Freeze-Reopens bleiben davon getrennt.
