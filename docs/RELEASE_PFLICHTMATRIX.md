# Vorrelease-Pflichtmatrix – DB_TOOL_2026

**Stand:** 24.10.2026 · **Ausgangs-HEAD `main`:** `eff5bb7e0db904e243518f4cdd7ead1f2308b2fb` · **Entwicklungszweig:** `automation/i180-editor-symlink-guard` · **PR:** wird nach Schritt 2 eröffnet · **Iteration:** I180.

**Bedeutung:** `PASS` = nur die konkret belegte Teilprüfung bestanden; `TEILWEISE` = vorhandene Funktion ohne vollständiges Release-Gate; `OFFEN` = noch kein ausreichender Nachweis; `BLOCKED` = abhängige Freigabe fehlt. Keine erfundenen Fertigstellungsprozente. Für den vollständigen Funktionspool siehe [TODO](../TODO.md) und [Produkt-Roadmap](PRODUCT_ROADMAP.md).

| Release-Pflicht | Soll / Grenzfälle | Beobachteter Stand und Beleg | Status / nächste Pflicht |
| --- | --- | --- | --- |
| Fachfunktionen | Vollständige Masken-, Daten- und Regelarbeit | Nur-Lese-Webpfad und browserlokale Maskenentwürfe vorhanden ([README](../README.md), [TODO](../TODO.md)) | TEILWEISE; fehlende Pflichtfunktionen einzeln implementieren |
| Grenzfälle | Leerwerte, falsche Typen, Abbruch, Mehrfachaktionen | Einzelne zielgerichtete Tests unter [tests/](../tests/) | TEILWEISE; vollständige Grenzfallmatrix |
| Datensicherheit | Keine stillen Änderungen, kontrollierte Schreibpfade | Nur-Lese-Modus; produktive Maskenpersistenz gesperrt ([README](../README.md)) | BLOCKED; Schreibvertrag und Datenintegrität |
| Wiederherstellung | Backup, Restore, Undo/Redo, Crash-Test | [TODO G](../TODO.md) überwiegend offen | OFFEN; isoliertes Recovery-Labor |
| Fehlerbehandlung | Verständliche Fehler, Ausfallpfade | I179 erkennt ein **leeres** Editor-Skript, I180 zusätzlich einen **symbolischen Link** ([Selbstcheck](../scripts/repo_self_check.sh)) | TEILWEISE; Fehler- und Ausfallmatrix |
| Sicherheit | Pfadschutz, Berechtigungen, sichere Datenzugriffe | GET-only/Loopback-Vertrag dokumentiert ([README](../README.md)) | TEILWEISE; unabhängige Negativtests |
| Gestaltung und Lesbarkeit | Konsistente große Schrift, Kontrast, verständliche Oberfläche | Teilweise Browser-Entwürfe und Nachweise ([tests/mask_builder](../tests/mask_builder)) | OFFEN; Gesamtprüfung |
| 800×600 / hohe Skalierung | Kein unbedienbarer Überlauf bei 100/150/200 % | Vorschaugrößen 1152/768/360 dokumentiert; **kein** vollständiger 800×600-Gesamtnachweis | OFFEN; reale Ansichts- und Zoommatrix |
| Tastatur / Barrierefreiheit | Fokus, Screenreader, Tastatur, reduzierte Bewegung | Teilprüfungen vorhanden; [TODO K](../TODO.md) offen | TEILWEISE; Gesamtmatrix |
| Leistung | Große Datenbestände, langsame Geräte, Abbruch | Kein belastbarer Release-Lasttest belegt | OFFEN; reproduzierbare Leistungsgrenzen |
| Wartbarkeit | Kleine Änderungen, nachvollziehbare Abhängigkeiten | [AGENTS.md](../AGENTS.md), Iterationsmanifeste und getrennte Module | TEILWEISE; Code-/Abhängigkeitsprüfung |
| Paketierung / Installation | Reproduzierbarer Start auf Kubuntu, Offline-Fall | Startskript und Browser-Installationsskript vorhanden ([scripts](../scripts)) | OFFEN; Installation und Deinstallation testen |
| Automatisierte Funktionstests | Kernfunktionen und Fehlerfälle | I180 isoliert: **4/4 PASS**, `bash -n` PASS, Python-Compile PASS; kein vollständiger Repo-Test | TEILWEISE; Funktionsabdeckung nachweisen |
| Integration | Zusammenspiel GUI, Web, Datenmodell, SQLite | Schichten und einzelne Integrationstests vorhanden ([tests/web](../tests/web)) | OFFEN; durchgehende Abläufe |
| GUI / Browser | Reale Interaktion, visuelle Regression, mehrere Skalierungen | I167-Screenshot-Testausnahme dokumentiert; keine neue reale I179-Browserprüfung erforderlich | OFFEN; Gesamt-Browser-Gate |
| Regression | Vorher/nachher, Fehlerfall rot, Normalfall grün | [I179-Tests](../tests/scripts/test_repo_self_check.py): fehlt/leer/vorhanden lokal geprüft | PASS **nur für I180-Teilscope**; weitere Produktregression offen |
| CI / Schutzregeln | Alle vorgeschriebenen Gates am finalen PR-HEAD grün | I180-PR noch zu eröffnen; GitHub-Gates auf finalem HEAD zu verifizieren | BLOCKED bis finaler CI-Beleg |
| Dokumentation | Nutzerhandbuch, Fehlerhilfe, aktuelle Release-Nachweise | README/TODO und diese Matrix; ältere Statusangaben teils I170 | TEILWEISE; Status-/Handbuchabgleich |
| Release-Vorbereitung | Vollständig getestet, eingefrorener Kandidat, gebündelte Endabnahme | Weder Vollabnahme noch Freigabe erfolgt | BLOCKED; erst alle Gates, dann eine Kubuntu-/Sicht-Endabnahme |

## I179 – reproduzierbare Nachweise

- **Befund:** Die bisherige `-f`-Prüfung akzeptierte auch eine Datei mit null Byte; das Editor-Skript kann dann beim Laden fehlen, obwohl der Strukturcheck GRÜN meldet.
- **Änderung:** Für `interaction_script.js` gilt nun zusätzlich `-s` (Datei muss Inhalt haben). Fehlende Datei bleibt ROT; leere Datei wird ausdrücklich ROT.
- **Lokaler isolierter Test (23.10.2026):** `bash -n scripts/repo_self_check.sh` PASS; `python -m py_compile tests/scripts/test_repo_self_check.py` PASS; `python -W error tests/scripts/test_repo_self_check.py` **3/3 PASS**. Die Testumgebung simuliert die zwei unabhängigen Python-Prüfprogramme, sie ersetzt **nicht** den vollständigen Checkout-/CI-Test.
- **Nicht geprüft:** echte Browserbedienung, vollständiger SQLite-Betrieb, Datenmigrationen, Kubuntu-Installation. Diese sind durch I179 nicht geändert.
- **Ausgangs-HEAD:** `835b12568136f33e69c8395dd0331d4d1762d769`; **Schritt-1-Commit:** `e050257f45d9a29f19f858b9e791a4c7c69ba47f`; finaler HEAD siehe PR #180.
- **Historie:** I179 wurde auf `main` übernommen (`eff5bb7e0db904e243518f4cdd7ead1f2308b2fb`); seine Teiltests bleiben getrennt von den neuen I180-Nachweisen.

**Release-Sperre:** Kein Merge, kein Release und keine vorgezogene persönliche Endabnahme. CP-03/CP-06 bleiben geschützt.

## I180 – Symlink-Schutz und Freigabestatus

- **Befund:** Ein nichtleerer symbolischer Link auf eine fremde JavaScript-Datei erfüllte bislang die `-f`/`-s`-Prüfung und wurde als vorhandenes Editor-Skript gewertet.
- **Änderung:** `scripts/repo_self_check.sh` lehnt `-L` für das Editor-Asset explizit ab. Keine Änderung am produktiven JavaScript oder der Datenbank.
- **Regression:** Vorher **3/4 PASS, 1 FAIL** (Symlink fälschlich grün); nachher **4/4 PASS**; `bash -n` und Python-Compile PASS (isolierte lokale Prüfung, 24.10.2026).
- **GitHub:** Branch `automation/i180-editor-symlink-guard`, Schritt-1-Commit `edc0f8a04af6643f79e8687e8e58c2e37f1da1bc`; finaler PR-HEAD und CI-Gates sind nach dem Dokumentationsschritt nachzuweisen.
- **Restpflichten:** JavaScript-Syntax, echte Browser- und 800×600-/Zoom-Prüfungen, produktive Recovery- und Integrationspfade, Installation und Gesamt-Release-Gates bleiben **OFFEN/BLOCKED**.
- **Nächster Schritt:** PR-HEAD und vorgeschriebene GitHub-Gates prüfen; bei ROT gezielt reparieren, sonst nach Rotation das nächste geeignete Nicht-Spiel-Repository bearbeiten. Keine Veröffentlichung.
