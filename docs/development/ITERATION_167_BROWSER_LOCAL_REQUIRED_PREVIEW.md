# Iteration 167 – Browserlokale Pflichtwert-Preview

## Ziel

Den in I166 freigegebenen `required`-Slice für temporäre Draft-Felder implementieren und leeren, Leerraum-, gefüllten sowie strukturell ungültigen Zustand einschließlich zugänglicher Hilfe absichern.

## Schritt 1 – Primäränderung

`browser_shell.py` ergänzt den gemeinsamen flüchtigen Regelzustand direkt am Draft-Feld:

- stabile `draft-rule-required-*`-ID,
- `kind = required`, Ziel-Feld-ID, Aktivstatus und leere Parameter,
- gemeinsame Auswertung als `satisfied`, `violated` oder `not_evaluable`,
- temporärer Testwert ohne Speicherung,
- verständlicher Live-Status statt interner Exception,
- zwei fokussierbare `?`-Tooltips für Umschaltung und Testwert.

Leer und reiner Leerraum verletzen die Regel; mindestens ein Nicht-Leerraum-Zeichen erfüllt sie. Ungültige Regel, Ziel oder Nicht-String-Wert scheitern geschlossen als `not_evaluable`.

**Zwischen-Gate:** Compile und fokussierter I167-Vertragstest sind GRÜN.

## Schritt 2 – Regression und Accessibility

Geplant waren reale Chromium-Prüfungen für Tastaturfokus, Tooltip-Anzeige, `aria-live=polite`, alle Ergebniszustände, schmale Darstellung und Screenshot. Der vorhandene I132-Chromium-Harness wurde gestartet, fand jedoch kein Chrome-/Chromium-Binary. Auch die gezielte Suche in den üblichen Cache-/Installationspfaden fand kein ausführbares Browser-Binary.

Status: **BLOCKIERT DURCH UMGEBUNG**. Es wurde kein unechter Screenshot erzeugt und kein visueller PASS behauptet. Pflichtwert und `Regel-Preview vor Aktivierung` bleiben deshalb in `TODO.md` offen.

## Sicherheitsgrenzen

- kein `fetch`, XHR, Local-/SessionStorage oder IndexedDB,
- kein Submit-, Speichern- oder Aktivieren-Control,
- kein Backend-, Repository-, Schema- oder Dependency-Patch,
- weitere Regelarten bleiben geschlossen,
- „zuletzt verwendet“, gespeicherte Ansichten und Massenwrites bleiben geschlossen,
- CP-03 und CP-06 bleiben geschlossen.

## Laienhilfe-Delta

Mit der neuen Vorschau lässt sich ausprobieren, ob ein Feld als Pflichtfeld einen Wert erhalten würde. Die `?`-Hilfen erklären die Schalter und den Testwert. Alles bleibt ein flüchtiger Versuch im Browser: Es wird keine Regel aktiviert, kein Testwert gespeichert und kein vorhandener Datensatz verändert.

## Nachzuholendes Abschlussgate

1. Vorhandenen Chromium-Harness mit installiertem Chrome/Chromium ausführen.
2. Leeren, Leerraum-, gefüllten und ungültigen Zustand sowie Tooltip-Fokus und Live-Status real bestätigen.
3. Screenshot bei 1440 × 900 im Dark Theme aufnehmen und erst danach die beiden TODO-Punkte schließen.
