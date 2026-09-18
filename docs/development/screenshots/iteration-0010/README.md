# Iteration 0010 – echter CatalogService-Browser-Referenzstand

**Datum:** 2026-09-18  
**Viewport:** 1440 × 900  
**Theme:** Neon Violett  
**Browser:** System-Chromium über Playwright  
**Datenquelle:** echter unveränderter `CatalogService` → echte Repositories → `WebCatalogReadAdapter` → HTML-Renderer  
**Original-PNG SHA-256:** `dc4ddd69e4efc44f8c22b5b65d9fb71c7d93af332a91826d6fe9a1499fdeacc9`  
**Repo-Vorschau:** [main-1440x900-preview.jpg](main-1440x900-preview.jpg)

## Deterministischer Browserlauf

- Kategorien: **3**
- Einträge: **3**
- Felder: **3**
- Arbeitsbereiche: **3**
- Buttons: **14**
- Seitentitel: `PROVOWARE DB TOOL 2026`
- `Akkuschrauber` sichtbar
- `Hersteller` sichtbar
- Rendering: erfolgreich

## Kurzfazit

🟢 Der reale Service-Lesepfad ist jetzt sichtbar bis in die Browseroberfläche durchgängig.  
🟢 Keine sichtbaren Überlagerungen oder abgeschnittenen Kernbereiche.  
🟢 Drei-Stufen-Struktur bleibt trotz realer Daten klar.  
🟢 Status- und Aktionsbereiche bleiben stabil.  
🟡 Feldtyptexte wie `single_choice` und `date` sind noch technische Bezeichnungen und sollten später laiengerecht lokalisiert werden.

## Vergleich zu Iteration 0005

Keine sichtbare Layoutregression. Iteration 0010 ersetzt die reine Demo-Daten-Baseline durch eine Baseline mit echtem Application-Service-Lesepfad.

## Sparregel

Es wurde absichtlich nur der verbindliche Referenz-Viewport 1440×900 gerendert. Zusätzliche Viewports erst bei einem konkreten Responsive-Befund oder einem späteren Deep-Gate.
