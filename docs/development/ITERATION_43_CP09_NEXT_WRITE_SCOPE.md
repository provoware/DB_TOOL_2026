# Iteration 43 – CP-09 nächster Write-Scope

## Zweck

I43 ist ausschließlich eine read-only Post-Reopen-/Masterplan-Auflösung nach dem eingefrorenen I42. Es wird kein Produktcode verändert und kein eingefrorener Bereich erneut geöffnet.

## Befund

I42 hat genau den ersten freigegebenen CP-09-Write-Use-Case „Kategorie anlegen“ bis zur TUI geführt. Der nächste logisch kleinere, bereits vorhandene öffentliche Application-Vertrag ist `CatalogService.create_entry(category_id, title, sort_order=0)`.

Der Vertrag besitzt bereits die für CP-09 geforderte Sicherheitsstruktur:

- Erzeugung über `Entry.new(...)`;
- Prüfung, dass die Parent-Kategorie aktiv vorhanden ist;
- Repository-Insert über den bestehenden `EntryRepository`;
- Audit-Ereignis `entry.create`;
- transaktionale Postcondition für den aktiven Eintrag;
- transaktionale Postcondition für Audit-Evidence;
- dieselben Postconditions nach Commit;
- koordinierte Ausführung über den bestehenden `CoordinatedWriter`.

Damit ist für die reine Nutzung dieses bestehenden Vertrags derzeit kein REOPEN von CP-03, CP-06 oder SQLite begründet.

## Nächster einzelner CP-09-Use-Case

**Eintrag in einer bereits ausgewählten aktiven Kategorie anlegen – ausschließlich über `CatalogService.create_entry()`.**

Dieser Schritt folgt der vorhandenen Datenhierarchie Kategorie → Eintrag → Felder und ist kleiner als Field-/Value-Writes, Papierkorb/Restore, Undo oder Recovery. Anders als Kategorie-Anlegen besitzt er eine Parent-Abhängigkeit; deshalb darf eine Folgeiteration nicht sofort die TUI umbauen.

## Freigabegrenze nach I43

Nach grünem Freeze von I43 darf ausschließlich eine separate Vertrags-/Adapter-Inventur prüfen, ob ein dünner `EntryWriteAdapter` analog zur eingefrorenen Kategorie-Seam möglich ist. Dabei müssen mindestens folgende Punkte belegt werden:

1. `category_id` stammt ausschließlich aus der aktuell ausgewählten aktiven Kategorie;
2. der Adapter delegiert genau einmal an `CatalogService.create_entry()`;
3. kein direkter Repository-/SQL-Zugriff entsteht;
4. `DOM-102` bzw. der bestehende NotFound-Vertrag wird unverändert durchgereicht;
5. noch keine TUI-Eingabe, kein Hotkey und kein Refresh werden in dieser Adapter-Inventur vorweggenommen;
6. falls später Runtime-Änderungen nötig sind, benötigen sie einen neuen expliziten engen CP-07T-REOPEN.

## Freeze-Grenzen / Non-Goals

Unverändert geschlossen bleiben:

- CP-03 / Schema V1 / Migrationen;
- CP-06 Domain-/Repository-Kern;
- `storage/sqlite/**` einschließlich Audit, Journal, Unit of Work und Coordinator;
- `CatalogService` und sein bestehender `create_entry()`-Vertrag;
- der in I42 wieder eingefrorene CP-07T-Runtimepfad;
- CP-07H;
- CP-08 Health-/Event-Surface;
- Field-/Value-Writes;
- Papierkorb/Restore;
- Undo;
- Autosave;
- Crash-Recovery;
- Polling/Hintergrundjobs;
- Theme/Layout/Dependencies/CI.

## Exit-Gates

1. Ausschließlich I43-Manifest und dieses Scope-Dokument sind geändert.
2. Kein Produktcode ist geändert.
3. Kein Frozen-Core- oder Runtime-Pfad ist geändert.
4. Repository Foundation ist grün.
5. Agent Governance ist grün.
6. Targeted Iteration validiert nur Manifest/Scope.
7. Kein Full-Suite-, Browser-, TUI- oder visueller Test ohne Produktänderung.
8. Erst nach grünem Freeze von I43 darf die dünne Entry-Write-Adapter-Seam separat inventarisiert bzw. freigegeben werden.

## Verbleibendes Risiko

Eintrag-Anlegen ist sicherheitstechnisch komplexer als Kategorie-Anlegen, weil eine gültige Parent-Auswahl benötigt wird. Die bestehende Application-Schicht deckt fehlende/inaktive Kategorien ab; noch ungeklärt ist jedoch die spätere UI-Selektion und Refresh-/Fokussemantik. Diese Frage gehört ausdrücklich nicht in I43.
