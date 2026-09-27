# I134 – Persistenz-Laborprogramm für Masken

## Status

**PROGRAMMPLAN / KEIN PRODUKTIVER SAVE.**

I134 zerlegt die in I129 definierte Persistenzgrenze in isolierte Laboriterationen. Keine dieser Laboriterationen darf allein einen Browser-, HTTP- oder produktiven Save-Pfad freischalten. Eine spätere Freigabe benötigt nach Abschluss aller Labore eine eigene Release-Iteration mit explizitem Gate.

## Ziel

Die Persistenzarbeit wird in drei unabhängige Risikostränge geteilt:

1. **Service-Labor** – Kandidat, Preview, Fingerprint und Commit-Orchestrierung.
2. **Recovery-Labor** – Recovery-Punkt, Restore-Plan und Wiederherstellungs-Simulation.
3. **Integritäts-Labor** – atomarer Commit, Read-back, Manipulations-/Crash- und Konkurrenzfälle.

Jeder Strang wird zunächst gegen temporäre Testverzeichnisse und injizierte/isolierte Store-Grenzen geprüft. Produktive UI- oder HTTP-Routen bleiben geschlossen.

## Abhängigkeitsgraph

```text
I135 Service-Lab A · Kandidat/Preview/Fingerprint
   ├──> I136 Service-Lab B · isolierter Commit-Orchestrator
   └──> I137 Recovery-Lab A · Recovery-Snapshot
             └──> I138 Recovery-Lab B · Restore-Plan/Simulation

I136 + I137
      └──> I139 Integrity-Lab A · atomarer Commit + Read-back

I138 + I139
      └──> I140 Integrity-Lab B · TOCTOU/Konkurrenz/Crash-Matrix

I135–I140 alle GRÜN
      └──> separate spätere RELEASE-ITERATION
           (nicht durch I134 freigegeben)
```

## Track S – Service

### I135 · Service-Lab A – Kandidat, Preview und Fingerprint

**Risikoklasse:** B, read-only/reine Transformation.

Ziel:
- Browser-Draft oder synthetischen Draft in einen unveränderlichen Commit-Kandidaten übersetzen;
- Kandidaten deterministisch normalisieren;
- `require_valid_template` anwenden;
- Vorher-/Nachher-Preview erzeugen;
- SHA-256-Fingerprint exakt über die deterministische Kandidatenrepräsentation bilden.

Mindestverträge:
- gleiche Eingabe -> gleicher Kandidat -> gleicher Fingerprint;
- Feld-/Elementreihenfolge wird nur nach ausdrücklich definierten Regeln normalisiert;
- unbekannte/inkompatible Draft-Zustände fail-closed;
- Preview und Fingerprint entstehen aus **demselben** Kandidatenobjekt;
- keine Store-`save`-Methode;
- kein Dateisystem-Write;
- kein HTTP-Write.

Negativtests:
- mutierter Draft nach Preview;
- ungültige IDs;
- ungültiges Raster;
- Choice-Default verweist auf fehlende Option;
- nicht deterministische Eingabereihenfolge darf keinen zufälligen Fingerprint erzeugen.

**Exit-Gate:** reine Service-Tests grün, keinerlei produktiver Write-Pfad.

### I136 · Service-Lab B – isolierter Commit-Orchestrator

**Voraussetzung:** I135 GRÜN.

Ziel:
- einen bereits bestätigten Kandidaten + Preview-Fingerprint entgegennehmen;
- erwartete aktuelle Version und vorherigen Fingerprint binden;
- einen injizierten isolierten Store ansprechen;
- Commit nur ausführen, wenn Bestätigung und Kandidat identisch sind.

Laborgrenzen:
- ausschließlich `tmp_path`/temporäres Verzeichnis;
- keine Browserroute;
- kein produktiver Standardpfad;
- keine Änderung des SQLite-Kerns;
- kein globaler Aktivierungsschalter.

Negativtests:
- Kandidat nach Bestätigung verändert;
- falscher Preview-Fingerprint;
- Versionskonflikt;
- falscher vorheriger Fingerprint;
- Store-Fehler;
- erneuter Commit derselben Bestätigung.

**Exit-Gate:** Commit-Orchestrator ist reproduzierbar, aber nur als Labor/API ohne Produktfreigabe vorhanden.

## Track R – Recovery

### I137 · Recovery-Lab A – Recovery-Snapshot

**Voraussetzung:** I135 GRÜN.

Ziel:
Vor einem isolierten Update wird die vollständige vorherige validierte Version als Recovery-Snapshot erzeugt.

Snapshot enthält mindestens:
- Template-ID;
- vorherige Version;
- deterministische vollständige Repräsentation;
- SHA-256-Fingerprint;
- Zielpfad/Store-Schlüssel;
- Operation-ID;
- gebundenen neuen Preview-Fingerprint.

Regeln:
- Update ohne erfolgreichen Snapshot -> blockiert;
- beschädigter Altzustand -> blockiert;
- Snapshot selbst wird nach dem Schreiben erneut gelesen und validiert;
- Neuanlage erhält statt Alt-Snapshot einen expliziten Create-Rollback-Plan.

**Exit-Gate:** Recovery-Artefakt ist vollständig, validierbar und vor Commit erzwingbar – weiterhin nur im Labor.

### I138 · Recovery-Lab B – Restore-Plan und Simulation

**Voraussetzung:** I137 GRÜN.

Ziel:
- Recovery-Artefakt lesen;
- aktuellen Zielzustand prüfen;
- Restore als deterministischen Plan erzeugen;
- Vorher-/Nachher-Vorschau und Restore-Fingerprint darstellen;
- Restore zunächst simulieren und erst im isolierten Labor anwenden.

Konfliktregeln:
- Zielversion verändert -> Restore blockiert;
- Ziel-Fingerprint verändert -> Restore blockiert;
- Recovery-Fingerprint ungültig -> Restore blockiert;
- Template-ID/Store-Ziel abweichend -> blockiert;
- stilles Überschreiben fremder Änderungen verboten.

**Exit-Gate:** Restore-Plan, Simulation und isolierter Restore grün; keine produktive Restore-Schaltfläche.

## Track I – Integrität

### I139 · Integrity-Lab A – Commit + Read-back-Verifikation

**Voraussetzungen:** I136 und I137 GRÜN.

Ziel:
Die bestehende atomare Store-Technik wird über den Labor-Orchestrator als vollständige Transaktion geprüft:

```text
Recovery vorhanden
-> bestätigter Kandidat
-> Temp-Write
-> fsync
-> os.replace
-> load/read-back
-> deterministische Re-Serialisierung
-> SHA-256-Vergleich
-> PASS oder fail-closed
```

Tests:
- Neuanlage;
- gültiges Update;
- Store-Exception;
- manipulierte Datei nach Write;
- Read-back weicht vom Kandidaten ab;
- ungültige serialisierte Datei;
- Rest-`.tmp` nach simuliertem Fehler;
- Verzeichnis-Sync soweit Plattformvertrag testbar.

**Exit-Gate:** kein erfolgreicher Abschluss ohne identischen Read-back-Fingerprint.

### I140 · Integrity-Lab B – TOCTOU, Konkurrenz und Crash-Matrix

**Voraussetzungen:** I138 und I139 GRÜN.

Ziel:
Die gesamte Laborpipeline gegen Zustandsänderungen zwischen Preview und Commit härten.

Matrix:
- Version ändert sich nach Preview;
- Alt-Fingerprint ändert sich nach Preview;
- zwei Commit-Versuche auf dieselbe `template_id`;
- stale Bestätigung;
- Recovery-Snapshot gehört zu anderer Operation;
- Crash vor Snapshot;
- Crash nach Snapshot/vor Write;
- Crash während Temp-Write;
- Crash nach Replace/vor Read-back;
- Read-back-Fehler;
- Restore nach konkurrierender Änderung.

Erwartung:
- niemals stiller Last-Writer-Wins;
- niemals PASS bei unbestimmtem Endzustand;
- Wiederanlauf liefert klaren Status: unverändert / committed+verified / recovery-required;
- globale Shadow-Single-Writer-Mechanik darf untersucht, aber nicht autoritativ aktiviert werden.

**Exit-Gate:** Konflikt-/Crash-Matrix vollständig grün.

## Gemeinsame Laborregeln

Alle I135–I140:
- verwenden eigene Iterationsmanifeste;
- besitzen jeweils genau zwei vorab geplante Schritte;
- starten vom jeweils bestätigten Main-SHA;
- schreiben nur in explizit zugewiesene Dateien;
- verwenden temporäre Dateisystemziele;
- dürfen keine produktive Browser-/HTTP-Write-Route ergänzen;
- dürfen CP-03 oder CP-06 nicht nebenbei reopen;
- müssen Negativtests enthalten;
- müssen Fail-closed-Verhalten dokumentieren;
- müssen einen klaren Recovery-Key bzw. Rückweg angeben.

## Separate Release-Grenze

Nach I140 gilt **nicht automatisch „Save freigegeben“**.

Eine spätere Release-Iteration muss separat prüfen:
- alle Labor-SHAs/Gates;
- endgültige Application-API;
- Produktpfad und Berechtigungsgrenze;
- Preview-Bestätigung in der echten UI;
- Recovery-Bedienweg;
- reale Browser-Evidence;
- Fehlertexte;
- Upgrade-/Rollback-Verhalten;
- Frozen-Core-Impact.

Erst diese separate Release-Iteration darf entscheiden, ob ein produktiver Save-Pfad geöffnet wird.

## Ergebnis von I134

I129 bleibt der übergeordnete Sicherheitsvertrag. I134 macht daraus eine ausführbare, kleine Reihenfolge:

**Service zuerst → Recovery separat → Integrität/Crash zuletzt → Release ausdrücklich separat.**
