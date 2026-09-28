# PROVOWARE DB TOOL 2026 – Master TODO

Stand: **I167 auf diesem Branch, Basis I166**. I167 implementiert die browserlokale Pflichtwert-Preview mit zugänglichen Tooltips; Pflichtwert und Regel-Preview bleiben bis zur realen Chromium-/Screenshot-Abnahme offen.

Diese Liste ist der Implementierungspool zur Produkt-Roadmap. Ein Haken bedeutet: der Punkt ist im bestätigten Produktstand umgesetzt. Ein offener Punkt ist **keine automatische Freigabe** zur Implementierung.

**Fortschritt A–M:** **40 von 132 = 30,3 %**. Die Prioritätenliste unten spiegelt vorhandene TODOs nur und wird nicht zusätzlich gezählt.

**Bestätigter Produktstand:** I167 enthält die Pflichtwert-Preview für temporäre Draft-Felder. Statische Vertragsprüfungen sind grün; das UI-Gate ist mangels Chrome-/Chromium-Binary noch blockiert. Persistenz und offene Datenarbeitsfunktionen bleiben separat geschützt.

## Nächste sichere Prioritäten

1. [ ] D · I167-Pflichtwert-Preview mit realem Chromium und Screenshot abnehmen.
2. [ ] Danach Pflichtwert und Regel-Preview vor Aktivierung gemeinsam schließen.
3. [ ] Weitere Regelarten sowie C · persistenzabhängige Datenarbeit bleiben bis zu eigenen Verträgen blockiert.

**Persistenz, CP-03 und CP-06 bleiben geschlossen.** Der Strukturblock B ist auf I146 eingefroren.


## Bestätigter Governance-Stand

Control Plane V2 ist bis **I124** vollständig als **Shadow-Vertrag** vorhanden, bleibt aber ausdrücklich **nicht autoritativ**. Die bestehende Governance bleibt maßgeblich.

- I120: Registry, Rollen-, Trigger- und Lifecycle-Verträge
- I121: versiegelter Plan, globaler Single-Writer-Lease und Validierungsvertrag
- I122: triggerbasierte read-only Inspektion, Findings und Planner-Intake
- I123: Controller-Sealing sowie append-only Event-/Audit-Kette
- I124: Finalizer, Lease-Release und immutable Outcome-Bindung

Diese Governance-Arbeit verändert weder Browser-Produktfunktionen noch Persistenz, CP-03 oder CP-06 und wird deshalb **nicht** in den 17/132 Produktpunkten A–M mitgezählt.

## A. Masken-Baukasten – Eigenschaften

- [x] Beschriftung temporär editieren
- [x] Label-Edit: Leerwert, Escape und Fokus-Rückgabe absichern
- [x] Hilfetext temporär editieren
- [x] Hilfetext mit zugänglicher Beschreibung verbinden
- [x] Pflichtfeld-Eigenschaft im Draft
- [x] Datentyp-Eigenschaft im Draft
- [x] typabhängigen skalaren Standardwert validieren
- [x] Choice-Datentypen `single_choice` und `multi_choice` browserlokal ergänzen
- [x] Auswahloptionen hinzufügen
- [x] Auswahloptionen entfernen
- [x] Auswahloptionen deterministisch neuordnen
- [x] stabile monotone `draft-option-*`-IDs beibehalten
- [x] Option-Controls: zugängliche Namen, Live-Status und Fokus-Rückgabe
- [x] Option-Controls in schmaler Darstellung erreichbar halten
- [x] vollständige 100/150/200-%-Evidence für die gesamte Eigenschaftenbearbeitung
- [x] statische Sichtbarkeit
- [x] Breite im 12-Spalten-Raster ändern
- [x] gemeinsame Eigenschaften-Vorschau vollständig abnehmen
- [x] `defaultSelection`-Vertrag planen und browserlokal umsetzen
- [x] Persistenzgrenze für Masken separat planen

## B. Masken-Baukasten – Struktur

- [x] Element duplizieren bei neuer monotoner Draft-ID
- [x] kontrolliertes Neuordnen ohne Drag-and-drop-Zwang
- [x] Abschnitte
- [x] einklappbare Gruppen
- [x] explizite Tab-Reihenfolge
- [x] Desktop-Vorschau
- [x] Tablet-Vorschau
- [x] schmale Vorschau
- [x] Raster-Assistent als read-only Vorschlag
- [x] Übernahme eines Rastervorschlags mit Vorher/Nachher

## C. Datenarbeit

- [x] Suche
- [x] Filter
- [x] Sortierung
- [x] starke Detailansicht
- [x] globale Suche Kategorie → Eintrag → Feldwert
- [x] Fundstelle eindeutig anzeigen
- [x] Favoriten
- [ ] zuletzt verwendet
- [ ] gespeicherte Ansichten
- [x] Mehrfachauswahl
- [x] Preview für Massenaktionen

## D. Regeln und Validierung

- [x] gemeinsames Regelmodell planen
- [ ] Pflichtwert
- [ ] Zahlenbereich
- [ ] Datum von/bis
- [ ] erlaubte Dateitypen
- [ ] eindeutige Werte
- [ ] statische/bedingte Sichtbarkeit
- [ ] Feldabhängigkeiten
- [ ] laienverständliche Fehlertexte
- [ ] Regel-Preview vor Aktivierung

## E. Assistentenmodus

- [ ] Anforderungsbeschreibung entgegennehmen
- [ ] Kategorien vorschlagen
- [ ] Felder/Datentypen vorschlagen
- [ ] Layout vorschlagen
- [ ] Regeln vorschlagen
- [ ] Vorschlag rein temporär anzeigen
- [ ] Nutzerkorrektur ermöglichen
- [ ] Übernahme erst nach expliziter Bestätigung
- [ ] produktive Übernahme erst nach Persistenz-/Recovery-Gate

## F. Vorlagen

- [ ] Kontakte
- [ ] Inventar
- [ ] Rechnungsübersicht
- [ ] Musikarchiv
- [ ] Dokumentenverwaltung
- [ ] Gerätebestand
- [ ] Projekte
- [ ] Termine
- [ ] freie Sammlung
- [ ] Kopieren-statt-Referenzvorlage-verändern erzwingen

## G. Sicherheit / Recovery

- [ ] gemeinsame Simulation
- [ ] Vorher-/Nachher-Vorschau
- [ ] Undo
- [ ] Redo
- [ ] Papierkorb
- [ ] Änderungsjournal
- [ ] Wiederherstellungspunkte
- [ ] Recovery
- [ ] Grün/Gelb/Rot für kritische Aktionen
- [ ] Crash-/Abbruchfälle testen

## H. Import / Export

- [ ] CSV-Export
- [ ] JSON-Export
- [ ] CSV-Import lesen
- [ ] Spaltenmapping-Vorschau
- [ ] fehlerhafte Zeilen separat ausweisen
- [ ] Import-Simulation
- [ ] bestätigter Import
- [ ] JSON-Import
- [ ] Tabellenformat später separat bewerten

## I. Anhänge

- [ ] Speichervertrag festlegen
- [ ] Größenlimits
- [ ] erlaubte Dateitypen
- [ ] Pfad-/Traversal-Schutz
- [ ] Backup/Restore-Vertrag
- [ ] fehlende Anhänge behandeln
- [ ] Bilder
- [ ] PDF
- [ ] Text
- [ ] weitere Dateitypen nur nach Freigabe

## J. Dashboard

- [ ] Anzahl Einträge
- [ ] zuletzt geändert
- [ ] offene Aufgaben
- [ ] Speicherbedarf
- [ ] einfache Diagramme
- [ ] Dashboard-Ansichten
- [ ] gleiche Query-/Datenverträge wie Hauptanwendung

## K. Accessibility

- [ ] Schriftgrößenregler
- [ ] Sehschwachenmodus
- [ ] hoher Kontrast
- [ ] Reduced Motion
- [ ] vollständige Tastaturmatrix
- [ ] Screenreader-Semantik als Gesamtmatrix
- [ ] gespeicherte Darstellungsprofile
- [ ] automatisierte Evidence 100/150/200 %
- [ ] Desktop/Tablet/schmal ohne horizontalen Overflow als Gesamtmatrix

Bereits vorhanden und weiterhin regressionsgeschützt: native Tastaturwege, sichtbarer Fokus, Live-Status und schmale Bedienbarkeit in mehreren Browser-Draft-Slices.

## L. Gesundheit / Wartung

- [ ] Datenbankstatus
- [ ] letzte Sicherung
- [ ] freier Speicher
- [ ] Integritätsprüfung
- [ ] Version
- [ ] letzte erfolgreiche Prüfung
- [ ] reparierbar ja/nein
- [ ] technische Details aufklappbar

## M. Beziehungen

- [ ] Relationsmodell fachlich planen
- [ ] Person ↔ Projekt als Beispiel
- [ ] Künstler ↔ Album als Beispiel
- [ ] Gerät ↔ Reparatur als Beispiel
- [ ] CP-03-/CP-06-Impact-Analyse
- [ ] Migrationsplan
- [ ] Rollback
- [ ] Deep-Gate
- [ ] erst danach Implementierung

## N. Dauerregeln für jede Iteration

Diese Punkte sind keine einmaligen TODOs, sondern bleiben ständig aktiv:

- Iterationsmanifest vor Feature-Write
- pro Iteration kleine abhängige Schritte
- Zwischen-Gate, wenn ein späterer Schritt vom ersten abhängt
- triggerbasierte statt unnötige Volltests
- Frozen-Core-Schutz
- keine ungeplanten Dateien
- reale Chromium-Evidence an vorgesehenen UI-Meilensteinen
- Persistenz nur mit geklärtem Recovery-/Integritätsvertrag
- bei rotem Gate zuerst die konkrete Ursache beheben
