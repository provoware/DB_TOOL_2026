from __future__ import annotations

from .constants import DatabaseKind

# SHA-256 over normalized sqlite_schema rows (tables + indexes).
# Regenerate only as part of an intentional schema migration.
EXPECTED_SCHEMA_FINGERPRINTS = {
    DatabaseKind.MAIN: "3376adc9284f6668d86bd20a673938227ab2c95c22d0810f0186c708ef162d48",
    DatabaseKind.STATE: "f46afd60f767e71b4d13b58b1980550907b15cb19544f2e49fb383fa2bf03cf1",
    DatabaseKind.TESTLAB: "eb1a337c669b86b95b428d11d6af8c27ec2b7e56b49ba12055018ae61442f80f",
}
