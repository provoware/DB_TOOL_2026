# I162 – Inventur „zuletzt verwendet“

## Ziel

Prüfen, ob der offene Punkt **C · Datenarbeit → zuletzt verwendet** ohne neue Persistenz oder semantische Verfälschung sicher umgesetzt werden kann.

## Ergebnis

Der Punkt ist **noch nicht sauber implementierbar**, ohne einen neuen Nutzungs-/Sitzungszustand einzuführen.

Vorhandene Daten sind dafür nicht geeignet:

- `entries.updated_at` bedeutet **zuletzt geändert**, nicht zuletzt geöffnet/verwendet.
- `created_at` bedeutet Erstellung.
- Audit-Events protokollieren produktive Mutationen und Undo/Restore, nicht normale GET-/Lesezugriffe.
- Der aktuelle GET-only Webpfad schreibt absichtlich keine Zugriffshistorie.
- Es existiert kein belastbarer `last_used_at`-, Recent-Session- oder browserlokaler Usage-Store.

Eine Sortierung nach `updated_at` als „zuletzt verwendet“ wäre fachlich falsch.

## Schutzentscheidung

I162 öffnet deshalb **keine** neue Persistenz und schließt den TODO-Punkt nicht.

Insbesondere wird nicht:

- ein GET-Aufruf zum Write gemacht,
- `updated_at` zweckentfremdet,
- ein Audit-Event für reine Navigation erzeugt,
- Browser-LocalStorage stillschweigend als neue Quelle eingeführt,
- ein neues Schemafeld ergänzt.

## Späterer sauberer Vertrag

Eine echte „zuletzt verwendet“-Funktion benötigt zuerst eine bewusste Produktentscheidung für einen separaten Usage-State, zum Beispiel:

1. **browserlokal/sessionlokal** – nicht synchronisiert, keine DB-Mutation;
2. **separate lokale Usage-State-DB** – getrennt von produktiven Fachdaten;
3. **produktive DB-Spalte/Usage-Tabelle** – nur mit explizitem Persistenz-, Recovery- und Datenschutzvertrag.

Erst danach darf „zuletzt verwendet“ umgesetzt und abgenommen werden.

## Nächster unabhängiger Read-only-Kandidat

**Mehrfachauswahl** ist aktuell der bessere nächste Slice:

- browserlokal möglich,
- keine neue Persistenz nötig,
- kein Repository-/Schema-Patch,
- kann zunächst rein temporär/read-only bleiben,
- bildet eine saubere Voraussetzung für die spätere Preview von Massenaktionen.

## Status

- „zuletzt verwendet“: bewusst **offen/blockiert durch fehlenden Usage-State-Vertrag**
- Persistenz: geschlossen
- CP-03 / CP-06: unverändert
- empfohlener nächster Slice: browserlokale Mehrfachauswahl
