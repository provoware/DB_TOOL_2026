# I173 – Projektlokaler Testbrowser

## Ziel und Status

I173 stellt einen sicheren, dependency-freien Bereitstellungspfad für das
I172-Chromium-Gate bereit. Das Browser-Binary wird nicht in Git aufgenommen.
Der bestehende Produktcode und der I172-CDP-Harness bleiben unverändert.

## Schritt 1 – Lockfile und sicherer Installer

`.provoware/browser-lock.json` legt Plattform, Revision, HTTPS-URL, SHA-256,
erlaubte Downloadhosts, Cachepfad und Executable-Pfad fest. Das eingecheckte
Lockfile ist absichtlich `UNCONFIGURED`, weil die aktuelle Umgebung weder den
offiziellen Chrome-for-Testing-Metadatenkanal noch npm oder Ubuntu-Pakete
erreichen kann. Ein erfundener Hash wäre kein Sicherheitsnachweis.

Nach Freigabe eines Artefakts werden `revision`, `url` und `sha256` auf dessen
geprüfte Werte gesetzt. Alternativ übernimmt `--archive` dasselbe gepinnte
Artefakt offline, ohne die URL aufzurufen:

```bash
python scripts/install_test_browser.py --archive /sicherer/pfad/chrome-linux64.zip
```

Der Installer akzeptiert nur den im Lockfile fixierten SHA-256, begrenzt die
Archivgröße, verwirft absolute Pfade, `..` und Symlinks, fordert das erwartete
Executable und veröffentlicht den entpackten Browser atomar. Ein Receipt bindet
Cacheinhalt, Revision und Hash; unvollständige oder manipulierte Cacheziele
werden nicht verwendet.

**Zwischen-Gate:** Compile sowie Offline-Installation, Hash-Mismatch und
Pfadtraversal-Negativtest sind GRÜN. Ein unkonfiguriertes Lockfile scheitert
erwartungsgemäß geschlossen.

## Schritt 2 – Projektlokaler Lookup und I172-Gate

Der I172-Wrapper sucht in dieser Reihenfolge:

1. ausführbarer Pfad aus `PROVOWARE_CHROMIUM`,
2. projektlokaler Cache mit gültigem Receipt,
3. vorhandenes Chrome/Chromium aus `PATH`.

Der Cache `.browser-cache/` ist von Git ausgeschlossen. Nach Bereitstellung
eines echten Artefakts lauten die Befehle:

```bash
python scripts/install_test_browser.py --archive /sicherer/pfad/chrome-linux64.zip
PYTHONPATH=src:. python tests/mask_builder/test_i172_chromium_evidence.py
```

Ohne freigegebenes Archiv bleibt das I172-Gate korrekt blockiert. Screenshot,
Hash und Statusdokumente dürfen erst bei echtem Browser-PASS übernommen werden.

## Sicherheitsgrenzen

- keine Browser-Binaries oder Archive in Git,
- kein Download von Hosts außerhalb der Lockfile-Allowlist,
- keine Installation außerhalb des projektlokalen Cache,
- keine neue Python-/Node-Abhängigkeit und keine CI-Änderung,
- keine Produkt-, Persistenz-, Schema- oder Repository-Änderung,
- CP-03 und CP-06 bleiben geschlossen.

## Laienhilfe-Delta

Das Projekt kennt nun einen sicheren Ablageplatz für einen Testbrowser. Wie bei
einem versiegelten Paket wird vor dem Öffnen sein digitaler Fingerabdruck
geprüft. Ohne passenden Fingerabdruck wird nichts installiert oder gestartet.

## Abschlussgate

- Bootstrap- und Sicherheitstests: GRÜN.
- Projektlokaler Lookup: GRÜN.
- Reales I172-Screenshot-Gate: bis zur Artefaktbereitstellung BLOCKIERT.
