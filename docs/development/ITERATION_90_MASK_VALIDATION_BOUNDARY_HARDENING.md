# Iteration 90 - Mask Validation Boundary Hardening

## Anlass

I89 wurde gemergt, danach blieben im Review zwei konkrete P2-Befunde offen:

1. Ein nicht-objektförmiger Eintrag in `fields` konnte vor der Fehlerübersetzung mit `AttributeError` ausbrechen.
2. Ein direkt erzeugtes `MaskFieldSpec(is_required="false")` konnte die gemeinsame Modellvalidierung passieren und gespeichert werden, obwohl der Loader denselben Wert später ablehnt.

## Schritt 1 - GRÜN

- `validate_template()` verlangt für `is_required` strikt einen echten Boolean.
- `template_from_dict()` verlangt `fields` als Liste aus JSON-Objekten, bevor `.get()` verwendet wird.
- Fokussierte Modellregressionen sichern beide Fehlerpfade.

Der Zwischen-Gate-Lauf 53 war vollständig grün.

## Schritt 2

Ohne weitere Produktcodeänderung sichern zwei Store-End-to-End-Regressionen die direkte Folge ab:

- `fields: ["bad"]` muss beim Laden kontrolliert zu `STORE-422` werden.
- Ein direkt konstruiertes nicht-boolesches `is_required` muss bereits vor dem Dateischreibpfad scheitern; es darf keine Vorlagendatei entstehen.

## Freeze-Schutz

CP-03, CP-06, Schema/Migrationen, Repositories, CatalogService, bestehende TUI/Web-Runtimes und Writer bleiben unverändert.

## Nächster Schritt

Nach grünem finalen Gate I90 SHA-gebunden squash-mergen. Erst danach darf der Browser-Maskeneditor als eigener UI-Slice wieder betrachtet werden.
