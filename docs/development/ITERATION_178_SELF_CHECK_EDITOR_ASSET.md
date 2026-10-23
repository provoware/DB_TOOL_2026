# I178 – Selbstprüfung erkennt fehlendes Editor-JavaScript
**Nachübertragung:** 23.10.2026 · **Ausgangs-HEAD:** `ecd184f1ff94cee42c2f25662850ac0794af0e59`.

## Befund
`browser_shell.py` nutzt das benachbarte `interaction_script.js`. Der Repository-Selbstcheck prüfte zuvor nur das Python-Modul. Eine fehlende JavaScript-Laufzeitdatei konnte deshalb eine falsche GRÜN-Meldung zulassen.

## Zwei zusammenhängende Schritte
1. Primär: vorhandene Dateiliste in `scripts/repo_self_check.sh` gezielt um `src/provoware_db/mask_builder/interaction_script.js` erweitern.
2. Direkt dazu: zwei Regressionstests, die ein vorhandenes Asset GRÜN und ein fehlendes ROT melden müssen.

## Nachweise und Risiken
- Isolierte vorherige Testkopie (22.10.2026): Ausgangsskript 2/2 Regression FAIL; korrigierte Kopie 2/2 PASS; Shell-/Python-Syntax PASS.
- Neuer GitHub-Commit: vollständiger Checkout-Test und CI **noch offen**.
- Die Tests simulieren absichtlich zwei unbeteiligte Python-Prüfgates; kein Ersatz für vollständige Installation oder Browser-E2E.
- Kein Nutzerdaten-Schreibzugriff, keine Schema-/Persistenzänderung, kein Reopen von CP-03 oder CP-06.
- **Branch:** `sync/20261023-selfcheck-editor-asset`. PR/Commit im GitHub-Verlauf abrufbar.

**Nächste Pflicht:** gezielten Regressionstest, `bash -n`, Fast-Context-/Preflight-Gates und GitHub-CI auf finalem Branch prüfen; nur bei grünen Gates integrieren.
