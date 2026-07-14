from __future__ import annotations

import os
from pathlib import Path

from automation_core.reporting.allure_cli import get_or_install_allure_cli as core_get_or_install_allure_cli


DEFAULT_ALLURE_VERSION = "2.29.0"


def get_or_install_allure_cli(project_root: Path, logger) -> str | None:
    version = os.getenv("ALLURE_CLI_VERSION", DEFAULT_ALLURE_VERSION)
    return core_get_or_install_allure_cli(project_root, logger, version=version)
