#!/bin/bash
# One screen against the approved baseline, with fresh captures.
QA="$(cd "$(dirname "$0")" && pwd)"
python3 "$QA/compare.py" "$1" --label gate --no-orig-cache 2>&1 | grep -v side-by-side
