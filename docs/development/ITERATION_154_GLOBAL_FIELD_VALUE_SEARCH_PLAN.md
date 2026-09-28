# I154 – Plan globale Feldwertsuche

## Ziel

Den offenen Punkt **C · globale Suche Kategorie → Eintrag → Feldwert** separat planen. Keine Implementierung in dieser Iteration.

## Abhängigkeit

**REQUIRES I153 – Fundstellenvertrag.**

Die globale Feldwertsuche darf erst produktiv werden, wenn jeder Treffer Kategorie → Eintrag → Feld eindeutig projizieren kann.

## Bestehender Suchpfad

Heute durchsucht `CatalogService.search()`:
1. Kategorienamen,
2. Eintragstitel,
3. Feldnamen.

Feldwerte sind bewusst noch nicht Teil dieses Pfads.

## Geplanter Suchumfang

Die spätere Erweiterung ergänzt ausschließlich **read-only Feldwerttreffer**:

- `text` / `long_text`: normalisierter Textinhalt,
- `integer` / `decimal` / `money`: kanonische gespeicherte Zahl plus menschenlesbare Darstellung,
- `date` / `datetime`: kanonischer ISO-Wert; Darstellung weiterhin über vorhandene Formatierungslogik,
- `boolean`: menschenlesbare Werte `Ja` / `Nein`,
- `single_choice` / `multi_choice`: aktive Optionsbezeichnungen.

## Ergebnisvertrag

Ein Feldwerttreffer benötigt mindestens:

- `match_kind = field_value`,
- `category_id`,
- `entry_id`,
- `field_id`,
- Feldbezeichnung,
- bereits formatierte, gekürzte Wertvorschau,
- eindeutige Fundstellenkette gemäß I153,
- deterministisches GET-Navigationsziel.

## Query- und Sicherheitsregeln

- leere/Whitespace-Suche liefert keine Treffer,
- bestehendes globales `limit` bleibt wirksam,
- gelöschte Kategorien, Einträge, Felder und Choice-Optionen werden ausgeschlossen,
- keine FTS-/Index-/Schemaänderung in der ersten Implementierung,
- keine Wildcard-Roh-SQL-Eingabe; Parameterbindung bleibt Pflicht,
- keine Writes, kein Audit-Event und keine Persistenz durch Suche,
- doppelte Multi-Choice-Treffer eines Feldes werden pro Eintrag/Feld deterministisch zusammengeführt,
- bestehende Kategorie-/Eintrag-/Feldname-Treffer behalten ihre bisherige Semantik.

## Architektur

Vorgesehener Pfad:

`CatalogService.search()`
→ bestehende Repository-Reads + neuer eng begrenzter Feldwert-Read
→ I153-Fundstellenprojektion
→ Web-Read-Adapter
→ vorhandener GET-only Suchbereich.

Da die spätere Query den geschützten Repository-Pfad berührt, muss ihre **Implementierung als Frozen-Core/Deep-Gate-Slice** laufen. I154 selbst bleibt rein planend und öffnet CP-06 nicht.

## Nicht enthalten

- keine Runtime-Implementierung,
- kein SQL in dieser Iteration,
- keine FTS-Tabelle,
- kein Suchindex,
- keine Rankinglogik,
- keine gespeicherten Suchen,
- keine Highlighting-Engine,
- keine Schemaänderung,
- kein produktiver Write.

## Empfohlene Implementierungsreihenfolge

1. I153-Fundstellenprojektion für bestehende Treffer implementieren und gaten.
2. Starken Detail-Zielpunkt aus I151 bereitstellen.
3. Feldwert-Read im isolierten Deep-Gate ergänzen.
4. Service/Web-Projektion anschließen.
5. End-to-End prüfen: Trefferart, Fundstelle, Navigation, Deleted-Parent-Schutz, Limit und `sqlite3.total_changes`.
