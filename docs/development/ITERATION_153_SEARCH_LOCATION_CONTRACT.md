# I153 – Fundstellenvertrag für Suchtreffer

## Ziel

Den offenen Punkt **C · Fundstelle eindeutig anzeigen** als eigenständigen Read-only-Vertrag planen. Noch keine Runtime- oder Repository-Änderung.

## Ausgangslage

Aktuelle `SearchHit`-Treffer enthalten:
- `entity_type`
- `entity_id`
- `label`
- optional `category_id`
- optional `entry_id`

Das reicht für Kategorie-, Eintrags- und Felddefinitions-Treffer zur Navigation, beschreibt aber noch nicht eindeutig **wo** ein späterer Feldwerttreffer gefunden wurde.

## Zielvertrag

Jeder Suchtreffer muss zukünftig eine eindeutige Fundstelle projizieren können:

- **Kategorie-Kontext:** `category_id` + sichtbare Kategoriebezeichnung
- **Eintrag-Kontext:** `entry_id` + sichtbarer Eintragstitel, falls vorhanden
- **Feld-Kontext:** `field_id` + Feldbezeichnung, falls vorhanden
- **Trefferart:** einer von `category_name`, `entry_title`, `field_name`, `field_value`
- **Trefferanzeige:** kurze menschenlesbare Fundstellenkette, z. B. `Werkzeug → Akkuschrauber → Hersteller`
- **Navigationsziel:** deterministischer GET-Zielpfad; Feldtreffer dürfen später auf einen stabilen Detail-/Feldanker zeigen
- **Wertvorschau:** nur bei `field_value`, gekürzt und bereits über vorhandene Formatierungsregeln gerendert; keine Rohdaten-Leaks

## Invarianten

- Ein Treffer ohne gültigen Elternkontext wird nicht als navigierbarer Treffer ausgegeben.
- Gelöschte Kategorie/Eintrag/Feld-Eltern bleiben ausgeschlossen.
- Fundstellenprojektion ist read-only und erzeugt keine Persistenz.
- Darstellung und Navigation verwenden dieselben IDs; keine Rekonstruktion aus Labels.
- Ein Feldwerttreffer darf nie nur „Wert X“ anzeigen, sondern muss Kategorie → Eintrag → Feld eindeutig benennen.
- Trefferart und Fundstelle sind Projektion, kein neues Datenbankschema.

## Abhängigkeiten

- **REQUIRES:** I151 Inventur starke Detailansicht.
- Für Feldanker-Navigation wird die spätere starke Detailansicht einen stabilen semantischen Feld-Zielpunkt bereitstellen.
- **BLOCKS:** produktive globale Feldwertsuche, weil deren Treffer ohne diesen Vertrag nicht eindeutig genug wären.

## Nicht enthalten

- keine Suche in Feldwerten,
- keine Änderung an `SearchHit`,
- keine Repository-Queries,
- keine UI-Markierung,
- keine Persistenz,
- kein CP-03-/CP-06-Reopen.

## Späterer Implementierungsschnitt

Die Implementierung soll zuerst den bestehenden Trefferarten den expliziten Fundstellenvertrag geben. Erst nach grünem Vertrag darf `field_value` als vierte Trefferart hinzukommen.
