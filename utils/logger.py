from __future__ import annotations

import logging
from pathlib import Path

from automation_core.logger import get_logger as core_get_logger


def get_logger(name: str) -> logging.Logger:
    reports_dir = Path(__file__).resolve().parents[1] / "reports"
    return core_get_logger(name, log_dir=reports_dir, file_name="framework.log")
