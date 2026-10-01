# .provoware – interne Projektsteuerung

Dieser Ordner ist **kein Cache und kein Datenmüll**. Er enthält versionierte Verträge und Nachweise, die den sicheren Entwicklungsprozess des PROVOWARE DB TOOL 2026 rekonstruierbar machen.

| Bereich | Zweck |
|---|---|
| `agents/` | Agentenrollen und Regeln |
| `control/` | Control-Plane-Verträge im Shadow-Modus |
| `examples/` | kleine Vertrags- und Planbeispiele |
| `freezes/` | explizite Freeze-Nachweise für geschützte Produktbereiche |
| `iterations/` | maschinenlesbare Iterationsmanifeste; historische Auditspur |
| `queues/` | nachvollziehbare Übergaben, Blocker und abgeschlossene Agentenaufträge |
| `schema/` | Schema der Iterationsmanifeste |
| `templates/` | Vorlage für neue Iterationspläne |
| `browser-lock.json` | reproduzierbarer Browser-Beschaffungsvertrag; der lokale Cache selbst liegt außerhalb der Versionsverwaltung |

## Aufräumregel

- Dateien in `iterations/`, `freezes/` und `control/` **nicht pauschal löschen, umbenennen oder verschieben**.
- Lokale Laufzeitdaten, Datenbanken, Logs, Browser-Cache und Build-Ausgaben gehören nicht in Git; dafür gelten die Regeln aus `.gitignore`.
- Historische menschenlesbare Erklärungen gehören nach `docs/`; aktuelle Nutzerinformationen bleiben in README, `docs/LAIEN_START.md` und den Bedienpfaden.
- Vor strukturellen Änderungen an diesem Ordner zuerst `AGENTS.md` und den Iterations-Preflight beachten.

## Für normale Nutzer

Für die Bedienung ist dieser Ordner nicht erforderlich. Beginne mit `docs/LAIEN_START.md` oder dem Schnellstart in der Haupt-`README.md`.
