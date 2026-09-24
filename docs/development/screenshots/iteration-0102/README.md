# Iteration 0102 – Real Chromium Remove Evidence

**Produktbasis:** `fe62618745c2009139be93420f0898aada6cea1f`  
**Step-1-Source-Head:** `f1044d7cd94d260917c7133d16e87d23411f9c16`  
**Browser:** Chromium 144.0.7559.96 auf Linux  
**Viewport:** 1440 × 900, DPR 1

## Schritt 1 – normaler Remove-Workflow

Der bereits in I101 vorhandene temporäre Remove-Slice wurde ohne Produktänderung in echtem Chromium über Playwright ausgeführt.

Geprüfter Ablauf:

1. `Eingabefeld` per Tastatur auswählen.
2. In Zielspalte 3 per Enter platzieren → `draft-1`.
3. `Entfernen` per Tastatur/Enter auslösen.
4. Fokus-Rückgabe auf die ursprüngliche Zielspalte 3 prüfen.
5. Leerzustand nach Entfernen des letzten Elements prüfen.
6. Direkt aus dem zurückgegebenen Fokus erneut platzieren → `draft-2`.
7. Vorschau, horizontalen Overflow, Browser-Konsole und Page-Errors prüfen.

### Evidence

- 🟢 Remove per Tastatur funktioniert
- 🟢 Fokus kehrt zu Zielspalte 3 zurück
- 🟢 letztes Entfernen stellt den Leerzustand wieder her
- 🟢 erneute Platzierung verwendet `draft-2`; ID wird nicht wiederverwendet
- 🟢 Vorschau bleibt konsistent: `Eingabefeld · Spalten 3–6`
- 🟢 kein horizontaler Overflow
- 🟢 Browser-Console-Errors: 0
- 🟢 Page-Errors: 0

**Step-1-Screenshot SHA-256:** `f500cc807ff6a7b45feb32b2cc0bc81c366643b2080cda5d8679b11e52b12197`

## Freeze-Schutz

🔒 Kein Produktpatch in Schritt 1  
🔒 Keine Persistenz  
🔒 Kein Edit/Move  
🔒 CP-03/CP-06 unverändert  
🔒 Schema/Migrationen/DB unverändert

## Zwischenstatus

**Schritt 1: GRÜN.** Schritt 2 bleibt bis zum erfolgreichen Zwischen-Gate gesperrt.


## Schritt 2 – rechter 4-Spalten-Randfall bei 200-%-Zoom-Äquivalent

Nach grünem Zwischen-Gate #77 wurde der rechte gültige 4-Spalten-Fall mit **720 × 450 CSS-Pixeln bei DPR 2** in echtem Chromium geprüft. Das Eingabefeld wurde an Spalte 9 platziert und belegt damit die Spalten 9–12.

### Evidence Schritt 2

- 🟢 Remove-Button vollständig sichtbar
- 🟢 Remove-Button fokussierbar
- 🟢 Remove per Enter funktioniert
- 🟢 Fokus kehrt nach Remove zu Zielspalte 9 zurück
- 🟢 sichtbarer Fokusrahmen: solid, 3 px, Offset 2 px
- 🟢 kein horizontaler Overflow
- 🟢 Browser-Console-Errors: 0
- 🟢 Page-Errors: 0

**200-%-Screenshot SHA-256:** `d559d1fb9d8ebe01a417c1a20dab2bf0ceb080db8fdd1be837d9f613e3095df4`

## I102-Ergebnis

**Schritt 1:** GRÜN.  
**Schritt 2:** GRÜN, **NO_FIX_REQUIRED**.  
**Produktcode:** unverändert.  
**Finaler Status:** wartet ausschließlich auf das abschließende I102-Gate.
