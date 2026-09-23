# Iteration 88 - Datenbank-Masken-Baukasten Foundation

## Ziel

I88 startet den Masken-Baukasten als eigenes Modul, ohne CP-03, Schema, bestehende Repositories oder Writer zu verändern.

Die Iteration besitzt genau zwei gekoppelte Schritte:

1. Modell + Validierung + deterministischer ApplicationPlan.
2. Erst nach grünem Zwischen-Gate: atomarer JSON-Vorlagenspeicher mit Versions-/Korruptionsschutz.

## Schritt 1

Die Vorlage ist strikt vom späteren Datenbankeintrag getrennt. Sie enthält:

- versionierte Vorlagenidentität,
- Felddefinitionen auf Basis der vorhandenen FieldType-Werte,
- ein festes 12-Spalten-Raster,
- Eingabefelder und Hilfselemente,
- eindeutige Feldbindungen,
- Kollisions- und Rasterprüfung.

build_application_plan() erzeugt ausschließlich einen deterministischen Plan. Es werden keine Datenbankeinträge angelegt und keine Writer aufgerufen.

## Nutzerfehler, die bereits abgefangen werden

- Elemente außerhalb des Rasters,
- überlappende Elemente,
- doppelte Element-IDs,
- doppelt gebundene Felder,
- unbekannte Feldbindungen,
- nicht platzierte Felddefinitionen,
- ungültige Auswahloptionen,
- unpassende Währungscodes,
- inkompatible Vorlagen-Dateiversionen.

Alle Fehler sind explizit und fail-closed.

## Freeze-Schutz

Unverändert bleiben CP-03, CP-06, Schema/Migrationen, bestehende Repositories, CatalogService, TUI/Web-Runtimes und Writer.

## Zwischen-Gate

Nur Compile + fokussierter Modellvertrag. Schritt 2 startet ausschließlich bei Grün.

## Geplanter Schritt 2

Ein MaskTemplateStore speichert validierte Vorlagen atomar als JSON außerhalb der autoritativen Datenbank. Er verhindert stille Versionsüberschreibung und lehnt beschädigte oder inkompatible Vorlagen ab.

## Danach

Erst nach I88 folgt der Browser-Editor mit Drag & Drop, Resize, Snap-to-Grid, Tastaturalternative, Undo/Redo, Vorschau und Vorlagenmenü.
