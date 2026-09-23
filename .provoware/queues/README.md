# Agent-Queues – kurz erklärt

Dieser Ordner ist ein interner Übergabebereich zwischen spezialisierten Entwicklungsagenten.

Normale Nutzer müssen hier nichts ändern.

## Ordner

- `review/` – neue Prüfhinweise oder Review-Aufträge
- `planning/` – bereits analysierte Punkte für die nächste Planung
- `blocked/` – Arbeit, die aktuell nicht sicher fortgesetzt werden kann
- `done/` – abgeschlossene Queue-Einträge

## Grundprinzip

Eine Datei in einer Queue bedeutet: **Dieser Punkt ist noch Teil des Arbeitsablaufs.**

Nach erfolgreicher Bearbeitung wird der Eintrag nicht einfach vergessen, sondern nachvollziehbar nach `done/` überführt.

## Mindestangaben einer Queue-Datei

Eine YAML- oder JSON-Datei enthält mindestens:

- `iteration` – zu welcher Iteration der Punkt gehört
- `source_agent` – welcher Agent ihn erzeugt hat
- `created_at` – Erstellungszeit
- `affected_files` – betroffene Dateien
- `reason` – warum der Punkt existiert
- `required_action` – was als Nächstes notwendig ist
- `status` – aktueller Bearbeitungsstand

## Sicherheitsregel

Queue-Dateien steuern Planung und Prüfung. Sie dürfen keinen Frozen-Core-Schutz umgehen und sind kein Ersatz für Gate oder Regressionstest.
