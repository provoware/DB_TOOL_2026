# PROVOWARE Entwicklungs- und Validierungsstandard

Diese Regeln sollen Änderungen sicher, klein und nachvollziehbar halten.

## 1. Sprache und Bedienbarkeit

Anleitungen werden so geschrieben, dass sie auch ohne Entwicklerwissen verständlich bleiben.

Wenn ein Fachbegriff nötig ist, wird er kurz erklärt.

Für lokale Terminalschritte wird, wenn sinnvoll, ein einziger kopierbarer Kettenbefehl bevorzugt.

## 2. Gate-Status

- 🟢 **GRÜN:** alle für diesen Schritt notwendigen Prüfungen bestanden.
- 🟡 **GELB:** kein bestätigter Fehler, aber eine notwendige Prüfung fehlt oder ist blockiert.
- 🔴 **ROT:** Fehler, Regression oder Schutzverletzung gefunden.
- 🔒 **FROZEN:** geschützter Bereich bleibt unverändert.

Ein rotes Gate wird nicht umgangen. Zuerst wird nur die konkrete Ursache behoben und danach erneut geprüft.

## 3. Welche Prüfungen sind nötig?

Die Prüfungen richten sich nach der Änderung.

### Nur Dokumentation
- Dateipfade und Links prüfen
- Struktur und Verständlichkeit prüfen
- kein Produktivtest ohne konkreten Grund

### UI, CSS oder HTML
- direkt betroffene UI-Tests
- Tastatur/Fokus, wenn betroffen
- relevante Zielgrößen
- Screenshot nur bei visueller Kernänderung oder vorgesehenem Screenshot-Meilenstein

### Application Service
- direkt betroffene Service-Tests
- notwendige Repository-Mocks oder Integrationen

### Domain oder Repository
- direkte Unit-/Integrations-Regression
- Frozen-Core-Gate, wenn ein geschützter Bereich berührt wird

### Schema oder Migration
- Migration prüfen
- Schema-Hash beziehungsweise Manifest prüfen
- `foreign_key_check`
- `integrity_check`
- vollständige Regression des betroffenen Datenbankpfads

## 4. Selbstvalidierung

Ein Gate prüft, soweit für die Änderung relevant:

- erwartete Dateien und Projektpfad,
- Python-Version,
- benötigte Abhängigkeiten,
- Frozen-Core-Schutz,
- Syntax oder Compile,
- direkt betroffene Tests,
- engste sinnvolle Regression,
- bei Datenbankänderungen Integritätsprüfungen,
- bei UI-Änderungen Tastatur, Fokus und relevante Layoutprüfungen,
- echten Prozess-Exitcode.

Nicht betroffene Prüfungen werden nicht künstlich ausgeführt.

## 5. Auswertung

Ein größerer Gate-Lauf dokumentiert mindestens:

- Datum und Projektstand,
- Iteration oder Checkpoint,
- ausgeführte Prüfungen,
- bestanden / fehlgeschlagen / übersprungen,
- Warnungen oder Blockaden,
- GRÜN / GELB / ROT,
- nächsten sinnvollen Schritt.

## 6. Änderungsvolumen

Am Abschluss wird kurz genannt:

- neue Dateien,
- geänderte Dateien,
- gelöschte Dateien,
- ausgeführte Tests,
- betroffene Schichten,
- Freeze-Status.

## 7. Sicherheitsregel

Produktive Daten werden nicht verändert, nur damit ein Test ausgeführt werden kann.

Testdaten und Testpfade müssen eindeutig isoliert sein.

## 8. Historische Nachweise

Dateien unter `docs/development/` können historische Entscheidungen und Gate-Nachweise enthalten. Sie werden nicht nachträglich kosmetisch vereinheitlicht, wenn dadurch die Auditspur verändert würde.
