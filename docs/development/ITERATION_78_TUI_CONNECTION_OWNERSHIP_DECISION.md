# Iteration 78 – TUI Connection Ownership Decision

## Änderung

I78 entscheidet ausschließlich den minimalen read-only Ownership-Vertrag, der nach I77 für eine spätere produktive TUI-Health-Quelle fehlt. Es wird kein Provider und kein Connection-Lifecycle implementiert.

## Befund

`ProvowareDbTui` konsumiert weiterhin ein bereits konstruiertes `TuiDataPort`. Die App erzeugt, besitzt und schließt keine SQLite-Connection. Diese Grenze bleibt erhalten.

`open_connection(path, read_only=True)` ist die vorhandene technische Factory. Der Web-Pfad zeigt bereits das sichere Muster, dass ein äußerer Runtime-/Composition-Owner eine Connection erzeugt, abhängige Objekte daraus konstruiert und die Connection am Ende selbst schließt. Der Web-Runtime selbst wird dabei nicht zur TUI-Abhängigkeit.

## Entscheidung

Für einen späteren produktiven read-only TUI-Composition-Root wird folgender minimale Ownership-Vertrag autorisiert:

1. Der äußere TUI-Composition-Root ist alleiniger Owner der von ihm geöffneten read-only SQLite-Connection.
2. Er öffnet für den gemeinsamen read-only TUI-Daten-/Health-Pfad genau eine Connection über die vorhandene `open_connection(..., read_only=True)`-Seam.
3. Aus dieser Connection dürfen `TuiDataPort` und ein später separat autorisierter Health-Provider konstruiert werden; beide leihen die Connection nur und schließen sie nicht.
4. `ProvowareDbTui` bleibt reiner Consumer injizierter Ports und erhält keine Connection-Ownership.
5. Der Composition-Root schließt die Connection genau einmal und auch bei Start-/Runtime-Fehlern über eine fail-safe `finally`-/Runtime-Close-Grenze.
6. Dieser Vertrag autorisiert weder einen zweiten Connection-Pool noch Writer-Connection-Sharing, Events, Starter-Wiring oder eine Änderung eingefrorener Checkpoints.

**`TUI_READONLY_CONNECTION_OWNERSHIP_AUTHORIZED`**

## Freeze-Schutz

Unverändert bleiben CP-03, CP-08, Schema/Migrationen, Storage-Implementierung, Repositories, Application-Core, TUI-Runtime, Events, Writer-Lifecycle, Starter und alle eingefrorenen CP-09-Slices. Der bestehende Web-Lifecycle wird nicht verändert und nicht als TUI-Code wiederverwendet.

## Prüfungen

- aktuellen `main` und I77 als direkte Ausgangsbasis bestätigt;
- `ProvowareDbTui` weiterhin als Consumer eines injizierten `TuiDataPort` bestätigt;
- vorhandene read-only Connection-Factory und Web-Ownership nur als bestehende technische Grenzen geprüft;
- Vertrag verhindert doppelte Close-Verantwortung und unnötige zweite read-only Connection für Data/Health;
- keine Produktdatei in den I78-Write-Scope aufgenommen.

## Verbleibendes Risiko

Der Vertrag legt Ownership fest, implementiert aber noch keinen Composition-Root. Insbesondere ist noch nicht bewiesen, dass ein konkreter Health-Provider ohne zusätzliche Semantik ausschließlich auf I74/I76 aufbauen kann. Writer-Verbindungen bleiben vollständig getrennt.

## Nächster sicherer Schritt

Nach grünem I78-Gate separat den kleinsten produktiven read-only `HealthReadPort`-Provider gegen I74, I76 und diesen Ownership-Vertrag entwerfen und nur die dafür unmittelbar notwendigen Tests ausführen. Noch kein Starter- oder Writer-Wiring und kein Freeze-Reopen.
