# AGENTS.md — PROVOWARE Entwicklungsregeln

Diese Regeln gelten für alle Agenten, Automationen und Entwicklungsiterationen in diesem Repository.

## 1. Oberste Prinzipien

### 1.1 Planung vor Änderung
Vor jedem Patch müssen feststehen:
- Ziel der Änderung
- betroffene Dateien
- betroffene Funktionen/Blöcke
- Patchgrund
- Risiken
- relevante Tests
- bewusst nicht veränderte Bereiche

Ohne diese Angaben darf kein Änderungsagent starten.

### 1.2 Codesparsamkeit
Es gilt immer der kleinste sinnvolle Eingriff.
- keine globalen Umformatierungen
- keine kosmetischen Nebenänderungen
- keine prophylaktischen Refactorings
- keine Umbenennungen ohne fachlichen Grund
- keine neuen Abstraktionen ohne konkreten Nutzen
- keine Duplikatbereinigung außerhalb des betroffenen Pfads
- keine Vollersetzung stabiler Dateien, wenn ein kleiner Patch reicht

### 1.3 Trafficsparsamkeit
Dateien werden nur gelesen, wenn sie für die aktuelle Iteration erforderlich sind.
Standard-Reihenfolge:
1. geänderte Datei
2. direkte Imports/Abhängigkeiten
3. betroffene Tests
4. relevante Manifest-/Freeze-Dateien
5. erst bei begründetem Bedarf weiterer Kontext

Full-Repo-Scans sind verboten, außer:
- Architekturgrenze betroffen
- Frozen Core betroffen
- Abhängigkeitsgraph unklar
- systemweiter Fehler
- explizites Deep-Gate

### 1.4 Keine unnötigen Tests
Tests werden risikobasiert gewählt.
Nach einem kleinen Patch:
- Syntax/Compile der betroffenen Dateien
- direkt betroffene Tests
- engste sinnvolle Regression

Keine Volltests ohne Anlass.
Keine Wiederholungsprüfung ohne neue Änderung oder neuen Befund.
Ein bereits grüner Test wird nicht erneut ausgeführt, solange sich sein relevanter Codepfad nicht geändert hat.

### 1.5 Keine Endlosschleifen
Maximal:
- 1 Diagnose
- 1 gezielter Patch
- 1 Validierung
pro Iterationsschritt.

Weitere Schleifen benötigen einen neuen konkreten Befund.

## 2. Dateibesitz und Kollisionsschutz

Pro Iteration darf jede schreibbare Datei genau einem Änderungsagenten gehören.

Vor Ausführung:
- Schreibdateien aller Pläne sammeln
- Überschneidungen prüfen
- bei Konflikt: ROT
- keine konkurrierenden Schreibzugriffe

Reviewer, Planer, Orchestrator, Gate- und Screenshot-Agenten sind read-only gegenüber Produktivcode.

## 3. Change-Manifest Pflicht

Jeder Änderungsagent erzeugt nach seinem Patch ein Manifest mit:
- Iteration
- Agent-ID
- geänderte Dateien
- Zweck
- gelesene Abhängigkeiten
- notwendige Tests
- erwartete Seiteneffekte
- bewusst nicht geprüfte Bereiche

Dieses Manifest ist die primäre Eingabe für Prüfagenten.

## 4. Prüfagenten

Prüfagenten lesen standardmäßig nur:
- Dateien aus changed_files
- direkte Abhängigkeiten
- betroffene Tests
- relevante Freeze-/Schema-/Policy-Dateien

Sie schreiben keine Produktivdateien.

Findings werden klassifiziert:
- BLOCKER
- HIGH
- MEDIUM
- LOW
- INFO

Nur BLOCKER/HIGH lösen automatisch eine neue Patch-Iteration aus.
MEDIUM wird geplant.
LOW/INFO wird gesammelt, nicht sofort umgesetzt.

## 5. Testauswahl nach Änderungsart

### Dokumentation
- Link-/Strukturprüfung
- kein Produktivtest

### UI/CSS/HTML
- betroffene UI-Tests
- responsive Zielgrößen
- Fokus/Keyboard falls betroffen
- Screenshot nur wenn Screenshot-Iteration oder visuelle Kernänderung

### Application Service
- betroffene Service-Tests
- relevante Repository-Mocks/Integrationen

### Domain/Repository
- direkte Unit-/Integrations-Regression
- Frozen-Core-Gate wenn geschützt

### Schema/Migration
- Migration
- Schema-Hash/Manifest
- foreign_key_check
- integrity_check
- komplette betroffene DB-Regression

## 6. Stop-Kriterien

Eine Iteration endet sofort, wenn:
- Ziel erfüllt
- relevante Tests grün
- kein BLOCKER/HIGH offen
- keine Dateikollision
- keine ungeplante Datei geändert
- Gate-Status bestimmbar

Nicht weiter optimieren, nur weil noch Zeit oder Kontext vorhanden ist.

## 7. Freeze-Schutz

CP-03 und CP-06 gelten als geschützt.

Eine Änderung dort benötigt:
- expliziten Plan
- Begründung
- neue Regression
- Impact-Analyse
- Deep-Gate

Keine beiläufige Anpassung durch UI- oder Komfortarbeiten.

## 8. UI- und Screenshot-Regel

Alle 5 Iterationen:
- Screenshot erzeugen
- feste Referenzgröße
- Theme dokumentieren
- Kurzfazit
- visuelle Regression ja/nein

Zwischen diesen Punkten nur dann Screenshot:
- visuelle Kernänderung
- Layoutfehler
- Fokus-/Accessibility-Fehler
- expliziter Review-Bedarf

## 9. Kosten- und Kontextbudget

Jede Iteration soll vorab grob klassifiziert werden:
- S = 1–2 Dateien
- M = 3–5 Dateien
- L = 6–10 Dateien
- XL = >10 Dateien

XL ist standardmäßig zu zerlegen.

Ziel:
- kleine PRs
- wenig Kontext
- geringe Dateistreuung
- klar begrenzte Testmatrix

## 10. Keine stillen Seiteneffekte

Verboten ohne explizite Freigabe:
- Dependency-Upgrades
- Formatierer über gesamtes Repo
- neue Runtime-Abhängigkeiten
- Änderungen an CI außerhalb des Ziels
- Versionssprünge
- Datenbankmigrationen
- API-Brüche
- Datei-/Ordnerumzüge

## 11. Selbstvalidierung

Jede Iteration dokumentiert:
- geplante Dateien
- tatsächlich geänderte Dateien
- Abweichungen
- Tests
- Gate
- offene Findings
- Änderungsvolumen
- nächste Empfehlung

Wenn tatsächlich geänderte Dateien von der Planung abweichen:
- Status GELB oder ROT
- Ursache erklären
- keine stillschweigende Fortsetzung

## 12. Priorität der Optimierung

Reihenfolge:
1. Korrektheit
2. Datensicherheit
3. Regression vermeiden
4. Verständlichkeit
5. Wartbarkeit
6. Performance
7. Komfort
8. Kosmetik

Kosmetik darf niemals Stabilität oder Testaufwand dominieren.

## 13. Abschlussformat

Jede größere Entwicklungsantwort endet mit:
- Projektname
- Repo
- Branch/PR
- Checkpoint
- Fortschritt
- Änderungsvolumen
- Gate-Status
- Freeze-Status
- Tooldetails
- Optimierungsempfehlung
- genau den nächsten zwei Schritten

## 14. Goldene Regel

Wenn eine Änderung nicht notwendig ist, wird sie nicht gemacht.
Wenn ein Test den geänderten Pfad nicht berührt, wird er nicht automatisch ausgeführt.
Wenn eine Datei nicht relevant ist, wird sie nicht gelesen.
