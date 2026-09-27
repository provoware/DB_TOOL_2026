# PROVOWARE DB TOOL 2026

PROVOWARE DB TOOL 2026 ist ein lokales Datenbankprojekt mit dem Ziel, Datenstrukturen auch ohne Datenbankwissen verständlich, sicher und schrittweise bedienbar zu machen.

> **Bestätigter Produktstand:** I132 auf `main`; `defaultSelection` für Choice-Felder browserlokal umgesetzt und weiterhin ohne Persistenz  
> **Governance-Stand:** I124 Control Plane V2 ist vollständig als Shadow-Vertrag gemergt; die bestehende Governance bleibt autoritativ  
> **Sicherheitsstatus:** Browser-Maskenentwurf ohne Persistenz und ohne produktiven Datenbankzugriff  
> **Frozen Core:** CP-03 und CP-06 bleiben geschlossen  
> **Gesamtfortschritt Master-TODO A–M:** **20 / 132 = 15,2 %**

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

Bis einschließlich **I132** besitzt der temporäre Browser-Draft:

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
- browserlokale `defaultSelection` über stabile Option-IDs für Einfach- und Mehrfachauswahl
- ausgewählte Default-Optionen gegen stilles Entfernen und ungültige Typverengung geschützt
- Optionen hinzufügen, entfernen und deterministisch hoch/runter verschieben
- Live-Status, Tastaturwege und deterministische Fokus-Rückgabe
- schmale Darstellung für die bisher freigegebenen Property-Controls
- **statische Sichtbarkeit:** Komponenten bleiben im Editor erreichbar, können aber aus der Vorschau ausgeblendet werden
- browserlokale Breitenbearbeitung von 1–12 Spalten mit Prüfung vor Mutation
- bestätigte 100/150/200-%-Evidence für die vollständige vorhandene Property-Matrix
- deterministische Preview ohne produktiven Write

### I115-Härtung

I115 hat zwei nach I113 gefundene Laufzeitrisiken gezielt repariert:

- versehentlich literal emittierte `\n`-Sequenzen im Browser-JavaScript
- Fokus-Rückgabe auf einen deaktivierten Reorder-Randbutton

Beide Reparaturen wurden über Targeted + Foundation gegatet.

## I118/I119 – bestätigte Produkt-Härtung

I118 ergänzt die browserlokale Breitenbearbeitung. Eine neue Breite wird nur übernommen, wenn das Element weiterhin vollständig in das 12-Spalten-Raster passt.

I119 liefert reproduzierbare reale Chromium-Evidence für die vollständige vorhandene Property-Matrix bei **100/150/200 %**. Die Evidence deckte zugleich einen Fokusverlust am Pflichtfeld-Toggle auf; dieser konkrete Befund wurde in derselben Iteration repariert und gegatet.

## I132 – browserlokale Standardauswahl

I132 setzt den I128-Vertrag im flüchtigen Browser-Draft um. Einfachauswahl referenziert maximal eine stabile `draft-option-*`-ID; Mehrfachauswahl hält eine geordnete, duplikatfreie ID-Liste. Options-Reorder erhält die Auswahl, ausgewählte Optionen können nicht still entfernt werden und eine Verengung von Mehrfach- auf Einfachauswahl wird bei mehreren Defaults vor Mutation blockiert.

Reale Chromium-Evidence prüft die neue Interaktion bei **100/150/200 %** inklusive Fokus-Rückgabe, Preview-Reihenfolge, Remove-Guard und horizontalem Overflow. Persistenz, Model, Store und Datenbank bleiben unverändert.

## I120–I124 – Control Plane V2 im Shadow-Modus

Die Governance-Kette ist inzwischen durchgängig modelliert: Registry/Lifecycle → versiegelter Plan und Single-Writer-Lease → triggerbasierte Inspektion/Planung → Controller-Sealing und Audit-Kette → Finalizer/Outcome.

Wichtig: Diese Kette ist **shadow-only und nicht autoritativ**. Sie verändert keine Produktfunktion, keine Persistenz und keinen Frozen Core. Deshalb erhöht I120–I124 den Produktfortschritt A–M nicht.

## I127 – gemeinsame Eigenschaften-/Preview-Abnahme

I127 bestätigt die bereits vorhandene gemeinsame Preview-Projektion mit einem eigenen Regressionsvertrag. Label, Breite, Hilfetext, Pflichtstatus, Datentyp, Choice-Optionen, skalarer Standardwert und Sichtbarkeit bleiben dadurch zusammen abgesichert. Es wurde keine neue Runtime-Funktion eingeführt; `defaultSelection` und Persistenz bleiben geschlossen.

## I128 – `defaultSelection` nur als Vertrag

I128 definiert den späteren browserlokalen Draft-Vertrag für Choice-Standardauswahlen. Referenzen laufen über stabile `draft-option-*`-IDs; stille Datenverluste bei Optionsentfernung oder Typverengung sind ausgeschlossen. Es existiert weiterhin **keine Runtime-Implementierung und keine Persistenz**.

## I129 – Persistenzgrenze geplant, Write weiter geschlossen

I129 bindet eine spätere Speicherung an denselben deterministischen Kandidaten über Preview-Fingerprint, Integritätsprüfung, Recovery-Punkt, atomaren Store-Commit und Read-back-Verifikation. Browser und Store bleiben getrennt; es existiert weiterhin **kein produktiver Save-Pfad**.

## Was bewusst noch nicht freigegeben ist

Der Browser-Maskenentwurf wird weiterhin **nicht gespeichert**. Ein Reload verwirft den Draft.

Noch offen sind insbesondere:

- browserlokale Umsetzung des bereits geplanten `defaultSelection`-Vertrags
- produktive Umsetzung der bereits geplanten Save-/Load-Grenze
- produktive Masken-Persistenz
- größere Struktur-, Regel-, Import-/Export-, Recovery- und Dashboard-Funktionen

## Nächste sichere Reihenfolge

1. Den geplanten `defaultSelection`-Vertrag in einer eigenen browserlokalen UI-Iteration umsetzen.
2. Danach eine kleine Struktur-Capability auswählen, ohne Persistenz zu öffnen.
3. Produktive Persistenz erst nach separaten Service-, Recovery- und Integritäts-Gates beginnen.

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

Die **15,2 %** sind kein geschätzter Marketingwert. Gezählt werden die eindeutigen Checkboxen des Implementierungspools **A–M** in `TODO.md`: aktuell **20 erledigt von 132**. Die separat aufgeführte Prioritätenliste wird nicht zusätzlich gezählt. Governance-Arbeit aus I120–I124 wird nicht als Produktpunkt mitgezählt.

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
