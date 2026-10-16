#!/bin/bash
# Cloud sessions start without pytest; install it so the full suite can run.
set -euo pipefail
[ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || exit 0
python3 -c "import pytest" 2>/dev/null || python3 -m pip install -q pytest
