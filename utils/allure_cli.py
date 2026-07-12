from __future__ import annotations

import os
from pathlib import Path
import shutil
import stat
import urllib.request
import zipfile


DEFAULT_ALLURE_VERSION = "2.29.0"


def get_or_install_allure_cli(project_root: Path, logger) -> str | None:
    system_allure = shutil.which("allure")
    if system_allure:
        return system_allure

    version = os.getenv("ALLURE_CLI_VERSION", DEFAULT_ALLURE_VERSION)
    install_dir = project_root / ".tools" / "allure" / f"allure-{version}"
    executable = _allure_executable_path(install_dir)
    if executable.exists():
        return str(executable)

    try:
        logger.info("Allure CLI not found. Installing Allure CLI %s locally...", version)
        _download_and_extract_allure(project_root, version, install_dir)
        executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
        logger.info("Installed local Allure CLI: %s", executable)
        return str(executable)
    except Exception as error:
        logger.warning("Could not install local Allure CLI. Falling back to built-in report: %s", error)
        return None


def _download_and_extract_allure(
    project_root: Path,
    version: str,
    install_dir: Path,
) -> None:
    tools_dir = project_root / ".tools" / "allure"
    cache_dir = tools_dir / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    archive_path = cache_dir / f"allure-commandline-{version}.zip"
    url = (
        "https://repo.maven.apache.org/maven2/io/qameta/allure/allure-commandline/"
        f"{version}/allure-commandline-{version}.zip"
    )

    if not archive_path.exists():
        urllib.request.urlretrieve(url, archive_path)

    if install_dir.exists():
        shutil.rmtree(install_dir)
    install_dir.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(archive_path) as archive:
        archive.extractall(install_dir.parent)


def _allure_executable_path(install_dir: Path) -> Path:
    if os.name == "nt":
        return install_dir / "bin" / "allure.bat"
    return install_dir / "bin" / "allure"
