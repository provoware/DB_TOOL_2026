# Iteration 75 – Health-Readiness Projection Decision

## Änderung

I75 prüft ausschließlich, ob der in I74 autorisierte binäre Database-Readiness-Vertrag bereits eindeutig auf den bestehenden `HealthItem`-/`HealthLevel`-Vertrag projiziert werden darf. Es wird kein Provider und kein Produktcode implementiert.

## Ausgangslage

I74 autorisiert genau zwei read-only Voraussetzungen: `SELECT 1` muss auf der bestehenden Verbindung funktionieren und `assert_schema_identity(con, DatabaseKind.MAIN)` muss erfolgreich sein. Das Ergebnis ist ausschließlich **readable/compatible** versus **not readable/not compatible**.

Der bestehende TUI-Vertrag stellt `HealthLevel.OK`, `HealthLevel.WARNING` und `HealthLevel.ERROR` sowie `HealthItem(label, level, detail)` bereit. Diese Typen definieren Darstellungswerte, aber keine Erzeugungsregel für technische Readiness-Signale.

CP-08 autorisiert nur die Darstellung bereits vorhandener `HealthItem`-Daten. Neue Datenquellen oder eine neue fachliche Statussemantik wurden dort ausdrücklich nicht freigegeben.

## Entscheidender Befund

Aus I74 folgt nicht eindeutig, dass `readable/compatible` zwingend `HealthLevel.OK` und `not readable/not compatible` zwingend `HealthLevel.ERROR` bedeuten muss. Insbesondere ist `WARNING` für den binären Readiness-Vertrag nicht definiert.

Eine solche Abbildung wäre zwar technisch naheliegend, wäre aber eine neue fachliche Health-Regel. Sie kann nicht allein aus den Enum-Namen abgeleitet werden, ohne die in I73/I74 bewusst gesetzte Semantikgrenze zu überschreiten.

## Entscheidung

**NO_HEALTH_READINESS_PROJECTION_AUTHORIZED**

I75 implementiert deshalb keinen Provider und keine Mapping-Funktion. Der bestehende `HealthLevel`-/`HealthItem`-Vertrag bleibt unverändert.

Damit wird zugleich verhindert, dass ein späterer Composition Root implizit Produktsemantik erzeugt, nur um `HealthReadPort` technisch befüllen zu können.

## Freeze-Schutz

Geschlossen bleiben CP-03, CP-08, Schema/Migrationen, Storage/SQLite/Repositories, `schema_guard.py`, `validation/gates.py`, TUI-View-Models und Runtime, Events, Writer-Lifecycle, Composition Root und Starter.

## Prüfstrategie

I75 ist scope-only. Passend sind Manifest-V2 und strikte `write_files`-Validierung. Produkt-, Datenbank-, TUI- und Volltests werden nicht ausgelöst, weil kein Produktcode geändert wird.

## Ergebnis

Der technische Readiness-Vertrag ist vorhanden, aber seine Health-Projektion ist weiterhin nicht fachlich autorisiert. Ein dünner produktiver `HealthReadPort`-Provider wäre deshalb aktuell nicht semantikneutral implementierbar.

## Verbleibendes Risiko

Ohne explizite Produktentscheidung bleibt die TUI-Health-Quelle produktiv ungebunden. Das ist sicherer als eine implizite Statusregel, blockiert aber weiterhin den vollständigen TUI-Composition-Root.

## Nächster Schritt

Nach grünem I75-Gate separat entscheiden, ob für **Database Readiness** genau eine minimale Health-Projektion ausdrücklich autorisiert werden soll. Erst eine solche explizite Entscheidung darf `OK`/`ERROR` zuordnen. `WARNING`, Events, Writer-Lifecycle, Starter sowie CP-03/CP-08 bleiben bis dahin geschlossen.
