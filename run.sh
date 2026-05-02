#!/usr/bin/env bash
set -euo pipefail

if [ -f ".env.local" ]; then
  set -a
  source ".env.local"
  set +a
fi

python3 aircraft_watch.py
