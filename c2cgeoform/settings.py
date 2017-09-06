import os
import configparser


def apply_local_settings(settings):
    """ Apply to the ``settings`` dict the settings found in the local settings
    file.
    """
    local_settings_path = settings.get('local_settings_path')
    if local_settings_path is not None and os.path.exists(local_settings_path):
        config_parser = configparser.ConfigParser()
        config_parser.read(local_settings_path)
        settings.update(config_parser.items('app:main'))
