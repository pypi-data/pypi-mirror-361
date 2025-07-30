import tomllib
from pathlib import Path
from typing import Any

import tomli_w


def load_settings(settings_path: Path) -> dict[str, Any]:
    with settings_path.open(mode="rb") as toml_file:
        settings_dict: dict[str, Any] = tomllib.load(toml_file)

    return settings_dict


def save_settings(settings_dict: dict[str, Any], settings_path: Path) -> None:
    with settings_path.open(mode="wb") as toml_file:
        tomli_w.dump(settings_dict, toml_file)
