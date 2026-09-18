# PROVOWARE Agent-Orchestrierung V1

## Ziel

Mehrere spezialisierte Agenten arbeiten nacheinander oder parallel, ohne dieselbe Datei gleichzeitig zu verändern. Prüfagenten analysieren bevorzugt nur geänderte Dateien und deren direkte Abhängigkeiten.

## Rollen

### 1. Änderungsagent
- setzt genau einen freigegebenen Patch um
- darf nur Dateien anfassen, die ihm im Plan zugewiesen sind
- schreibt anschließend ein Change-Manifest

### 2. Prüfagent
- liest das Change-Manifest
- prüft nur angefasste Dateien plus direkte Abhängigkeiten
- erzeugt Findings, aber ändert keinen Produktivcode
- schreibt Findings in die Review-Queue

### 3. Analyseagent
- nimmt Findings aus der Review-Queue
- gruppiert, dedupliziert und bewertet sie
- erzeugt daraus eine konkrete Patch-Empfehlung
- schreibt diese in die Planning-Queue

### 4. Planungsagent
- baut aus Findings einen kleinen, sicheren Iterationsplan
- nennt Ziel, Dateien, Risiken, Tests und bewusste Nicht-Änderungen
- darf keinen Code verändern

### 5. Orchestrator
- prüft vor Start jeder Iteration Dateikollisionen
- vergibt Dateibesitz für die Iteration
- entscheidet Reihenfolge und Parallelisierbarkeit
- startet erst danach Änderungsagenten
- prüft am Ende Vollständigkeit, Gate-Status und Queue-Reste

### 6. Gate-Agent
- führt nur relevante Tests aus
- validiert Frozen-Core, Syntax, Regression und betroffene Schichten
- erzeugt GRÜN/GELB/ROT und eine TXT-Auswertung
- ändert keinen Produktivcode

### 7. Screenshot-Agent
- alle 5 Iterationen
- erzeugt definierte UI-Screenshots
- schreibt Kurzfazit in die Entwicklerdokumentation
- vergleicht gegen letzte freigegebene Referenz

## Ablauf

```text
Änderungsplan
    ↓
Kollisionsprüfung
    ↓
Dateibesitz reservieren
    ↓
Änderungsagent
    ↓
Change-Manifest
    ↓
Prüfagent
    ↓
Review-Queue
    ↓
Analyseagent
    ↓
Planning-Queue
    ↓
Planungsagent
    ↓
Orchestrator entscheidet Reihenfolge
    ↓
nächste Iteration
```

## Grundregel: keine konkurrierenden Schreibzugriffe

Eine Datei darf pro Iteration nur genau einem Änderungsagenten gehören.

Beispiel:

```yaml
ownership:
  src/provoware_db/web/routes.py: agent-web-01
  src/provoware_db/application/catalog_service.py: agent-core-01
```

Wenn zwei Pläne dieselbe Datei beanspruchen, ist der Status ROT und beide Patches werden blockiert.

## Change-Manifest

Nach jedem Patch:

```yaml
iteration: 12
agent: agent-web-01
changed_files:
  - src/provoware_db/web/routes.py
  - tests/web/test_routes.py
reason: "Neue Kategorieansicht"
tests_required:
  - tests/web/test_routes.py
dependencies_read:
  - src/provoware_db/application/catalog_service.py
```

Der Prüfagent liest primär diese Dateien.

## Queue-Prinzip

```text
.provoware/queues/review/
.provoware/queues/planning/
.provoware/queues/blocked/
.provoware/queues/done/
```

Datei vorhanden = Arbeit vorhanden.

Nach erfolgreicher Verarbeitung wird die Datei nach `done/` verschoben.

## Screenshot-Regel

Alle fünf Iterationen:

- gleiche Referenz-Viewportgrößen
- gleiche Testdaten
- aktives Theme dokumentieren
- Screenshot speichern
- Kurzfazit mit maximal 5 Punkten
- Abweichungen markieren

Pfad:

```text
docs/development/screenshots/iteration-0005/
docs/development/screenshots/iteration-0010/
...
```

## Kosten-/Kontext-Regel

Prüfagenten dürfen standardmäßig nur lesen:

1. geänderte Dateien
2. direkte Importe/Abhängigkeiten
3. betroffene Tests
4. relevante Manifest-/Freeze-Dateien

Ein Full-Repo-Scan ist nur erlaubt, wenn:
- Architektur verändert wurde
- Frozen-Core betroffen ist
- Abhängigkeitsgraph unklar ist
- Gate einen systemweiten Fehler meldet

## Abschluss jeder Iteration

Der Orchestrator bestätigt:

- keine offenen Dateisperren
- keine Queue-Leichen
- keine unbewerteten Findings
- alle vorgesehenen Tests gelaufen
- Änderungsvolumen dokumentiert
- nächste Iteration kollisionsfrei planbar
