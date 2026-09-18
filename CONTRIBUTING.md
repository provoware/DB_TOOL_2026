# Mitwirken

## Grundsatz

Planung vor Änderung. Kleinster sinnvoller Patch. Stabilen Code nicht beiläufig anfassen.

## Vor jedem Patch

- Ziel benennen
- betroffene Dateien bestimmen
- Risiken nennen
- bewusste Nicht-Änderungen festhalten
- relevante Tests festlegen

## Nach jedem Patch

- Syntax/Compile
- direkt betroffene Tests
- Regression der berührten Schicht
- Gate
- TXT-Auswertung
- Änderungsvolumen

## Frozen Core

CP-03 und CP-06 gelten als geschützt. Änderungen dort benötigen eine eigene begründete Iteration und neue Regressionstests.

## Pull Requests

Ein PR soll klein, nachvollziehbar und thematisch geschlossen bleiben. Keine globalen Umformatierungen zusammen mit Funktionsänderungen.
