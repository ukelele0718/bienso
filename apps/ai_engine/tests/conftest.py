"""Pytest configuration for ai_engine tests.

Adds the repo root to sys.path so tests can import via the full
package path: apps.ai_engine.src.plate_ocr
"""

from __future__ import annotations

import sys
from pathlib import Path

# Insert repo root (datn/) so `apps.ai_engine.src` is importable
_REPO_ROOT = Path(__file__).resolve().parents[3]  # datn/
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
