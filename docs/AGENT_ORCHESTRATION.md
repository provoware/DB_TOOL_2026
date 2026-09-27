# PROVOWARE Agent-Orchestrierung V2

## Ziel

V2 reduziert Wartezeit, Kontextverbrauch und unnötige Agentenübergaben, ohne Scope-, Evidence-, Single-Writer-, Freeze- oder Recovery-Schutz abzuschwächen. Der Standardweg nutzt **drei Kernrollen**; Spezialisten werden ausschließlich durch fachliche Risiken ausgelöst.

Die Control-Plane-V2-Verträge I120–I124 bleiben **shadow-only und nicht autoritativ**. V2 ist eine operative Arbeitsweise innerhalb der weiterhin maßgeblichen Repository-Governance.

## 1. Fast Context

Jede Iteration startet mit:

```bash
python scripts/build_iteration_context.py --check
```

Der Fast Context bündelt:
- neuesten Iterationsstand,
- bestätigte Statuszeilen aus README,
- A–M-Fortschritt aus tatsächlichen Checkboxen,
- nächste Prioritäten,
- Roadmap-Stand,
- Hashes der zentralen Kontextquellen.

Der PR-Router führt denselben Drift-Check aus, bevor Manifest und Scope geroutet werden. Dadurch werden widersprüchliche README-/TODO-Fortschrittsstände früh und billig gestoppt.

## 2. Drei Kernrollen

### A. Orchestrator/Planner · read-only
- nimmt Fast Context als Startpunkt statt eines neuen Repo-Scans
- klärt Ziel, Risikoklasse, Write-Set, Nicht-Scope und Tests
- prüft Ausgangs-SHA, Dateikollisionen und Frozen-Core-Trigger
- versiegelt beide Schritte der Iteration vor dem ersten Write
- entscheidet, welche Spezialisten tatsächlich gebraucht werden

### B. Executor · Single Writer
- besitzt ausschließlich das freigegebene Write-Set
- setzt pro Schritt genau den kleinsten notwendigen Patch um
- sucht während des Writes nicht nach neuen Nebenoptimierungen
- veröffentlicht pro abgeschlossenem Schritt genau einen atomaren Head
- stoppt bei abweichendem SHA, Scope oder Invariant

### C. Validator/Finalizer · read-only
- prüft Diff gegen Manifest und Ausgangs-SHA
- führt nur die risikobasiert notwendigen Gates aus
- bestätigt oder verwirft Evidence-Reuse
- klassifiziert Findings
- gibt Merge nur bei reproduzierbarem GRÜN frei
- finalisiert Recovery-Key, nächsten Schritt und Queue-Reste

## 3. Spezialisten nur bei Trigger

| Spezialist | Trigger |
|---|---|
| Deep/Frozen Inspector | Schema, Domain, Repository, Storage, CP-03/CP-06 |
| Accessibility/Chromium | sichtbare UI, Keyboard, Fokus, responsive Darstellung |
| Screenshot | visueller Trigger oder fünfte UI-relevante Iteration seit Referenz |
| Recovery/Integrität | produktiver Write, Import, Massenaktion, Restore |
| Dependency/Security | neue/geänderte Runtime- oder Build-Abhängigkeit |
| Analyse/Root-Cause | reproduzierter Fehler, BLOCKER/HIGH oder unklare Ursache |

Ohne Trigger wird die Rolle nicht gestartet.

## 4. Fast-Path-Ablauf

```text
Fast Context + Ausgangs-SHA
        ↓
Orchestrator/Planner
        ↓
Scope + Write-Set + 2 Schritte versiegelt
        ↓
Executor Schritt 1
        ↓
kleinstes Zwischen-Gate
        ↓ grün
Executor Schritt 2 oder NO_FIX_REQUIRED
        ↓
Validator/Finalizer
        ↓
relevante Gates + Evidence
        ↓
SHA-gebundener Merge
```

Bei Persistenz/Frozen-Core/Architektur-Unklarheit:

```text
Fast Path -> ESCALATE -> Deep/Recovery/Spezialist -> vollständiges Gate
```

## 5. Kontext- und Leseökonomie

Eine zentrale Quelle wird pro unverändertem Hash nur einmal vollständig gelesen. Danach arbeiten read-only Rollen mit dem Fast Context und gezielten Ausschnitten.

Standardbudget:
1. Fast Context
2. geplante Write-Datei
3. direkte Abhängigkeit
4. betroffener Test
5. nur bei Trigger Freeze-/Architekturquelle

Ein Full-Repo-Scan ist weiterhin ausschließlich bei systemweitem oder unklarem Impact erlaubt.

## 6. Evidence-Reuse

Grüne Evidence darf wiederverwendet werden, wenn ihre relevanten Quellen unverändert sind. Dafür dienen die Fast-Context-Hashes als schnelle Vorprüfung.

Beispiel: Ein Dokumentations- oder Testvertrag, der den Browser-Runtime-Code nicht verändert, erzwingt keinen neuen Chromium-Lauf, wenn vorhandene reale Chromium-Evidence exakt denselben unveränderten Runtime-Pfad abdeckt.

Nicht wiederverwendbar bei:
- geändertem relevanten Quellpfad,
- neuem Fehlerbefund,
- erweitertem Scope,
- neuem Accessibility-/Layout-Risiko,
- produktivem Write oder Recovery-Änderung.

## 7. Screenshot-Regel

Gezählt werden nur Iterationen, die sichtbares Rendering verändern oder UI-Evidence fachlich erweitern. Reine Docs-/Governance-/Scope-Iterationen verbrauchen keinen Slot.

Spätestens jede fünfte UI-relevante Iteration erzeugt eine neue Referenz. Visuelle Kern-, Layout-, Fokus- oder Accessibility-Änderungen erzeugen unabhängig davon sofort Evidence.

## 8. Parallelität

Parallel erlaubt:
- unabhängige read-only Inspektionen,
- bereits klar getrennte Recherche-/Evidence-Auswertungen.

Nicht parallel:
- zwei Writer im selben Scope,
- Planänderung während eines laufenden Executor-Schritts,
- Merge und nachgelagerte abhängige Mutation gleichzeitig.

Damit steigt die Lesegeschwindigkeit, ohne Write-Kollisionen zu riskieren.

## 9. Findings und Next Queue

BLOCKER/HIGH stoppen den Fast Path. MEDIUM wird geplant. LOW/INFO wird gesammelt.

Neue Anforderungen erweitern niemals den laufenden versiegelten Plan. Sie gehen mit Beziehung wie REQUIRES, BLOCKS, DUPLICATE, SUPERSEDES oder CONFLICTS in die nächste Queue.

## 10. Abschluss

Der Validator/Finalizer bestätigt:
- Ausgangs-SHA und finalen Head,
- geplante versus tatsächliche Dateien,
- relevante Tests/Evidence,
- offene Findings,
- Frozen-Core-Status,
- Recovery-Key,
- nächsten erlaubten Schritt.

**Leitsatz:** Einmal Kontext bauen, einmal schreiben, gezielt prüfen, nur bei Risiko eskalieren.
