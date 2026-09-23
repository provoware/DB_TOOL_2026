# Iteration 90 - Mask Validation Boundary Hardening

## Anlass

I89 wurde gemergt, danach blieben im Review zwei konkrete P2-Befunde offen:

1. Ein nicht-objektförmiger Eintrag in `fields` konnte vor der Fehlerübersetzung mit `AttributeError` ausbrechen.
2. Ein direkt erzeugtes `MaskFieldSpec(is_required="false")` konnte die gemeinsame Modellvalidierung passieren und gespeichert werden, obwohl der Loader denselben Wert später ablehnt.

## Zwei-Schritt-Plan

### Schritt 1 - Primärkorrektur

- `validate_template()` verlangt für `is_required` strikt einen echten Boolean.
- `template_from_dict()` verlangt `fields` als Liste aus JSON-Objekten, bevor `.get()` verwendet wird.
- Fokussierte Modellregressionen sichern beide Fehlerpfade.

### Schritt 2 - direkte Folgemaßnahme

Nur nach grünem Zwischen-Gate werden Store-End-to-End-Regressionen ergänzt:

- malformed `fields: ["bad"]` muss beim Laden zu `STORE-422` werden,
- direkt konstruierte nicht-boolesche Pflichtfeldwerte dürfen nicht gespeichert werden und keine Datei hinterlassen.

## Freeze-Schutz

CP-03, CP-06, Schema/Migrationen, Repositories, CatalogService, bestehende TUI/Web-Runtimes und Writer bleiben unverändert.

## Nächster Schritt

Nach grünem Schritt 1 ausschließlich Schritt 2 ergänzen. Erst nach finalem Gate darf der Browser-Maskeneditor wieder betrachtet werden.
