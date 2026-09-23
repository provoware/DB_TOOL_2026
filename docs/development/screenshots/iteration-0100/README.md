# Iteration 0100 – Real Chromium Interaction Evidence

**Basis:** `4354065c23cf4a9f0262fdd90e38ee7e13f14e58`  
**Browser:** Chromium 144.0.7559.96 auf Linux  
**Referenz-Viewport:** 1440 × 900  
**Theme:** aktueller Mask-Builder-Dark-Stand  
**Screenshot-Meilenstein:** ja

## Schritt 1 – 1440×900

Der aktuelle I99-Masken-Baukasten wurde mit echtem Chromium ausgeführt. Geprüft wurde der reale HTML-/CSS-/JavaScript-Interaktionspfad aus `render_editor_shell()`.

Ablauf:

1. `Eingabefeld` per Tastatur auswählen.
2. Fokus mit zweimal `→` von Zielspalte 1 auf Zielspalte 3 bewegen.
3. Mit `Enter` platzieren.
4. Vollbreite `Überschrift` auswählen.
5. Platzierung an Spalte 12 versuchen und als ungültig blockieren.
6. Vorschau, Fokus, Overflow und Browser-Konsole prüfen.

## Reproduzierbarer Befund und Reparatur

Der erste Browserlauf war **ROT**: Nach erfolgreicher Platzierung blieb der Leertext **„Noch keine Komponenten platziert.“** sichtbar.

Ursache war ausschließlich die CSS-Regel `.canvas-empty { display:grid }`, die den `hidden`-Zustand sichtbar überlagerte.

Minimaler Fix:

```css
.canvas-empty[hidden] { display:none; }
```

Nach exakt derselben Wiederholungsprüfung ist Schritt 1 **GRÜN**.

## Evidence

- 🟢 Tastaturauswahl funktioniert
- 🟢 Zielspalte 3 per Pfeiltasten erreicht
- 🟢 Platzierung per Enter funktioniert
- 🟢 Vorschau: `Eingabefeld · Spalten 3–6`
- 🟢 ungültige Vollbreiten-Platzierung an Spalte 12 blockiert
- 🟢 Leerzustand nach Platzierung verborgen
- 🟢 kein horizontaler Overflow
- 🟢 Browser-Console-Errors: 0
- 🟢 Page-Errors: 0
- 🟢 Screenshot exakt 1440 × 900 erzeugt

**Original-PNG SHA-256:** `d22503b6a483170b6ca235cfa57922ce1c41464eb97de954f80c33dad8354a7a`  
**Generierte WebP-Vorschau SHA-256:** `aca2d618a61962974b0957f93b2e4cafe22eb9056b5d841bb003f807ca244963`

Die Binärvorschau wird in Schritt 1 nicht zusätzlich versioniert; die reproduzierbare Browser-Evidence und die Hashes sind im Repository dokumentiert.

## Kurzfazit

Die I99-Interaktion funktioniert nach dem gezielten Leerzustand-Fix bei 1440 × 900 konsistent. Die Platzierungsgrenze ist sichtbar und funktional; der Fokusrahmen ist klar erkennbar.

## Visuelle Regression

**Vor Fix:** ja – veralteter Leerzustand blieb sichtbar.  
**Nach Fix:** keine blockierende visuelle Regression.

## Freeze-Schutz

🔒 CP-03 unverändert  
🔒 CP-06 unverändert  
🔒 Schema/Migrationen unverändert  
🔒 Kein Save, POST, SQL, CatalogService oder MaskTemplateStore

Schritt 2 prüft anschließend 200-%-Zoom-Äquivalent, Fokus und horizontalen Overflow. Eine weitere Produktänderung erfolgt nur bei reproduzierbarem Befund.
