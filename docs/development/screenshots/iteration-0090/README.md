# Iteration 0090 – nachgetragener Chromium-Screenshot-Meilenstein

**Datum:** 2026-09-23  
**Viewport:** 1440 × 900  
**Browser:** Chromium 144.0.7559.96 auf Linux  
**Validierter Head:** `9e81c21fda3d5c629dec6526da12d0e1b7839ba2`  
**Theme:** aktueller Dark-Stand mit Cyan-/Lila-Akzenten  
**Produktcode geändert:** nein

## Anlass

Für Iteration 90 war nach der Repository-Regel ein visueller Fünfer-Meilenstein fällig. Der veraltete PR #95 hatte diesen Pflichtpunkt nicht erfüllt und wurde geschlossen. Diese Evidence schließt ausschließlich den fehlenden visuellen Nachweis gegen den aktuellen `main`.

## Realer Browserlauf

Der Stand wurde mit echtem Chromium bei exakt 1440 × 900 gerendert. Die Ausführungsumgebung blockiert Browser-Navigation zu `file://` und `localhost`; deshalb wurden die **unveränderten aktuellen** Dateien `src/provoware_db/web/templates/index.html` und `src/provoware_db/web/static/app.css` per Playwright `set_content()` an Chromium übergeben.

Das ist kein synthetisches Mockup: Chromium führt den realen HTML-/CSS-Layout- und Renderingpfad aus; lediglich der URL-Navigationsschritt entfällt wegen der Umgebungssperre.

## Evidence

- 🟢 Referenzgröße 1440 × 900
- 🟢 `NUR LESEN` sichtbar
- 🟢 drei Kernbereiche Kategorie / Eintrag / Felder sichtbar
- 🟢 `+ Neu`, `Bearbeiten`, `Undo`, `Papierkorb` deaktiviert
- 🟢 `Hilfe` bleibt verfügbar
- 🟢 kein horizontaler Overflow
- 🟢 Browser-Console-Errors: 0
- 🟢 CP-03 / CP-06 und Produktcode unverändert

## Screenshot

- Repository-Vorschau: `main-1440x900-preview.jpg` (komprimierte Vorschau des echten 1440×900-Laufs)
- Original-PNG SHA-256: `a17edba35a7f0087fe02c0d0917a3c910e438b2deb0390d451e2d7913515ab20`
- Preview-JPG SHA-256: `ffd222fc345130a6d108f79042bf8739f5261538f52d1453dba7ba72611f02d4`
- Maschinenlesbare Evidence: `iteration-90-evidence.json`

## Kurzfazit

Der aktuelle Nur-Lese-Webstand rendert bei 1440 × 900 ruhig und ohne abgeschnittene oder überlappende Kernbereiche. Die drei Arbeitsbereiche sind klar getrennt; die mutierenden Aktionen sind sichtbar deaktiviert.

## Visuelle Regression

Seit den Mask-Builder-Iterationen I88–I90 wurde der bestehende Web-Shell-Produktcode nicht verändert. Der Screenshot bestätigt den erwarteten aktuellen Stand.

**Blockierende visuelle Regression:** nein.

## Freeze

**Evidence:** 🟢 GRÜN  
**CP-03:** unverändert / geschützt  
**CP-06:** unverändert / geschützt  
**Schema/Migrationen:** unverändert  
**Produktcode:** unverändert
