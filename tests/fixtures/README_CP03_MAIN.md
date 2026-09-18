# CP-03 MAIN Schema V1 – Testfixture

Diese Datei ist ein **nichtproduktives Testfixture**.

- Quelle: eingefrorenes `CP03_main_schema.sql`
- SHA-256: `4119f49eef696cb7bafaed5bf4147c03e8340848381946adaed77227c76c81f6`
- Git-Blob des Originaltexts: `58d38dae615b0528f1e4ca4b5b8dfee49a95d601`
- erwarteter MAIN-Schema-Fingerprint: `3376adc9284f6668d86bd20a673938227ab2c95c22d0810f0186c708ef162d48`
- `user_version`: 1
- `application_id`: PVM1 / `0x50564D31`

Die SQL-Datei wird im Test bytegenau geprüft und anschließend ausschließlich in einem temporären Verzeichnis zu einer Test-`main.db` aufgebaut. Deterministische Demo-Daten werden **nach** dem Schemaaufbau eingefügt und verändern den Schema-Fingerprint nicht.

Sie darf niemals als Nutzerdatenbank oder Produktionsdatenquelle verwendet werden.
