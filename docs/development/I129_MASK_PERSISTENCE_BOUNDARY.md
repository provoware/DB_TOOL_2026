# I129 – Persistenzgrenze für Masken

## Status

**PLAN/CONTRACT ONLY.** Diese Iteration öffnet keinen Browser-Write und verändert weder Datenbankschema noch produktive Persistenz.

## Ziel

Eine spätere Speicherung des Browser-Maskenentwurfs darf erst möglich werden, wenn exakt derselbe validierte Kandidat durch Preview, Integritätsprüfung und Recovery-Vorbereitung gegangen ist. Preview und Commit dürfen nicht auf unterschiedlichen Zuständen basieren.

## Geplanter Datenfluss

```text
Browser-Draft
  -> normalisierter Commit-Kandidat
  -> Validierung
  -> deterministische Preview
  -> Preview-Fingerprint
  -> explizite Bestätigung
  -> Recovery-Punkt
  -> atomarer Store-Commit
  -> Read-back + Fingerprint-Prüfung
  -> Abschlussstatus
```

Der Browser spricht später **nicht direkt** mit `MaskTemplateStore`. Eine eigene Application-Grenze erzeugt Kandidat, Preview und Commit-Auftrag.

## 1. Preview-Vertrag

Vor jedem produktiven Save muss ein unveränderlicher Kandidat vorliegen:

- normalisierte Feld- und Layoutdaten;
- Ziel-`template_id` und Zielversion;
- erwartete aktuelle Version oder `null` bei Neuanlage;
- deterministische serialisierte Repräsentation;
- SHA-256-Fingerprint des Kandidaten;
- sichtbare Vorher-/Nachher-Zusammenfassung;
- Liste aller fachlich relevanten Änderungen.

Die spätere Bestätigung bindet exakt diesen Fingerprint. Ändert sich der Draft danach, verfällt die Bestätigung.

## 2. Integritätsvertrag

Vor Commit müssen mindestens grün sein:

1. `require_valid_template(candidate)`;
2. sichere Vorlagen-ID und Pfadableitung;
3. erwartete Vorversion stimmt;
4. Zielversion ist bei Update strikt größer;
5. Kandidaten-Fingerprint stimmt mit bestätigter Preview;
6. kein Schema-/Frozen-Core-Drift;
7. atomarer Temp-Write + `fsync` + `os.replace`;
8. anschließendes `load(template_id)`;
9. Read-back serialisiert deterministisch zum erwarteten Kandidaten;
10. Read-back-Fingerprint stimmt mit dem bestätigten Kandidaten.

Ein Fehler führt zu **kein PASS** und darf nicht als teilweiser Erfolg behandelt werden.

## 3. Recovery-Vertrag

Vor Überschreiben einer bestehenden Vorlage muss ein Recovery-Artefakt vorhanden sein:

- vollständige vorherige validierte Version;
- ursprünglicher Fingerprint;
- Zielpfad;
- Versionsnummer;
- Zeit-/Vorgangskennung;
- Referenz auf den bestätigten Preview-Fingerprint.

Regeln:

- kein produktiver Update-Commit ohne erfolgreich geschriebenen Recovery-Punkt;
- Neuanlage benötigt einen eindeutigen Delete-/Rollback-Plan;
- Recovery schreibt nicht blind zurück: Zielzustand und Version werden vor Restore geprüft;
- Restore ist eine eigene bestätigte Operation mit Vorher-/Nachher-Preview;
- beschädigte oder nicht validierbare Recovery-Artefakte blockieren den Write.

## 4. Konflikt- und Parallelitätsvertrag

- Updates benötigen `expected_current_version`.
- Zusätzlich wird der vorher gelesene Fingerprint gebunden.
- Version oder Fingerprint abweichend -> Konflikt, kein Write.
- Pro `template_id` darf nur ein produktiver Commit gleichzeitig aktiv sein.
- Der bestehende globale Single-Writer-Vertrag darf später als zusätzliche Schutzschicht genutzt werden, wird durch I129 aber nicht autoritativ geschaltet.

## 5. Verantwortungsgrenzen

### Browser
- Draft bearbeiten
- Preview anzeigen
- Bestätigung auslösen
- keine Store-Imports
- kein Dateisystemzugriff

### Application-Grenze
- Draft in Kandidat übersetzen
- validieren
- Preview/Fingerprint erzeugen
- Bestätigung prüfen
- Recovery vorbereiten
- Store-Commit orchestrieren
- Read-back verifizieren

### MaskTemplateStore
- validierte Vorlage atomar speichern/laden
- Versionskonflikte fail-closed behandeln
- keine UI-Entscheidungen

## 6. Nicht-Scope

- kein HTTP-POST/PUT/PATCH
- keine Browser-Persistenz
- keine Änderung an `MaskTemplateStore`
- keine Änderung an `MaskTemplate` oder Schema-Version
- keine SQLite-Persistenz
- kein CP-03-/CP-06-Reopen
- kein Undo/Redo-UI
- keine produktive Recovery-Implementierung

## 7. Spätere Implementierungs-Gates

Eine produktive Save-Funktion braucht mindestens:

1. reine Kandidaten-/Preview-Funktion mit deterministischem Fingerprint;
2. Konflikt- und Manipulations-Negativtests;
3. isoliertes Store-Labor für Create/Update/Crash-Szenarien;
4. Recovery-Punkt + Restore-Labor;
5. atomare Commit-/Read-back-Verifikation;
6. HTTP-/UI-Grenze erst nach grüner Service-Schicht;
7. reale Browser-Evidence für Preview, Bestätigung, Fehlermeldungen und Fokus.

Bis diese Gates separat abgeschlossen sind, bleibt der Browser-Draft flüchtig.
