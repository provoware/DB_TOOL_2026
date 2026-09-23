# PROVOWARE DB TOOL 2026 – Einstieg ohne Fachwissen

Diese Seite erklärt den Projektstand in Alltagssprache.

## Worum geht es?

Das Programm soll Daten übersichtlich in drei Ebenen verwalten:

**Kategorie → Eintrag → Feld**

Beispiel:

```text
Werkzeuge
└── Akkuschrauber
    ├── Hersteller
    ├── Kaufdatum
    └── Notiz
```

Später sollen solche Daten bequem über eine verständliche Oberfläche angelegt, gefunden, geändert und abgesichert werden können.

## Was kann ich aktuell erwarten?

Das Projekt befindet sich noch in Entwicklung.

Bereits vorhanden sind technische Grundlagen und mehrere geprüfte Nur-Lese-Bereiche. Zusätzlich gibt es einen ersten Browser-Maskenbaukasten mit Komponentenpalette, 12-Spalten-Raster und Vorschau.

**Noch nicht freigegeben ist in diesem Maskenbaukasten:**
- dauerhaftes Speichern,
- Schreiben in die Datenbank,
- produktive Änderung vorhandener Daten.

Das ist Absicht. Neue Bedienfunktionen werden erst isoliert geprüft und erst danach mit dem Datenkern verbunden.

## Was bedeuten die Statusfarben?

- 🟢 **GRÜN:** alle für diesen Schritt notwendigen Prüfungen bestanden.
- 🟡 **GELB:** kein bestätigter Fehler, aber eine notwendige Prüfung fehlt oder ist blockiert.
- 🔴 **ROT:** ein Fehler, eine Regression oder eine Schutzverletzung wurde gefunden.
- 🔒 **FROZEN:** dieser Bereich ist geschützt und darf nicht nebenbei verändert werden.

## Was muss ich als normaler Nutzer nicht lesen?

Diese Bereiche sind hauptsächlich für Entwicklung und Prüfung gedacht:

- `.provoware/`
- `.github/`
- `tests/`
- `docs/development/`
- `AGENTS.md`

Sie dürfen im Repository bleiben. Für die normale Bedienung sind sie nicht gedacht.

## Welche Datei ist für mich wichtig?

Beginne mit `README.md` und dieser Datei.

Wenn später ein freigegebener Ein-Klick-Start vorhanden ist, wird er hier eindeutig beschrieben. Bis dahin behandelt das Projekt Startwege als Entwicklungsfunktion und verspricht keinen fertigen Produktstart.

## Warum ist das so streng?

Das Projekt soll lieber einen Schritt später freigeben als bestehende Daten oder einen stabilen Datenbankkern unbemerkt zu beschädigen.

Darum gilt:

**kleine Änderung → passende Prüfung → Gate → erst dann nächster Schritt**
