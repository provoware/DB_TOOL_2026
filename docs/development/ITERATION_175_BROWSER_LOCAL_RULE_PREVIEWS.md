# I175 – Browserlokale Regelvorschauen

## Kurz erklärt

Der Maskenentwurf kann jetzt drei Regeln ausprobieren: einen Zahlenbereich, einen
Zeitraum von/bis und erlaubte Dateiendungen. „Browserlokal“ bedeutet dabei: Die
Eingaben dienen nur als Vorschau im aktuell geöffneten Editor. Sie werden weder
gespeichert noch auf vorhandene Datensätze oder echte Dateien angewendet.

Beim Datumsbereich darf eine Seite offen bleiben; ein Von-Datum nach dem
Bis-Datum wird verständlich abgelehnt. Bei Dateitypen werden Endungen wie
`.pdf, .jpg` mit einem eingegebenen Test-Dateinamen verglichen. Der Inhalt einer
Datei wird nicht geöffnet oder gelesen.

## Grenzen

- keine produktive Aktivierung oder Persistenz;
- keine Prüfung vorhandener Daten oder Dateien;
- keine Eindeutigkeits-, Sichtbarkeits- oder Feldabhängigkeitsregel;
- CP-03 und CP-06 bleiben unverändert und geschlossen.

Die sichtbaren Zustände und die Tastaturbedienung benötigen vor dem Abhaken der
drei TODO-Punkte weiterhin einen echten Chromium- und Screenshot-Nachweis.
