# Iteration 56 – Wartbarkeits-Scope für Texte, Helper und Capabilities

## Zweck

I56 prüft ausschließlich, **welche Wiederverwendung im aktuellen Repository tatsächlich Wartbarkeit verbessert**.

Es wird keine Registry und kein Refactoring implementiert.

## Ergebnis in einem Satz

**Zentraler Textkatalog: gezielt sinnvoll. Helper: normale Python-Funktionen. Dynamische Capability-Registry: derzeit nicht begründet.**

---

## 1. Text-Wiederverwendung

### Reale Kandidaten

Im aktuellen Stand existieren bereits sichtbare Begriffe und Meldungen mit gleicher oder sehr ähnlicher Semantik in mehreren Oberflächen bzw. Kontexten.

Beispiele:

- „Keine Kategorien vorhanden.“
- Nur-Lese-/Nur-Lesen-Kennzeichnung
- Feldtyp-Bezeichnungen
- Kategorie / Eintrag / Feld
- leere Werte wie „Nicht gesetzt“
- wiederkehrende Status- und Navigationsbegriffe

Besonders deutlich ist die Feldtyp-Semantik:

Die Domain besitzt stabile `FieldType`-Werte, während die Web-Schicht bereits eigene laienfreundliche Labels pflegt:

- `text → Text`
- `long_text → Langer Text`
- `integer → Ganzzahl`
- `decimal → Dezimalzahl`
- `money → Geldbetrag`
- `date → Datum`
- `datetime → Datum und Uhrzeit`
- `boolean → Ja / Nein`
- `single_choice → Einfachauswahl`
- `multi_choice → Mehrfachauswahl`

Eine spätere TUI-`FieldType`-Auswahl würde dieselben Begriffe benötigen.

Damit liegt hier ein **echter gemeinsamer Semantikbestand** vor.

### Freigegebene spätere Richtung

Eine zukünftige kleine Textkatalog-Iteration darf gemeinsame sichtbare **semantische Begriffe** zentralisieren.

Empfohlene stabile IDs:

- `field_type.text.label`
- `field_type.long_text.label`
- `field_type.integer.label`
- `field_type.decimal.label`
- `field_type.money.label`
- `field_type.date.label`
- `field_type.datetime.label`
- `field_type.boolean.label`
- `field_type.single_choice.label`
- `field_type.multi_choice.label`
- `common.read_only`
- `common.not_set`
- `empty.categories`

### Nicht freigegeben

Nicht jeder einmalige UI-Satz soll ausgelagert werden.

Beispiele wie:

- konkrete Fehlermeldungen eines einzelnen Flows;
- einmalige Hilfetexte;
- technisch eng an eine Funktion gebundene Meldungen

sollen lokal bleiben, solange kein zweiter echter Verbraucher existiert.

**Regel:** Zentralisieren nur bei gemeinsamer Semantik, nicht allein wegen gleicher Wörter.

---

## 2. Versionierung eines späteren Textkatalogs

Git bleibt die eigentliche Änderungshistorie.

Zusätzlich ist nur eine kleine Strukturversion nötig, zum Beispiel:

- `registry_version: 1`
- stabile Text-ID;
- aktueller Text;
- optional `deprecated`;
- optional `replacement`.

Einzelne Texte benötigen nicht automatisch jeweils eigene Versionsnummern.

Das verhindert unnötigen Metadatenaufwand.

---

## 3. Helper-Wiederverwendung

### Befund

Im Repository gibt es mehrere kleine Hilfsfunktionen und wiederkehrende Muster, aber derzeit **keinen belastbaren Grund für eine allgemeine Helper-Registry**.

Beispiele:

- Query-Parameter normalisieren;
- sichere relative Pfade validieren;
- Listenindex → stabile ID auflösen;
- Status-/Wertformatierung.

Diese Funktionen gehören weiterhin in normale Python-Module.

### Extraktionsregel

Ein Helper soll erst ausgelagert werden, wenn:

1. mindestens zwei reale Aufrufer dieselbe Semantik benötigen;
2. die Funktion möglichst pure ist;
3. kein versteckter UI-/Storage-State transportiert wird;
4. die Extraktion weniger Code und weniger Testduplikation erzeugt als sie kostet.

### Kein `utils.py`-Sammelbecken

Ein allgemeines unspezifisches `utils.py` wird nicht empfohlen.

Bevorzugt werden fachliche Namen, zum Beispiel später:

- `field_labels.py`
- `path_validation.py`
- `selection_identity.py`

aber nur, wenn echte Mehrfachnutzung entsteht.

---

## 4. Capability-Registry

### Aktueller Stand

Das Projekt besitzt bereits typisierte Capability-Grenzen über `Protocol`, beispielsweise:

- `CategoryCreateService`
- `EntryCreateService`
- `EntryFieldCreateService`
- `TuiDataPort`
- `CatalogReadPort`

Diese Grenzen sind:

- statisch typisierbar;
- einfach testbar;
- direkt nachvollziehbar;
- ohne Laufzeit-Lookup.

### Entscheidung

**Eine dynamische Capability-Registry wird in I56 nicht freigegeben.**

Sie wäre erst sinnvoll, wenn mindestens einer dieser realen Fälle auftritt:

- Plugins;
- optional ladbare Module;
- mehrere austauschbare Implementierungen zur Laufzeit;
- Capability-Erkennung durch einen Launcher;
- dynamische Feature-Verfügbarkeit, die nicht bereits sauber über optionale Adapter abbildbar ist.

Solange das nicht existiert, ist:

`normaler Import + Protocol + Dependency Injection`

wartbarer als:

`registry.resolve("capability.name.v1")`.

---

## 5. Wiederverwendung für Laienhilfe

Der in I49 eingeführte Laienhilfe-Agent profitiert besonders von stabilen gemeinsamen Fachbegriffen.

Ein zukünftiger Textkatalog darf deshalb gemeinsame **Produktbegriffe** liefern, die von:

- TUI;
- Web;
- Hilfe;
- Laienanleitung

konsistent verwendet werden.

Der Agent soll jedoch keine Runtime-Texte selbst verändern oder neue Produkttexte erfinden.

---

## 6. Verhältnis zu I55 / I57 / I58

I56 verändert die in I55 festgelegte TUI-Integrationsgrenze nicht.

Vor einem möglichen Feld-Create-Reopen gilt:

- stabile `entry_id` bleibt Pflicht;
- erlaubte `FieldType`-Menge bleibt Pflicht;
- `MONEY` und Choice-Typen bleiben geschlossen;
- Read-Port-Refresh bleibt Pflicht.

Ein späterer Textkatalog kann die sichtbaren Feldtyp-Bezeichnungen liefern, ist aber **keine technische Voraussetzung**, die I57-Reopen-Entscheidung künstlich zu blockieren.

---

## 7. Wartbarkeitsregeln aus I56

### Texte

**Zentralisieren**, wenn:
- mehrere Oberflächen/Hilfen dieselbe fachliche Bedeutung benötigen.

**Lokal lassen**, wenn:
- der Text nur zu einem einzelnen Flow gehört.

### Funktionen

**Extrahieren**, wenn:
- mindestens zwei reale Verbraucher dieselbe pure Semantik nutzen.

**Nicht extrahieren**, wenn:
- nur zukünftige Wiederverwendung vermutet wird.

### Capabilities

**Protocol/Import verwenden**, solange:
- Abhängigkeiten beim Start bekannt sind.

**Registry erst prüfen**, wenn:
- echte dynamische Austauschbarkeit oder Plugins existieren.

---

## 8. Freigegebene Folgearbeit

I56 autorisiert **noch keine Implementierung**.

Eine spätere separate Wartbarkeitsiteration darf als kleinsten sinnvollen Block ausschließlich die gemeinsamen `FieldType`-Labels zentralisieren, sobald mindestens TUI und Web diese tatsächlich gemeinsam benötigen.

Eine allgemeine Text- oder Capability-Plattform ist nicht freigegeben.

## Ergebnis

Die gewünschte Wiederverwendbarkeit ist möglich, aber sie soll **nicht pauschal** eingeführt werden.

Der wartbarste aktuelle Kurs lautet:

**gemeinsame Texte gezielt zentralisieren · Helper fachlich extrahieren · Capabilities weiterhin typisiert injizieren**
