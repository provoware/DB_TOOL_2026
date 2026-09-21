# Iteration 64 – Minimaler Scalar-Value-Adaptervertrag

## Zweck

Dieser Vertrag bereitet ausschließlich den kleinsten späteren Adapter für den in I64 Schritt 1 gewählten CP-09-Scope **Entry Scalar Field Value Write** vor.

Es wird kein Produktcode implementiert.

## Vorhandener autoritativer Servicevertrag

`CatalogService.set_scalar_value(entry_id: str, field_id: str, value: Any) -> ScalarValue`

Dieser Vertrag bleibt autoritativ für:

- Feldtypvalidierung;
- Umwandlung über `ScalarValue.from_input(...)`;
- Entry-/Field-Existenzprüfung;
- Prüfung, ob das Feld auf den Entry anwendbar ist;
- Persistenz über den `CoordinatedWriter`;
- Audit;
- Postconditions.

Der Adapter darf diese Semantik nicht duplizieren.

## Vorbereiteter minimaler Seam

Eine spätere Implementierungsiteration darf genau folgende Form verwenden:

```python
class EntryScalarValueWriteService(Protocol):
    def set_scalar_value(
        self,
        entry_id: str,
        field_id: str,
        value: Any,
    ) -> ScalarValue: ...


class EntryScalarValueWriteAdapter:
    def __init__(self, service: EntryScalarValueWriteService) -> None:
        self._service = service

    def set_scalar_value(
        self,
        entry_id: str,
        field_id: str,
        value: Any,
    ) -> ScalarValue:
        return self._service.set_scalar_value(entry_id, field_id, value)
```

Dies ist eine Vertragsform, **keine Implementierung in I64**.

## Harte Adapterregeln

Der spätere Adapter:

1. delegiert exakt einmal;
2. verändert `entry_id` nicht;
3. verändert `field_id` nicht;
4. parst oder normalisiert `value` nicht;
5. liest kein Repository;
6. greift nicht auf SQL/Storage zu;
7. klassifiziert Exceptions nicht neu;
8. gibt dieselbe `ScalarValue` unverändert zurück.

## Warum value weiterhin Any bleibt

Der bestehende Service akzeptiert unterschiedliche Domain-Eingaben abhängig vom tatsächlichen Feldtyp:

- TEXT / LONG_TEXT → String;
- INTEGER → Integer;
- DECIMAL → durch Domain konvertierbarer Wert;
- DATE → ISO-String;
- DATETIME → ISO-String;
- BOOLEAN → Boolean;
- MONEY → kleinste Währungseinheit als Integer.

Eine neue Adapter-Union würde entweder:

- den bestehenden Servicevertrag duplizieren;
- zu früh UI-Parsing festlegen;
- zukünftige Domainvalidierung auseinanderziehen.

Darum bleibt der Adapter an dieser Stelle bewusst ein verlustfreier Durchreicher.

## UI-Grenze

Dieser Adaptervertrag ist **keine TUI-Freigabe**.

Eine spätere Integrationsentscheidung muss separat festlegen:

- wie der ausgewählte `field_id` stabil erfasst wird;
- wie `field_type` aus dem Read-Modell interpretiert wird;
- wie Text zu INTEGER/DECIMAL/DATE/DATETIME/BOOLEAN laienfreundlich eingegeben wird;
- wie ValidationError verständlich angezeigt wird;
- wie nach Erfolg genau der betroffene Read-Pfad refresht wird.

Diese Parsing-/UX-Regeln gehören nicht in den Adapter.

## Erste spätere UI-Typmenge

Falls später ein TUI-Reopen erfolgt, bleibt die erste zulässige Typmenge identisch mit der eingefrorenen Feldanlage:

- TEXT
- LONG_TEXT
- INTEGER
- DECIMAL
- DATE
- DATETIME
- BOOLEAN

Nicht freigegeben:

- MONEY;
- SINGLE_CHOICE;
- MULTI_CHOICE.

Der Adapter selbst soll diese Typmenge **nicht** hart kodieren.

## Fehlervertrag

Unverändert durchzureichen sind insbesondere bestehende Service-/Domainfehler wie:

- DOM-105 – Feld nicht gefunden;
- DOM-101 – Eintrag nicht gefunden;
- VAL-430 – Choice benötigt Choice-Repository;
- VAL-431 bis VAL-439 – typabhängige Scalar-Validierung;
- VAL-440 / VAL-441 – Feld gehört nicht zu diesem Entry.

Keine neue Adapter-Fehlerklasse wird eingeführt.

## Rückgabegrenze

Rückgabe ist exakt:

`ScalarValue`

Kein neues Create-/Write-Result-Modell.

Begründung:

- `ScalarValue` ist bereits der bestehende Domain-Rückgabevertrag;
- kein Informationsverlust;
- keine unnötige Mapping-Schicht;
- spätere UI soll ohnehin über den Read-Port refreshen, nicht den Rückgabewert direkt rendern.

## Späterer Implementierungsumfang

Eine spätere Implementierungsiteration darf ausschließlich ergänzen:

- `EntryScalarValueWriteService` Protocol;
- `EntryScalarValueWriteAdapter`;
- fokussierte Adaptertests.

Noch **nicht** zulässig:

- Runtime-Anbindung;
- neue Eingabewidgets;
- Choice-Writes;
- MONEY-UI;
- Kategorie-Felder;
- Repository-/Storage-/Serviceänderungen.

## Ergebnis

Der kleinste vorbereitete nächste Vertrag lautet:

**`entry_id + field_id + raw domain-compatible value → exakt ein set_scalar_value() → unveränderte ScalarValue`**

Damit bleibt I64 ein reiner Scope-/Vertragsschritt ohne Produktimplementierung.
