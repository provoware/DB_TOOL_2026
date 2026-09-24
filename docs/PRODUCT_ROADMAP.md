# PROVOWARE DB TOOL 2026 – Produkt-Roadmap

Stand: nach I103 auf `main`.

Diese Roadmap bündelt den langfristigen Funktionspool. Sie ist **keine Freigabe, alle Punkte in einem Patch umzusetzen**. Jede Funktion erhält weiterhin eine kleine Iteration mit eigenem Scope, Zwischen-Gate und Freeze-Prüfung.

## 1. Zielbild

PROVOWARE soll sich für normale Anwender wie ein lokaler, sicherer No-Code-Datenbaukasten verhalten:

1. Datenmodell und Datenbanktechnik bleiben im Hintergrund.
2. Masken werden visuell aus Bausteinen aufgebaut.
3. Jede Änderung ist nachvollziehbar, validiert und möglichst reversibel.
4. Schreibende Funktionen werden erst nach Preview, Simulation und expliziter Freigabe geöffnet.
5. Tastatur, große Darstellung, Screenreader und ruhige Layouts sind Teil des Funktionsvertrags.
6. CP-03 und CP-06 bleiben geschützt, bis ein eigener Reopen-Plan mit Deep-Gate vorliegt.

## 2. Aktuelle belastbare Basis

Auf `main` ist bis I103 bestätigt:

- Komponentenpalette
- 12-Spalten-Canvas
- temporäre Platzierung
- deterministische Draft-IDs
- temporäres Entfernen
- temporäres Verschieben bei stabiler Draft-ID
- Blockierung ungültiger Rasterziele
- Escape-/Fokus-Verträge für Move
- deterministische Vorschau
- GET-only-/Loopback-only-Browser-Shell
- reale Chromium-Evidence bis 200-%-Zoom-Äquivalent
- weiterhin keine Persistenz des Browser-Drafts

## 3. Ausbauprinzip

Jede neue Capability wird vor Umsetzung einer Risikoklasse zugeordnet:

| Klasse | Bedeutung | Standard-Gate |
|---|---|---|
| A | rein temporär/read-only im Browser | gezielte UI-/Keyboard-Regression |
| B | Application-/Datenzugriff ohne Schemaänderung | Service-/Repository-Regression |
| C | persistente Produktänderung | Write-/Undo-/Recovery-/Integritäts-Gate |
| D | Schema, Beziehungen, Attachment-Speicher oder Frozen Core | expliziter Reopen + Impact-Analyse + Deep-Gate |

Ein Roadmap-Eintrag ist erst implementierbar, wenn seine direkten Abhängigkeiten grün sind.

## 4. Programmblöcke

### P1 – Masken-Eigenschaften

Ziel: Ein bereits platziertes Element schrittweise fachlich konfigurierbar machen.

Reihenfolge:

1. **Beschriftung**
   - temporär ändern
   - stabile Draft-ID
   - Preview sofort aktualisieren
   - Leerwert/Abbruch/Fokus härten
2. **Hilfetext**
   - rein browserintern beginnen
   - Screenreader-Zuordnung von Anfang an berücksichtigen
3. **Pflichtfeld**
   - semantische Kennzeichnung
   - noch keine Datenvalidierung erzwingen, solange das Regelmodul nicht freigegeben ist
4. **Datentyp**
   - Typauswahl nur für geeignete Elementarten
   - Typwechsel zunächst nur im Draft
5. **Standardwert**
   - typabhängige Validierung
6. **Auswahloptionen**
   - nur für Auswahltypen
   - Reihenfolge deterministisch
7. **Sichtbarkeit**
   - zunächst statisch sichtbar/verborgen
   - bedingte Sichtbarkeit erst im Regelmodul
8. **Breite**
   - Rastergrenzen vor Mutation prüfen
   - Move-/Preview-Verträge wiederverwenden

**Gate vor Persistenz:** Die temporären Eigenschaften müssen gemeinsam identitätsstabil, keyboard-first und bei 200 % bedienbar sein.

### P2 – Masken-Struktur und Layout

- Element duplizieren
- kontrolliert neuordnen
- Abschnitte
- einklappbare Gruppen
- definierbare Tab-Reihenfolge
- Desktop-/Tablet-/schmale Vorschau
- später Raster-Assistent mit Vorschlag statt automatischer stiller Änderung

Der Raster-Assistent darf zuerst nur Vorschläge erzeugen. Übernahme erst nach expliziter Bestätigung.

### P3 – Datenarbeit und Navigation

Read-only zuerst:

- Suche
- Filter
- Sortierung
- starke Detailansicht
- globale Suche Kategorie → Eintrag → Feldwert mit sichtbarer Fundstelle

Persistenzabhängig:

- Favoriten
- zuletzt verwendet
- gespeicherte Ansichten
- Mehrfachauswahl-Aktionen

Mehrfachauswahl erhält vor jeder schreibenden Massenaktion eine Vorschau und klare Anzahl betroffener Einträge.

### P4 – Regeln und Validierung

Ein gemeinsames Regelmodell statt verstreuter Sonderlogik:

- Pflichtwert
- Zahlenbereich
- Datum von/bis
- erlaubte Dateitypen
- eindeutige Werte
- bedingte Sichtbarkeit
- Abhängigkeiten zwischen Feldern

Fehlertexte müssen fachlich erklären:
- was nicht passt,
- wo der Fehler liegt,
- wie er behoben werden kann.

Keine kryptischen internen Exception-Texte in der normalen Oberfläche.

### P5 – Assistentenmodus

Der Nutzer beschreibt sein Ziel, zum Beispiel eine Adress- oder Musiksammlung.

Der Assistent erzeugt zunächst ausschließlich einen **Entwurf**:

- vorgeschlagene Kategorien
- Felder
- Datentypen
- Layout
- optionale Regeln

Ablauf:

`Beschreibung → Vorschlag → visuelle Prüfung → Änderungen → explizite Übernahme`

Keine automatische Datenbankänderung aus einem Sprachvorschlag.

### P6 – Vorlagen

Startvorlagen:

- Kontakte
- Inventar
- Rechnungsübersicht
- Musikarchiv
- Dokumentenverwaltung
- Gerätebestand
- Projekte
- Termine
- leere freie Sammlung

Regel: Vorlage wird **kopiert und angepasst**. Die Referenzvorlage bleibt unverändert.

### P7 – Sicherheit, Undo und Recovery

Gemeinsame Infrastruktur für spätere Schreibfunktionen:

- Simulation
- Vorher-/Nachher-Vorschau
- Undo/Redo
- Papierkorb
- Änderungsjournal
- Wiederherstellungspunkte
- Recovery
- Grün/Gelb/Rot-Klassifikation kritischer Aktionen

Dieser Block ist Voraussetzung für größere Massenänderungen, Import und produktive Assistentenübernahme.

### P8 – Import und Export

Reihenfolge:

1. CSV-Export
2. JSON-Export
3. CSV-Import mit Mapping-Vorschau
4. JSON-Import
5. Tabellenformate später nach eigener Dependency-/Sicherheitsentscheidung

Importvertrag:

`Datei lesen → Spalten erkennen → Zuordnung anzeigen → Fehler separat zeigen → Simulation → Bestätigung → Commit`

Fehlerhafte Zeilen dürfen nicht stillschweigend verworfen werden.

### P9 – Anhänge

Mögliche Anhänge:

- Bilder
- PDF
- Text
- weitere freigegebene Dateitypen

Vor Implementierung erforderlich:

- eigener Speichervertrag
- Größenlimits
- Dateitypprüfung
- Pfad-/Traversal-Schutz
- Backup-/Restore-Vertrag
- Verhalten bei fehlenden Dateien
- klare Entscheidung: eingebettet oder referenziert

Das ist Klasse D und darf CP-/Schema-Grenzen nicht nebenbei öffnen.

### P10 – Dashboard-Baukasten

Auf bestehenden Daten- und Query-Verträgen aufbauen:

- Anzahl Einträge
- zuletzt geändert
- offene Aufgaben
- Speicherbedarf
- einfache Diagramme
- gespeicherte Dashboard-Ansichten

Kein zweites paralleles Datenmodell.

### P11 – Accessibility-Profile

- Schriftgrößenregler
- Sehschwachenmodus
- hoher Kontrast
- Reduced Motion
- vollständige Tastatursteuerung
- Screenreader-Beschriftungen
- gespeicherte Darstellungsprofile

Die bestehende Chromium-Evidence wird schrittweise zu einer Matrix:

- 100 %
- 150 %
- 200 %
- Desktop
- Tablet
- schmal
- Tastatur
- Fokus
- horizontaler Overflow
- Screenreader-semantische Prüfungen

### P12 – Gesundheits- und Wartungsbereich

Laienansicht:

- Datenbank okay?
- letzte Sicherung
- verfügbarer Speicher
- Integritätsprüfung
- Programmversion
- letzte erfolgreiche Prüfung
- Problem automatisch reparierbar: ja/nein

Technische Details bleiben aufklappbar.

### P13 – Beziehungen zwischen Datensätzen

Beispiele:

- Person ↔ Projekt
- Künstler ↔ Album
- Gerät ↔ Reparatur

Vorbedingungen:

- stabile einfache Einträge
- stabile Masken
- geklärter Persistenzvertrag
- eigenes Relationsmodell
- Migrations-/Rollback-Konzept
- CP-03-/CP-06-Reopen nur mit separatem Deep-Gate

## 5. Empfohlene Umsetzungsreihenfolge

### Phase A – Browser-Draft vervollständigen
P1 Eigenschaften → P2 Struktur/Layout → P11 Accessibility-Härtung.

### Phase B – Read-only Datenkomfort
P3 Suche/Filter/Sortierung/Detail/globaler Fundpfad → P10 read-only Dashboard-Grundlage → P12 Health read-only.

### Phase C – Persistenz-Sicherheitsgrenze
P7 Simulation/Journal/Undo/Recovery als Voraussetzung für neue Schreibpfade.

### Phase D – Persistente Komfortfunktionen
gespeicherte Ansichten/Favoriten → Vorlagen → Assistentenübernahme → Import.

### Phase E – Hochrisiko-Erweiterungen
Anhänge → Beziehungen → weiterführende Automatisierung.

## 6. Architekturregeln

- UI führt kein SQL aus.
- Browser-Shell erhält keinen versteckten Persistenzpfad.
- Draft-Operationen mutieren nur die ausdrücklich freigegebene Eigenschaft.
- Identitäten werden bei Edit/Move nicht durch Remove+Recreate ersetzt.
- Preview und produktiver Commit verwenden später denselben validierten Plan.
- Mehrfach- und Importaktionen benötigen eine deterministische Operationsliste.
- Schemaänderungen sind eigene Iterationen.
- neue Runtime-Abhängigkeiten benötigen eine explizite Dependency-Entscheidung.
- jede schreibende Funktion benötigt einen nachvollziehbaren Recovery-Pfad.

## 7. Definition of Done pro Capability

Eine Capability gilt erst als fertig, wenn:

- Scope und Nicht-Scope dokumentiert sind,
- betroffene Dateien im Manifest stehen,
- gezielte Tests grün sind,
- kein BLOCKER/HIGH offen ist,
- Accessibility für betroffene UI geprüft ist,
- Preview/Fehlertexte deterministisch sind,
- Frozen Core unverändert blieb oder explizit reopened wurde,
- bei Persistenz Undo/Recovery/Integrität geklärt sind,
- Evidence und nächster Schritt dokumentiert sind.

## 8. Unverrückbare Schutzgrenzen

Bis zu einem eigenen Reopen-Plan bleiben verboten:

- beiläufige Änderung von CP-03
- beiläufige Änderung von CP-06
- Schemaänderung für Komfortfeatures
- stiller produktiver Browser-Write
- Drag-and-drop als Ersatz für Tastaturbedienung
- Massenänderung ohne Preview
- Import ohne Mapping-/Fehler-Vorschau
- Assistent, der ungeprüft Daten oder Schema schreibt
