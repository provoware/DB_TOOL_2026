# I96 – Archiventscheidung für historische Sonderbranches

Stand der Entscheidung: `main c709bc58935a9edd609013cb56a89b9140d14fc7`

Diese Datei bewahrt ausschließlich die **noch nützlichen Erkenntnisse** zweier historischer, nicht gemergter Branches. Die alten Implementierungen werden ausdrücklich **nicht** in den aktuellen Produktstand übernommen.

## 1. `release/i20-package`

Historischer Tip:

`6a20a9b4ba4fc9b66f99139b7df13a07bde2b45d`

Einziger eigener Commit:

`release: package frozen I20 test ZIP`

### Warum der Workflow nicht übernommen wird

Der Branch enthält einen GitHub-Actions-Workflow, der absichtlich auf den eingefrorenen I20-Commit

`00539c3de678b1cd634caeb64ea774733cc73384`

fest verdrahtet ist.

Damit ist er heute kein allgemeiner Release-Weg:

- er paketiert ausdrücklich nur den alten I20-Stand,
- seine Pflichtdateien und Tests bilden I20 ab,
- Paketname und Prüfsummen sind I20-spezifisch,
- spätere Iterationen und der aktuelle Masken-Baukasten fehlen,
- ein unverändertes Übernehmen würde einen historischen Teststand als aktuellen Release-Pfad erscheinen lassen.

### Wiederverwendbare Idee

Für eine spätere echte Release-Iteration sind folgende Muster sinnvoll:

1. Paket aus einem **explizit freigegebenen Commit** bauen.
2. Paketinhalt aus einem sauberen Git-Archiv erzeugen.
3. `start.sh`, `stop.sh` und eine laiengerechte Selbstprüfung gemeinsam ausliefern.
4. Start ausschließlich auf Loopback/`127.0.0.1`, solange keine Netzfreigabe vorgesehen ist.
5. freien Port kontrolliert ermitteln.
6. Demo-/Testdaten strikt innerhalb des Paketordners erzeugen.
7. ZIP nach Erstellung erneut validieren.
8. SHA-256-Prüfsumme neben dem ZIP erzeugen.
9. Release-Prüfung nur gegen den tatsächlich freigegebenen aktuellen Stand binden.

Diese Punkte sind **Entwurfsmuster**, keine aktuelle Release-Freigabe.

### Entscheidung

**ARCHIVIERT / Branch danach löschbar.**

Der historische Workflow soll nicht als aktiver Workflow in `main` erscheinen.

---

## 2. `i21/visual-parity`

Historischer Tip:

`cbea4d8090d730d70929f7962ada51372abb20e2`

Der Branch enthält neun eigene Commits mit einer nie gemergten visuellen Neugestaltung des alten CP-07H-Webpfads.

Der tatsächlich gemergte I21-Checkpoint PR #28 definierte Produktcode und CSS ausdrücklich als **Non-Goal**. Damit ist diese Oberfläche kein freigegebener Produktstand.

### Warum der Produktcode nicht übernommen wird

Die Branch-Version verändert unter anderem:

- `src/provoware_db/web/render.py`
- `src/provoware_db/web/static/app.css`
- `src/provoware_db/web/templates/index.html`
- einen eigenen Visual-Gate-Workflow

Der heutige `main` hat sich fachlich und strukturell weiterentwickelt. Ein direktes Cherry-Pick oder Merge würde deshalb alte Layoutentscheidungen mit neueren Read-only-, Such- und Mask-Builder-Grenzen vermischen.

### Wiederverwendbare UX-/Test-Erkenntnisse

Folgende Punkte sind weiterhin wertvoll:

- Chromium-Referenzlauf mit **exakt 1440 × 900** statt nur angeforderter Fenstergröße.
- Screenshot-Abmessungen maschinell verifizieren.
- **200-%-Zoom-Äquivalent** prüfen und horizontales Überlaufen verhindern.
- Fokus sichtbar halten; der historische Gate verlangte mindestens **3 px** sichtbare Fokusmarkierung.
- zentrale CSS-Design-Tokens statt verstreuter Inline-Werte.
- visuelle Änderungen dürfen bestehende HTML-/Suchverträge nicht unbeabsichtigt brechen.
- Read-only-Aktionen müssen auch nach visueller Überarbeitung deaktiviert bleiben.
- Browser-Konsole auf schwerwiegende Fehler prüfen.
- Geometrie nur dort hart testen, wo sie tatsächlich Teil eines freigegebenen Referenzdesigns ist.

### Nicht verbindlich übernommen

Die historische violett/türkise Farbpalette, konkrete Sidebar-Breite von 272 px und die damalige DateiFinder-Parität sind **keine aktuelle Designvorgabe**. Sie können später als Referenz dienen, dürfen aber nicht automatisch den heutigen UI-Stand überschreiben.

### Entscheidung

**ARCHIVIERT / Branch danach löschbar.**

Die wiederverwendbaren Qualitätskriterien sind hier dokumentiert; die alte UI-Implementierung bleibt bewusst außerhalb von `main`.

---

## I96-Gesamtentscheidung

Nach Merge dieser Archivnotiz gelten zusätzlich als bereinigungsfähig:

- `release/i20-package`
- `i21/visual-parity`

I96 ändert keinen Produktcode und öffnet keinen eingefrorenen Checkpoint.

🔒 CP-03 unverändert  
🔒 CP-06 unverändert  
🔒 Schema/Migrationen unverändert  
🔒 Runtime/Produktcode unverändert
