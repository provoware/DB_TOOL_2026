# Iteration 55 – EntryFieldWriteAdapter Integrationsentscheidung

## Zweck

I55 entscheidet ausschließlich, **wie** der in I54 eingefrorene `EntryFieldWriteAdapter` später sicher in die TUI eingebunden werden könnte.

Es wird kein Runtime-Code geändert und CP-07T wird nicht reopened.

## Ausgangslage

Die aktuelle Runtime besitzt bereits zwei relevante Muster:

1. Kategorie → Eintrag wird über stabile IDs geladen.
2. Beim Anlegen eines Eintrags wird die Parent-Kategorie beim Start des Befehls in `_entry_create_category_id` festgehalten.

Dieses zweite Muster ist die richtige Vorlage für eine spätere Feldanlage.

## 1. Parent-Provenienz: entry_id beim Start einfrieren

Eine spätere Feldanlage darf die Entry-ID **nicht erst beim Submit** aus dem aktuellen Listenindex ableiten.

Stattdessen muss beim Start des Create-Kommandos:

1. der aktuell ausgewählte Eintrag validiert werden;
2. exakt dessen `NavItem.id` erfasst werden;
3. diese ID bis Erfolg oder Abbruch stabil bleiben.

Konzeptionell:

`selected entry → captured entry_id → type selection/name input → submit`

Wenn der Nutzer während des Eingabemodus die sichtbare Auswahl verändert, darf das den erfassten Parent nicht verändern.

## 2. FieldType: keine Freitexteingabe

`FieldType` ist ein Domain-`StrEnum`.

Eine spätere UI darf deshalb keine beliebigen Strings an den Adapter übergeben.

Zulässig ist nur eine explizite Auswahl, die intern direkt auf einen bekannten `FieldType` abbildet.

### Erste sichere Typmenge

Für einen ersten möglichen TUI-Reopen sind nur Typen sinnvoll, die mit dem aktuellen I54-Vertrag vollständig angelegt werden können:

- `TEXT`
- `LONG_TEXT`
- `INTEGER`
- `DECIMAL`
- `DATE`
- `DATETIME`
- `BOOLEAN`

### Noch geschlossen

#### MONEY

`FieldDefinition.new(...)` verlangt für `MONEY` zusätzlich einen dreistelligen `currency_code`.

Der I54-Adapter exponiert bewusst nur:

- `entry_id`
- `name`
- `field_type`

Damit ist `MONEY` über diesen Vertrag noch nicht vollständig beschreibbar und bleibt für eine erste TUI-Feldanlage gesperrt.

#### SINGLE_CHOICE / MULTI_CHOICE

Diese Felddefinitionen könnten technisch erzeugt werden, wären für Laien aber ohne Options-Writes nicht sinnvoll vollständig konfigurierbar.

Da Choice-Option-Writes weiterhin geschlossen sind, bleiben auch diese Typen aus einer ersten TUI-Anlage ausgeschlossen.

## 3. Interaktionsfolge

Eine spätere Integration sollte genau einen kontrollierten Create-Modus besitzen:

1. Entry auswählen.
2. Feld-anlegen-Kommando starten.
3. `entry_id` sofort erfassen.
4. Feldtyp explizit aus sicherer Typmenge auswählen.
5. Feldname eingeben.
6. genau einmal `EntryFieldWriteAdapter.create_entry_field(entry_id, name, field_type)` aufrufen.
7. bei Erfolg nur die Felder des erfassten Eintrags neu lesen.
8. bei Fehler Eingabestatus, Parent-ID und Typauswahl beibehalten.
9. Escape verwirft Namen, Typ und Parent-ID ohne Write.

I55 entscheidet noch **nicht**, ob Typ oder Name zuerst abgefragt werden. Diese Detail-UX kann im späteren Reopen minimal gewählt werden, solange die Provenienzregeln eingehalten werden.

## 4. Refresh nach Erfolg

Die zurückgegebene `FieldDefinition` darf nicht direkt in die sichtbare `field-list` injiziert werden.

Stattdessen muss nach Erfolg dieselbe read-only Quelle verwendet werden, die bereits für normale Feldanzeige gilt:

`TuiDataPort.fields(captured_entry_id)`

Begründung:

- die Darstellung bleibt zentral über `FieldRow`;
- keine Domain-Objekte gelangen direkt in die Runtime-Darstellung;
- Sortierung und Sichtbarkeitsregeln bleiben identisch;
- zukünftige Mapping-Änderungen bleiben auf der Read-Seite gekapselt.

Der Refresh soll ausschließlich die Feldliste des erfassten Eintrags neu laden.

Kategorie- und Entry-Listen dürfen dabei nicht vollständig neu geladen werden.

## 5. Fokusvertrag

### Start

Wenn kein Entry ausgewählt ist:

- kein Write-Modus;
- verständlicher Status;
- Fokus auf `entry-list` bzw. den nächst sinnvollen Navigationsbereich.

### Während Eingabe

Der jeweils aktive Create-Control behält Fokus.

### Fehler

Bei Domain-/Validation-Fehler:

- kein Refresh;
- kein zweiter Write;
- Parent-ID bleibt erhalten;
- ausgewählter FieldType bleibt erhalten;
- Fokus bleibt beim aktiven Create-Control.

### Erfolg

Nach erfolgreichem Refresh:

- der erfasste Eintrag bleibt ausgewählt;
- die Feldliste wird aus `TuiDataPort.fields(entry_id)` neu aufgebaut;
- Fokus geht auf die Feldliste, wenn Felder vorhanden sind;
- alternativ zurück auf die Entry-Liste, falls der Read-Port wider Erwarten leer liefert.

### Abbruch

Escape:

- kein Write;
- Create-Control schließen;
- erfasste `entry_id` löschen;
- FieldType-Auswahl löschen;
- Fokus zurück auf den ursprünglichen Entry.

## 6. Minimal notwendiger späterer Runtime-State

Ein späterer Reopen benötigt höchstens:

- optionalen `EntryFieldWriteAdapter`;
- eine erfasste `entry_id`;
- einen erfassten `FieldType`;
- temporäre Controls für Typ und Name.

Kein Repository, SQL oder CatalogService darf in die Runtime gelangen.

## 7. Pflichtregressionen für einen späteren Reopen

Mindestens zu prüfen:

- read-only Konstruktion ohne Field-Writer bleibt unverändert;
- kein ausgewählter Entry → kein Write;
- Parent-ID wird beim Start erfasst;
- Änderung des sichtbaren Entry-Index während Create ändert Parent nicht;
- nur erlaubter `FieldType` wird transportiert;
- genau ein Write;
- Erfolg refresht nur `fields(captured_entry_id)`;
- Fehler refresht nichts;
- Fehler behält Parent, Typ und Fokus;
- Escape schreibt nichts und löscht transienten State;
- bestehende Kategorie-/Entry-Navigation bleibt unverändert;
- MONEY und Choice-Typen sind im ersten Reopen nicht auswählbar.

## 8. Reopen-Entscheidung

I55 begründet, dass ein späterer enger CP-07T-Reopen **technisch möglich** ist.

Er ist aber erst dann zulässig, wenn:

1. I55 eingefroren ist;
2. der geplante Wartbarkeits-Scope I56 abgeschlossen ist;
3. eine eigene Folgeiteration den Reopen ausdrücklich auf die oben beschriebenen Grenzen festlegt.

## 9. I56-Vormerkung

Vor einem Runtime-Reopen soll I56 ausschließlich inventarisieren:

- wiederholte UI-Texte;
- echte Helper-Duplikate;
- mögliche Capability-Grenzen.

I56 darf keine breite Registry einführen, nur weil Wiederverwendung grundsätzlich möglich wäre.

## Ergebnis

Eine spätere Feldanlage ist sicher integrierbar, wenn:

**stabile entry_id + expliziter sicherer FieldType + genau ein Adapter-Write + Read-Port-Refresh + deterministischer Fokus**

streng getrennt bleiben.

Value-/Choice-Writes bleiben geschlossen.
