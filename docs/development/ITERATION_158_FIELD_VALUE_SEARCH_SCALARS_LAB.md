# I158 – Deep-Gate-Labor restliche Scalar-Typen

## Ziel

Das isolierte I157-Feldwertsuche-Labor auf die restlichen Scalar-Typen erweitern, weiterhin ohne Service-/Web-Anbindung.

## Ergänzte Typen

- integer
- decimal
- money
- boolean
- date
- datetime

## Such- und Anzeigeformen

Das Labor akzeptiert sowohl kanonische gespeicherte Werte als auch menschenlesbare Repräsentationen:

- Integer: z. B. `42`
- Decimal: `12.5` und `12,5`
- Money: intern Minor Units, Anzeige z. B. `12,99 EUR`
- Boolean: `Ja/Nein`, zusätzlich technische Aliaswerte für robuste Labortests
- Date: ISO `2026-09-28` und `28.09.2026`
- Datetime: ISO sowie `28.09.2026, 14:30`

## Invarianten

- keine Änderung an Service/Web/API,
- keine Schemaänderung,
- keine Writes,
- Deleted-Parent-Schutz bleibt unverändert,
- deterministische Sortierung/Limit bleiben erhalten,
- menschenlesbare Suchrepräsentation wird im Repository-Labor erzeugt, ohne Web-Abhängigkeit.

## Nicht enthalten

- produktive Integration,
- SearchHit-Erweiterung,
- Ranking,
- Highlighting,
- FTS/Index,
- TODO-Abschluss der globalen Feldwertsuche.
