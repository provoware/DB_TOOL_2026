# I161 – Read-only Favoritenfilter

## Ziel

Den offenen Punkt **C · Datenarbeit → Favoriten** als kleinsten unabhängigen Read-only-Slice schließen, ohne neue Persistenz oder Schreibpfade zu öffnen.

## Ausgangslage

Einträge besitzen bereits das persistierte Domain-/Repository-Merkmal `is_favorite`. Die Webprojektion zeigte Favoriten bereits mit einem Stern (`★`), konnte die Eintragsliste aber noch nicht auf Favoriten begrenzen.

## Umsetzung

I161 ergänzt ausschließlich einen GET-only Listenfilter:

- `favorites=1` zeigt innerhalb der gewählten Kategorie nur favorisierte Einträge.
- Die Webprojektion transportiert `is_favorite` explizit als boolesches Merkmal.
- Der Filter wertet **nicht** das Sternzeichen im sichtbaren Label aus.
- Titel-Filter, Sortierung und Favoritenfilter erhalten ihren Zustand gegenseitig.
- Ohne `favorites=1` bleibt die bisherige Eintragsliste unverändert.
- Der aktive Zustand wird sichtbar als `Nur Favoriten · N Einträge sichtbar` gemeldet.

## Sicherheitsgrenze

- kein neuer SQL-Read,
- kein Repository-Patch,
- kein Schema-Patch,
- keine neue Persistenz,
- keine Änderung des Favoritenstatus,
- keine POST-/Write-Route,
- CP-03 und CP-06 bleiben geschlossen.

## Abnahme

Gezielte Tests prüfen:

- nur favorisierte Einträge sichtbar,
- deaktivierter Filter verändert die Standardliste nicht,
- Komposition mit Titel-Filter und Sortierung,
- sichtbarer/zugänglicher Checkbox-Zustand,
- `sqlite3.total_changes` bleibt unverändert.

## Ergebnis

Der TODO-Punkt **Favoriten** bezeichnet in I161 ausschließlich den vorhandenen Favoritenbestand als read-only Datenkomfort. Das aktive Setzen/Entfernen von Favoriten wäre ein separater Write-/Persistenz-Slice und ist ausdrücklich nicht Teil dieser Iteration.
