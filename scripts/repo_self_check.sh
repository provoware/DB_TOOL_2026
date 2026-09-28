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

for f in README.md TODO.md AGENTS.md CONTRIBUTING.md .gitignore .editorconfig docs/PROJECT_STANDARDS.md scripts/build_iteration_context.py scripts/iteration_preflight.py src/provoware_db/mask_builder/browser_shell.py; do
  if [[ -f "$f" ]]; then
    echo "GRÜN: $f vorhanden"
  else
    echo "ROT: $f fehlt"
    FAILS=$((FAILS+1))
  fi
done

echo
if python3 scripts/build_iteration_context.py --check; then
  echo "GRÜN: Fast Context"
else
  echo "ROT: Fast Context"
  FAILS=$((FAILS+1))
fi
if python3 scripts/iteration_preflight.py; then
  echo "GRÜN: Iterations-Preflight"
else
  echo "ROT: Iterations-Preflight"
  FAILS=$((FAILS+1))
fi

echo
if [[ "$FAILS" -eq 0 ]]; then
  echo "GESAMTSTATUS: GRÜN"
  echo "Umfang: Repository-Struktur und Iterations-Preflight; keine vollständige Produkt- oder Browserabnahme."
  echo "Nächster Schritt: I167-Chromium-Gate mit installiertem Browser ausführen."
  exit 0
fi

echo "GESAMTSTATUS: ROT"
echo "Fehler: $FAILS"
exit 1
