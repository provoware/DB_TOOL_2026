# I172 – Browserlokale Zahlenbereichs-Preview

## Ziel und Status

I172 implementiert den kleinsten durch I171 freigegebenen Slice: Ein temporäres
Draft-Zahlenfeld kann wahlweise gegen genau eine inklusive Unter- oder Obergrenze
geprüft werden. Regel, Grenze und Testwert bleiben ausschließlich im Browser.

## Schritt 1 – Implementierung und Zwischen-Gate

Der reine Auswerter akzeptiert nur das kanonische Dezimalformat aus I171. Leere,
lokalisierte oder von Leerzeichen umgebene Werte sind `not_evaluable`. Werte
unter der Untergrenze oder über der Obergrenze sind `violated`; der exakte
Grenzwert und Werte innerhalb der erlaubten Richtung sind `satisfied`.

Die Oberfläche erscheint nur bei einem Draft-Feld vom Typ `number`. Sie bietet
eine Grenzart, einen Grenzwert und einen Testwert. Genau eine Grenze ist aktiv.
Das Ergebnis besitzt `role="status"` und `aria-live="polite"`; beide Eingaben
verweisen auf denselben fokussierbaren Hilfetext und den Ergebnisstatus.

Compile, die fokussierte I172-Vertragsregression sowie 35 direkte Browser-Shell-
und Pflichtwert-Regressionen sind grün. **Zwischen-Gate: GRÜN.**

## Schritt 2 – Chromium-, Accessibility- und Screenshot-Gate

Der I172-Harness prüft Unter- und Obergrenzen, exakte inklusive Grenzwerte,
ungültige Eingabe, Tastaturfokus des Tooltips, Beschreibungsbeziehungen,
Live-Status, 1440×900-Dark-Layout, horizontalen Overflow und Browserfehler. Bei
Erfolg erzeugt er Screenshot und SHA-256-Hash unter `runtime/iteration-0172/`.

Das Gate ist **BLOCKIERT DURCH UMGEBUNG**: Kein Chrome-/Chromium-Binary ist
installiert. Der Installationsversuch scheiterte an HTTP-403-Antworten des
konfigurierten Paket-Proxys. Es wurde kein Screenshot erzeugt und kein visueller
PASS behauptet. Der reproduzierbare Nachholbefehl lautet:

```bash
PYTHONPATH=src python tests/mask_builder/test_i172_chromium_evidence.py
```

## Sicherheitsgrenzen

- keine produktive Regelaktivierung oder Speicherung,
- kein Netzwerk-, LocalStorage-, SessionStorage-, Repository- oder Datenbankpfad,
- keine zweite gleichzeitig gesetzte Grenze,
- kein Schema, keine Migration und keine Dependency- oder CI-Änderung,
- CP-03 und CP-06 bleiben geschlossen,
- TODO- und Roadmap-Fortschritt bleiben bis zum echten Browser-PASS unverändert.

## Laienhilfe-Delta

Bei einem Zahlenfeld lässt sich jetzt vorläufig ausprobieren: „mindestens“ oder
„höchstens“ welcher Wert? Die Anzeige erklärt sofort, ob ein Testwert passt.
Nach Neuladen ist alles verworfen; vorhandene Daten werden nicht verändert.

## Abschlussgate

- Schritt 1: GRÜN.
- Schritt 2: BLOCKIERT DURCH UMGEBUNG, kein Screenshot-PASS.
- Gesamstatus: GELB; implementiert, aber nicht visuell abgenommen.
