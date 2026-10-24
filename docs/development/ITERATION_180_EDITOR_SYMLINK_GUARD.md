# I180 – Symbolische Links als Editor-Skript im Selbstcheck abweisen

**Datum:** 24.10.2026 · **Basis:** `eff5bb7e0db904e243518f4cdd7ead1f2308b2fb` · **Branch:** `automation/i180-editor-symlink-guard` · **Schritt 1:** `edc0f8a04af6643f79e8687e8e58c2e37f1da1bc`.

## Befund und Wirkung

Der bisherige Strukturcheck akzeptierte `interaction_script.js` auch dann als vorhanden, wenn die Datei nur ein symbolischer Link auf eine andere, nichtleere JavaScript-Datei war. Damit konnte eine ausgetauschte Verknüpfung die Integritätsprüfung passieren, obwohl das erwartete reguläre Repository-Asset fehlte. Der Schutz prüft nun vor dem bisherigen Leerdatei-Test explizit `-L` und meldet `ROT`.

## Geplante und ausgeführte Zwei-Schritt-Iteration

1. **Primäränderung:** In `scripts/repo_self_check.sh` symbolische Links für das Editor-Asset abweisen und `tests/scripts/test_repo_self_check.py` um einen Negativtest mit einem existierenden, nichtleeren Linkziel ergänzen. Vorhandene Fälle für fehlend, leer und regulär bleiben erhalten.
2. **Direkte Folge:** Den Sicherheitsgewinn, die Grenzen der Prüfung und den Vorrelease-Status in dieser Notiz und in der Release-Pflichtmatrix dokumentieren. Keine zusätzliche Produktfunktion.

## Prüfnachweise

- **Vorher (isolierter Test gegen I179-Prüflogik):** 3/4 Tests PASS, neuer Symlink-Negativtest **FAIL**; ein vorhandener Symlink wurde als GRÜN akzeptiert.
- **Nachher (isolierte lokale Kopie des geänderten Prüfscripts):** `bash -n` PASS; Python-Compile PASS; `python3 -W error tests/scripts/test_repo_self_check.py` **4/4 PASS**.
- **Remote-Nachweis:** Schritt-1-Commit `edc0f8a04af6643f79e8687e8e58c2e37f1da1bc` enthält die Symlink-Prüfung und den Negativtest. GitHub-CI auf dem finalen PR-HEAD muss gesondert ausgewertet werden; lokale Tests sind kein vollständiger Repository-Checkout.
- **Nicht geprüft:** JavaScript-Syntax, echte Chromium-Bedienung, Datenbankbetrieb, Datenmigration, Kubuntu-Installation, visuelle Skalierung. Diese Bereiche wurden nicht geändert.
- **Grenze:** Ein nichtleeres reguläres Skript kann weiterhin syntaktisch oder fachlich defekt sein. Das reale Browser-Gate bleibt erforderlich.

**Schutzgrenzen:** Keine Änderung an CP-03, CP-06, Datenbank, Nutzerdaten, JavaScript-Logik oder UI. Kein Merge, keine Veröffentlichung. Eine persönliche Kubuntu-/Sicht-Endabnahme wird erst für den vollständigen Release-Kandidaten verlangt.
