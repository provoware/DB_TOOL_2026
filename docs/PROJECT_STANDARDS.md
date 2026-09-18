# PROVOWARE Entwicklungs- und Validierungsstandard

## Benutzerperspektive

Anleitungen sind laiengerecht. Fachbegriffe werden kurz erklärt. Wenn sinnvoll, gibt es einen einzigen kopierbaren Kettenbefehl.

## Gate-Status

- **GRÜN**: alle erforderlichen Prüfungen vollständig bestanden
- **GELB**: kein Fehler nachgewiesen, aber eine notwendige Prüfung ist blockiert oder unvollständig
- **ROT**: Fehler, Regression oder Schutzverletzung

## Selbstvalidierung

Ein Gate prüft soweit relevant:

- Projektpfad und erwartete Dateien
- Python-Version
- isolierte virtuelle Umgebung
- Abhängigkeiten
- Frozen-Core-Prüfsummen
- Syntax/Compile
- relevante Unit-, Integrations- und Regressionstests
- SQLite integrity_check und foreign_key_check
- bei UI: Layoutgrößen, Tastatur, Fokus und visuelle Snapshots
- echten Prozess-Exitcode

## TXT-Auswertung

Jeder große Gate-Lauf erzeugt eine Textdatei mit Datum/Zeit, Projekt/Repo, Checkpoint, Toolversionen, ausgeführten Prüfungen, bestanden/fehlgeschlagen/übersprungen, Warnungen/Blockaden, GRÜN/GELB/ROT und nächster Empfehlung.

## Änderungsvolumen

Jeder Abschluss nennt neue, geänderte und gelöschte Dateien, Tests, betroffene Schichten, ungefähre Codezeilen soweit sinnvoll und den Freeze-Status.

## Sicherheitsregel

Keine produktiven Datenmanipulationen nur zum Zweck eines Tests. Testpfade und Testdaten müssen eindeutig isoliert sein.
