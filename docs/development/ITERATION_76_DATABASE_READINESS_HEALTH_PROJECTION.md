# Iteration 76 – Database-Readiness Health Projection

## Änderung

I76 trifft ausschließlich die in I75 bewusst vertagte Produktentscheidung für die minimale binäre Projektion des bereits autorisierten I74-Database-Readiness-Vertrags. Es wird noch kein Provider und kein Produktcode implementiert.

## Autorisierte Projektion

Für genau den I74-Vertrag gilt künftig:

- **Database Ready** – `SELECT 1` funktioniert und `assert_schema_identity(con, DatabaseKind.MAIN)` besteht – wird als `HealthLevel.OK` projiziert.
- **Database Not Ready** – mindestens eine dieser beiden Voraussetzungen scheitert – wird als `HealthLevel.ERROR` projiziert.

`HealthLevel.WARNING` wird durch diesen binären Vertrag **nicht** erzeugt.

## Begründung

I74 hat die technische Aussage bereits absichtlich binär begrenzt: readable/compatible versus not readable/not compatible. I75 hat korrekt verhindert, dass ein späterer Provider daraus stillschweigend eine Statusregel ableitet. I76 autorisiert diese eine Abbildung nun ausdrücklich und hält sie ebenso binär.

Damit wird keine neue Datenbankprüfung eingeführt. Insbesondere werden `pre_write_gate()`, freier Speicher, Verzeichnis-Schreibbarkeit, `query_only`, Foreign-Key-Konfiguration sowie `fast_validate()`/`deep_validate()` nicht Teil der Health-Projektion.

## WARNING-Grenze

`WARNING` bleibt reserviert für eine spätere, separat begründete degradierte Semantik. Ein Provider darf aus Ausnahmen, Schreibbereitschaft oder zusätzlichen Validierungsfakten nicht eigenmächtig WARNING ableiten.

## Freeze-Schutz

Geschlossen bleiben CP-03, CP-08, Schema/Migrationen, Storage/SQLite/Repositories, `schema_guard.py`, `validation/gates.py`, TUI-View-Models und Runtime, Events, Writer-Lifecycle, Composition Root und Starter.

Die vorhandenen Enum-Werte werden nicht verändert. I76 autorisiert nur ihre Verwendung für diesen einen bereits festgelegten Readiness-Vertrag.

## Prüfstrategie

I76 ist scope-only. Das passende Gate ist Manifest-V2 plus strikte `write_files`-Validierung. Produkt-, Datenbank-, TUI- und Volltests werden nicht ausgelöst, weil kein ausführbarer Produktpfad verändert wurde.

## Ergebnis

**DATABASE_READINESS_HEALTH_PROJECTION_AUTHORIZED**

Der semantische Blocker aus I75 ist für den minimalen binären Database-Readiness-Fall aufgelöst. Ein späterer dünner `HealthReadPort`-Provider kann nun diese Abbildung implementieren, ohne selbst Produktsemantik erfinden zu müssen.

## Verbleibendes Risiko

Die Projektion kennt bewusst keinen degradierten Zustand. Außerdem ist noch nicht entschieden, wer die bestehende Connection für einen produktiven Health-Provider besitzt. Beides darf nicht als Nebenänderung in I76 gelöst werden.

## Nächster Schritt

Nach grünem I76-Gate separat den kleinsten produktiven read-only `HealthReadPort`-Provider entwerfen: ausschließlich I74-Readiness auswerten und genau auf `OK`/`ERROR` projizieren. Connection-Ownership, Events, Writer-Lifecycle, Starter sowie CP-03/CP-08 bleiben dabei geschlossen, sofern der Provider nicht ohne neue Lifecycle-Entscheidung implementierbar ist.
