# I159 – Integrationsvertrag Feldwertsuche

## Ziel

Die Verbindung **Repository → CatalogService → SearchHit** für Feldwerttreffer separat planen und gaten. Diese Iteration verändert noch keine Runtime.

## Ausgangslage

Das I157/I158-Labor liefert für alle Feldtypen bereits read-only Treffer mit:
- Kategorie-ID/-Name,
- Eintrag-ID/-Titel,
- Feld-ID/-Name,
- formatierter Wertvorschau,
- deterministischer Sortierung,
- Deleted-Parent-/Deleted-Option-Schutz,
- globalem Labor-Limit,
- No-Write-Nachweis.

I156 projiziert für bestehende Treffer bereits eindeutige Fundstellen und stabile Detail-/Feldziele.

## Integrationsvertrag

### Repository

Der bisherige Laborread wird in der Produktiteration in einen neutral benannten Read-Pfad überführt, z. B. `search_values()`.

Er bleibt:
- read-only,
- parametergebunden,
- ohne Schemaänderung,
- ohne FTS/Index,
- deterministisch,
- mit Deleted-Parent-Schutz.

### CatalogService

`CatalogService.search()` bleibt der einzige Application-Einstiegspunkt.

Reihenfolge:
1. Kategorie,
2. Eintrag,
3. Feldname,
4. Feldwert.

Das bestehende globale `limit` bleibt am Service-Ende autoritativ. Leere Suche bleibt `[]`.

### SearchHit

Für Rückwärtskompatibilität bleiben bestehende Felder erhalten. Feldwerttreffer benötigen zusätzlich optionale Projektion:

- `match_kind`: `category_name | entry_title | field_name | field_value`
- `field_id`: Feld-ID für stabile Navigation
- `value_preview`: bereits formatierte Wertvorschau nur für `field_value`

Bestehende Treffer dürfen dadurch semantisch nicht verändert werden.

### Web-Read-Projektion

I156 bleibt verantwortlich für:
- Kategorie-/Eintrags-/Feld-Kontext,
- Fundstellenkette,
- ID-basierte Navigation.

Für `field_value` wird die Feldbezeichnung weiterhin als Trefferlabel verwendet; `value_preview` wird separat sichtbar angezeigt. Ziel ist `#field-<id>`.

## Gate-Grenze

Die spätere Umsetzung berührt:
- `src/provoware_db/storage/`,
- `src/provoware_db/application/catalog_service.py`,
- `src/provoware_db/domain/models.py`.

Damit ist die Produktintegration **Frozen-Core/Deep-Gate**.

## End-to-End-Abnahmekriterien der Folgeiteration

- Feldwerttreffer aller Feldtypen erreichbar,
- bestehende Kategorie-/Eintrag-/Feldnamen-Treffer unverändert,
- eindeutige Fundstellenkette,
- stabiler Feldanker,
- globales Limit,
- leere Suche,
- Deleted-Parent-/Deleted-Option-Schutz,
- `sqlite3.total_changes` unverändert,
- POST weiterhin 405,
- keine Schemaänderung,
- keine Persistenz.

## Nicht enthalten

- keine Runtime-Änderung,
- kein Repository-Patch,
- kein SearchHit-Patch,
- keine Service-Anbindung,
- keine Web-Anbindung,
- kein TODO-Abschluss der globalen Feldwertsuche.
