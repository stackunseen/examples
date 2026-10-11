#!/usr/bin/env bash
# CI gate: retrieval must keep finding the right section in the top five for at least 90% of the test questions.
set -euo pipefail
PY=$(command -v python || command -v python3)
"$PY" evaluate.py --min-recall 0.9
