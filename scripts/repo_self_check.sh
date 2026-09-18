#!/usr/bin/env bash
set -u

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 90

STAMP="$(date '+%Y-%m-%d_%H-%M-%S')"
REPORT="REPO_SELF_CHECK_${STAMP}.txt"
FAILS=0

exec > >(tee -a "$REPORT") 2>&1

echo "PROVOWARE REPOSITORY SELF-CHECK"
echo "Repo: $ROOT"
echo "Zeit: $(date --iso-8601=seconds 2>/dev/null || date)"
echo

for f in README.md CONTRIBUTING.md .gitignore .editorconfig docs/PROJECT_STANDARDS.md; do
  if [[ -f "$f" ]]; then
    echo "GRÜN: $f vorhanden"
  else
    echo "ROT: $f fehlt"
    FAILS=$((FAILS+1))
  fi
done

echo
if [[ "$FAILS" -eq 0 ]]; then
  echo "GESAMTSTATUS: GRÜN"
  echo "Empfehlung: Produktcode über separaten Import-PR hinzufügen und danach CI auf echte CP-Gates erweitern."
  exit 0
fi

echo "GESAMTSTATUS: ROT"
echo "Fehler: $FAILS"
exit 1
