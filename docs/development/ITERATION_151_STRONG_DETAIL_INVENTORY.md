# I151 – Inventur starke Detailansicht

## Ziel

Den offenen Punkt **C · Datenarbeit → starke Detailansicht** fachlich und technisch inventarisieren, ohne Runtime-Verhalten zu ändern.

## Bereits vorhanden

Der GET-only Webpfad liefert bereits:
- gewählte Kategorie,
- gewählten Eintrag,
- sichtbare Felder des Eintrags,
- formatierte Feldwerte,
- Pflichtfeldkennzeichnung,
- sichere GET-Navigation,
- weiterhin keine produktive Browser-Persistenz.

Damit ist keine neue Repository- oder Schemafähigkeit erforderlich.

## Konkrete Lücken

Für eine starke Detailansicht fehlen noch:

1. **Expliziter Detailkopf** für den gewählten Eintrag statt ausschließlich Markierung in der Navigationsliste.
2. **Eindeutiger Kontext**: Kategorie + Eintrag müssen im Detailbereich sichtbar zusammengehören.
3. **Feldanzahl und klarer Leerzustand**, damit sofort erkennbar ist, ob und wie viele Felder dargestellt werden.
4. **Stabiler Detail-Zielpunkt** im DOM, auf den Such-/Listen-Navigation später deterministisch verweisen kann.
5. **Trennung von Daten- und Fundstellenvertrag**: Die Detailansicht darf noch keine globale Feldwertsuche vorwegnehmen.

## Kleinster späterer Umsetzungsslice

Die spätere Produktiteration soll ausschließlich die vorhandene Web-Read-Projektion ergänzen:
- Detailkopf mit Eintragstitel,
- Kategoriebezug,
- Anzahl sichtbarer Felder,
- stabiler semantischer Detailcontainer,
- verständlicher Leerzustand.

## Nicht enthalten

- keine globale Feldwertsuche,
- keine Fundstellenmarkierung,
- keine Bearbeitung,
- keine Persistenz,
- kein neues Repository-Query,
- keine Schemaänderung,
- kein CP-03-/CP-06-Reopen.

## Gate-Empfehlung

Produkt-/UI-Gate nur für die spätere Runtime-Umsetzung. Diese Inventur selbst ist **scope-only**.
