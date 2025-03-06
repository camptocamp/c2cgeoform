import configparser
from pathlib import Path

import pyramid.config.settings


def apply_local_settings(settings: pyramid.config.settings.Settings) -> None:
    """Apply to the ``settings`` dict the settings found in the local settings file."""
    local_settings_path_str = settings.get("local_settings_path")
    local_settings_path = None if local_settings_path_str is None else Path(local_settings_path_str)
    if local_settings_path is not None and local_settings_path.exists():
        config_parser = configparser.ConfigParser()
        config_parser.read(local_settings_path_str)
        settings.update(config_parser.items("app:main"))
