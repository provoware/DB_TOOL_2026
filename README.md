# PROVOWARE DB TOOL 2026

PROVOWARE DB TOOL 2026 ist ein lokales Datenbankprojekt mit dem Ziel, Datenstrukturen auch ohne Datenbankwissen verständlich, sicher und schrittweise bedienbar zu machen.

> **Bestätigter Produktstand:** I113 auf `main`  
> **Sicherheitsstatus:** Browser-Maskenentwurf weiterhin ohne Persistenz und ohne produktiven Datenbankzugriff  
> **Frozen Core:** CP-03 und CP-06 bleiben geschlossen

## Was das Projekt heute kann

### Datenbasis

- lokaler SQLite-Kern
- Kategorien, Einträge und frei definierbare Felder als fachliche Grundlage
- getrennte Application-/Domain-/Repository-Schichten
- freigegebene Nur-Lese-Pfade
- Regressionen für Freeze-Schutz, Scope und Repository-Gesundheit

### Browser-Masken-Baukasten

Bis einschließlich **I113** ist der temporäre Browser-Draft schrittweise ausgebaut:

- Komponentenpalette
- feste 12-Spalten-Arbeitsfläche
- deterministische Draft-IDs
- temporäres Platzieren, Verschieben und Entfernen
- Blockierung ungültiger Rasterziele vor Mutation
- Escape- und Fokus-Rückgabe bei Interaktionen
- temporäre Beschriftungsbearbeitung
- temporärer Hilfetext
- zugängliche Hilfetext-Zuordnung
- Pflichtfeld-Eigenschaft im Draft
- Datentypen `text`, `number`, `date`, `boolean`, `single_choice`, `multi_choice`
- typabhängig validierter skalarer Standardwert
- Standardwert bleibt bei Choice-Typen inaktiv statt still umgeschrieben zu werden
- browserlokale Choice-Optionen
- stabile monotone `draft-option-*`-IDs
- Choice-Optionen hinzufügen, entfernen und deterministisch hoch/runter verschieben
- eindeutige zugängliche Namen für Option-Controls
- Live-Status und deterministische Fokus-Rückgabe
- schmale Darstellung ohne abgeschnittene Option-Controls
- deterministische Vorschau

## Was bewusst noch nicht freigegeben ist

Der Browser-Maskenentwurf wird weiterhin **nicht gespeichert**. Ein Reload verwirft den Draft.

Noch offen sind unter anderem:

- statische Sichtbarkeit
- Breitenänderung im 12-Spalten-Raster
- gemeinsame Accessibility-Abnahme der vollständigen Eigenschaftenbearbeitung
- `defaultSelection` für Choice-Felder
- Save-/Load-Grenze für Masken
- produktive Masken-Persistenz
- größere Struktur-, Regel-, Import-/Export- und Recovery-Funktionen

Diese Grenzen sind Absicht. Neue Schreibpfade werden erst geöffnet, wenn Preview, Integrität und Recovery ausreichend geklärt sind.

## Nächste sichere Reihenfolge

Der aktuelle `TODO.md`-Stand priorisiert nach I113:

1. **statische Sichtbarkeit** ausschließlich browserlokal
2. **Breite im 12-Spalten-Raster** mit Vorabvalidierung
3. **gemeinsame Eigenschaften-/Accessibility-Abnahme**
4. **Persistenzgrenze separat planen**, erst danach über Save/Load entscheiden

Keiner dieser Punkte öffnet automatisch CP-03 oder CP-06.

## Schutz der Datenbank

Bestimmte Bereiche sind eingefroren und dürfen nicht beiläufig geändert werden:

- **CP-03:** Datenbankschema
- **CP-06:** Domain-/Repository-Kern

Eine Änderung dort benötigt einen eigenen Reopen-Plan, passende Regressionen und ein separates Deep-Gate.

## Architekturregel

```text
Oberfläche
↓
Application Service
↓
Domain / Repository
↓
SQLite
```

Die Oberfläche führt kein direktes SQL aus. Der Browser-Masken-Baukasten besitzt aktuell keinen versteckten produktiven Schreibpfad.

## Qualitäts- und Gate-Modell

Änderungen werden in kleinen, begrenzten Iterationen durchgeführt:

1. Scope und Nicht-Scope im Iterationsmanifest festlegen.
2. Nur die geplanten Dateien ändern.
3. Triggerbasierte, passende Regressionen ausführen.
4. Bei Rot ausschließlich die konkrete Ursache beheben.
5. CP-/Freeze-Bereiche unverändert lassen, solange kein eigener Reopen beschlossen wurde.
6. Erst nach grünem Gate mergen.

Für UI-Slices gehören Tastaturbedienung, Fokus, zugängliche Beschriftung und schmale Darstellung zum Funktionsvertrag.

## Projektdateien

- `TODO.md` – aktueller Implementierungspool mit erledigten und offenen Punkten
- `docs/PRODUCT_ROADMAP.md` – langfristige Abhängigkeiten und Risikoklassen
- `docs/LAIEN_START.md` – kurze Erklärung ohne Entwicklerfokus
- `AGENTS.md` – Entwicklungs- und Freeze-Regeln
- `CONTRIBUTING.md` – Mitarbeit am Repository
- `docs/PROJECT_STANDARDS.md` – Prüf- und Qualitätsstandard
- `.provoware/iterations/` – maschinenlesbare Iterationsverträge
- `docs/development/` – historische Entwicklungs- und Evidence-Dokumente

## Repository-Hygiene

`main` ist die stabile Basis. Neue Arbeiten starten vom bestätigten `main` und laufen über kleine Branches und Pull Requests.

Historische Branches oder alte Iterationsnachweise sind keine Abkürzung für neue Entwicklung. Keine kosmetischen Massenänderungen werden mit Produktänderungen vermischt.

## Lizenz

Noch nicht festgelegt.
