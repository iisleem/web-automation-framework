import re

import pytest

from automation_core.config import ConfigReader as CoreConfigReader
from automation_core.helpers.cleanup import CleanupRegistry as CoreCleanupRegistry
from automation_core.helpers.soft_assertions import SoftAssert as CoreSoftAssert

from utils.config_reader import ConfigReader
from utils.helpers.cleanup import CleanupRegistry
from utils.helpers.data import random_email, timestamped_value, unique_id
from utils.helpers.files import assert_file_exists, cleanup_directory
from utils.helpers.soft_assertions import SoftAssert
from utils.helpers.text import extract_numbers
from utils.helpers.wait import wait_until


pytestmark = pytest.mark.helpers


def test_config_reader_wraps_core_and_preserves_web_load_shape(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "settings.yaml").write_text(
        "execution:\n  browsers:\n    - chromium\nreporting:\n  report_kind: core\n",
        encoding="utf-8",
    )
    (config_dir / "environments.yaml").write_text(
        "qa:\n  base_url: https://www.saucedemo.com/\n  username: standard_user\n",
        encoding="utf-8",
    )

    reader = ConfigReader(tmp_path)
    loaded = reader.load("qa")

    assert isinstance(reader, CoreConfigReader)
    assert loaded["env"] == "qa"
    assert loaded["execution"]["browsers"] == ["chromium"]
    assert loaded["base_url"] == "https://www.saucedemo.com/"
    assert loaded["username"] == "standard_user"


def test_data_wrappers_preserve_web_defaults():
    assert re.fullmatch(r"order-[a-f0-9]{10}", unique_id("order"))
    assert re.fullmatch(r"automation\.[a-f0-9]{10}@example\.com", random_email())
    assert re.fullmatch(r"run-\d{20}", timestamped_value("run"))


def test_wait_text_file_and_soft_assertion_wrappers_keep_public_behavior(tmp_path):
    file_path = tmp_path / "artifact.txt"
    file_path.write_text("ready", encoding="utf-8")

    assert wait_until(lambda: "done", timeout_seconds=0.1, interval_seconds=0.01) == "done"
    assert extract_numbers("Total 42.50 and tax 3") == ["42", "50", "3"]
    assert assert_file_exists(file_path) == file_path

    directory = tmp_path / "cleanup"
    directory.mkdir()
    (directory / "old.txt").write_text("old", encoding="utf-8")
    cleanup_directory(directory)
    assert directory.exists()
    assert list(directory.iterdir()) == []

    softly = SoftAssert()
    assert isinstance(softly, CoreSoftAssert)
    softly.assert_equal("actual", "expected")
    with pytest.raises(AssertionError, match="Soft assertion failures"):
        softly.assert_all()


def test_cleanup_registry_import_path_wraps_core():
    registry = CleanupRegistry()

    assert isinstance(registry, CoreCleanupRegistry)
