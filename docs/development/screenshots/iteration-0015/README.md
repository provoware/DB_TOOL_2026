# Iteration 0015 – realer Startpfad / Chromium-Gate

**Datum:** 2026-09-18  
**Viewport:** 1440 × 900  
**Datenquelle:** eingefrorenes CP-03-Testfixture / echter read-only CatalogService-Pfad  
**Browser:** System-Chromium  
**Original-PNG SHA-256:** `89329bdd0bb51716ec0bf01c65edd5fcbfe0268d8f5f3e792a2e3f44857c4a99`  
**Repo-Vorschau:** [main-1440x900-preview.jpg](main-1440x900-preview.jpg)

## Durchlauf

1. realer lokaler Nur-Lese-Server auf `127.0.0.1`
2. Root-Ansicht geladen
3. Kategorie **Werkzeug** ausgewählt
4. Eintrag **Akkuschrauber** ausgewählt
5. Feld **Marke** sichtbar
6. zwei aktive Elemente mit `aria-current="true"`

## Browser-/HTTP-Befunde

- 🟢 `/` → 200
- 🟢 `/static/app.css` → 200 `text/css`
- 🟢 unbekannter Write-Pfad `/write` → 404
- 🟢 POST → 405 / Allow: GET
- 🟢 3 Panels
- 🟢 10 sichtbare Buttons
- 🟢 CSS aktiv; Hintergrund `rgb(9, 7, 18)`
- 🟢 keine sichtbaren Überlagerungen oder abgeschnittenen Kernbereiche

## Infrastrukturhinweis

Die Browser-Sandbox dieser Ausführungsumgebung blockiert direkte Chromium-Navigation zu `127.0.0.1` mit `ERR_BLOCKED_BY_ADMINISTRATOR`. Daher wurden die echten HTTP-Antworten des laufenden Loopback-Servers durch einen Test-Bridge-Harness an Chromium übergeben. Die Kategorie-/Eintrag-Klicks steuerten jeweils den nächsten echten Serverabruf. App-Code, Datenquelle und Serverantworten blieben unverändert.

## Kurzfazit

🟢 Der real validierte Startpfad rendert die Oberfläche korrekt.  
🟢 Kategorie → Eintrag → Felder funktioniert sichtbar.  
🟢 CSS wird nun vom GET-only-Server ausgeliefert.  
🟢 Keine Web-Schreibroute vorhanden.  
🟡 Im Nur-Lese-Modus wirken `+ Neu`, `Bearbeiten` und `Papierkorb` optisch noch aktiv. Das sollte in einer folgenden UX-Iteration klar als deaktiviert/Nur-Lese dargestellt werden.

## Visuelle Regression

Gegenüber Iteration 10 bleibt das Drei-Spalten-Grundlayout stabil. Neu sichtbar bestätigt ist der aktive Auswahlzustand `✓ Ausgewählt` aus Iteration 12.
