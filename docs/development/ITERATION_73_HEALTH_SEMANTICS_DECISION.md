# Iteration 73 – Health-Semantik Decision Scope

## Änderung

I73 prüft ausschließlich read-only, welche bereits vorhandenen Signale eine spätere minimale Health-Semantik tragen könnten. Es wird kein Provider und keine neue Statusregel implementiert.

## Autorisierte Ausgangslage

`README.md` fordert eine nachvollziehbare GRÜN/GELB/ROT-Selbstvalidierung. Der eingefrorene CP-08-Vertrag autorisiert dagegen nur die Darstellung bereits vorhandener `HealthItem`-Daten. I72 hat deshalb korrekt festgestellt: Consumer-Seam vorhanden, produktive Health-Quelle nicht autorisiert.

`HealthLevel` stellt bereits `OK`, `WARNING` und `ERROR` bereit. Diese drei Werte sind Darstellungszustände; aus ihnen folgt noch nicht, welche technische Beobachtung welchen Zustand erzeugt.

## Vorhandene beobachtbare Kandidaten

In `validation/gates.py` existieren bereits technische Prüfprimitiven für sichere Schreibvorgänge. Darin sind Fakten erkennbar, die grundsätzlich beobachtbar sind:

- Schema-Identität bzw. erwartete Schema-Version;
- offene Transaktion;
- Foreign-Key-Prüfung aktiv/inaktiv;
- Query-only-Modus;
- Beschreibbarkeit des Datenbankordners;
- freier Speicher gegen eine vorhandene Mindestgrenze;
- einfache Datenbank-Erreichbarkeit via `SELECT 1`.

Diese Signale werden in I73 **nicht ausgeführt, kopiert oder als Health-Regeln übernommen**.

## Entscheidender Befund

`pre_write_gate()` beantwortet die Frage „ist ein sicherer Schreibvorgang jetzt zulässig?“. Das ist nicht identisch mit „ist die Anwendung gesund?“.

Insbesondere sind `query_only=1` oder ein nicht beschreibbarer Ordner für einen bewusst read-only gestarteten Modus nicht automatisch ein Fehler. Würde Health direkt auf `pre_write_gate()` aufbauen, würde die Statusanzeige Schreibbereitschaft mit allgemeiner Systemgesundheit vermischen.

Auch die vorhandene Mindestgrenze für freien Speicher ist als Write-Sicherheitsgrenze definiert. Ohne expliziten Produktvertrag darf daraus kein WARNING-/ERROR-Schwellwert für die allgemeine Health-Anzeige abgeleitet werden.

## Zwischen-Gate-Entscheidung

Es gibt **vorhandene technische Kandidatensignale**, aber noch **keine autorisierte Zuordnung zu `HealthLevel`**.

Daher endet I73 bewusst ohne Produktimplementierung. Es wird weder `pre_write_gate()` wiederverwendet noch eine parallele Health-Prüflogik angelegt.

## Freeze-Schutz

Geschlossen bleiben CP-03, Schema/Migrationen, CP-08-Semantik, Storage/SQLite/Repositories, `validation/gates.py`, TUI-Runtime, Events, Writer-Lifecycle, Composition Root und Starter.

## Prüfstrategie

Da ausschließlich Scope-/Entscheidungsdokumentation geändert wird, ist das passende Gate Manifest-V2 plus strikte `write_files`-Validierung. Produkt-, Datenbank-, TUI- und Volltests werden nicht ausgelöst.

## Ergebnis

Die nächste Health-Entscheidung kann jetzt präzise erfolgen: Sie darf nicht „alle vorhandenen Write-Gates als Health anzeigen“, sondern muss genau **einen minimalen read-only Readiness-Vertrag** autorisieren und dessen Bedeutung von Schreibbereitschaft trennen.

Als kleinster Kandidat bietet sich Datenbank-Erreichbarkeit/Schema-Kompatibilität an, weil beides für sinnvolles Lesen erforderlich ist. Eine konkrete `OK/WARNING/ERROR`-Abbildung bleibt jedoch bis zu diesem separaten Vertrag ausdrücklich unautorisiert.

## Nächster Schritt

Nach grünem I73-Gate separat den minimalen **read-only Database-Readiness-Vertrag** entscheiden: welche bereits vorhandene, nicht mutierende Beobachtung zulässig ist und wie ausschließlich deren Ergebnis in Health übersetzt werden darf. Noch kein Provider, kein Starter und kein CP-03-/CP-08-Reopen.