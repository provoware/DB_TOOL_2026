# Iteration 22 – CP-07 next-scope resolution

## Zweck

Iteration 22 ist ausschließlich ein Planungs- und Schutzgrenzen-Gate. Nach dem in Iteration 21 konsolidierten CP-07H-Nur-Lese-Checkpoint wird der nächste sichere Funktionsblock festgelegt, ohne Produktcode zu verändern.

## Befund aus aktuellem main

Der dokumentierte Zielstand nennt CP-07 UI Foundation weiterhin als „in Validierung“. Der bereits eingefrorene CP-07H-Browserpfad deckt Kategorie → Eintrag → Felder, sichtbare Werte, Nur-Lese-Suche, Tastatur/Enter-Suche und die explizite Nur-Lese-Grenze ab. Nicht eingefroren sind insbesondere Textual-Runtime-/Snapshot-Arbeit, Schreibpfade, CRUD, Papierkorb/Restore/Undo und weitere unbegründete Theme-/Responsive-Arbeit.

Daraus folgt: Ein Wechsel zu Schreib-/CRUD-Funktionen wäre verfrüht. Der nächste logisch sichere Block bleibt innerhalb CP-07 und schließt zuerst die noch offene UI-Foundation-Validierung.

## Gewählter nächster Funktionsblock

**CP-07T – Textual Runtime / Snapshot Validation**

Ziel des späteren Funktionsbranches ist ausschließlich zu beweisen, dass die vorhandene Textual-Oberfläche den eingefrorenen Service-/Repository-Kern ohne direkte SQL-Zugriffe und ohne Schreibpfade korrekt nutzt und in den vorgesehenen Terminalgrößen stabil darstellbar ist.

## Scope

Erlaubt sind nur:

- Inventur der vorhandenen Textual-UI und ihrer Start-/Runtime-Pfade,
- bestehende Kategorie-, Eintrag- und Feld-Lesepfade anbinden oder validieren,
- Tastatur-/Fokusführung validieren,
- Snapshot-/Layout-Tests für repräsentative Terminalgrößen ergänzen, sofern im aktuellen Stand noch nicht vorhanden,
- ausschließlich reproduzierbare CP-07T-Befunde minimal beheben.

## Non-Goals

Ausdrücklich nicht Teil von CP-07T sind:

- Änderungen an CP-03 Schema V1 oder Migrationen,
- Änderungen an CP-06 / Frozen Core ohne explizites REOPEN,
- Änderungen an der SQLite-Repository-Schicht,
- neue SQL-Zugriffe aus einer UI,
- Schreib-, CRUD-, Papierkorb-, Restore- oder Undo-Oberflächen,
- neue Produktfeatures außerhalb der UI-Foundation,
- kosmetische Theme-/Responsive-Arbeit ohne reproduzierbaren Gate-Befund,
- Änderungen am eingefrorenen CP-07H-Browserpfad ohne konkreten Regressionbefund.

## Freeze-Grenzen

CP-03, Schema/Migrationen, CP-06/Frozen Core, SQLite-Repository-Schicht und der in Iteration 21 konsolidierte CP-07H-Nur-Lese-Browserpfad bleiben geschlossen. Jeder notwendige Eingriff dort benötigt einen separat dokumentierten REOPEN-Grund und ist nicht Bestandteil dieses Scopes.

## Minimale Exit-Gates für den späteren CP-07T-Funktionsblock

1. Syntax/Compile nur für tatsächlich betroffene Textual-Dateien.
2. Gezielt betroffene Textual-Unit-/Integrationstests.
3. Nachweis: kein direkter SQL-Zugriff aus der Textual-UI.
4. Nachweis: keine mutierende UI-Route bzw. kein neuer Schreibpfad.
5. Snapshot-/Layout-Gate für mindestens 80×24 und einen großen Referenzviewport; weitere Größen nur bei konkretem Responsive-Befund.
6. Tastatur-/Fokus-Smoke für die tatsächlich berührte Navigation.
7. Frozen-Grenzen unverändert; bei Abweichung Gate ROT und kein Merge.
8. Kein Full-Suite-Lauf ohne Dependency-/Regressionstrigger.

## Exit-Kriterium dieser Planungsiteration

Iteration 22 selbst ist abgeschlossen, wenn ausschließlich dieses Scope-Dokument auf einem frischen Branch gegen den aktuellen `main` geprüft wurde und Repository-/Governance-Gates grün sind. Erst danach darf ein separater CP-07T-Funktionsbranch vom dann aktuellen `main` eröffnet werden.

## Nächster Schritt

Nach grünem Planungs-Gate: Scope-PR mergen und einfrieren. Danach auf einem neuen Branch zunächst nur die Textual-Runtime inventarisieren und den kleinsten reproduzierbaren CP-07T-Validierungsblock auswählen; noch keine Schreibfunktion beginnen.
