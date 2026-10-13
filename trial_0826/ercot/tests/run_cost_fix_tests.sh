#!/bin/bash
# Prompt 36 T1 test run — PCM_ERCOT on the CRC front-end (Kay pastes the output).
#   cd /groups/adowling/ylu28/RTS-GMLC-ercot && git pull && bash trial_0826/ercot/tests/run_cost_fix_tests.sh
set -u
export PYTHONNOUSERSITE=1 OMP_NUM_THREADS=4
REPO=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
cd "$REPO/trial_0826" || exit 1
echo "branch $(git rev-parse --abbrev-ref HEAD) @ $(git rev-parse --short HEAD); python $(command -v python)"
rc=0
echo "== (a)-(e) + RTS round trip: ercot/tests"
python -m pytest ercot/tests -s -q -p no:cacheprovider || rc=1
echo "== (f) campaign suite"
python -m pytest campaign/tests -q -p no:cacheprovider || rc=1
echo "== (f) multi_pem suite"
python -m pytest multi_pem/tests -q -p no:cacheprovider || rc=1
echo "== verify_metadata on v2"
python ercot/verify_metadata.py --data_dir ercot/data/ercot123_2019_v2 || rc=1
[ $rc -eq 0 ] && echo "COST-FIX TESTS PASS" || echo "COST-FIX TESTS FAIL"
exit $rc
