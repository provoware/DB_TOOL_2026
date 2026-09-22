# Iteration 72 – Health-Provider-Grenze

## Änderung

I72 isoliert nach I71 ausschließlich die kleinste noch offene Health-Grenze. Es wird weder ein Provider noch ein Starter implementiert.

## Schritt 1 – Vertragsprüfung

Der eingefrorene CP-08-Scope autorisiert ausschließlich die read-only Darstellung bereits vorhandener `HealthItem`-Daten aus `TuiDataPort.health()`. Er schließt ausdrücklich neue Datenquellen, SQL, Repository-Änderungen und neue Service-/Repository-Adapter aus.

Der aktuelle `TuiCatalogReadAdapter` hält diese Grenze ein: `HealthReadPort` definiert nur `health()`, und die konkrete Quelle wird per Konstruktor injiziert. Der Adapter erzeugt und besitzt diese Quelle nicht.

`CatalogService` ist die fachliche Quelle für Kategorie → Entry → Feld/Wert. Ihn zusätzlich zum Health-Owner zu machen wäre eine neue Verantwortlichkeit und ist weder durch CP-08 noch durch I71 begründet.

Damit ist der verbleibende Blocker präziser als zuvor: Nicht die Consumer-Seam fehlt, sondern eine fachlich autorisierte produktive Quelle für die Health-Semantik.

## Zwischen-Gate-Entscheidung

Eine konkrete produktive Health-Quelle lässt sich aus dem bestehenden freigegebenen Vertrag nicht eindeutig ableiten.

**Schritt 2 = NO_HEALTH_PROVIDER_CONTRACT_REQUIRED.**

Ein dünner Provider wäre technisch leicht zu schreiben, würde aber seine Statusregeln und Ownership erfinden. Genau das wird nicht getan.

## Freeze-Schutz

Unverändert bleiben insbesondere:

- CP-03 und Schema/Migrationen;
- CP-08-Semantik und dessen eingefrorene Runtime-Darstellung;
- Storage und SQLite-Repositories;
- Domain/Application-Core und `CatalogService`;
- TUI-Runtime und `TuiCatalogReadAdapter`;
- Event-Quelle und Writer-/Connection-Lifecycle;
- Composition Root und Starter.

## Prüfstrategie

I72 ist scope-only. Das passende Gate ist deshalb ausschließlich Manifest-V2-/Write-Scope-Validierung. Produkt-, Datenbank-, TUI- und Volltests würden keinen geänderten Produktpfad prüfen und werden bewusst nicht ausgelöst.

## Ergebnis

Die Health-Grenze ist jetzt eindeutig klassifiziert: Consumer-Vertrag vorhanden, produktive Quelle nicht autorisiert. Der nächste Schritt darf deshalb nicht `HealthReadPort` implementieren, sondern muss zuerst die kleinste fachliche Health-Semantik als separaten Decision Scope bestimmen, ohne dafür eingefrorene Persistenz zu öffnen.

## Nächster Schritt

Nach grünem I72-Gate separat entscheiden, welche bereits vorhandenen, read-only beobachtbaren Signale überhaupt den minimalen Health-Status bilden dürfen. Erst eine explizite Freigabe dieser Semantik kann einen produktiven Provider autorisieren. Events, Writer-Lifecycle, Starter und CP-03 bleiben dabei geschlossen.
