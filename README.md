# PROVOWARE DB TOOL 2026

Lokale, robuste Datenbankanwendung mit SQLite-Kern und austauschbaren Oberflächen.

## Projektstatus

- CP-03 Schema V1: **frozen**
- CP-06 Domain/Repository: **frozen**
- CP-07 UI Foundation: **in Validierung**
- Oberflächen dürfen **niemals direkt SQL** ausführen.
- Kernänderungen benötigen Impact-Analyse, Regressionstest und Gate.

## Zielbild

Ein laienfreundliches Datenbanktool mit:

- Kategorien → Einträge → frei definierbare Felder
- Text-, Zahlen-, Datums-, Boolean- und Choice-Felder
- Suche, Papierkorb/Restore, Undo, Audit und Crash-Recovery
- Autosave-/Statuskonzept
- große/extra große Darstellung und High-Contrast-Modus
- nachvollziehbare GRÜN/GELB/ROT-Selbstvalidierung

## Technische Grundregel

```text
UI
↓
Application Service
↓
Domain / Repository
↓
SQLite
```

Die UI ist austauschbar. Textual und ein lokales HTML-Frontend können denselben eingefrorenen Service-Kern verwenden.

## Entwicklungsstandard

Jede größere Iteration endet mit:

1. relevantem Testlauf,
2. Selbstvalidierung,
3. Gate-Status,
4. professioneller TXT-Auswertung,
5. Änderungsvolumen,
6. nächster Optimierungsempfehlung.

Details: `docs/PROJECT_STANDARDS.md`.

## Repository-Workflow

Stabile Basis bleibt auf `main`. Änderungen erfolgen über kleine Branches und Pull Requests. Keine kosmetischen Massenänderungen neben funktionalen Patches.

## Lizenz

Noch nicht festgelegt.
