# I174 – Autonomes Chromium-Evidence-Gate in CI

## Ziel und Status

I174 verlagert die reale I172-Browserabnahme in den vorhandenen PR-Workflow auf
`ubuntu-latest`. Der bestehende CDP-Harness, seine Zustands-/Accessibility-
Prüfungen und der Screenshot-Hash bleiben unverändert.

## Schritt 1 – Generischer CI-Ausführungspfad

Der Targeted Workflow führt weiterhin ausschließlich die im neuesten Manifest
genannten Compile- und Testziele aus. Sein `PYTHONPATH` enthält nun sowohl
`src` als auch den Repository-Root. Dadurch kann der I172-Wrapper neben dem
Produktmodul auch den sicherheitsgeprüften Browserinstaller aus `scripts`
importieren.

Der vorhandene Evidence-Upload bleibt `if: always()` und übernimmt
`runtime/iteration-*`. Damit stehen Diagnose-JSON und Screenshot auch nach
einem roten Browser-Gate als Workflow-Artefakt zur Verfügung, sofern der
Harness sie erzeugen konnte.

**Zwischen-Gate:** Workflow-Vertrag, Python-Syntax, Manifest-Routing und lokaler
Preflight sind GRÜN.

## Schritt 2 – Reales I172-Gate als Manifestziel

Das I174-Manifest führt zuerst den statischen CI-Vertragstest und anschließend
`tests/mask_builder/test_i172_chromium_evidence.py` aus. Der Wrapper sucht
weiterhin explizites Executable, receipt-geprüften Projektcache und schließlich
Chrome/Chromium aus `PATH`.

Der PR-Lauf ist nur grün, wenn ein echter Browser den unveränderten Harness mit
Exitstatus 0 abschließt, `overall_status` den Wert `GREEN` trägt und Screenshot
sowie SHA-256 vorhanden sind. Ein Runner ohne Browser endet sichtbar BLOCKIERT;
es gibt keinen Skip und keine Testausnahme.

## Sicherheitsgrenzen

- kein Browser-Binary und keine neue Dependency im Repository,
- kein Downloadskript oder fremdes CI-Action-Setup im Workflow,
- keine Abschwächung des I172-Gates,
- keine README-/TODO-/Roadmap-Fortschreibung vor grünem Remote-Nachweis,
- kein Produkt-, Persistenz-, Schema- oder Repository-Eingriff,
- CP-03 und CP-06 bleiben geschlossen.

## Laienhilfe-Delta

Die Browserprüfung läuft nun automatisch beim Pull Request auf einem separaten
Testrechner. Nur ein echter Screenshot mit passendem digitalen Fingerabdruck
zählt als bestanden; fehlt dort der Browser, wird der Lauf sichtbar rot.

## Abschlussgate

- Lokaler CI-/Manifestvertrag: GRÜN.
- Reales Chromium-/Screenshot-Gate: `CI_GATE_PENDING` bis zum PR-Lauf.
- Produktfortschritt: unverändert 42/132.
