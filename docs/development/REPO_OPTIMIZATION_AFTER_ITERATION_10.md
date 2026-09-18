# Repo-Optimierung nach Iteration 10

Diese Analyse priorisiert **Kosten-, Traffic-, Kollisions- und Wartungsreduktion**. Keine kosmetischen Änderungen.

## 1. Gestapelte PR-Kette konsolidieren — PRIORITÄT HOCH

Aktuell existiert eine lange kanonische Kette von PR #2 bis zum Iteration-10-PR. Zusätzlich bestehen parallele Alternativpfade.

**Nutzen einer Konsolidierung:**
- weniger offene PRs
- weniger doppelte GitHub-Actions-Läufe
- einfachere Branch-Historie
- geringerer Review-Kontext
- weniger Risiko, versehentlich auf einen veralteten Zwischenbranch weiterzubauen

**Regel:** Nicht blind schließen. Zuerst einzigartige Findings/Dokumentation sichern, dann obsolete Pfade schließen.

## 2. Doppelte Iterationspfade #7/#9 und #8/#10 bereinigen — PRIORITÄT HOCH

Für Iteration 5 und 6 existieren parallele PR-Pfade. Mindestens PR #7 enthält ein eigenes UI-Finding zur Feldabstands-Darstellung.

Empfehlung:
1. einzigartige Findings/Regeln in die kanonische Kette übernehmen,
2. Inhalte vergleichen,
3. danach obsolete PRs schließen.

## 3. GitHub-Actions-Traffic reduzieren — PRIORITÄT HOCH

`Repository Foundation` und `Agent Governance` laufen derzeit bei vielen gestapelten Änderungen mehrfach.

Empfehlung:
- Path-Filter weiter schärfen,
- Governance nur bei Governance-/Manifeständerung oder explizitem Gate laufen lassen,
- Produktprüfungen über Iterationsmanifest gezielt auswählen.

## 4. Manifest-gesteuerte Targeted-Test-CI — PRIORITÄT HOCH

Lokale direkte Tests sind kostensparend, aber GitHub sollte den deklarierten Zieltest ebenfalls reproduzieren können.

Empfehlung:
- kleines Skript liest `tests_required` aus dem aktuellen Iterationsmanifest,
- erlaubt nur freigegebene Befehlsarten,
- führt gezielt diese Tests aus,
- erzeugt TXT-Artefakt.

Kein automatischer Full-Suite-Fallback.

## 5. Eine Iteration = ein Git-Commit — PRIORITÄT MITTEL

Der Contents-API-Workflow erzeugt derzeit häufig einen Commit pro Datei.

Besser:
- Blobs erstellen,
- einen Tree bauen,
- genau einen Iterationscommit erzeugen.

Vorteile:
- deutlich ruhigere Historie,
- weniger Commit-Traffic,
- einfacheres Review/Rollback.

## 6. Screenshot-Artefakte schlank halten — BEREITS GUT

Vollauflösende PNG-Dateien müssen nicht dauerhaft das Repo aufblasen.

Beibehalten:
- kleine Vorschau im Repo,
- Original-SHA-256 dokumentieren,
- Full-Resolution als Build-/Chat-/CI-Artefakt.

## 7. AGENTS.md ↔ rules.yaml Drift verhindern — PRIORITÄT MITTEL

Die menschliche und maschinenlesbare Regelbasis kann langfristig auseinanderlaufen.

Empfehlung:
- semantischen Paritätscheck erweitern,
- nur Kernregeln doppelt abbilden,
- keine zweite vollständige Regelkopie erzeugen.

## 8. Branch Protection erst nach Konsolidierung — PRIORITÄT MITTEL

Nach Bereinigung der PR-Kette sollten auf `main` erforderliche Checks gesetzt werden:
- Repository Foundation
- Agent Governance / Targeted Gate

Dies ist eine Repo-Einstellung mit Außenwirkung und sollte erst nach der Konsolidierung bewusst aktiviert werden.

## Fazit

Die größte aktuelle Optimierung liegt **nicht im Produktcode**, sondern in PR-/CI-Hygiene. Produktarchitektur und kleine Iterationsgrößen funktionieren bereits wie vorgesehen.
