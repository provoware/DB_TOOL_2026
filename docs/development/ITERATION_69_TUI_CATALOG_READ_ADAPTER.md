# Iteration 69 – TUI Catalog Read Adapter

## Änderung

Schritt 1 bestätigt den I68-Vertrag gegen den aktuellen `main`: `TuiDataPort` erwartet weiterhin Kategorie, Entry, Feld/Wert, Health und Events. `CatalogService` liefert die drei fachlichen Navigations-Reads bereits; `HealthItem` und `EventItem` sind fertige TUI-Projektionen. Es entsteht deshalb kein Grund für SQL-, Repository-, Domain-, CP-03- oder CP-08-Änderungen.

Das Zwischen-Gate ist fachlich grün. Schritt 2 implementiert ausschließlich `TuiCatalogReadAdapter`.

## Adaptergrenze

Der Adapter:

- projiziert `list_categories()` auf `NavItem`;
- projiziert `list_entries(category_id)` auf `NavItem`;
- projiziert `list_fields_with_values(entry_id)` auf `FieldRow`;
- verwendet den bestehenden neutralen `field_type_label`-Helper;
- erhält Health und Events als getrennte injizierte Read-Quellen;
- reicht das Event-Limit unverändert weiter.

Er öffnet keine Connection, führt kein SQL aus, konstruiert keinen `CatalogService`, kennt keinen Writer und verändert keinen Runtime-Zustand.

## Formatierung

Die TUI-Wertedarstellung bleibt vorerst lokal. Sie importiert ausdrücklich nichts aus `provoware_db.web`. Eine gemeinsame neutrale Werteprojektion darf erst entstehen, wenn die Duplikation in einer eigenen Iteration begründet und gegen beide Oberflächen abgesichert wird.

## Freeze-Schutz

Unverändert bleiben insbesondere CP-03, Schema/Migrationen, Storage/Repositories, CP-08-Semantik, `CatalogService`, TUI-Runtime, Writer und Composition Root.

## Exit-Gates

1. Adapter und fokussierter Test kompilieren.
2. Kategorie/Entry/Feld-Wert-Projektion ist grün.
3. Health/Event-Delegation inklusive Limit ist grün.
4. Shared-FieldType-Label-Regression bleibt grün.
5. Manifest-/Write-Scope bleibt exakt auf vier I69-Dateien begrenzt.
