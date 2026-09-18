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
