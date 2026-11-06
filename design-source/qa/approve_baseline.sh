#!/bin/bash
# Make the workspace the new approved baseline. Run this only after the owner's change is reviewed
# and published, so later gates compare against what the owner accepted.
set -eu
QA="$(cd "$(dirname "$0")" && pwd)"
SRC="$(dirname "$QA")"
rm -rf "$SRC/baseline"
mkdir -p "$SRC/baseline"
cp "$SRC"/workspace/project/*.dc.html "$SRC"/workspace/project/tokens.css "$SRC/baseline/"
echo "baseline updated: $(ls "$SRC/baseline" | wc -l | tr -d ' ') files"
