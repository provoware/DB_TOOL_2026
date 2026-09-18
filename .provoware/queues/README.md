# Agent Queues

Diese Ordner bilden den Übergabemechanismus zwischen spezialisierten Agenten.

- `review/`: neue Findings oder Review-Aufträge
- `planning/`: analysierte Findings für den Planungsagenten
- `blocked/`: blockierte Arbeit, z. B. Dateikollision
- `done/`: abgeschlossene Queue-Einträge

Jede Queue-Datei ist YAML oder JSON und enthält mindestens:

- iteration
- source_agent
- created_at
- affected_files
- reason
- required_action
- status
