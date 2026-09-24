# PROVOWARE DB TOOL 2026 – Master TODO

Diese Liste ist der Implementierungspool zur Produkt-Roadmap. Checkboxen bedeuten **Planungsstatus**, nicht automatische Freigabe.

## A. Masken-Baukasten – Eigenschaften

- [ ] Beschriftung temporär editieren (I104 ist bereits geplant)
- [ ] Label-Edit: Leerwert, Escape, Fokus, 200-%-Evidence
- [ ] Hilfetext temporär editieren
- [ ] Hilfetext mit zugänglicher Beschreibung verbinden
- [ ] Pflichtfeld-Eigenschaft im Draft
- [ ] Datentyp-Eigenschaft im Draft
- [ ] typabhängigen Standardwert validieren
- [ ] Auswahloptionen hinzufügen/entfernen/neuordnen
- [ ] statische Sichtbarkeit
- [ ] Breite im 12-Spalten-Raster ändern
- [ ] gemeinsame Eigenschaften-Vorschau
- [ ] gemeinsame 100/150/200-%-Accessibility-Evidence
- [ ] Persistenzgrenze für Masken separat planen

## B. Masken-Baukasten – Struktur

- [ ] Element duplizieren bei neuer monotone Draft-ID
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
- [ ] Screenreader-Semantik
- [ ] gespeicherte Darstellungsprofile
- [ ] automatisierte Evidence 100/150/200 %
- [ ] Desktop/Tablet/schmal ohne horizontalen Overflow

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

## N. Globale Gates

- [ ] kein Feature direkt aus dieser TODO-Liste implementieren, ohne Iterationsmanifest
- [ ] pro Iteration genau zwei abhängige Schritte planen
- [ ] Zwischen-Gate nach Schritt 1
- [ ] triggerbasierte Tests
- [ ] Frozen-Core-Schutz
- [ ] keine ungeplanten Dateien
- [ ] reale Chromium-Evidence bei vorgesehenem UI-Meilenstein
- [ ] Persistenz nur mit Recovery-/Integritätsvertrag
