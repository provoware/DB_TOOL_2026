# Iteration 0020 – realer Chromium-Such-/Navigations-Gate

**Datum:** 2026-09-19  
**Viewport:** 1440 × 900  
**Browser:** Google Chrome/Chromium 152.0.7977.82 auf Linux  
**Datenquelle:** deterministisches CP-03-Testfixture, nur lesend  
**Validierter Head:** `afd5f5a85b824b17d009fd4bbab531cb503fe0d6`  
**Workflow-Run:** `35455431882`  
**Artifact-ID:** `10587887987`  
**Artifact-Digest:** `sha256:7ef0f97379e1afff0eb1d206bdc5a079f32e71ea05bea0be7d1f4bd9b409675e`

## Evidence

- 🟢 lokaler Nur-Lese-Server auf `127.0.0.1:8765`
- 🟢 Startseite lädt im echten Chromium
- 🟢 `NUR LESEN` sichtbar
- 🟢 `Neu`, `Bearbeiten`, `Undo`, `Papierkorb` deaktiviert
- 🟢 Kategorie **Werkzeug** → Eintrag **Akkuschrauber**
- 🟢 Felder **Hersteller**, **Zustand**, **Kaufdatum** sichtbar
- 🟢 Suche Kategorie / Eintrag / Feld
- 🟢 Keine-Treffer-Zustand
- 🟢 Tastaturfokus erreicht Suchfeld und Buttons
- 🟢 Suche per Enter
- 🟢 keine `SEVERE`-Einträge in der Browser-Konsole
- 🟢 fehlgeschlagene Checks: 0

## Konkreter Befund und Minimalpatch

Der erste automatisierte Chromium-Lauf war funktional vollständig grün, wurde aber durch genau einen Browser-Konsolenbefund blockiert:

`GET /favicon.ico → 404`

Chromium wertete diesen fehlenden Browser-Nebenrequest als `SEVERE`. Es wurde ausschließlich diese Ursache behoben:

`GET /favicon.ico → 204 No Content`

Dazu existiert gezielte Regression-Coverage in `tests/web/test_http_navigation.py`. Keine Schema-, Migrations-, CP-03- oder Core-Änderung.

## Test-Harness-Nachhärtung

Beim anschließend aktivierten gezielten Regressionstest wurden zwei reine Test-Harness-Abweichungen sichtbar und korrigiert:

1. das Mini-Fixture enthielt noch nicht die bereits vom Read-Pfad verwendeten Value-Tabellen;
2. die Erwartung `text · Pflichtfeld` stammte aus dem Stand vor der bereits eingefrorenen Lokalisierung und wurde auf `Text · Pflichtfeld` angepasst.

Beides verändert keinen Produktpfad.

## Harness-Retry

Der erste Evidence-/Freeze-Rerun traf beim Seitenwechsel auf eine transiente Selenium-`StaleElementReferenceException`. Das war kein Produktfehler. Der Browser-Harness ignoriert diese kurzlebige Navigation-Staleness nun innerhalb von `WebDriverWait` und wiederholt dieselbe Assertion.

Der exakt wiederholte Chromium-Gate auf Head `7f6db1e7...` lief anschließend vollständig grün. Das Original-PNG ist pixelidentisch zum vorherigen grünen Lauf (identische SHA-256).

## Screenshot

- Repository-Vorschau: `main-1440x900-preview.jpg`
- Original-PNG SHA-256: `594e14a9c13a548bd0a14b7085e08d9ac68e7f23df32fb2f066dcb7eeb2977dc`
- Repository-JPG SHA-256: `1a24c7b778e809b35443768b56d0a572ce524b52c7e4d5c267512f8b5dbabd40`
- Maschinenlesbare Evidence: `iteration-20-evidence.json`

## Visuelle Regression

Gegenüber Iteration 0015 bleibt das Drei-Stufen-Grundlayout bei 1440 × 900 stabil. Keine überlappenden oder abgeschnittenen Kernbereiche sind sichtbar.

Die sichtbaren Unterschiede sind erwartete, bereits geplante Weiterentwicklungen:
- Suchpanel aus Iteration 19,
- eindeutig deaktivierte Schreibaktionen,
- lokalisierte Feldtypen,
- sichtbare Feldwerte.

**Blockierende visuelle Regression:** nein.

## Freeze

**Gate:** 🟢 GRÜN  
**Status:** `FROZEN_I20`  
**CP-03:** unverändert / eingefroren  
**Schema/Migrationen:** unverändert  
**Frozen Core:** unverändert
