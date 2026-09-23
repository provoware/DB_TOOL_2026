# Iteration 88 - Datenbank-Masken-Baukasten Foundation

## Ziel

I88 startet den Masken-Baukasten als eigenes Modul, ohne CP-03, CP-06, Schema, bestehende Repositories oder Writer zu verändern.

Die Iteration besitzt genau zwei gekoppelte Schritte:

1. Modell + Validierung + deterministischer ApplicationPlan.
2. Atomarer JSON-Vorlagenspeicher mit Versions- und Korruptionsschutz.

## Schritt 1 - GRÜN

Die Vorlage ist strikt vom späteren Datenbankeintrag getrennt. Sie enthält:

- versionierte Vorlagenidentität,
- Felddefinitionen auf Basis der vorhandenen FieldType-Werte,
- ein festes 12-Spalten-Raster,
- Eingabefelder und Hilfselemente,
- eindeutige Feldbindungen,
- Kollisions- und Rasterprüfung.

build_application_plan() erzeugt ausschließlich einen deterministischen Plan. Es werden keine Datenbankeinträge angelegt und keine Writer aufgerufen.

Der Zwischen-Gate-Lauf 49 war grün. Deshalb durfte Schritt 2 starten.

## Schritt 2

MaskTemplateStore speichert ausschließlich bereits validierte Vorlagen außerhalb der autoritativen Datenbank als JSON.

Sicherheitsregeln:

- Speicherung erfolgt über eine temporäre Datei und os.replace() im gleichen Verzeichnis.
- Bestehende Vorlagen dürfen nur mit explizit bekannter Vorversion ersetzt werden.
- Neue Versionen müssen streng größer sein.
- Veraltete Writer werden als Versionskonflikt abgewiesen.
- Beschädigte oder inkompatible JSON-Dateien werden fail-closed abgelehnt.
- Dateiname und gespeicherte Vorlagen-ID müssen übereinstimmen.
- Eine ungültige neue Vorlage erreicht den Dateischreibpfad nicht und ersetzt keine letzte gültige Version.

## Nutzerfehler, die bereits abgefangen werden

- Elemente außerhalb des Rasters,
- überlappende Elemente,
- doppelte Element-IDs,
- doppelt gebundene Felder,
- unbekannte Feldbindungen,
- nicht platzierte Felddefinitionen,
- ungültige Auswahloptionen,
- unpassende Währungscodes,
- inkompatible Vorlagen-Dateiversionen,
- stille Überschreibung einer neueren Vorlage,
- beschädigte Vorlagendateien,
- manipulierte Dateiname/Vorlagen-ID-Zuordnung.

## Freeze-Schutz

Unverändert bleiben CP-03, CP-06, Schema/Migrationen, bestehende Repositories, CatalogService, TUI/Web-Runtimes und Writer.

## Prüfstrategie

Schritt 1 wurde bereits gezielt grün geprüft und wird ohne relevante Codeänderung nicht unnötig wiederholt. Schritt 2 prüft ausschließlich Store-Compile, atomaren Roundtrip, Versionierung, Korruptionsschutz und unveränderte letzte gültige Version.

## Danach

Der nächste fachliche Slice ist der lokale Browser-Editor als eigenes UI des Masken-Baukastens:

- Komponentenpalette,
- 12-Spalten-Canvas,
- Drag & Drop,
- Resize und Snap-to-Grid,
- Tastaturalternative für Move/Resize,
- Undo/Redo,
- Eigenschaftenpanel,
- Live-Vorschau,
- Vorlagenmenü.

Auch dieser Editor bleibt zunächst vom produktiven Datenbank-Write-Lifecycle getrennt.
