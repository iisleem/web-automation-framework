from pathlib import Path
from typing import Any

import yaml


class ConfigReader:
    def __init__(self, project_root: Path | None = None) -> None:
        self.project_root = project_root or Path(__file__).resolve().parents[1]
        self.config_dir = self.project_root / "config"

    def read_settings(self) -> dict[str, Any]:
        return self._read_yaml(self.config_dir / "settings.yaml")

    def read_environments(self) -> dict[str, Any]:
        return self._read_yaml(self.config_dir / "environments.yaml")

    def get_environment_config(self, env_name: str) -> dict[str, Any]:
        environments = self.read_environments()
        if env_name not in environments:
            available = ", ".join(sorted(environments))
            raise ValueError(f"Unknown environment '{env_name}'. Available: {available}")
        return environments[env_name]

    def load(self, env_name: str) -> dict[str, Any]:
        settings = self.read_settings()
        environment = self.get_environment_config(env_name)
        return {"env": env_name, **settings, **environment}

    @staticmethod
    def _read_yaml(path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
        return data or {}
