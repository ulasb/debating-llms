#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

source .venv/bin/activate

pip install -q -r requirements.txt

URL="http://127.0.0.1:8000"
(sleep 2 && open -a "Google Chrome" "$URL") &

exec uvicorn app:app --reload
