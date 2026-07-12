import json
from pathlib import Path
from typing import Any


class DataReader:
    def __init__(self, project_root: Path | None = None) -> None:
        self.project_root = project_root or Path(__file__).resolve().parents[1]
        self.data_dir = self.project_root / "data"

    def read_json(self, file_name: str) -> dict[str, Any]:
        path = self.data_dir / file_name
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
