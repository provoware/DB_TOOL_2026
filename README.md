# PROVOWARE DB TOOL 2026

PROVOWARE DB TOOL 2026 ist ein lokales Datenbankprojekt mit dem Ziel, Datenstrukturen auch ohne Datenbankwissen verständlich, sicher und schrittweise bedienbar zu machen.

> **Bestätigter Produktstand:** I155 auf diesem Branch; starke GET-only Detailansicht mit stabilen Detail-/Feldankern ist umgesetzt  
> **Governance-Stand:** I152 führt einen gemeinsamen lokalen/CI-Preflight für Kontext, Manifest und Gate-Routing ein; Control Plane V2 bleibt Shadow-Vertrag  
> **Sicherheitsstatus:** Browser-Maskenentwurf ohne Persistenz und ohne produktiven Datenbankzugriff  
> **Frozen Core:** CP-03 und CP-06 bleiben geschlossen  
> **Gesamtfortschritt Master-TODO A–M:** **34 / 132 = 25,8 %**

## Zielbild

Das Projekt trennt Oberfläche, Anwendungslogik, Fachmodell und SQLite strikt voneinander. Neue Funktionen werden zuerst klein, reversibel und möglichst browserlokal oder read-only entwickelt. Produktive Schreibpfade werden erst geöffnet, wenn Preview, Integrität und Recovery geklärt sind.

## Sicherer Schnellstart

### Nur-Lese-Webmodus

Für eine bereits vorhandene und kompatible `main.db`:

```bash
python3 scripts/start_readonly_web.py --main-db /pfad/zu/main.db
```

Der Start:

- prüft Datenbankidentität und Schema,
- öffnet SQLite read-only,
- setzt `PRAGMA query_only = ON`,
- bindet ausschließlich an `127.0.0.1`,
- blockiert bei fehlender oder inkompatibler Datenbank.

Standardadresse: `http://127.0.0.1:8765`.

### Repository-Selbstprüfung

```bash
bash scripts/repo_self_check.sh
```

Die Entwicklungsgates wählen zusätzlich abhängig vom Iterationsmanifest nur die jeweils betroffenen Compile- und Regressionstests.

## Was das Projekt heute kann

### Datenbasis

- lokaler SQLite-Kern
- Kategorien, Einträge und frei definierbare Felder
- getrennte Application-, Domain- und Repository-Schichten
- freigegebene Nur-Lese-Pfade
- Schema-/Freeze-Schutz und Repository-Selbstprüfung
- deterministische Iterations- und Scope-Gates

### Browser-Masken-Baukasten

Bis einschließlich **I146** besitzt der temporäre Browser-Draft:

- Komponentenpalette und feste 12-Spalten-Arbeitsfläche
- deterministische monotone Draft-IDs
- temporäres Platzieren, Verschieben, Entfernen und Duplizieren mit neuer monotoner Draft-ID
- kontrolliertes Neuordnen ganzer Draft-Elemente per Hoch/Runter-Controls ohne Drag-and-drop-Zwang
- semantische Vorschau-Abschnitte über den vorhandenen Bereich-Baustein
- browserlokales Ein-/Ausklappen dieser Abschnitte mit zugänglichem Toggle
- explizite natürliche Tab-Reihenfolge mit roving Tabstop für die 12 Zielspalten
- feste Desktop-Vorschau mit 1152-px-Viewport in horizontal scrollbarem Rahmen
- browserlokale Umschaltung auf eine Tablet-Vorschau mit 768 px, Desktop bleibt Standard
- zusätzlicher schmaler Preview-Modus mit 360 px; alle drei Modi teilen dieselben Preview-Daten
- gemeinsame reale Chromium-Abnahme der drei Viewports auf Fokus, Umschaltung, Beschriftung, Overflow und Inhaltskonsistenz
- Blockierung ungültiger Rasterziele vor Mutation
- Label- und Hilfetext-Bearbeitung
- Pflichtfeld-Eigenschaft
- Datentypen `text`, `number`, `date`, `boolean`, `single_choice`, `multi_choice`
- typabhängig validierten skalaren Standardwert
- inaktive statt still umgeschriebene Standardwerte bei Choice-Typen
- browserlokale Choice-Optionen
- stabile monotone `draft-option-*`-IDs
- browserlokale `defaultSelection` über stabile Option-IDs für Einfach- und Mehrfachauswahl
- ausgewählte Default-Optionen gegen stilles Entfernen und ungültige Typverengung geschützt
- Optionen hinzufügen, entfernen und deterministisch hoch/runter verschieben
- Live-Status, Tastaturwege und deterministische Fokus-Rückgabe
- schmale Darstellung für die bisher freigegebenen Property-Controls
- **statische Sichtbarkeit:** Komponenten bleiben im Editor erreichbar, können aber aus der Vorschau ausgeblendet werden
- browserlokale Breitenbearbeitung von 1–12 Spalten mit Prüfung vor Mutation
- bestätigte 100/150/200-%-Evidence für die vollständige vorhandene Property-Matrix
- deterministische Preview ohne produktiven Write
- read-only Raster-Assistent: kompakter Layout-Vorschlag aus bestehender Reihenfolge und bestehenden Breiten, ohne Übernahme
- explizite Vorher/Nachher-Tabelle mit geplanter Zeilen-/Spaltenänderung pro Element; tatsächliche Übernahme weiterhin gesperrt
- separater flüchtiger Browser-Layoutvertrag `draft-id → {row, column}`; die Arbeitsfläche rendert daraus, ohne Persistenz
- atomare browserlokale Übernahme eines bestätigten Rastervorschlags mit Stale-Schutz, Fokus-Rückgabe und echter Chromium-Vorher/Nachher-Evidence

### I115-Härtung

I115 hat zwei nach I113 gefundene Laufzeitrisiken gezielt repariert:

- versehentlich literal emittierte `\n`-Sequenzen im Browser-JavaScript
- Fokus-Rückgabe auf einen deaktivierten Reorder-Randbutton

Beide Reparaturen wurden über Targeted + Foundation gegatet.

## I118/I119 – bestätigte Produkt-Härtung

I118 ergänzt die browserlokale Breitenbearbeitung. Eine neue Breite wird nur übernommen, wenn das Element weiterhin vollständig in das 12-Spalten-Raster passt.

I119 liefert reproduzierbare reale Chromium-Evidence für die vollständige vorhandene Property-Matrix bei **100/150/200 %**. Die Evidence deckte zugleich einen Fokusverlust am Pflichtfeld-Toggle auf; dieser konkrete Befund wurde in derselben Iteration repariert und gegatet.

## I132 – browserlokale Standardauswahl

I132 setzt den I128-Vertrag im flüchtigen Browser-Draft um. Einfachauswahl referenziert maximal eine stabile `draft-option-*`-ID; Mehrfachauswahl hält eine geordnete, duplikatfreie ID-Liste. Options-Reorder erhält die Auswahl, ausgewählte Optionen können nicht still entfernt werden und eine Verengung von Mehrfach- auf Einfachauswahl wird bei mehreren Defaults vor Mutation blockiert.

Reale Chromium-Evidence prüft die neue Interaktion bei **100/150/200 %** inklusive Fokus-Rückgabe, Preview-Reihenfolge, Remove-Guard und horizontalem Overflow. Persistenz, Model, Store und Datenbank bleiben unverändert.

## I133 – browserlokales Duplizieren

I133 ergänzt eine kleine Struktur-Capability: Ein bestehendes Draft-Element kann per Tastatur oder Klick dupliziert werden. Die Kopie erhält eine neue monotone `draft-*`-ID. Bei Choice-Feldern werden auch alle Optionen tief kopiert und mit neuen monotonen `draft-option-*`-IDs versehen; eine vorhandene `defaultSelection` wird auf die neuen IDs umgebunden.

Reale Chromium-Evidence prüft die Identitätstrennung, Preview und Fokus-Rückgabe bei **100/150/200 %**. Die Duplizierung bleibt vollständig browserlokal und flüchtig.

## I135 – kontrolliertes browserlokales Neuordnen

I135 ergänzt für ganze Draft-Elemente deterministische **Hoch-/Runter-Controls**. Jeder Schritt verschiebt genau ein Element um genau eine Position; erstes und letztes Element sperren jeweils die nicht mögliche Richtung.

Editor und Vorschau beziehen ihre Reihenfolge weiterhin aus derselben flüchtigen `draftElements`-Sequenz. Nach einer Verschiebung kehrt der Fokus zu einem erreichbaren Reihenfolge-Control desselben Elements zurück. Es gibt weder Drag-and-drop-Zwang noch Persistenz, Store- oder Datenbankzugriff.

## I136 – semantische Vorschau-Abschnitte

I136 macht den bereits vorhandenen **Bereich**-Baustein zu einer echten Strukturgrenze in der Vorschau. Ein sichtbarer Bereich erzeugt einen semantischen Abschnitt mit eigener Überschrift; die nachfolgenden sichtbaren Elemente werden bis zum nächsten sichtbaren Bereich dort einsortiert.

Die Zugehörigkeit wird **nicht separat gespeichert**, sondern deterministisch aus der aktuellen Reihenfolge der browserlokalen `draftElements` abgeleitet. Dadurch bleibt I135-Reorder automatisch konsistent. Einklappen, Persistenz und Gruppenstatus bleiben weiterhin geschlossen.

## I137 – einklappbare Vorschau-Gruppen

I137 baut direkt auf I136 auf: Jeder sichtbare Bereich erhält in der Vorschau einen zugänglichen Toggle mit `aria-expanded` und `aria-controls`. Der zugehörige Inhaltsblock wird über den nativen `hidden`-Zustand ein- oder ausgeblendet.

Der Einklapp-Zustand lebt bewusst **außerhalb des Draft-Datenobjekts** in einem flüchtigen Browser-`Set`. Dadurch bleibt er rein UI-lokal, wird nicht dupliziert oder gespeichert und verschwindet bei einem Seitenreload. Nach jedem Toggle wird der Fokus deterministisch an denselben Abschnitt zurückgegeben.

## I138 – explizite Tab-Reihenfolge

I138 macht den Tastaturpfad des Masken-Baukastens explizit, ohne fragile positive `tabindex`-Werte einzuführen. Die Hauptbereiche bleiben in natürlicher DOM-Reihenfolge **Komponenten → Arbeitsfläche → Vorschau**.

Das 12-Spalten-Raster verwendet einen **roving Tabstop**: Nur eine Zielspalte liegt gleichzeitig im normalen Tabpfad. Mit ←/→ wird der aktive Tabstop verschoben; Fokus, Klick, Move-Start und Remove-Rückgabe halten diesen Zustand synchron. Dadurch bleiben die zwölf Zielspalten vollständig tastaturbedienbar, ohne zwölf zusätzliche Tab-Schritte zu erzwingen.

## I139 – feste Desktop-Vorschau

I139 ergänzt einen expliziten **Desktop-Preview-Vertrag**. Die Vorschau wird in einem festen **1152-px-Viewport** gerendert; ein schmaleres Bedienpanel darf diese Geometrie nicht still responsiv zusammendrücken, sondern stellt stattdessen einen horizontal scrollbaren Rahmen bereit.

Der aktive Modus ist sichtbar als **Desktop · 1152 px** gekennzeichnet und semantisch beschrieben. Tablet- und schmale Vorschau werden bewusst noch nicht eingeführt und bleiben getrennte spätere Slices. Persistenz, Datenmodell, Store und Datenbank bleiben unverändert.

## I140 – Tablet-Vorschau

I140 erweitert den bestätigten I139-Desktop-Vertrag um einen separaten **Tablet-Modus mit 768 px**. Desktop bleibt beim Laden unverändert der Standard mit **1152 px**; die Umschaltung verändert ausschließlich den Preview-Viewport und keine Draft-Daten.

Die beiden Modus-Buttons verwenden `aria-pressed`, die sichtbare Modusbezeichnung und die semantische Breitenbeschreibung werden synchron aktualisiert. Eine schmale Vorschau wird noch nicht eingeführt. Der Modus bleibt vollständig browserlokal und wird nicht gespeichert.

## I141 – schmale Vorschau

I141 schließt die browserlokale Preview-Viewport-Matrix ab. Neben **Desktop 1152 px** und **Tablet 768 px** steht nun ein dritter Modus **Schmal 360 px** bereit. Desktop bleibt weiterhin der initiale Standard.

Intern werden die drei Viewport-Verträge über eine kleine feste Modus-Tabelle beschrieben. Die Umschaltung verändert ausschließlich Breite, sichtbare Modusbezeichnung und Accessibility-Status; die Draft- und Preview-Daten bleiben identisch. Der Modus wird weiterhin nicht gespeichert.

## I142 – gemeinsame Preview-Abnahme

I142 ist eine **Evidence-/Härtungsiteration**, kein neuer Produktpunkt. Desktop **1152 px**, Tablet **768 px** und Schmal **360 px** werden gemeinsam in realem Chromium geprüft.

Die Abnahme kontrolliert Tastaturaktivierung und Fokus, genau einen aktiven `aria-pressed`-Modus, sichtbare und semantische Breitenbeschriftung, identischen Preview-Inhalt über alle Viewports sowie die Overflow-Grenze: Die Seite selbst darf nicht horizontal überlaufen; breite Preview-Modi dürfen ausschließlich innerhalb ihres Preview-Rahmens scrollen.

Der Master-TODO-Fortschritt bleibt deshalb bei **28 / 132 = 21,2 %**. Runtime-Code wird in I142 nur geändert, wenn die reale Evidence einen reproduzierbaren Defekt zeigt.

## I143 – Raster-Assistent als read-only Vorschlag

I143 ergänzt einen bewusst **nicht schreibenden Raster-Assistenten**. Er liest ausschließlich die aktuelle browserlokale `draftElements`-Reihenfolge und die vorhandenen Breiten. Daraus berechnet er deterministisch eine kompakte Platzierung von links nach rechts im 12-Spalten-Raster; passt das nächste Element nicht mehr in die aktuelle Zeile, beginnt eine neue Zeile.

Der Vorschlag zeigt **Zeile, Startspalte und Breite** pro Draft-Element. Vor und nach der Berechnung wird ein Positions-/Breiten-Snapshot verglichen; eine Mutation des Drafts wird als Fehler behandelt. Es gibt in I143 ausdrücklich **keinen Anwenden-/Übernehmen-Button**, keine Änderung von `column` oder `width` und keine Persistenz.

## I144 – Rastervorschlag Vorher/Nachher-Vertrag

I144 erweitert den I143-Assistenten um eine explizite **Vorher/Nachher-Vorschau**, ohne den Draft zu verändern. Pro Element werden aktuelles Layout und vorgeschlagenes Layout gegenübergestellt: **Zeile, Startspalte und Breite**. Änderungen werden konkret als beispielsweise `Zeile 3 → 1` oder `Spalte 7 → 5` ausgewiesen.

Dabei wurde eine wichtige Mutationsgrenze sichtbar: Die aktuelle Arbeitsfläche leitet die Rasterzeile aus der Draft-Reihenfolge ab; der Draft besitzt noch keine eigene Zeilenposition. Deshalb bleibt die Übernahme in I144 ausdrücklich gesperrt. Ein späterer Mutations-Slice muss **Zeile und Spalte gemeinsam** als temporären Layoutvertrag behandeln, bevor irgendeine Position tatsächlich verändert wird.

I144 schließt den Master-TODO-Punkt „Übernahme eines Rastervorschlags mit Vorher/Nachher“ noch **nicht** ab. Der Produktfortschritt bleibt daher bei **29 / 132 = 22,0 %**.

## I145 – temporärer Raster-Layoutvertrag für Zeile + Spalte

I145 schließt die in I144 sichtbar gewordene Zustandslücke, ohne die Rastervorschlagsübernahme bereits freizugeben. Zeile und Spalte werden jetzt in einer **separaten flüchtigen Browser-Map** pro Draft-ID gehalten. Der persistierbare Draft selbst erhält bewusst noch kein neues Feld.

Die Arbeitsfläche rendert ihre CSS-Rasterposition aus diesem temporären Vertrag. Bestehende Interaktionen bleiben synchron: neues Platzieren legt eine temporäre Position an, Verschieben aktualisiert die Spalte, Duplizieren erhält eine neue Zeile, Entfernen räumt den Layoutzustand auf und Neuordnen normalisiert die Zeilen entsprechend der aktuellen Draft-Reihenfolge.

Damit ist erstmals sauber definiert, **wo** ein später angenommener Rastervorschlag Zeile und Spalte atomar setzen darf. I145 enthält weiterhin keinen Übernehmen-/Anwenden-Button und keine Persistenz. Der offene Master-TODO-Punkt bleibt daher offen; der Fortschritt bleibt **29 / 132 = 22,0 %**.

## I146 – tatsächliche browserlokale Rasterübernahme

I146 schließt den zuvor vorbereiteten Raster-Assistenten vollständig browserlokal ab. Nach der Vorher/Nachher-Prüfung erscheint nur bei echten Änderungen der Button **„Rastervorschlag übernehmen“**. Die Übernahme schreibt ausschließlich in `temporaryGridLayout`.

Vor dem Commit werden alle Zielpositionen gegen Breite und 12-Spalten-Raster validiert. Zusätzlich bindet ein Fingerprint den Apply-Schritt an genau den zuvor berechneten Zustand; ist der Vorschlag inzwischen veraltet, wird nichts mutiert und der Vergleich neu berechnet. Erst nach vollständiger Vorvalidierung wird eine neue Layout-Map vorbereitet und synchron übernommen.

`draftElements`, Reihenfolge, Labels und Breiten bleiben unverändert. Canvas und textuelle Preview lesen danach dieselbe temporäre Spaltenposition. Der Fokus kehrt deterministisch zum Raster-Assistenten zurück. Eine reale Chromium-Evidence prüft den vollständigen Vorher/Nachher-Weg inklusive Tastaturauslösung.

Persistenz, Store, SQLite sowie CP-03/CP-06 bleiben geschlossen.

## I147 – Struktur-Freeze und nächste Produktinventur

I147 führt **keine neue Produktfunktion** ein. Der vollständig abgeschlossene TODO-Bereich **B · Masken-Baukasten – Struktur** wird auf dem bestätigten I146-`main`-Stand **`e875670d…`** maschinenprüfbar eingefroren. Der Freeze hält die zehn bestätigten Strukturpunkte sowie die Schutzinvarianten fest: keine Masken-Persistenz, CP-03/CP-06 geschlossen und Rasterübernahme weiterhin ausschließlich browserlokal.

Die Inventur der offenen Bereiche zeigt zugleich, dass der TODO-Punkt **C · Datenarbeit → Suche** nicht bei null beginnt. Bereits vorhanden sind `CatalogService.search()`, die Web-Read-Projektion, der GET-Parameter `q` sowie die Suchergebnisdarstellung im Read-only-Web-UI. Deshalb wird als nächster Slice **I148 – vorhandene Read-only-Suche formell abnehmen** gewählt. Erst wenn dieser bestehende Pfad den Produktvertrag erfüllt, wird der TODO-Punkt geschlossen; eine unnötige Neuimplementierung wird vermieden.

Der Produktfortschritt bleibt in I147 unverändert bei **30 / 132 = 22,7 %**.

## I148 – formelle Read-only-Suche-Abnahme

I148 baut keine zweite Suche, sondern nimmt den bereits vorhandenen Pfad **Service → Repository → Web-Adapter → GET-only HTTP → Ergebnisdarstellung** end-to-end ab. Leere bzw. nur aus Leerzeichen bestehende Suchbegriffe liefern keinen Suchlauf, Treffer und Nicht-Treffer werden klar angezeigt, und POST bleibt mit `405 Method Not Allowed` blockiert.

Die Abnahme hat genau eine konkrete Lücke gefunden: Eintragsspezifische Feldtreffer lieferten bislang ihre `entry_id`, aber nicht die Eltern-`category_id`. Dadurch waren sie sichtbar, konnten aber nicht sicher zum zugehörigen Eintrag navigieren. Der Read-only-Repository-Query projiziert dafür jetzt `COALESCE(f.category_id, e.category_id)` als Kategoriebezug. Es gibt keine Schema- oder Schreibänderung.

Ein End-to-End-Test prüft zusätzlich, dass Such-GETs den SQLite-`total_changes`-Zähler nicht verändern und Treffer unter gelöschten Eltern weiterhin ausgeschlossen bleiben. Die getrennte spätere **globale Suche Kategorie → Eintrag → Feldwert** bleibt ausdrücklich offen.

## I149 – Read-only Titel-Filter für Einträge

I149 schließt den nächsten kleinen Datenarbeits-Slice ohne den Frozen Core zu öffnen. Sobald eine Kategorie gewählt ist, kann ihre bereits geladene Eintragsliste über den GET-Parameter `filter` nach einem im Titel enthaltenen Text eingeschränkt werden. Der Vergleich ist ohne Beachtung der Groß-/Kleinschreibung; Leerzeichen-only verhält sich wie „Filter aus“.

Der Filter arbeitet ausschließlich auf der Web-Read-Projektion. Es gibt kein SQL, keinen Repository-Write, keine Browser-Persistenz und keinen gespeicherten Filter. Ein eigener Regressionstest prüft Treffer, Nicht-Treffer, Leerzustand und dass SQLite-`total_changes` durch Filter-GETs unverändert bleibt. Sortierung und globale Feldwertsuche bleiben getrennte spätere Slices.

## I150 – Read-only Titel-Sortierung

I150 ergänzt ausschließlich die explizite Sortierung der bereits geladenen Eintragsliste: Standardreihenfolge, Titel A–Z oder Titel Z–A. Die Sortierung ist deterministisch, GET-only und arbeitet nach dem I149-Filter auf derselben Web-Read-Projektion. Filter und Sortierung erhalten ihren jeweiligen Zustand gegenseitig.

Es gibt weiterhin keinen Repository-Write, keine Schemaänderung, keine gespeicherte Sortierung und keine Browser-Persistenz. Der gezielte Test prüft Standardreihenfolge, beide Sortierrichtungen, Filter+Sort-Komposition und unveränderte SQLite-`total_changes`.

## I151 – Inventur starke Detailansicht

I151 verändert keine Runtime. Die vorhandene Detaildarstellung wurde inventarisiert und der kleinste spätere Umsetzungsscope auf die bestehende Web-Read-Projektion begrenzt: expliziter Detailkopf, Kategorie-/Eintragskontext, Feldanzahl, stabiler semantischer Detailcontainer und klarer Leerzustand. Repository, Schema, Persistenz, Fundstellenvertrag und globale Feldwertsuche bleiben geschlossen.

## I153 – Fundstellenvertrag separat geplant

I153 implementiert noch keine Feldwertsuche. Der Vertrag legt stattdessen fest, dass jeder spätere Treffer Kategorie-, Eintrags- und optional Feldkontext sowie eine explizite Trefferart tragen muss. Feldwerttreffer dürfen erst entstehen, wenn ihre Fundstelle als deterministische Kette und als stabiles GET-Navigationsziel eindeutig projizierbar ist.

Damit wird verhindert, dass die spätere globale Suche zwar Werte findet, aber nicht eindeutig zeigen kann, **wo** der Treffer liegt.

## I154 – globale Feldwertsuche separat geplant

I154 implementiert noch keine neue Suche. Der Plan legt fest, welche vorhandenen Feldtypen später read-only durchsuchbar werden, wie Wertvorschauen formatiert werden, wie Choice-Treffer dedupliziert werden und welche Deleted-Parent-/Limit-/No-Write-Invarianten gelten.

Die spätere Repository-Erweiterung wird ausdrücklich als **Deep-Gate/Frozen-Core-Slice** behandelt. I153-Fundstellenvertrag und der stabile Detail-Zielpunkt aus I151 sind Vorbedingungen; FTS, Suchindex, Ranking und Schemaänderungen bleiben außerhalb des ersten Feldwert-Slices.

## I155 – starke Read-only Detailansicht

I155 ergänzt einen expliziten Detailbereich für den gewählten Eintrag: sichtbarer Kategorie-/Eintragskontext, Anzahl sichtbarer Felder, klarer Leerzustand und stabile DOM-Ziele `#detail` sowie `#field-<id>`. Dadurch kann die spätere I153-Fundstellenprojektion deterministisch in den richtigen Detailbereich beziehungsweise direkt zum Feld navigieren.

Der Slice bleibt vollständig GET-only; Repository, Schema, Persistenz und Feldwertsuche bleiben unverändert.

## I120–I124 – Control Plane V2 im Shadow-Modus

Die Governance-Kette ist inzwischen durchgängig modelliert: Registry/Lifecycle → versiegelter Plan und Single-Writer-Lease → triggerbasierte Inspektion/Planung → Controller-Sealing und Audit-Kette → Finalizer/Outcome.

Wichtig: Diese Kette ist **shadow-only und nicht autoritativ**. Sie verändert keine Produktfunktion, keine Persistenz und keinen Frozen Core. Deshalb erhöht I120–I124 den Produktfortschritt A–M nicht.

## I127 – gemeinsame Eigenschaften-/Preview-Abnahme

I127 bestätigt die bereits vorhandene gemeinsame Preview-Projektion mit einem eigenen Regressionsvertrag. Label, Breite, Hilfetext, Pflichtstatus, Datentyp, Choice-Optionen, skalarer Standardwert und Sichtbarkeit bleiben dadurch zusammen abgesichert. Es wurde keine neue Runtime-Funktion eingeführt; `defaultSelection` und Persistenz bleiben geschlossen.

## I128 – `defaultSelection` nur als Vertrag

I128 definiert den späteren browserlokalen Draft-Vertrag für Choice-Standardauswahlen. Referenzen laufen über stabile `draft-option-*`-IDs; stille Datenverluste bei Optionsentfernung oder Typverengung sind ausgeschlossen. Es existiert weiterhin **keine Runtime-Implementierung und keine Persistenz**.

## I129 – Persistenzgrenze geplant, Write weiter geschlossen

I129 bindet eine spätere Speicherung an denselben deterministischen Kandidaten über Preview-Fingerprint, Integritätsprüfung, Recovery-Punkt, atomaren Store-Commit und Read-back-Verifikation. Browser und Store bleiben getrennt; es existiert weiterhin **kein produktiver Save-Pfad**.

## Was bewusst noch nicht freigegeben ist

Der Browser-Maskenentwurf wird weiterhin **nicht gespeichert**. Ein Reload verwirft den Draft.

Noch offen sind insbesondere:


- produktive Umsetzung der bereits geplanten Save-/Load-Grenze
- produktive Masken-Persistenz
- größere Struktur-, Regel-, Import-/Export-, Recovery- und Dashboard-Funktionen

## Nächste sichere Reihenfolge

1. I151: `starke Detailansicht` als nächsten unabhängigen Read-only-Datenarbeits-Slice inventarisieren.
2. Fundstellenvertrag und globale Feldwertsuche danach getrennt behandeln.
3. Globale Feldwertsuche, Persistenz und gespeicherte Ansichten bleiben separat geschlossen.

Keiner dieser Schritte öffnet automatisch CP-03 oder CP-06.

## Schutz der Datenbank

Eingefrorene Bereiche dürfen nicht beiläufig verändert werden:

- **CP-03:** Datenbankschema
- **CP-06:** Domain-/Repository-Kern

Änderungen dort benötigen einen eigenen Reopen-/Impact-Plan, passende Regressionen und ein separates Deep-Gate.

## Architektur

```text
Oberfläche
↓
Application Service
↓
Domain / Repository
↓
SQLite
```

Die Oberfläche führt kein direktes SQL aus. Der Browser-Masken-Baukasten besitzt aktuell keinen produktiven Schreibpfad.

## Qualitäts- und Gate-Modell

1. Scope und Nicht-Scope im Iterationsmanifest festlegen.
2. Nur die geplanten Dateien ändern.
3. Bei Zwei-Schritt-Iterationen nach Schritt 1 ein Zwischen-Gate ausführen.
4. Triggerbasierte statt unnötige Volltests verwenden.
5. Bei Rot ausschließlich die konkrete Gate-Ursache beheben.
6. Frozen-Core-Bereiche ohne eigenen Reopen unverändert lassen.
7. Erst nach vollständig grünem, SHA-genauem Gate mergen.

Für UI-Slices gehören Tastaturbedienung, sichtbarer Fokus, zugängliche Namen/Status und schmale Darstellung zum Funktionsvertrag.

## Fortschrittsmessung

Die **25,8 %** sind kein geschätzter Marketingwert. Gezählt werden die eindeutigen Checkboxen des Implementierungspools **A–M** in `TODO.md`: aktuell **34 erledigt von 132**. Die separat aufgeführte Prioritätenliste wird nicht zusätzlich gezählt. Governance-Arbeit aus I120–I124 wird nicht als Produktpunkt mitgezählt.

Dadurch ist die Zahl bewusst konservativ: große und kleine TODO-Punkte zählen jeweils einmal.

## Wichtige Projektdateien

- `TODO.md` – Master-Implementierungspool
- `docs/PRODUCT_ROADMAP.md` – langfristige Abhängigkeiten und Risikoklassen
- `docs/LAIEN_START.md` – kurze Erklärung ohne Entwicklerfokus
- `AGENTS.md` – Entwicklungs-, Gate- und Freeze-Regeln
- `CONTRIBUTING.md` – Mitarbeit am Repository
- `docs/PROJECT_STANDARDS.md` – Prüf- und Qualitätsstandard
- `.provoware/iterations/` – maschinenlesbare Iterationsverträge
- `scripts/repo_self_check.sh` – Repository-Gesundheitsprüfung
- `scripts/start_readonly_web.py` – sicherer lokaler Nur-Lese-Webstart

## Entwicklungs-Preflight

Vor Produktänderung oder PR:

```bash
python scripts/iteration_preflight.py
```

Das Kommando prüft Fortschrittskonsistenz, aktuelles Manifest, Gate-Profil, Frozen-Core-Eskalation und Gate-Routing mit derselben Logik, die auch GitHub Actions verwendet. Die separate Scope-Prüfung bleibt zusätzlich bestehen.

## Repository-Hygiene

`main` ist die bestätigte stabile Basis. Neue Produktarbeit startet von dort und läuft über kleine Branches und Pull Requests. Historische Branches und alte Evidence-Stände ersetzen kein aktuelles Gate.

## Lizenz

Noch nicht festgelegt.
