# PROVOWARE DB TOOL 2026

PROVOWARE DB TOOL 2026 ist ein lokales Datenbankprojekt mit dem Ziel, auch für Menschen ohne Datenbankwissen verständlich und sicher bedienbar zu sein.

> **Aktueller Stand:** Entwicklungsprojekt. Die vorhandenen Oberflächen und Funktionen werden schrittweise freigegeben. Nicht jede geplante Komfortfunktion ist bereits fertig.

## Was ist bereits vorhanden?

- lokaler SQLite-Kern
- Kategorien, Einträge und frei definierbare Felder als fachliche Grundlage
- Nur-Lese-Oberflächen für bereits freigegebene Datenpfade
- Browser-Grundlagen und Masken-Baukasten
- Prüfungen für Freeze-Schutz, Regressionen und UI-Grenzen
- dokumentierte GRÜN/GELB/ROT-Gates

### Neuester bestätigter Stand

**Iteration 92** ist auf `main` gemergt.

Der neue Browser-Maskeneditor zeigt bereits:
- eine Komponentenpalette,
- eine feste 12-Spalten-Arbeitsfläche,
- einen Vorschau-Bereich.

Wichtig: Dieser Schritt ist absichtlich noch **ohne Speichern und ohne Datenbankzugriff**. Dadurch bleibt der bestehende Datenbankkern geschützt.

## Für Einsteiger

Die kurze Erklärung ohne Entwicklerbegriffe steht in:

**`docs/LAIEN_START.md`**

Dort steht:
- was das Projekt heute kann,
- was noch nicht freigegeben ist,
- was GRÜN/GELB/ROT bedeutet,
- welche Dateien normale Nutzer ignorieren können.

## Schutz der Datenbank

Bestimmte Bereiche sind eingefroren und dürfen nicht nebenbei verändert werden:

- **CP-03:** Datenbankschema
- **CP-06:** Domain-/Repository-Kern

Eine Änderung an diesen Bereichen braucht eine eigene Begründung, passende Regressionstests und ein separates Gate.

## Technische Grundregel

```text
Oberfläche
↓
Application Service
↓
Domain / Repository
↓
SQLite
```

Eine Oberfläche darf nicht direkt SQL ausführen.

## Für Entwickler

- Entwicklungsregeln: `AGENTS.md`
- Mitwirken: `CONTRIBUTING.md`
- Prüf- und Qualitätsstandard: `docs/PROJECT_STANDARDS.md`
- historische Iterationsnachweise: `docs/development/`

Die Dateien unter `docs/development/` sind bewusst technische Verlaufs- und Nachweisdokumente. Sie werden nicht nachträglich vereinfacht, weil sie den tatsächlichen Entwicklungsstand einer Iteration dokumentieren.

## Repository-Regel

`main` ist die stabile Basis. Änderungen erfolgen über kleine, klar begrenzte Branches und Pull Requests. Keine kosmetischen Massenänderungen zusammen mit Produktänderungen.

## Lizenz

Noch nicht festgelegt.
