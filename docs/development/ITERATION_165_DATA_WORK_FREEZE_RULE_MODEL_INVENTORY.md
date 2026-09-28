# Iteration 165 – Datenarbeits-Freeze und Regelmodell-Inventur

## Ziel

Den bestätigten persistenzfreien Datenarbeitsblock C auf dem grünen I164-Stand einfrieren und den unmittelbar nächsten unabhängigen Produktbereich D ausschließlich als Planungsauftrag für ein gemeinsames Regelmodell abgrenzen.

## Schritt 1 – Persistenzfreien Datenkomfort einfrieren

I148–I164 bestätigen Suche, Filter, Sortierung, starke Detailansicht, eindeutige Feldwert-Fundstellen, den GET-only Favoritenfilter sowie browserlokale Mehrfachauswahl und Massenaktions-Preview. Diese Funktionen bleiben read-only beziehungsweise flüchtig; I165 verändert ihr Runtime-Verhalten nicht.

Der Freeze umfasst ausdrücklich **nicht**:

- „zuletzt verwendet“, weil ohne Usage-State keine korrekte Nutzungszeit existiert,
- gespeicherte Ansichten, weil sie einen eigenen Persistenz- und Recovery-Vertrag benötigen,
- das Ausführen von Massenaktionen, weil Preview allein keinen produktiven Write autorisiert.

**Zwischen-Gate:** Der bestätigte I164-Stand bleibt unverändert, der Fortschritt bleibt 39/132, alle drei persistenzabhängigen Punkte bleiben offen und CP-03/CP-06 geschlossen. Damit ist Schritt 1 GRÜN.

## Schritt 2 – Gemeinsames Regelmodell inventarisieren

Der nächste unabhängige Scope ist `D · Regeln und Validierung → gemeinsames Regelmodell planen`. Eine Folgeiteration darf zunächst nur einen Vertrag festlegen, der:

1. Regeldefinition und Feldbezug typisiert beschreibt,
2. dieselbe Regel für Preview und spätere Aktivierung auswertbar macht,
3. Fehler eindeutig Feld und Regel zuordnet,
4. laienverständlich erklärt, was nicht passt und wie es behoben werden kann,
5. eine rein temporäre Preview vor jeder produktiven Aktivierung vorsieht.

Diese Inventur gibt weder einzelne Regeltypen noch Persistenz, Schemaänderungen oder produktive Aktivierung frei. Der kleinste Folgeslice ist deshalb eine separate Vertragsiteration; erst danach darf über eine temporäre Regel-Preview entschieden werden.

## Risiken und Schutzgrenzen

- Kein Regeltyp darf vor dem gemeinsamen Modell als Sonderlogik implementiert werden.
- Preview und spätere Aktivierung dürfen nicht unterschiedliche Auswertungssemantik erhalten.
- Fehlertexte dürfen keine internen Exceptions an Nutzende durchreichen.
- Produktive Regelaktivierung benötigt weiterhin einen eigenen Write-, Integritäts- und Recovery-Vertrag.
- CP-03, CP-06, Repository, Schema, Dependencies und Runtime bleiben unverändert.

## Laienhilfe-Delta

„Eingefroren“ heißt hier: Der aktuell sichere, nicht speichernde Komfortumfang ist geprüft und wird nicht nebenbei erweitert. Es heißt nicht, dass alle Wünsche erledigt sind. Funktionen, die Nutzungsdaten speichern oder viele Einträge verändern, warten weiterhin auf eigene Sicherheitsregeln. Als Nächstes wird nur festgelegt, wie Validierungsregeln künftig einheitlich beschrieben und verständlich erklärt werden sollen.

## Gate

- Dokument- und Manifeststruktur prüfen.
- Fortschritt und offene Checkboxen konsistent halten.
- Single-Source-Preflight ausführen.
- Keine Produkt-, UI-, Storage- oder Chromium-Tests, weil kein Runtime-Pfad geändert wird.
