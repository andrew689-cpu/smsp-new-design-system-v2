#!/bin/bash
# The full review gate. Run from anywhere: bash design-source/qa/gate.sh [Screen ...]
# With no arguments it checks all 34 screens. Exit 0 only when every check passes.
set -u
QA="$(cd "$(dirname "$0")" && pwd)"
SRC="$(dirname "$QA")"
export REAL_IMAGES="$SRC/images" SETTLE_MS="${SETTLE_MS:-3000}"
FAIL=0
python3 "$QA/merge_tokens.py" "$SRC/workspace" | sed -n '2p'

echo "== 1. Strict rule (one component, configured by props)"
python3 "$QA/lint_strict.py" | tail -1
[ "${PIPESTATUS[0]}" -eq 0 ] || { python3 "$QA/lint_strict.py" --summary; FAIL=1; }

echo "== 2. Component format"
python3 "$QA/lint_components.py" "$SRC/workspace/project" > /tmp/smsp-lint.$$ 2>&1 || FAIL=1
grep -E 'ERROR|^checked' /tmp/smsp-lint.$$ | tail -8; rm -f /tmp/smsp-lint.$$

SCREENS=("$@")
if [ "${#SCREENS[@]}" -eq 0 ]; then
  while IFS= read -r s; do SCREENS+=("$s"); done < <(python3 -c "
import json,sys
c=json.load(open(sys.argv[1],encoding='utf-8'))
print('\n'.join(sorted(k[:-8] for k,v in c['boards'].items() if v.get('page')=='salinan4')))" "$SRC/workspace/project/canvas.json")
fi

echo "== 3. Screens contain only components (${#SCREENS[@]} screens)"
python3 "$QA/lint_board.py" "${SCREENS[@]}" > /tmp/smsp-board.$$ 2>&1 || FAIL=1
echo "pass $(grep -c '^PASS' /tmp/smsp-board.$$), fail $(grep -cE '^(FAIL|MISSING)' /tmp/smsp-board.$$)"
grep -E '^(FAIL|MISSING)|^    ' /tmp/smsp-board.$$ | head -20; rm -f /tmp/smsp-board.$$

echo "== 4. Same as the approved baseline (real images, fresh captures)"
printf '%s\n' "${SCREENS[@]}" | xargs -n1 -P 6 bash "$QA/compare_one.sh" > /tmp/smsp-cmp.$$ 2>&1
P=$(grep -c '^PASS' /tmp/smsp-cmp.$$); F=$(grep -c '^FAIL' /tmp/smsp-cmp.$$)
echo "pass $P, fail $F"
grep -E '^FAIL|^  x ' /tmp/smsp-cmp.$$ | cut -c1-240
[ "$F" -eq 0 ] && [ "$P" -eq "${#SCREENS[@]}" ] || FAIL=1
rm -f /tmp/smsp-cmp.$$

if [ "$FAIL" -eq 0 ]; then echo "GATE PASS"; else echo "GATE FAIL"; fi
exit "$FAIL"
