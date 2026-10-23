# Vorrelease-Pflichtmatrix – DB_TOOL_2026

**Stand:** 23.10.2026 · **Ausgangs-HEAD `main`:** `835b12568136f33e69c8395dd0331d4d1762d769` · **Entwicklungszweig:** `automation/i179-editor-asset-nonempty` · **PR:** [#180](https://github.com/provoware/DB_TOOL_2026/pull/180) · **Iteration:** I179.

**Bedeutung:** `PASS` = nur die konkret belegte Teilprüfung bestanden; `TEILWEISE` = vorhandene Funktion ohne vollständiges Release-Gate; `OFFEN` = noch kein ausreichender Nachweis; `BLOCKED` = abhängige Freigabe fehlt. Keine erfundenen Fertigstellungsprozente. Für den vollständigen Funktionspool siehe [TODO](../TODO.md) und [Produkt-Roadmap](PRODUCT_ROADMAP.md).

| Release-Pflicht | Soll / Grenzfälle | Beobachteter Stand und Beleg | Status / nächste Pflicht |
| --- | --- | --- | --- |
| Fachfunktionen | Vollständige Masken-, Daten- und Regelarbeit | Nur-Lese-Webpfad und browserlokale Maskenentwürfe vorhanden ([README](../README.md), [TODO](../TODO.md)) | TEILWEISE; fehlende Pflichtfunktionen einzeln implementieren |
| Grenzfälle | Leerwerte, falsche Typen, Abbruch, Mehrfachaktionen | Einzelne zielgerichtete Tests unter [tests/](../tests/) | TEILWEISE; vollständige Grenzfallmatrix |
| Datensicherheit | Keine stillen Änderungen, kontrollierte Schreibpfade | Nur-Lese-Modus; produktive Maskenpersistenz gesperrt ([README](../README.md)) | BLOCKED; Schreibvertrag und Datenintegrität |
| Wiederherstellung | Backup, Restore, Undo/Redo, Crash-Test | [TODO G](../TODO.md) überwiegend offen | OFFEN; isoliertes Recovery-Labor |
| Fehlerbehandlung | Verständliche Fehler, Ausfallpfade | I179 erkennt zusätzlich ein **leeres** Editor-Skript ([Selbstcheck](../scripts/repo_self_check.sh)) | TEILWEISE; Fehler- und Ausfallmatrix |
| Sicherheit | Pfadschutz, Berechtigungen, sichere Datenzugriffe | GET-only/Loopback-Vertrag dokumentiert ([README](../README.md)) | TEILWEISE; unabhängige Negativtests |
| Gestaltung und Lesbarkeit | Konsistente große Schrift, Kontrast, verständliche Oberfläche | Teilweise Browser-Entwürfe und Nachweise ([tests/mask_builder](../tests/mask_builder)) | OFFEN; Gesamtprüfung |
| 800×600 / hohe Skalierung | Kein unbedienbarer Überlauf bei 100/150/200 % | Vorschaugrößen 1152/768/360 dokumentiert; **kein** vollständiger 800×600-Gesamtnachweis | OFFEN; reale Ansichts- und Zoommatrix |
| Tastatur / Barrierefreiheit | Fokus, Screenreader, Tastatur, reduzierte Bewegung | Teilprüfungen vorhanden; [TODO K](../TODO.md) offen | TEILWEISE; Gesamtmatrix |
| Leistung | Große Datenbestände, langsame Geräte, Abbruch | Kein belastbarer Release-Lasttest belegt | OFFEN; reproduzierbare Leistungsgrenzen |
| Wartbarkeit | Kleine Änderungen, nachvollziehbare Abhängigkeiten | [AGENTS.md](../AGENTS.md), Iterationsmanifeste und getrennte Module | TEILWEISE; Code-/Abhängigkeitsprüfung |
| Paketierung / Installation | Reproduzierbarer Start auf Kubuntu, Offline-Fall | Startskript und Browser-Installationsskript vorhanden ([scripts](../scripts)) | OFFEN; Installation und Deinstallation testen |
| Automatisierte Funktionstests | Kernfunktionen und Fehlerfälle | I179 isoliert: **3/3 PASS**, `bash -n` PASS, Python-Compile PASS; kein vollständiger Repo-Test | TEILWEISE; Funktionsabdeckung nachweisen |
| Integration | Zusammenspiel GUI, Web, Datenmodell, SQLite | Schichten und einzelne Integrationstests vorhanden ([tests/web](../tests/web)) | OFFEN; durchgehende Abläufe |
| GUI / Browser | Reale Interaktion, visuelle Regression, mehrere Skalierungen | I167-Screenshot-Testausnahme dokumentiert; keine neue reale I179-Browserprüfung erforderlich | OFFEN; Gesamt-Browser-Gate |
| Regression | Vorher/nachher, Fehlerfall rot, Normalfall grün | [I179-Tests](../tests/scripts/test_repo_self_check.py): fehlt/leer/vorhanden lokal geprüft | PASS **nur für I179-Teilscope**; weitere Produktregression offen |
| CI / Schutzregeln | Alle vorgeschriebenen Gates am finalen PR-HEAD grün | [PR #180](https://github.com/provoware/DB_TOOL_2026/pull/180) ist Entwurf; GitHub-Gates auf finalem HEAD zu verifizieren | BLOCKED bis finaler CI-Beleg |
| Dokumentation | Nutzerhandbuch, Fehlerhilfe, aktuelle Release-Nachweise | README/TODO und diese Matrix; ältere Statusangaben teils I170 | TEILWEISE; Status-/Handbuchabgleich |
| Release-Vorbereitung | Vollständig getestet, eingefrorener Kandidat, gebündelte Endabnahme | Weder Vollabnahme noch Freigabe erfolgt | BLOCKED; erst alle Gates, dann eine Kubuntu-/Sicht-Endabnahme |

## I179 – reproduzierbare Nachweise

- **Befund:** Die bisherige `-f`-Prüfung akzeptierte auch eine Datei mit null Byte; das Editor-Skript kann dann beim Laden fehlen, obwohl der Strukturcheck GRÜN meldet.
- **Änderung:** Für `interaction_script.js` gilt nun zusätzlich `-s` (Datei muss Inhalt haben). Fehlende Datei bleibt ROT; leere Datei wird ausdrücklich ROT.
- **Lokaler isolierter Test (23.10.2026):** `bash -n scripts/repo_self_check.sh` PASS; `python -m py_compile tests/scripts/test_repo_self_check.py` PASS; `python -W error tests/scripts/test_repo_self_check.py` **3/3 PASS**. Die Testumgebung simuliert die zwei unabhängigen Python-Prüfprogramme, sie ersetzt **nicht** den vollständigen Checkout-/CI-Test.
- **Nicht geprüft:** echte Browserbedienung, vollständiger SQLite-Betrieb, Datenmigrationen, Kubuntu-Installation. Diese sind durch I179 nicht geändert.
- **Ausgangs-HEAD:** `835b12568136f33e69c8395dd0331d4d1762d769`; **Schritt-1-Commit:** `e050257f45d9a29f19f858b9e791a4c7c69ba47f`; finaler HEAD siehe PR #180.
- **Nächster automatischer Schritt:** finalen PR-HEAD, Scope, Manifest V2, Fast Context, gezielte Regression und GitHub-Gates prüfen. Bei ROT Fehler reparieren; keine Integration ohne GRÜN.

**Release-Sperre:** Kein Merge, kein Release und keine vorgezogene persönliche Endabnahme. CP-03/CP-06 bleiben geschützt.
