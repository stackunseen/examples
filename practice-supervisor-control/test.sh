#!/usr/bin/env bash
# CI gate: the solution passes every check, and supervisor.py as handed out does not, so the checks really test the TODOs.
set -euo pipefail
PY=$(command -v python || command -v python3)
PRACTICE_SOLUTION=1 "$PY" -m unittest -q
if "$PY" -m unittest -q > /dev/null 2>&1; then
  echo "supervisor.py passes as handed out: the checks do not test the TODOs." >&2
  exit 1
fi
