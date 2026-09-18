# CatalogService Scope nach Iteration 8

Automatische AST-Abhängigkeitsanalyse gegen den vollständigen eingefrorenen CP-07-Quellstand.

## Ergebnis

Transitive lokale Python-Dateien für den unveränderten `CatalogService`: **18**.

Nach Iteration 8 bereits vorhanden: **8** relevante Abhängigkeiten plus Repository-Paketexport.

Noch fehlend: **10 Dateien**:

1. `provoware_db/application/catalog_service.py`
2. `provoware_db/storage/sqlite/audit.py`
3. `provoware_db/storage/sqlite/constants.py`
4. `provoware_db/storage/sqlite/coordinator.py`
5. `provoware_db/storage/sqlite/errors.py`
6. `provoware_db/storage/sqlite/operation_journal.py`
7. `provoware_db/storage/sqlite/schema_guard.py`
8. `provoware_db/storage/sqlite/schema_manifest.py`
9. `provoware_db/storage/sqlite/unit_of_work.py`
10. `provoware_db/validation/gates.py`

## Gate-Entscheidung

🟡 **Noch kein S/M-Patch möglich.**

10 fehlende Dateien entsprechen nach `AGENTS.md` einem **L-Patch**. Der echte unveränderte `CatalogService` wird deshalb in Iteration 8 **nicht** an `WebCatalogReadAdapter` angeschlossen.

## Nächste optimale Zerlegung

Zuerst die kleineren Infrastructure-Abhängigkeiten importieren:
- constants
- errors
- schema_manifest
- schema_guard
- unit_of_work

Danach erneut berechnen. Audit/Coordinator/OperationJournal/Gates bleiben bis dahin getrennt.

Diese Entscheidung verhindert einen unnötigen XL-/L-Sprung und hält Review und Regression gezielt.
