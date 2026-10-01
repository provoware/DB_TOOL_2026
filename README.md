# PROVOWARE DB TOOL 2026

PROVOWARE DB TOOL 2026 ist ein lokales Datenbankprojekt mit dem Ziel, Datenstrukturen auch ohne Datenbankwissen verständlich, sicher und schrittweise bedienbar zu machen.

> **Aktueller Produktstand:** `TODO.md` und `docs/PRODUCT_ROADMAP.md` sind die maßgeblichen Quellen.  
> **Entwicklungshistorie:** `docs/DEVELOPMENT_HISTORY.md` bündelt die aus der README ausgelagerten Iterationsnotizen.  
> **Sicherheitsstatus:** Browser-Maskenentwurf ohne Persistenz und ohne produktiven Datenbankzugriff.  
> **Frozen Core:** CP-03 und CP-06 bleiben geschlossen.

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

Der Selbstcheck prüft die zentralen Projektdateien, den aktuellen Iterationskontext
und den gemeinsamen Preflight. Ein grünes Ergebnis bescheinigt ausschließlich diese
Repository-Prüfung. Die vollständige Produktabnahme und das noch blockierte
I167-Chromium-Gate sind gesonderte Prüfungen.

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

Bis einschließlich **I146** besitzt der temporäre Browser-Draft:

- Komponentenpalette und feste 12-Spalten-Arbeitsfläche
- deterministische monotone Draft-IDs
- temporäres Platzieren, Verschieben, Entfernen und Duplizieren mit neuer monotoner Draft-ID
- kontrolliertes Neuordnen ganzer Draft-Elemente per Hoch/Runter-Controls ohne Drag-and-drop-Zwang
- semantische Vorschau-Abschnitte über den vorhandenen Bereich-Baustein
- browserlokales Ein-/Ausklappen dieser Abschnitte mit zugänglichem Toggle
- explizite natürliche Tab-Reihenfolge mit roving Tabstop für die 12 Zielspalten
- feste Desktop-Vorschau mit 1152-px-Viewport in horizontal scrollbarem Rahmen
- browserlokale Umschaltung auf eine Tablet-Vorschau mit 768 px, Desktop bleibt Standard
- zusätzlicher schmaler Preview-Modus mit 360 px; alle drei Modi teilen dieselben Preview-Daten
- gemeinsame reale Chromium-Abnahme der drei Viewports auf Fokus, Umschaltung, Beschriftung, Overflow und Inhaltskonsistenz
- Blockierung ungültiger Rasterziele vor Mutation
- Label- und Hilfetext-Bearbeitung
- Pflichtfeld-Eigenschaft
- Datentypen `text`, `number`, `date`, `boolean`, `single_choice`, `multi_choice`
- typabhängig validierten skalaren Standardwert
- inaktive statt still umgeschriebene Standardwerte bei Choice-Typen
- browserlokale Choice-Optionen
- stabile monotone `draft-option-*`-IDs
- browserlokale `defaultSelection` über stabile Option-IDs für Einfach- und Mehrfachauswahl
- ausgewählte Default-Optionen gegen stilles Entfernen und ungültige Typverengung geschützt
- Optionen hinzufügen, entfernen und deterministisch hoch/runter verschieben
- Live-Status, Tastaturwege und deterministische Fokus-Rückgabe
- schmale Darstellung für die bisher freigegebenen Property-Controls
- **statische Sichtbarkeit:** Komponenten bleiben im Editor erreichbar, können aber aus der Vorschau ausgeblendet werden
- browserlokale Breitenbearbeitung von 1–12 Spalten mit Prüfung vor Mutation
- bestätigte 100/150/200-%-Evidence für die vollständige vorhandene Property-Matrix
- deterministische Preview ohne produktiven Write
- read-only Raster-Assistent: kompakter Layout-Vorschlag aus bestehender Reihenfolge und bestehenden Breiten, ohne Übernahme
- explizite Vorher/Nachher-Tabelle mit geplanter Zeilen-/Spaltenänderung pro Element; tatsächliche Übernahme weiterhin gesperrt
- separater flüchtiger Browser-Layoutvertrag `draft-id → {row, column}`; die Arbeitsfläche rendert daraus, ohne Persistenz
- atomare browserlokale Übernahme eines bestätigten Rastervorschlags mit Stale-Schutz, Fokus-Rückgabe und echter Chromium-Vorher/Nachher-Evidence

## Entwicklungsstand und Historie

Die README bleibt bewusst auf **Einstieg, Sicherheitsgrenzen, Bedienpfade und Architektur** fokussiert. Iteration-für-Iteration-Protokolle werden hier nicht mehr dupliziert.

- **Aktueller Umsetzungsstand:** `TODO.md`
- **Langfristige Abhängigkeiten und Risikoklassen:** `docs/PRODUCT_ROADMAP.md`
- **Lesbare Entwicklungshistorie:** `docs/DEVELOPMENT_HISTORY.md`
- **Maschinenlesbare Auditspur:** `.provoware/iterations/`
- **Erklärung des internen Steuerordners:** `.provoware/README.md`

Damit bleibt die Startseite kurz genug für Nutzer und Entwickler, während die vollständige Nachvollziehbarkeit erhalten bleibt.

## Was bewusst noch nicht freigegeben ist

Der Browser-Maskenentwurf wird weiterhin **nicht gespeichert**. Ein Reload verwirft den Draft.

Noch offen sind insbesondere:


- produktive Umsetzung der bereits geplanten Save-/Load-Grenze
- produktive Masken-Persistenz
- größere Struktur-, Regel-, Import-/Export-, Recovery- und Dashboard-Funktionen

## Nächste sichere Reihenfolge

1. I170-Testausnahme für Pflichtwert und browserlokale Regel-Preview nachvollziehbar beibehalten; ein späterer echter Browser-Test kann die Evidenzlücke schließen.
2. Nächste Regelart nur als eigene browserlokale Iteration mit gezielter Prüfung planen.
3. Persistenzabhängige Datenarbeit bis zu eigenen Preview-, Integritäts- und Recovery-Verträgen geschlossen halten.

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

Der aktuelle Fortschritt wird aus den eindeutigen Checkboxen des Implementierungspools A–M in `TODO.md` abgeleitet. Die folgende kompakte Zeile bleibt absichtlich erhalten, weil der gemeinsame lokale/CI-Preflight sie als Driftkontrolle prüft.

> **Gesamtfortschritt Master-TODO A–M:** **42 / 132 = 31,8 %**

## Wichtige Projektdateien

- `TODO.md` – Master-Implementierungspool
- `docs/PRODUCT_ROADMAP.md` – langfristige Abhängigkeiten und Risikoklassen
- `docs/DEVELOPMENT_HISTORY.md` – lesbare Iterationshistorie; ältere Aussagen können durch spätere Iterationen überholt sein
- `.provoware/README.md` – Erklärung der internen Audit-, Freeze-, Queue- und Control-Plane-Dateien
- `docs/LAIEN_START.md` – kurze Erklärung ohne Entwicklerfokus
- `AGENTS.md` – Entwicklungs-, Gate- und Freeze-Regeln
- `CONTRIBUTING.md` – Mitarbeit am Repository
- `docs/PROJECT_STANDARDS.md` – Prüf- und Qualitätsstandard
- `.provoware/iterations/` – maschinenlesbare Iterationsverträge
- `scripts/repo_self_check.sh` – Repository-Gesundheitsprüfung
- `scripts/start_readonly_web.py` – sicherer lokaler Nur-Lese-Webstart

## Entwicklungs-Preflight

Vor Produktänderung oder PR:

```bash
python scripts/iteration_preflight.py
```

Das Kommando prüft Fortschrittskonsistenz, aktuelles Manifest, Gate-Profil, Frozen-Core-Eskalation und Gate-Routing mit derselben Logik, die auch GitHub Actions verwendet. Die separate Scope-Prüfung bleibt zusätzlich bestehen.

## Repository-Hygiene

`main` ist die bestätigte stabile Basis. Neue Produktarbeit startet von dort und läuft über kleine Branches und Pull Requests. Historische Branches und alte Evidence-Stände ersetzen kein aktuelles Gate.

## Lizenz

Noch nicht festgelegt.
