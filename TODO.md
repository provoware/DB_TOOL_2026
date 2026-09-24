# PROVOWARE DB TOOL 2026 – Master TODO

Stand: **nach I116 auf `main`**.

Diese Liste ist der Implementierungspool zur Produkt-Roadmap. Ein Haken bedeutet: der Punkt ist im bestätigten Produktstand umgesetzt. Ein offener Punkt ist **keine automatische Freigabe** zur Implementierung.\n\n**Fortschritt A–M:** **15 von 132 = 11,4 %**. Die Prioritätenliste unten spiegelt vorhandene TODOs nur und wird nicht zusätzlich gezählt.\n\n**Bestätigte Härtung:** I115 reparierte die Browser-JavaScript-Newline-Regressionsstelle und die Fokus-Rückgabe beim Choice-Reorder; Targeted + Foundation waren grün.

## Nächste sichere Prioritäten

1. [ ] Breite im 12-Spalten-Raster ändern, Grenzen vor Mutation prüfen
2. [ ] vollständige 100/150/200-%-Evidence und gemeinsame Accessibility-Abnahme
3. [ ] `defaultSelection`-Vertrag separat planen
4. [ ] Persistenzgrenze für Masken separat planen

Bis dahin bleiben **Persistenz, `defaultSelection`, CP-03 und CP-06 geschlossen**.

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
- [ ] vollständige 100/150/200-%-Evidence für die gesamte Eigenschaftenbearbeitung
- [x] statische Sichtbarkeit
- [ ] Breite im 12-Spalten-Raster ändern
- [ ] gemeinsame Eigenschaften-Vorschau vollständig abnehmen
- [ ] `defaultSelection`-Vertrag separat planen
- [ ] Persistenzgrenze für Masken separat planen

## B. Masken-Baukasten – Struktur

- [ ] Element duplizieren bei neuer monotoner Draft-ID
- [ ] kontrolliertes Neuordnen ohne Drag-and-drop-Zwang
- [ ] Abschnitte
- [ ] einklappbare Gruppen
- [ ] explizite Tab-Reihenfolge
- [ ] Desktop-Vorschau
- [ ] Tablet-Vorschau
- [ ] schmale Vorschau
- [ ] Raster-Assistent als read-only Vorschlag
- [ ] Übernahme eines Rastervorschlags mit Vorher/Nachher

## C. Datenarbeit

- [ ] Suche
- [ ] Filter
- [ ] Sortierung
- [ ] starke Detailansicht
- [ ] globale Suche Kategorie → Eintrag → Feldwert
- [ ] Fundstelle eindeutig anzeigen
- [ ] Favoriten
- [ ] zuletzt verwendet
- [ ] gespeicherte Ansichten
- [ ] Mehrfachauswahl
- [ ] Preview für Massenaktionen

## D. Regeln und Validierung

- [ ] gemeinsames Regelmodell planen
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
