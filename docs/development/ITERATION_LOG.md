# Entwicklerprotokoll

## Pflicht pro Iteration

- Iterationsnummer
- Ziel
- betroffene Dateien
- neue/geänderte/gelöschte Dateien
- Tests
- Gate-Status
- offene Findings
- nächste Empfehlung

## Screenshot-Pflicht

Alle 5 Iterationen wird zusätzlich dokumentiert:

- Screenshot-Pfad
- Auflösung / Viewport
- Theme
- Kurzfazit
- visuelle Regression: ja/nein
- offene UI-Probleme

### Vorlage

```text
Iteration: 0005
Screenshot: docs/development/screenshots/iteration-0005/main-1440x900.png
Theme: Neon Violet
Fazit:
- Layout stabil
- Fokus klar
- keine Überlagerungen
- Kontrast ausreichend
- keine Regression zum letzten Referenzstand
```

## Iteration 0005 – CP-07H Browser-Referenz

- Ziel: erster verbindlicher Chromium-Screenshot
- Viewport: 1440 × 900
- Theme: Neon Violett
- Screenshot: `docs/development/screenshots/iteration-0005/main-1440x900.png`
- Browserprüfung: 3 Panels / 14 Buttons / Rendering erfolgreich
- Gate: 🟢 GRÜN
- Visuelle Regression: Baseline erstellt; noch kein Vorgänger vorhanden
- Kurzfazit: Layout stabil und klar; technische Feldtyp-Bezeichnungen später lokalisieren.
- Nächste Empfehlung: erst bei konkretem Responsive-Befund zusätzliche Viewports rendern.


## Iteration 0010 – echter CatalogService-Web-Lesepfad

- Ziel: unveränderten CatalogService read-only bis in die HTML-Oberfläche verbinden
- Produkt-Scope: 5 eingefrorene Core-Dateien, M-Budget
- Validierung: Compile + SHA/Git-Blob-Identität + echter Read-Integrationstest
- Integrationstest: 🟢 2 / 2 mit `-W error`
- Webgrenze: nur `list_categories`, `list_entries`, `list_fields`
- Direkter Web-SQL-Zugriff: 0
- Web-Schreib-API: 0
- Screenshot: `docs/development/screenshots/iteration-0010/main-1440x900-preview.jpg`
- Original-Viewport: 1440 × 900
- Original-PNG SHA-256: `dc4ddd69e4efc44f8c22b5b65d9fb71c7d93af332a91826d6fe9a1499fdeacc9`
- Browserprüfung: 3 Kategorien / 3 Einträge / 3 Felder / 3 Panels / 14 Buttons
- Gate: 🟢 lokal GRÜN; GitHub-CI separat nach Commit geprüft
- Visuelle Regression: keine sichtbare Regression gegenüber Iteration 0005
- Offenes UX-Finding: 🟡 technische Feldtyp-Bezeichnungen später lokalisieren
- Repo-Finding: 🟡 gestapelte/duplizierte PR-Kette nach diesem Checkpoint konsolidieren


## Iteration 0020 – realer Chromium-Such-/Navigations-Gate

- Ziel: den in Iteration 19 gemergten Nur-Lese-Suchpfad im echten Chromium inklusive Navigation, Tastatur, Leerzustand und Browser-Konsole abnehmen
- Validierter Head: `afd5f5a85b824b17d009fd4bbab531cb503fe0d6`
- Chromium: 152.0.7977.82 / Linux
- Viewport: 1440 × 900
- Screenshot: `docs/development/screenshots/iteration-0020/main-1440x900-preview.jpg`
- Evidence: `docs/development/screenshots/iteration-0020/iteration-20-evidence.json`
- Workflow-Run: `35455431882`
- Browserprüfung: 🟢 Start / Nur-Lese / Kategorie → Eintrag → Felder / 3 Suchpfade / Leerzustand / Tastatur / Enter-Suche
- Browser-Konsole: 🟢 0 SEVERE
- Konkreter Produktbefund: erster Lauf meldete ausschließlich `/favicon.ico → 404`; minimal auf `204 No Content` behoben und gezielt regressionsgetestet
- Test-Harness: Value-Tabellen ergänzt; alte technische Erwartung `text · Pflichtfeld` an bereits eingefrorene Lokalisierung `Text · Pflichtfeld` angepasst
- CP-03 / Schema / Migrationen / Frozen Core: unverändert
- Full Suite: nicht ausgeführt
- Gate: 🟢 GRÜN / `FROZEN_I20`
- Visuelle Regression: keine blockierende Regression gegenüber Iteration 0015; Drei-Stufen-Layout stabil
- Offene Findings: keine für Iteration 20
- Nächste Empfehlung: PR #27 nur noch auf die durch diesen Evidence-/Freeze-Commit ausgelösten Gates prüfen und bei komplett Grün squash-mergen.
