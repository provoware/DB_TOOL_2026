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

## 1.6 Zwei-Schritt-Iteration

Ab I59 besteht jede Entwicklungsiteration aus **genau zwei vorab geplanten, logisch aufeinanderfolgenden Arbeitsschritten**.

Grundform:
1. **Schritt 1 – Primäränderung:** kleinster fachlich notwendiger Patch oder Entscheidung.
2. **Schritt 2 – direkte Folgemaßnahme:** unmittelbar abhängige Härtung, Integration, Regression oder Wartbarkeitsverbesserung im selben fachlichen Scope.

Regeln:
- beide Schritte werden vor dem ersten Write im selben Iterationsplan festgelegt
- ein gemeinsamer Branch und grundsätzlich ein gemeinsamer PR
- nach Schritt 1 erfolgt ein **interner Zwischen-Gate**
- Schritt 2 startet nur, wenn Schritt 1 für seinen Scope GRÜN ist
- bei ROT/BLOCKER/HIGH in Schritt 1 wird Schritt 2 als **BLOCKIERT** dokumentiert und nicht erzwungen
- Schritt 2 darf keinen neuen unabhängigen Produkt-Scope eröffnen
- Freeze/Squash-Merge erst nach Abschluss bzw. dokumentierter Blockierung beider Schritte
- Tests werden je Schritt nur für neu betroffene Pfade ergänzt; keine doppelte Wiederholung bereits grüner Tests ohne neuen relevanten Code
- zwei kleine direkt abhängige Schritte sollen einen Branch-/PR-/CI-Zyklus teilen, statt künstlich zwei Iterationen zu erzeugen
- Frozen-Core-, Schema-, Dependency- oder Architekturgrenzen dürfen nicht durch Bündelung umgangen werden
- pro abgeschlossenem Schritt wird **genau ein atomarer Remote-Head** veröffentlicht; mehrere Dateiänderungen eines Schritts werden vor dem Ref-Update in einem gemeinsamen Git-Tree/Commit gebündelt
- ein zusätzlicher Repair-Head ist nur nach einem reproduzierbaren fehlgeschlagenen Gate zulässig
- wenn Schritt 2 nach grünem Schritt 1 ausschließlich `NO_FIX_REQUIRED` ergibt und keine versionierte Produkt-, Vertrags-, Freeze- oder Evidence-Änderung nötig ist, entsteht **kein** Status-only Commit und kein zweiter CI-Lauf
- ein formaler Freeze oder eine versionierte Vertrags-/Evidence-Änderung ist kein NO_FIX-Fall und benötigt weiterhin einen atomaren Step-2-Head mit Abschlussgate
- alle in `ci.compile` und `ci.python_tests` genannten Repository-Dateien werden vor dem ersten Remote-Head auf Existenz geprüft

Geeignete Kombinationen:
- Implementierung → gezielte Regression/Härtung
- Scope-Entscheidung → unmittelbar daraus folgende kleine Vertragspräzisierung
- kleiner Refactor → direkte Consumer-Migration
- UI-Funktion → fokussierte Accessibility-/Keyboard-Härtung

Ungeeignete Kombinationen:
- zwei fachlich unabhängige Features
- Produktänderung plus beiläufige CI-/Governance-Änderung
- Frozen-Core-Änderung plus Komfortarbeit
- zwei Schritte, die unterschiedliche Reopen-/Freeze-Entscheidungen benötigen

## 1.7 Produktpool, Roadmap und große Funktionsanforderungen

Breite Funktionswünsche werden zuerst als **Roadmap/Produktpool** zerlegt. Eine Roadmap ist Planungsgrundlage, aber **keine Implementierungsfreigabe**.

Regeln:
- kein Sammel-PR für fachlich unabhängige Features
- jedes Feature erhält eine eigene kleine Iteration oder einen klar abgegrenzten Teil einer zusammenhängenden Zwei-Schritt-Iteration
- TODO-Checkboxen beschreiben offenen Umfang, nicht Freigabe- oder Fertigstatus
- vor Umsetzung wird jede Capability einer Risikoklasse zugeordnet:
  - **A:** temporär/read-only/UI
  - **B:** Application-/Datenzugriff ohne Schemaänderung
  - **C:** produktive Persistenz/Schreibpfad
  - **D:** Schema, Beziehungen, Attachment-Speicher oder Frozen Core
- Klasse C benötigt vor produktivem Write einen expliziten Preview-/Simulation-, Integritäts- und Recovery-/Undo-Vertrag
- Klasse D benötigt einen separaten Reopen-/Impact-Plan und Deep-Gate; CP-03/CP-06 dürfen nicht als Nebeneffekt geöffnet werden
- Assistenten, Rastervorschläge und Vorlagen arbeiten zuerst als Vorschlag/Preview; produktive Übernahme braucht eine eigene Freigabe
- Massenänderungen und Import benötigen vor Commit eine deterministische Operationsliste beziehungsweise Mapping-Vorschau
- Accessibility ist Bestandteil des Funktionsvertrags, nicht nachträgliche Kosmetik

Der aktuelle langfristige Funktionspool steht in `docs/PRODUCT_ROADMAP.md`; die abhakbare Umsetzungsliste in `TODO.md`.

## 2. Dateibesitz und Kollisionsschutz

Pro Iteration darf jede schreibbare Datei genau einem Änderungsagenten gehören.

Vor Ausführung:
- Schreibdateien aller Pläne sammeln
- Überschneidungen prüfen
- bei Konflikt: ROT
- keine konkurrierenden Schreibzugriffe

Reviewer, Planer, Orchestrator, Gate-, Screenshot- und Laienhilfe-Agenten sind read-only gegenüber Produktivcode.

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

### 3.1 Laienhilfe-Subagent

Jede Iteration erzeugt zusätzlich genau ein kurzes **Laienhilfe-Delta**:
- nur den tatsächlich geänderten oder neu geklärten Aspekt erklären
- keine neue Produktfunktion erfinden
- Fachbegriffe kurz in Alltagssprache übersetzen
- vorhandene Erklärung bevorzugt gezielt verbessern statt neue Paralleltexte anzulegen
- standardmäßig nur Change-Manifest, betroffene Datei und den direkt relevanten Anleitungskontext lesen
- niemals Produktivcode verändern

Der Laienhilfe-Agent arbeitet inkrementell und trafficsparsam. Bei rein internen Iterationen optimiert er genau eine passende Erklärung oder dokumentiert verständlich, warum sich für die Bedienung nichts ändert. Eine größere Handbuch-Konsolidierung ist ein separater, begründeter Schritt.

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

Jede größere Entwicklungsantwort endet mit einer kompakten Abschlusskarte.

Pflichtfelder:
- Projektname
- Repo
- Branch/PR
- Checkpoint / Iteration
- Entwicklungsfortschritt als Prozentzahl und Balken
- Änderungsvolumen: neu / geändert / gelöscht / Tests / ungefähre Zeilen
- Gate-Status
- Freeze-Status
- relevante Tooldetails
- wichtigste Optimierungsempfehlung
- exakt die nächsten drei Schritte

Statusdarstellung:
- 🟢 GRÜN = vollständig bestanden
- 🟡 GELB = unvollständig, blockiert oder Review-Finding
- 🔴 ROT = echter Fehler, Regression oder Schutzverletzung
- 🔒 FROZEN = geschützter Bereich unverändert
- 📸 SCREENSHOT = Screenshot-Meilenstein erreicht

Beispiel Fortschritt:
`█████████░ 93 %`

Die Abschlusskarte soll auf einen Blick lesbar sein und keine langen Wiederholungen der vorherigen Detailanalyse enthalten.

## 14. Goldene Regel

Wenn eine Änderung nicht notwendig ist, wird sie nicht gemacht.
Wenn ein Test den geänderten Pfad nicht berührt, wird er nicht automatisch ausgeführt.
Wenn eine Datei nicht relevant ist, wird sie nicht gelesen.

---

## PROVOWARE GLOBAL DEVELOPMENT CONTRACT

Dieser globale Kern gilt zusätzlich zu den projektspezifischen Regeln. Bei Sicherheits- oder Nachvollziehbarkeitskonflikten hat er Vorrang; lokale Regeln dürfen ihn verschärfen, nicht stillschweigend abschwächen.

- **Frozen Current Plan:** Laufenden freigegebenen Plan nicht durch neue Ideen erweitern; Neues in die nächste Iteration einordnen.
- **Conflict Gate:** Unterbrechen nur bei nachgewiesenem Konflikt mit Planvoraussetzung, Sicherheit, Ausgangs-SHA, Scope oder Invariant.
- **Single Writer:** Pro produktivem Scope nur ein autorisierter Executor; Analyse/Planung/Prüfung dürfen parallel lesen.
- **SHA + Scope:** Vor Mutation HEAD und erlaubten/verbotenen Scope prüfen; keine stillen Nebenrefactorings.
- **Evidence:** Kein PASS ohne echten Test; Evidence muss zum geprüften HEAD gehören.
- **Controlled Evidence Lab:** Echte Mutationen, Fehler-Injektion und Recovery-Tests nur in isolierten Testbereichen; Produktivdaten bleiben geschützt.
- **Next Queue:** Neue Anforderungen/Findings append-only erfassen und Beziehungen wie BLOCKS, REQUIRES, SUPERSEDES, DUPLICATE oder CONFLICTS dokumentieren.
- **Statusklarheit:** OBSERVED/SUSPECTED/REPRODUCED/CONFIRMED/DISPROVED nicht vermischen.
- **Recovery Key:** Nach Abbruch oder Agentenwechsel müssen Stand, Ziel, Frozen Plan, Scope, Findings, Gates und nächster erlaubter Schritt ohne alten Chat rekonstruierbar sein.
- **Traceability:** Requirement/Decision → Finding → Plan → Change → Test/Evidence → Gate/Checkpoint nachvollziehbar halten.
- **Negativtests:** Schutzmechanismen absichtlich gegen falschen SHA, zweiten Writer, Scope-Verstoß und unbelegtes PASS testen.
- **Sichtbarer Fortschritt:** Längere Prüfungen mit Schritt, Fortschritt, Ergebnis und Ampelstatus darstellen.

Leitsatz: **Kein Agent muss sich erinnern. Kein Agent darf raten. Keine Änderung verliert ihren Ursprung. Kein PASS existiert ohne Evidence.**
