# Iteration 37 – Post-CP08 Checkpoint-Auflösung

## Zweck

Iteration 37 ist ausschließlich eine Planungs- und Architekturgrenzen-Iteration nach dem eingefrorenen CP-08. Es wird kein Produktcode verändert.

## Ausgangslage

`main` steht nach I36 auf `b78c704dd1d1ac0a7b5f2eeb6eef7ad73a4f0ed7`. CP-08 ist geschlossen. Das Zielbild nennt weiterhin Suche, Papierkorb/Restore, Undo, Audit, Crash-Recovery und ein Autosave-/Statuskonzept.

Im bestehenden Kern liegen bereits SQLite-Bausteine für Audit, Operation Journal und Unit of Work. Ihre Existenz ist jedoch keine Freigabe, diese Frozen-Bereiche zu verändern oder direkt aus einer Oberfläche anzusprechen.

## Auflösung

Der nächste sichere Checkpoint ist **CP-09 Write-Safety Foundation – zunächst nur als Scope**.

Begründung: Die verbleibenden Zielbild-Funktionen Papierkorb/Restore, Undo, Autosave und Crash-Recovery erzeugen oder verändern Zustand. Vor einem einzelnen Komfortfeature muss deshalb zuerst verbindlich feststehen, über welche bereits vorhandenen Application-/Repository-Verträge Schreiboperationen laufen dürfen, welche atomaren Grenzen gelten und wie Fehler ohne Datenverlust zurückrollen. Dadurch wird vermieden, dass eine UI-Funktion nebenbei CP-03, CP-06 oder SQLite-Frozen-Core öffnet.

I37 autorisiert **noch keinen CP-09-Produktpatch**. Sie bestimmt nur die Reihenfolge und die Sicherheitsgrenze.

## CP-09 Planungsgrenze

Eine spätere CP-09-Funktionsiteration darf erst starten, wenn ein separater Scope mindestens festlegt:

- genau einen kleinsten Write-Use-Case,
- ausschließlich vorhandene öffentliche Application-/Repository-Verträge oder einen expliziten REOPEN,
- Transaktions-/Rollback-Verhalten,
- Audit-/Journal-Erwartung ohne Schemaänderung,
- isolierte Testdaten und keine produktive Datenmanipulation,
- Fehler- und Abbruchverhalten,
- direkt betroffene Regressionstests,
- eindeutige Undo-/Restore-Grenze, falls der gewählte Use-Case sie berührt.

## Freeze-Grenzen

Unverändert geschlossen bleiben:

- CP-03 / Schema V1 / Migrationen,
- CP-06 / Domain-/Repository-Kern,
- SQLite-Repositories,
- `storage/sqlite/audit.py`, `operation_journal.py` und `unit_of_work.py`,
- CP-07H Browserpfad,
- CP-07T Navigationssemantik,
- CP-08 Health-/Event-Surface.

Jede Änderung an diesen Bereichen benötigt einen expliziten REOPEN mit Begründung, Impact-Analyse und direkt betroffener Regression.

## Non-Goals

I37 implementiert ausdrücklich nicht:

- CRUD oder sonstige Schreiboperationen,
- Autosave,
- Papierkorb oder Restore,
- Undo,
- Audit-Persistenzänderungen,
- Crash-Recovery,
- Polling/Hintergrundjobs,
- neue Datenbanktabellen oder Migrationen,
- neue UI-Navigation,
- Theme-/Layout-Änderungen,
- Dependency- oder CI-Änderungen.

## Exit-Gates

1. Ausschließlich I37-Manifest und dieses Scope-Dokument sind geändert.
2. Kein Produktcode ist geändert.
3. CP-03, CP-06, CP-07H, CP-07T und CP-08 bleiben unverändert.
4. SQLite-/Audit-/Journal-/Unit-of-Work-Dateien bleiben unverändert.
5. Repository Foundation ist grün.
6. Agent Governance ist grün.
7. Targeted Iteration validiert ausschließlich Manifest und Scope; kein Full-Suite- oder UI-Test ohne Produktänderung.
8. Kein Screenshot, da keine visuelle Änderung vorliegt.
9. Erst nach grünem Freeze von I37 darf eine Folgeiteration den **ersten einzelnen CP-09-Write-Use-Case** konkret auswählen und separat freigeben.

## Verbleibendes Risiko

Die konkrete erste Schreiboperation ist absichtlich noch nicht gewählt. Vor deren Auswahl muss der vorhandene `CatalogService` gegen Audit/Journal/Unit-of-Work nur lesend inventarisiert werden. Falls der benötigte Vertrag bereits vorhanden und ausreichend ist, bleibt Frozen Core geschlossen. Falls nicht, ist statt eines stillen Patches ein expliziter REOPEN erforderlich.

## Nächster Schritt nach Freeze

Nach komplett grün eingefrorenem I37 folgt ausschließlich die read-only Vertragsinventur für **einen** kleinsten CP-09-Write-Use-Case. Erst danach darf entschieden werden, ob eine Funktionsiteration ohne Frozen-Core-Änderung möglich ist.
