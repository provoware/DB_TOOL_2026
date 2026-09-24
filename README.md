# PROVOWARE DB TOOL 2026

PROVOWARE DB TOOL 2026 ist ein lokales Datenbankprojekt mit dem Ziel, Datenstrukturen auch ohne Datenbankwissen verständlich, sicher und schrittweise bedienbar zu machen.

> **Bestätigter Produktstand:** I116 auf `main`  
> **Gate-Stand:** Targeted + Foundation für I116 grün  
> **Sicherheitsstatus:** Browser-Maskenentwurf ohne Persistenz und ohne produktiven Datenbankzugriff  
> **Frozen Core:** CP-03 und CP-06 bleiben geschlossen  
> **Gesamtfortschritt Master-TODO A–M:** **15 / 132 = 11,4 %**

## Zielbild

Das Projekt trennt Oberfläche, Anwendungslogik, Fachmodell und SQLite strikt voneinander. Neue Funktionen werden zuerst klein, reversibel und möglichst browserlokal oder read-only entwickelt. Produktive Schreibpfade werden erst geöffnet, wenn Preview, Integrität und Recovery geklärt sind.

## Sicherer Schnellstart

### Nur-Lese-Webmodus

Für eine bereits vorhandene und kompatible `main.db`:

```bash
python3 scripts/start_readonly_web.py --main-db /pfad/zu/main.db
```

Der Start:

- prüft Datenbankidentität und Schema,
- öffnet SQLite read-only,
- setzt `PRAGMA query_only = ON`,
- bindet ausschließlich an `127.0.0.1`,
- blockiert bei fehlender oder inkompatibler Datenbank.

Standardadresse: `http://127.0.0.1:8765`.

### Repository-Selbstprüfung

```bash
bash scripts/repo_self_check.sh
```

Die Entwicklungsgates wählen zusätzlich abhängig vom Iterationsmanifest nur die jeweils betroffenen Compile- und Regressionstests.

## Was das Projekt heute kann

### Datenbasis

- lokaler SQLite-Kern
- Kategorien, Einträge und frei definierbare Felder
- getrennte Application-, Domain- und Repository-Schichten
- freigegebene Nur-Lese-Pfade
- Schema-/Freeze-Schutz und Repository-Selbstprüfung
- deterministische Iterations- und Scope-Gates

### Browser-Masken-Baukasten

Bis einschließlich **I116** besitzt der temporäre Browser-Draft:

- Komponentenpalette und feste 12-Spalten-Arbeitsfläche
- deterministische monotone Draft-IDs
- temporäres Platzieren, Verschieben und Entfernen
- Blockierung ungültiger Rasterziele vor Mutation
- Label- und Hilfetext-Bearbeitung
- Pflichtfeld-Eigenschaft
- Datentypen `text`, `number`, `date`, `boolean`, `single_choice`, `multi_choice`
- typabhängig validierten skalaren Standardwert
- inaktive statt still umgeschriebene Standardwerte bei Choice-Typen
- browserlokale Choice-Optionen
- stabile monotone `draft-option-*`-IDs
- Optionen hinzufügen, entfernen und deterministisch hoch/runter verschieben
- Live-Status, Tastaturwege und deterministische Fokus-Rückgabe
- schmale Darstellung für die bisher freigegebenen Property-Controls
- **statische Sichtbarkeit:** Komponenten bleiben im Editor erreichbar, können aber aus der Vorschau ausgeblendet werden
- deterministische Preview ohne produktiven Write

### I115-Härtung

I115 hat zwei nach I113 gefundene Laufzeitrisiken gezielt repariert:

- versehentlich literal emittierte `\n`-Sequenzen im Browser-JavaScript
- Fokus-Rückgabe auf einen deaktivierten Reorder-Randbutton

Beide Reparaturen wurden über Targeted + Foundation gegatet.

## Was bewusst noch nicht freigegeben ist

Der Browser-Maskenentwurf wird weiterhin **nicht gespeichert**. Ein Reload verwirft den Draft.

Noch offen sind insbesondere:

- Breitenänderung im 12-Spalten-Raster
- vollständige 100/150/200-%-Evidence der gesamten Eigenschaftenbearbeitung
- gemeinsame Eigenschaften-/Preview-Abnahme
- `defaultSelection`-Vertrag für Choice-Felder
- Save-/Load-Grenze für Masken
- produktive Masken-Persistenz
- größere Struktur-, Regel-, Import-/Export-, Recovery- und Dashboard-Funktionen

## Nächste sichere Reihenfolge

1. **Breite im 12-Spalten-Raster** browserlokal ändern und Grenzen vor Mutation prüfen.
2. **Gesamte Eigenschaftenbearbeitung** bei 100/150/200 % sowie Tastatur/Fokus/schmaler Darstellung abnehmen.
3. **`defaultSelection`-Vertrag** separat planen, ohne Persistenz vorwegzunehmen.
4. **Persistenzgrenze für Masken** separat planen; erst danach Save/Load bewerten.

Keiner dieser Schritte öffnet automatisch CP-03 oder CP-06.

## Schutz der Datenbank

Eingefrorene Bereiche dürfen nicht beiläufig verändert werden:

- **CP-03:** Datenbankschema
- **CP-06:** Domain-/Repository-Kern

Änderungen dort benötigen einen eigenen Reopen-/Impact-Plan, passende Regressionen und ein separates Deep-Gate.

## Architektur

```text
Oberfläche
↓
Application Service
↓
Domain / Repository
↓
SQLite
```

Die Oberfläche führt kein direktes SQL aus. Der Browser-Masken-Baukasten besitzt aktuell keinen produktiven Schreibpfad.

## Qualitäts- und Gate-Modell

1. Scope und Nicht-Scope im Iterationsmanifest festlegen.
2. Nur die geplanten Dateien ändern.
3. Bei Zwei-Schritt-Iterationen nach Schritt 1 ein Zwischen-Gate ausführen.
4. Triggerbasierte statt unnötige Volltests verwenden.
5. Bei Rot ausschließlich die konkrete Gate-Ursache beheben.
6. Frozen-Core-Bereiche ohne eigenen Reopen unverändert lassen.
7. Erst nach vollständig grünem, SHA-genauem Gate mergen.

Für UI-Slices gehören Tastaturbedienung, sichtbarer Fokus, zugängliche Namen/Status und schmale Darstellung zum Funktionsvertrag.

## Fortschrittsmessung

Die **11,4 %** sind kein geschätzter Marketingwert. Gezählt werden die eindeutigen Checkboxen des Implementierungspools **A–M** in `TODO.md`: aktuell **15 erledigt von 132**. Die separat aufgeführte Prioritätenliste wird nicht zusätzlich gezählt.

Dadurch ist die Zahl bewusst konservativ: große und kleine TODO-Punkte zählen jeweils einmal.

## Wichtige Projektdateien

- `TODO.md` – Master-Implementierungspool
- `docs/PRODUCT_ROADMAP.md` – langfristige Abhängigkeiten und Risikoklassen
- `docs/LAIEN_START.md` – kurze Erklärung ohne Entwicklerfokus
- `AGENTS.md` – Entwicklungs-, Gate- und Freeze-Regeln
- `CONTRIBUTING.md` – Mitarbeit am Repository
- `docs/PROJECT_STANDARDS.md` – Prüf- und Qualitätsstandard
- `.provoware/iterations/` – maschinenlesbare Iterationsverträge
- `scripts/repo_self_check.sh` – Repository-Gesundheitsprüfung
- `scripts/start_readonly_web.py` – sicherer lokaler Nur-Lese-Webstart

## Repository-Hygiene

`main` ist die bestätigte stabile Basis. Neue Produktarbeit startet von dort und läuft über kleine Branches und Pull Requests. Historische Branches und alte Evidence-Stände ersetzen kein aktuelles Gate.

## Lizenz

Noch nicht festgelegt.
