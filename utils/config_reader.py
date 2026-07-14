from __future__ import annotations

from pathlib import Path
from typing import Any

from automation_core.config import ConfigReader as CoreConfigReader


class ConfigReader(CoreConfigReader):
    """Compatibility wrapper preserving the web framework config import path."""

    def __init__(self, project_root: Path | None = None) -> None:
        super().__init__(project_root or Path(__file__).resolve().parents[1])

    def load(self, env_name: str) -> dict[str, Any]:
        return super().load(
            env_name,
            environment_key="env",
            merge_environment=True,
        )
