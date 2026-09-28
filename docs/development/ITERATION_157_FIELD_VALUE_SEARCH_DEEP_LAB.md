# I157 – isoliertes Deep-Gate-Labor Feldwertsuche

## Ziel

Den ersten Repository-Read für die geplante globale Feldwertsuche **isoliert** untersuchen und absichern. Es erfolgt noch keine Service- oder Web-Integration.

## Laborumfang

`FieldRepository.search_value_lab()` durchsucht ausschließlich:

- `text` und `long_text` über gespeicherten `value_text`,
- aktive Single-Choice-Optionsbezeichnungen,
- aktive Multi-Choice-Optionsbezeichnungen.

Treffer enthalten nur den für den späteren I153/I154-Vertrag notwendigen Kontext:

- Kategorie-ID/-Name,
- Eintrag-ID/-Titel,
- Feld-ID/-Name,
- Wertvorschau,
- interne Labor-Quellart.

## Sicherheitsinvarianten

- leerer Suchbegriff bzw. `limit <= 0` liefert keine Treffer,
- gelöschte Kategorien, Einträge, Felder und Optionen sind ausgeschlossen,
- Felddefinition muss tatsächlich auf den Eintrag anwendbar sein,
- Multi-Choice-Treffer werden pro Eintrag/Feld deterministisch zusammengeführt,
- globales Limit wird nach deterministischer Sortierung angewendet,
- keine Writes, kein Audit und keine Persistenzmutation,
- Methode ist nicht an `CatalogService.search()`, Web-Adapter oder HTTP angebunden.

## Bewusst noch nicht enthalten

- Integer/Decimal/Money,
- Boolean,
- Date/Datetime,
- Service-Integration,
- Web-/Fundstellenintegration,
- produktiver TODO-Abschluss der globalen Feldwertsuche,
- FTS/Index/Schemaänderung.

## Deep-Gate-Begründung

Die Änderung berührt `src/provoware_db/storage/` und damit CP-06/Frozen Core. Deshalb ist ausschließlich `gate_profile=deep` zulässig. Ein grünes Labor bedeutet nur, dass dieser isolierte Read-Baustein tragfähig ist; es autorisiert **keine** automatische Produktintegration.
