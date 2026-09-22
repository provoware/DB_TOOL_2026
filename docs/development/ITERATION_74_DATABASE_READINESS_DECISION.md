# Iteration 74 – Database-Readiness Decision Scope

## Änderung

I74 legt ausschließlich den kleinsten read-only Database-Readiness-Vertrag fest. Es wird kein Provider implementiert und keine neue Health-Semantik eingeführt.

## Autorisierte Ausgangslage

I73 hat gezeigt, dass `pre_write_gate()` Schreibbereitschaft prüft und deshalb nicht als allgemeine Health-Quelle verwendet werden darf. Gleichzeitig existiert mit `assert_schema_identity()` bereits eine nicht mutierende Prüfung der Datenbankidentität und Schema-Kompatibilität.

## Minimaler Readiness-Vertrag

Für eine sinnvoll lesbare Hauptdatenbank gelten genau zwei Voraussetzungen als minimal autorisiert:

1. Die bestehende Verbindung muss eine einfache read-only Abfrage ausführen können (`SELECT 1`).
2. `assert_schema_identity(con, DatabaseKind.MAIN)` muss erfolgreich sein.

Die zweite Prüfung umfasst bereits erwartete Schema-Version, `application_id`, erwartete Tabellen und den vorhandenen Schema-Fingerprint. Damit wird keine parallele Schema-Logik definiert.

## Bewusst nicht Bestandteil

Nicht Teil dieses Readiness-Vertrags sind offene Transaktion, `foreign_keys`, `query_only`, Beschreibbarkeit des Datenbankordners oder freier Speicher. Diese Bedingungen gehören ganz oder teilweise zur Schreibsicherheit und dürfen nicht in die allgemeine Lesebereitschaft hineinrutschen.

Auch `fast_validate()` und `deep_validate()` werden nicht zum Minimalvertrag erhoben. Sie enthalten zusätzliche Integritätsprüfungen und sind für den kleinsten Start-/Readiness-Nachweis breiter als erforderlich.

## Semantische Grenze

I74 autorisiert nur die Aussage **readable/compatible** versus **not readable/not compatible**. Daraus folgt ausdrücklich noch keine neue Zuordnung zu `HealthLevel.OK`, `WARNING` oder `ERROR`.

Insbesondere wird kein WARNING-Zustand erfunden. Eine spätere Health-Projektion muss diese Grenze separat und explizit entscheiden.

## Freeze-Schutz

Geschlossen bleiben CP-03, CP-08, Schema/Migrationen, Storage/SQLite/Repositories, `schema_guard.py`, `validation/gates.py`, TUI-Runtime, Events, Writer-Lifecycle, Composition Root und Starter.

## Prüfstrategie

Da I74 ausschließlich eine bestehende read-only Grenze dokumentiert, ist Manifest-V2 plus strikte `write_files`-Validierung das passende Gate. Produkt-, Datenbank- und Volltests werden nicht ausgelöst.

## Ergebnis

Der kleinste Database-Readiness-Vertrag ist jetzt eindeutig: bestehende Verbindung reagiert auf eine harmlose Leseabfrage und besteht die bereits vorhandene Schema-Identitätsprüfung. Schreibfähigkeit und umfassende Integrität bleiben davon getrennt.

## Verbleibendes Risiko

`assert_schema_identity()` beweist Schema-Kompatibilität, aber keine vollständige Datenintegrität. Das ist für diesen minimalen Readiness-Scope beabsichtigt; eine Ausweitung auf `quick_check` oder `integrity_check` benötigt einen eigenen begründeten Vertrag.

## Nächster Schritt

Nach grünem I74-Gate separat prüfen, ob aus genau diesem Vertrag ein dünner produktiver read-only Readiness-Provider abgeleitet werden kann. Noch keine HealthLevel-Abbildung, keine Events, kein Writer-Lifecycle, kein Starter und kein CP-03-/CP-08-Reopen.
