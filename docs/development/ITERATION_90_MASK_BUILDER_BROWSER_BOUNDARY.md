# Iteration 90 – Masken-Baukasten Browser-Grenze

## Ziel

I90 klärt ausschließlich die kleinste sichere Grenze für den lokalen Browser-Editor des Masken-Baukastens. Es wird noch keine UI implementiert und kein bestehender Web-Runtime-Pfad verändert.

## Schritt 1 – Scope-Entscheidung

Der Editor wird **nicht** in `provoware_db.web.http_app` eingebaut. Dieser bestehende WSGI-Pfad ist ausdrücklich GET-only und dient dem lesenden Katalog. Eine Editor-Route dort würde dessen Sicherheitsvertrag unnötig aufweiten.

Der Masken-Editor erhält stattdessen später eine eigene lokale UI-Grenze innerhalb von `provoware_db.mask_builder`. Diese Grenze darf ausschließlich mit `MaskTemplate`, `MaskTemplateStore`, `validate_template` und der deterministischen Vorschau `build_application_plan` arbeiten.

Nicht zulässig sind direkte Datenbank-Repositories, SQL, Writer, CatalogService-Schreibpfade oder Änderungen an CP-03/CP-06.

## Schritt 2 – Minimaler UI-Vertrag

Der erste spätere Implementierungsslice wird auf drei read-/preview-orientierte Bausteine begrenzt:

1. **Komponentenpalette**: vorhandene `MaskElementKind`- und `FieldType`-Möglichkeiten anzeigen.
2. **12-Spalten-Canvas**: Elemente aus einem `MaskTemplate` deterministisch darstellen; noch kein produktiver Datenbankbezug.
3. **Live-Vorschau**: ausschließlich `validate_template` und `build_application_plan` verwenden; ungültige Vorlagen fail-closed anzeigen.

Drag & Drop, Resize, Undo/Redo, persistierende Editor-Aktionen und Vorlagenmenü bleiben nachgelagerte Slices. Damit entsteht zuerst eine kleine, testbare Darstellungsgrenze statt eines großen UI-Batches.

## Sicherheits- und Freeze-Grenzen

- CP-03 und CP-06 bleiben unverändert.
- Keine Schema-/Migrationsänderung.
- Keine Repository-/CatalogService-Änderung.
- Keine Writer- oder SQL-Anbindung.
- `src/provoware_db/web/http_app.py` bleibt unverändert und GET-only.
- Keine neue Runtime-Abhängigkeit.
- Vorlagenpersistenz bleibt ausschließlich beim bereits vorhandenen `MaskTemplateStore`.

## Prüfentscheidung

Da I90 nur die Architekturgrenze dokumentiert, sind keine Produktivtests ausgelöst. Geprüft werden ausschließlich Scope-Konsistenz, vorhandener GET-only-Webvertrag und die direkte I88/I89-Mask-Builder-Grenze.

## Nächster Slice

I91 darf als kleinste Produktänderung eine eigenständige, lokale, nicht-datenbankschreibende Browser-Darstellung für Palette + 12-Spalten-Canvas beginnen. Die Vorschau muss auf dem bestehenden Modellvertrag aufsetzen; bestehende Web-, Datenbank- und Frozen-Core-Pfade bleiben unangetastet.
