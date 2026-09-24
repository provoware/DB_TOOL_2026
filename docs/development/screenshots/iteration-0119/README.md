# Iteration 0119 – Property Accessibility Baseline

**Produktbasis vor I119:** `913fdf5f5a92cefc83e01e3847a101835b90dae8` (I118)  
**PR:** #122  
**Browser:** Google Chrome auf GitHub Linux Runner  
**Produktumfang:** unverändert; I119 ist Evidence/Härtung

## Ziel

Vor dem geplanten PROVOWARE Development Control Plane V2 wird die vorhandene browserlokale Eigenschaftenbearbeitung als reproduzierbare Verhaltens- und Accessibility-Baseline geprüft.

Der neue Evidence-Harness besitzt **keine zusätzliche Paketabhängigkeit**. Er nutzt Node.js plus ein bereits vorhandenes Chrome/Chromium und steuert den Browser direkt über das Chrome DevTools Protocol.

## Gefundene und behobene Befunde

### 1. Evidence-Harness – Tastaturaktivierung

Der erste Lauf zeigte, dass der neue CDP-Harness `Enter` noch nicht vollständig als native Tastatureingabe übergab. Dadurch konnte die Palette nicht aktiviert werden; alle nachfolgenden Property-Fehler waren Kaskadenfehler des Harness.

**Reparatur:** Enter übergibt jetzt zusätzlich den Text-/UnmodifiedText-Anteil. Danach funktionierten reale Button-Aktivierungen per Tastatur.

### 2. Browser-Runtime – Favicon 404

Der reale Browser meldete einmal `/favicon.ico → 404`.

**Reparatur:** Die weiterhin GET-only gebundene Editor-Anwendung beantwortet ausschließlich `/favicon.ico` mit `204 No Content`. Unbekannte andere Pfade bleiben `404`.

### 3. Accessibility – Pflichtfeld-Fokus

Nach dem Umschalten von `Pflichtfeld` wurde die DOM-Karte neu gerendert, ohne den Fokus auf den neu erzeugten Toggle zurückzugeben.

**Reparatur:** `focusRequiredControl(id)` stellt den Fokus deterministisch auf denselben Draft-Toggle zurück.

Dies war der einzige durch die funktionierende Property-Matrix bestätigte Produktfehler.

## Schritt 1 – 100 % + 150 %

**Source Head:** `194e9268c0c1b5683e3a1b86e3bcdc18780a59e3`  
**Workflow Run:** `36054718120`  
**Ergebnis:** 🟢 Targeted + Foundation

Geprüft wurden unter anderem:

- sichtbarer 3-px-Tastaturfokus,
- Palette und Feldplatzierung per Tastatur,
- Beschriftung und Hilfetext inklusive Fokus-Rückgabe,
- Pflichtfeld, Sichtbarkeit, Breite und Datentyp,
- skalarer Standardwert und Preview,
- Choice-Optionen hinzufügen, neuordnen und entfernen,
- kein horizontaler Overflow,
- keine Browserfehler.

Screenshot-SHA-256:

- **100 %:** `b4c4b61d31597c34af51dced8b2d6aa50f4fa4872e59217e1e15d4d94eaa0285`
- **150 %:** `dea4529ae5f26b8f59d289573b3acecfcd8eaa2268265e9b37c66154a5d6ede0`

## Schritt 2 – gemeinsame 100/150/200-%-Baseline

**Source Head:** `d3a2fa64d8f63c28a63769bf0a51493a9d3f0384`  
**Workflow Run:** `36054873714`  
**Ergebnis:** 🟢 Targeted + Foundation

Die vollständige Matrix wurde auf demselben Head bei allen drei Skalierungen erneut ausgeführt.

Zusätzlich für **200 %**:

- CSS-Viewport 720 × 450,
- DPR 2,
- alle Property-Controls erreichbar,
- Fokus-Rückgaben stabil,
- Choice-Interaktion stabil,
- kein horizontaler Overflow,
- Browser-Console/Page-Errors: 0.

**200-%-Screenshot SHA-256:** `84946b7b314f4546aeeaf921ec9b55da004f9476549c046e4d2deb8b1db0d06d`

## Baseline-Vertrag nach I119

Folgende vorhandene Browser-Draft-Eigenschaften sind gemeinsam real-browser-geprüft:

- Label,
- Hilfetext,
- Pflichtfeld,
- Datentyp,
- skalarer Standardwert,
- Choice-Optionen,
- Sichtbarkeit,
- Breite,
- Fokus-Rückgabe,
- Preview-Konsistenz.

Diese Evidence bildet die Referenz für den nächsten geplanten **Development Control Plane V2**-Block. Ein späterer Capability-Freeze kann sich auf diese Baseline beziehen, ohne I119 nachträglich zu verändern.

## Schutzgrenzen

- 🔒 CP-03 unverändert
- 🔒 CP-06 unverändert
- 🔒 Schema/Migrationen unverändert
- 🔒 keine Datenbankänderung
- 🔒 kein MaskTemplateStore Save/Load
- 🔒 keine Persistenz
- 🔒 kein `defaultSelection`
- 🔒 keine neue Property

## Ergebnis

**I119 Property Accessibility Baseline: 🟢 GRÜN.**
