# I170 – I167-Abnahme unter ausdrücklicher Testausnahme

Basis: `main` c1506a1. Der Nutzer verlangte, eine echte HTML-/Screenshot-Route
zu suchen und andernfalls das Browser-Gate zu überspringen und als akzeptiert
zu behandeln. Die statische I167-Prüfung und der lokale HTTP-Smoke waren grün.

## Schritt 1 – Entscheidung und Zwischen-Gate

Es ist kein lokales Chrome-/Chromium-Binary vorhanden. Der Cloud-Browser sperrt
lokale `file:`-URLs durch seine Sicherheitsrichtlinie und untersagt Umwege.
Eine echte Browser-Screenshot-Evidence wurde daher nicht erzeugt. Der
Manifest-/Preflight-Scope ist grün; I167 wird **WAIVED_BY_USER** geführt.

## Schritt 2 – Statussynchronisierung

Die zwei Punkte „Pflichtwert“ und „Regel-Preview vor Aktivierung“ werden nur
für den vorhandenen browserlokalen Pflichtwert-Draft unter dieser ausdrücklichen
Testausnahme als akzeptiert gezählt. Fortschritt: 42/132 = 31,8 %. README,
TODO und Roadmap nennen dieselbe Grenze. Das ist eine Produktentscheidung,
**kein bestandener Chromium-Test** und keine generelle Ausnahme für spätere UI-Arbeit.

## Risiko und Laienhilfe

Eine unentdeckte Tastatur-, Tooltip- oder Layoutabweichung ist möglich. Die
Regel speichert und aktiviert nichts; Reload verwirft den Draft. Ein späterer
echter Browser-Test kann die Evidenzlücke schließen. CP-03/CP-06, Schema,
Repository, CI und produktive Schreibpfade bleiben unverändert.

## Abschlussgate

- Fast Context, Manifest V2, Preflight und Diff-Whitespace: GRÜN.
- A–M-Checkboxen: 42 erledigt, 90 offen; README/TODO konsistent.
- Fünf geplante Dokumentationsdateien; keine Produkt- oder Testdatei geändert.
- Chromium-/Screenshot-Gate: **WAIVED_BY_USER**, nicht PASS.
