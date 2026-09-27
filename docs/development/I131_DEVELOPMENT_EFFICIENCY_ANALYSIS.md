# I131 – Analyse und Optimierung des Entwicklungsverfahrens

## Ausgangslage

Das bisherige Verfahren war qualitativ stark: Single Writer, Zwei-Schritt-Iterationen, kleine PRs, risikobasierte Tests, Frozen-Core-Schutz und SHA-genaue Gates haben Regressionen gut begrenzt. Die letzten Iterationen zeigen zugleich vermeidbare Prozesskosten.

## Beobachtete Effizienzbremsen

### 1. Wiederholtes Kontextlesen
Mehrere Rollen waren so beschrieben, dass sie nacheinander README, TODO, Roadmap, Manifest und Governance-Kontext erneut erschließen konnten. Das erhöht Leseaufwand und macht unterschiedliche Momentaufnahmen wahrscheinlicher.

### 2. Zu viele Standard-Handoffs
Orchestrierung V1 beschrieb sieben Rollen als normale Pipeline. Für kleine Docs-, Test- oder browserlokale Änderungen sind Analyseagent, Planungsagent, Prüfagent, Gate-Agent und Orchestrator häufig logisch getrennte Tätigkeiten, aber nicht fünf notwendige Übergaben.

### 3. Statusdrift wurde spät sichtbar
I125 musste README/TODO an den echten Stand angleichen. I130 fand zusätzlich eine Roadmap, die noch I103 meldete. Die Ursache ist weniger fehlende Sorgfalt als fehlende billige maschinelle Frühprüfung.

### 4. Screenshot-Zähler war zu grob
Die Regel „alle fünf Iterationen“ zählte auch reine Docs-/Governance-Arbeit. Solche Änderungen können keine visuelle Regression erzeugen, verursachen aber potentiell Browser-/Screenshot-Aufwand.

### 5. Evidence-Reuse war Prinzip, aber kein Startsignal
AGENTS verbot unnötige Wiederholung bereits grüner Tests, bot aber keinen kompakten Fingerprint der zentralen Kontextquellen. Dadurch musste die Anwendbarkeit früherer Evidence häufiger manuell erneut begründet werden.

## Was bewusst erhalten bleibt

- Planung vor Mutation
- zwei logisch abhängige Schritte pro Iteration
- genau ein produktiver Writer
- atomare Remote-Heads
- SHA- und Scope-Bindung
- kein PASS ohne echte Evidence
- BLOCKER/HIGH stoppen
- Frozen Core nur mit Reopen/Deep-Gate
- persistente Writes nur mit Preview/Integrität/Recovery
- keine Nebenrefactorings
- keine Status-only Commits bei echtem NO_FIX_REQUIRED

## Änderungen ab I131

### Fast Context
`scripts/build_iteration_context.py` erzeugt aus fünf zentralen Quellen einen kompakten Zustand und prüft README-/TODO-Fortschritt gegen die tatsächlichen A–M-Checkboxen. Die Quellen werden gehasht; unveränderte Hashes erlauben gezieltes Wiederverwenden von Kontext und Evidence.

Der PR-Router führt diesen Check vor dem eigentlichen Manifest-/Scope-Routing aus. Drift wird damit vor teureren Jobs erkannt.

### Drei Kernrollen statt sieben Standard-Handoffs
Operativ genügen im Normalfall:
1. Orchestrator/Planner,
2. Executor,
3. Validator/Finalizer.

Die früheren Spezialaufgaben verschwinden nicht. Sie werden triggerbasiert zugeschaltet, wenn ihr Risiko tatsächlich vorliegt.

### Trigger statt pauschaler Spezialarbeit
Chromium, Screenshot, Deep/Frozen, Recovery und Dependency/Security laufen nur bei den jeweils definierten Triggern. Das reduziert Arbeit gerade bei Docs-, Scope- und nicht-visuellen Governance-Iterationen.

### UI-bezogene Screenshot-Kadenz
Die Fünferregel zählt nur noch UI-relevante Iterationen. Jede echte Layout-/Fokus-/Accessibility-Änderung löst weiterhin sofort Evidence aus.

### Evidence-Reuse mit Hash-Vorprüfung
Unveränderte relevante Quellen + vorhandene grüne Evidence ermöglichen Wiederverwendung. Eine Hash-Gleichheit ersetzt den Nachweis nicht, sie macht nur schnell feststellbar, ob der frühere Nachweis überhaupt noch anwendbar sein kann.

## Qualitätswirkung

Die Optimierung entfernt keine Prüfung, die ein reales Risiko abdeckt. Sie verschiebt Prüfungen von „immer“ zu „bei Trigger“ und macht den gemeinsamen Ausgangskontext maschinenprüfbar.

Fail-closed bleibt erhalten:
- Kontextdrift -> ROT,
- Scopeabweichung -> ROT,
- Frozen-Core ohne Deep -> ROT,
- fehlende Evidence -> kein PASS,
- zweiter Writer -> ROT,
- geänderte relevante Quelle -> Evidence muss neu bewertet werden.

## Erwarteter Effizienzgewinn

Ohne künstliche Prozentversprechen sind die konkreten Einsparungen strukturell klar:
- weniger vollständige Dokument-Lesevorgänge,
- weniger Agentenübergaben bei kleinen Iterationen,
- frühere Fehlererkennung vor teuren Gates,
- weniger nutzlose Screenshots bei nicht-visueller Arbeit,
- weniger Wiederholung unveränderter Evidence,
- weiterhin derselbe Schutz bei riskanten Änderungen.

## Neue Standardentscheidung

**Fast Path**, wenn Scope lokal, Write-Set klar und kein Deep-/Persistenztrigger aktiv ist.

**Eskalation**, sobald Architektur, Frozen Core, produktiver Write, Recovery, Dependency oder Beweislage unklar wird.

Damit lautet das neue Entwicklungsprinzip:

> **Einmal Kontext bauen. Einmal schreiben. Gezielt prüfen. Nur bei Risiko eskalieren.**
