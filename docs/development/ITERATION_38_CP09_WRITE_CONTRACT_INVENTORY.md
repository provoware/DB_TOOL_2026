# Iteration 38 – CP-09 Write-Contract-Inventur

## Zweck

I38 ist ausschließlich eine read-only Vertragsinventur. Kein Produktcode und kein eingefrorener Bereich wird verändert.

## Befund

`CatalogService` besitzt bereits öffentliche Schreibverträge. `create_category()` ist der kleinste eigenständige Write-Use-Case: Er erzeugt genau eine Kategorie, prüft Namenskonflikte, schreibt den Audit-Eintrag und delegiert die koordinierte Ausführung an den bereits vorhandenen `CoordinatedWriter`.

Der vorhandene Vertrag enthält bereits:

- Domain-Erzeugung über `Category.new(...)`,
- Konfliktprüfung vor dem Insert,
- Repository-Insert über den bestehenden `CategoryRepository`,
- Audit-Ereignis `category.create`,
- transaktionale Postcondition: Kategorie ist aktiv vorhanden,
- transaktionale Postcondition: Audit-Ereignis zur Operation existiert,
- dieselben Postconditions nach Commit,
- Ausführung über `CoordinatedWriter.execute(...)` statt direktem UI-/SQL-Schreibzugriff.

Damit ist für diesen Use-Case **kein REOPEN von CP-03, CP-06 oder SQLite-Frozen-Core begründet**. Die vorhandenen Verträge reichen für eine spätere, separat freizugebende Funktionsiteration aus.

## Gewählter erster CP-09-Use-Case

**Kategorie anlegen über den bestehenden öffentlichen `CatalogService.create_category()`-Vertrag.**

Begründung: Der Use-Case ist kleiner und unabhängiger als Entry-/Field-Erzeugung, Papierkorb/Restore, Undo oder Feldwerte. Er benötigt keine vorhandene Parent-ID, keine neue Tabelle, keine Migration und keine Änderung an Repository-, Audit-, Journal- oder Unit-of-Work-Code.

## Spätere Funktionsgrenze

Eine folgende Implementierungsiteration darf ausschließlich eine dünne Application-/UI-Anbindung an `CatalogService.create_category()` ergänzen. Sie darf den vorhandenen Write-Vertrag nicht umbauen.

Erforderliche direkte Regressionen der Folgeiteration:

1. gültiger Kategoriename erzeugt genau eine aktive Kategorie;
2. doppelter aktiver Name schlägt über den vorhandenen Konfliktvertrag fehl;
3. erfolgreicher Write besitzt Audit-/Operation-Evidence über den bestehenden Writer;
4. ein Fehler darf keinen halbfertigen Kategoriezustand hinterlassen;
5. bestehende read-only Navigation und CP-08-Flächen bleiben unverändert.

## Freeze-Grenzen / Non-Goals

Geschlossen bleiben:

- CP-03 / Schema V1 / Migrationen,
- CP-06 Domain-/Repository-Kern,
- `storage/sqlite/**` einschließlich Repositories, Audit, Operation Journal, Unit of Work und Coordinator,
- bestehende Implementierung von `CatalogService.create_category()`,
- CP-07H,
- CP-07T-Navigationssemantik,
- CP-08 Health-/Event-Surface,
- Entry-/Field-/Value-Writes,
- Papierkorb/Restore,
- Undo,
- Autosave,
- Crash-Recovery,
- Polling/Hintergrundjobs,
- Themes/Layout.

## Exit-Gates I38

1. Nur dieses Inventurdokument und das I38-Manifest werden hinzugefügt.
2. Kein Produktcode wird geändert.
3. Kein Frozen-Core-Pfad wird geändert.
4. Targeted Iteration prüft ausschließlich Manifest/Scope.
5. Repository Foundation und Agent Governance bleiben grün.
6. Kein Screenshot, weil keine visuelle Änderung vorliegt.
7. Erst nach grünem Freeze von I38 darf eine Folgeiteration die minimale Kategorie-Anlegen-Anbindung planen/implementieren.

## Verbleibendes Risiko

Die Inventur bestätigt den vorhandenen Application-Vertrag, aber noch nicht die konkrete Oberfläche oder den Eingabefluss. Diese dürfen nicht vorweggenommen werden. Falls die spätere Anbindung eine Änderung des vorhandenen `CatalogService`- oder SQLite-Vertrags verlangen würde, muss sie stoppen und einen expliziten REOPEN begründen.
