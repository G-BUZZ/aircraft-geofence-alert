#!/usr/bin/env bash
set -euo pipefail

# Load local configuration if present.
# The .env file is intentionally ignored by git.
if [[ -f ".env" ]]; then
  set -a
  source ".env"
  set +a
else
  echo "Missing .env file."
  echo "Copy .env.example to .env and configure POINT_LAT and POINT_LON before running."
  exit 1
fi

python3 aircraft_watch.py
