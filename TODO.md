# PROVOWARE DB TOOL 2026 – Master TODO

Stand: **I148 auf Feature-Branch, Basis I147 auf `main`**. I148 nimmt die vorhandene Read-only-Suche end-to-end ab und repariert ausschließlich die Navigation eintragsspezifischer Feldtreffer; I127 schließt die gemeinsame Eigenschaften-/Preview-Abnahme als Regression/Evidence, während I120–I124 ausschließlich Control-Plane-V2-Shadow-Governance bleiben.

Diese Liste ist der Implementierungspool zur Produkt-Roadmap. Ein Haken bedeutet: der Punkt ist im bestätigten Produktstand umgesetzt. Ein offener Punkt ist **keine automatische Freigabe** zur Implementierung.

**Fortschritt A–M:** **35 von 132 = 26,5 %**. Die Prioritätenliste unten spiegelt vorhandene TODOs nur und wird nicht zusätzlich gezählt.

**Bestätigter Produktstand:** I156 projiziert eindeutige Fundstellen für bestehende Suchtreffer; I155 ergänzt die starke GET-only Detailansicht mit stabilen Detail-/Feldankern; I154 plant die globale Feldwertsuche separat auf Basis des I153-Fundstellenvertrags; I153 plant den eindeutigen Fundstellenvertrag getrennt von der späteren Feldwertsuche; I151 inventarisiert die starke Detailansicht ohne Runtime-Änderung; I150 ergänzt eine explizite GET-only Titel-Sortierung A–Z/Z–A und erhält den Filterzustand; I149 ergänzt den kleinsten GET-only Titel-Filter für Einträge innerhalb der gewählten Kategorie; I148 bestätigt die bestehende GET-only Suche von Service bis Ergebnisnavigation; eintragsspezifische Feldtreffer erhalten für sichere Navigation nun ihre Eltern-Kategorie. I147 friert den vollständig erledigten Strukturblock B auf dem I146-main-Stand ein. I146 übernimmt einen bestätigten Rastervorschlag atomar in die flüchtige Zeile+Spalte-Layout-Map, mit Stale-Schutz, Fokus-Rückgabe und echter Chromium-Evidence; Draftdaten und Persistenz bleiben unverändert. I145 hält Rasterzeile und -spalte explizit in einer flüchtigen Browser-Layout-Map und rendert daraus, ohne Persistenz oder Vorschlagsübernahme. I144 stellt aktuelles und vorgeschlagenes Raster inklusive geplanter Zeilen-/Spaltenänderungen gegenüber, ohne zu mutieren. I143 ergänzt einen deterministischen read-only Raster-Assistenten ohne Übernahmeweg oder Persistenz. I142 nimmt Desktop 1152 px, Tablet 768 px und Schmal 360 px gemeinsam in realem Chromium auf Fokus, Umschaltung, Beschriftung, Overflow und Inhaltskonsistenz ab. I141 ergänzt den dritten browserlokalen Preview-Modus Schmal mit 360 px und erhält Desktop 1152 px sowie Tablet 768 px unverändert. I140 ergänzt einen browserlokalen Tablet-Modus mit 768 px und erhält I139 Desktop 1152 px als Standard. I139 ergänzt eine feste browserlokale Desktop-Vorschau mit 1152-px-Viewport. I138 ergänzt eine explizite natürliche Tab-Reihenfolge mit roving Tabstop für die Zielspalten. I137 ergänzt browserlokales Ein-/Ausklappen der I136-Vorschau-Abschnitte mit zugänglichem Toggle. I136 ergänzt semantische Vorschau-Abschnitte über den vorhandenen Bereich-Baustein. I135 ergänzt kontrolliertes browserlokales Neuordnen ganzer Draft-Elemente per Hoch/Runter-Controls. I133 ergänzt browserlokales Duplizieren mit neuen monotonen Draft- und Choice-Option-IDs sowie umgebundener `defaultSelection`. I132 liefert die Choice-Default-Basis; I120–I124 erweitern ausschließlich die nicht-authoritative Shadow-Governance.

## Nächste sichere Prioritäten

1. [ ] I157: Feldwertsuche ausschließlich im isolierten Deep-Gate-Labor beginnen; noch nicht an Service/Web produktiv anbinden.
2. [ ] Erst nach grünem Labor einen separaten Integrations-Slice planen.
3. [ ] Globale Suche bis zu Feldwerten und Fundstellen bleibt ein eigener späterer Vertrag.

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
- [ ] globale Suche Kategorie → Eintrag → Feldwert
- [x] Fundstelle eindeutig anzeigen
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
