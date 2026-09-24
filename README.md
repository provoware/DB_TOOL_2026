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

### Neuester bestätigter Produktstand

**Iteration 103** ist der neueste bestätigte Produkt-Slice auf `main`.

Der Browser-Maskeneditor besitzt inzwischen:
- eine Komponentenpalette,
- eine feste 12-Spalten-Arbeitsfläche,
- einen deterministischen Vorschau-Bereich,
- temporäre Platzierung mit monotonen Draft-IDs,
- temporäres Entfernen,
- keyboard-first Verschieben bei stabiler Draft-ID,
- Blockierung ungültiger Rasterziele,
- Escape-/Fokus-Rückgabe beim Verschieben,
- reale Chromium-Nachweise bis 200-%-Zoom-Äquivalent ohne horizontalen Overflow.

Wichtig: Der Browser-Draft bleibt absichtlich **ohne Persistenz und ohne produktiven Datenbankzugriff**. Ein Reload verwirft den Entwurf. Damit bleibt die spätere Save-Grenze separat plan- und prüfbar.

### Repository-Hygiene

**Iteration 98** dokumentiert den damaligen Hygiene-Freeze als historischen Nachweis. Aussagen dort über Branches oder offene Pull Requests beziehen sich auf diesen damaligen Zeitpunkt und sind kein dauerhafter Statusvertrag.

Neue Entwicklungsiterationen starten weiterhin vom bestätigten `main` und verwenden klar begrenzte Branches/PRs.

## Produkt-Roadmap

Der freigegebene langfristige Ausbaupool ist jetzt getrennt vom aktuellen Produktstand dokumentiert:

- **`docs/PRODUCT_ROADMAP.md`** – Abhängigkeiten, Risikoklassen und empfohlene Reihenfolge
- **`TODO.md`** – abhakbarer Implementierungspool

Dort enthalten sind unter anderem Masken-Eigenschaften, Layout/Struktur, Suche und Filter, Regeln/Validierung, Assistentenmodus, Vorlagen, Undo/Recovery, Import/Export, Anhänge, Dashboard, Accessibility, Gesundheitsbereich und Beziehungen.

Wichtig: Ein Roadmap-Punkt ist **keine automatische Implementierungsfreigabe**. Jede Capability wird weiterhin als kleine, gatebare Iteration umgesetzt.

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

Nach I98 gilt zusätzlich: historische Arbeitsbranches werden nicht als Abkürzung für neue Entwicklung wiederverwendet. Neue Iterationen starten vom aktuellen `main`.

## Lizenz

Noch nicht festgelegt.
