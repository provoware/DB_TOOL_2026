# Mitwirken am PROVOWARE DB TOOL 2026

Diese Datei beschreibt den normalen Änderungsweg in kurzer Form.

## Kurzregel

**Erst Ziel festlegen, dann klein ändern, passend prüfen und erst danach mergen.**

Stabilen Code nicht nebenbei anfassen.

## Vor einer Änderung

Vor dem ersten Schreibzugriff muss klar sein:

- **Ziel:** Was soll genau besser oder anders werden?
- **Dateien:** Welche Dateien müssen wirklich geändert werden?
- **Risiko:** Was könnte dadurch kaputtgehen?
- **Nicht betroffen:** Welche geschützten Bereiche bleiben ausdrücklich unverändert?
- **Prüfungen:** Welche Tests oder Gates passen genau zu dieser Änderung?

Wenn diese Punkte nicht klar sind, wird noch nicht geändert.

## Nach einer Änderung

Es werden nur die Prüfungen ausgeführt, die zum geänderten Pfad passen:

1. Syntax oder Struktur prüfen, falls relevant.
2. Direkt betroffene Tests ausführen.
3. Engste sinnvolle Regression prüfen.
4. Gate auswerten.
5. Ergebnis und Restrisiko kurz dokumentieren.

Ein kompletter Volltest ist **nicht automatisch nötig**.

## Geschützte Bereiche

Diese Bereiche sind eingefroren:

- **CP-03:** Datenbankschema
- **CP-06:** Domain-/Repository-Kern

Änderungen dort benötigen eine eigene begründete Iteration, Impact-Analyse und passende Regressionstests.

## Pull Requests

Ein Pull Request soll:

- klein und thematisch geschlossen sein,
- keine unnötigen Nebenänderungen enthalten,
- keine globale Umformatierung mit Funktionsänderungen mischen,
- bei fehlgeschlagenem Gate zuerst nur die konkrete Ursache beheben.

## Branches

Arbeitsbranches werden erst entfernt, wenn sicher nachgewiesen ist, dass keine benötigten Änderungen verloren gehen. Alte oder divergierte Branches werden deshalb nicht pauschal gelöscht.

## Wo stehen die ausführlichen Regeln?

- `AGENTS.md` – verbindliche Entwicklungs- und Agentenregeln
- `docs/PROJECT_STANDARDS.md` – Prüf- und Qualitätsstandard
- `docs/LAIEN_START.md` – Projektstand ohne Entwicklerwissen
