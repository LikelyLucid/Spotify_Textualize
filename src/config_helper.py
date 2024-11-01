import os
from pathlib import Path
import yaml  # Import YAML for handling configuration files

APP_NAME = "Spotify-Textualize"


def get_config_directory():
    """
    Get or create the .config directory for the given application name.

    Parameters:
    - APP_NAME: The name of the application, used to create a subdirectory within .config

    Returns:
    - Path object representing the configuration directory
    """
    # Get the user's home directory
    home = Path.home()

    # Construct the .config path regardless of OS
    config_dir = home / ".config" / APP_NAME

    # Create the directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)

    return config_dir


def get_cache_directory():
    """
    Get or create the cache directory for the given application name.

    Parameters:
    - APP_NAME: The name of the application, used to create a subdirectory within .config/cache

    Returns:
    - Path object representing the cache directory
    """
    # Get the user's home directory
    home = Path.home()

    # Construct the .config/cache path regardless of OS
    cache_dir = home / ".config" / APP_NAME / "cache"

    # Create the directory if it doesn't exist
    cache_dir.mkdir(parents=True, exist_ok=True)

    return cache_dir


def save_config(config_filename: str, config_data):
    """
    Save configuration data to a YAML file in the application's .config directory.

    Parameters:
    - config_filename: The name of the configuration file to save (should have .yaml extension)
    - config_data: The configuration data to write into the file (dictionary or string)
    """
    config_dir = get_config_directory()
    config_file_path = config_dir / config_filename

    with config_file_path.open("w") as config_file:
        if isinstance(config_data, dict):
            yaml.safe_dump(config_data, config_file, default_flow_style=False)
        elif isinstance(config_data, str):
            config_file.write(config_data)
        else:
            raise TypeError("config_data must be a dictionary or a string")

    print(f"Configuration saved to: {config_file_path}")


def read_config(config_filename: str):
    """
    Read configuration data from a YAML file in the application's .config directory.

    Parameters:
    - config_filename: The name of the configuration file to read

    Returns:
    - A dictionary containing the key-value pairs from the configuration file, or None if the file does not exist
    """
    config_dir = get_config_directory()
    config_file_path = config_dir / config_filename

    if config_file_path.exists():
        with config_file_path.open("r") as config_file:
            return yaml.safe_load(config_file) or {}
    else:
        print(f"Configuration file not found: {config_file_path}")
        return None


def get_default_keybindings():
    """Return the default keybinding configuration."""
    return {
        "focus_left": "h",
        "focus_right": "l",
        "focus_up": "k",
        "focus_down": "j",
        "play_pause": "space",
        "next_track": "n",
        "previous_track": "p",
        "volume_up": "+",
        "volume_down": "-",
    }


def get_default_settings():
    """Return the default settings configuration."""
    return {
        "volume_step": 5,  # Added default volume step
        "keybindings": get_default_keybindings(),
    }


def read_settings():
    """Read settings from a YAML config file, or return default settings."""
    settings_dir = get_config_directory()
    settings_file = settings_dir / "settings.yaml"

    if not settings_file.exists():
        default_settings = get_default_settings()
        save_config("settings.yaml", default_settings)
        return default_settings

    settings = read_config("settings.yaml")
    return settings if settings else get_default_settings()


def setup_settings():
    """Ensure default settings are present."""
    settings_dir = get_config_directory()
    settings_file = settings_dir / "settings.yaml"

    if not settings_file.exists():
        default_settings = get_default_settings()
        save_config("settings.yaml", default_settings)

    return read_settings()


def setup_keybindings():
    """Setup default keybindings if they don't exist."""
    binds_file = get_config_directory() / "binds.yaml"

    if not binds_file.exists():
        default_binds = {
            # Navigation
            "focus_left": "h",
            "focus_right": "l",
            "focus_up": "k",
            "focus_down": "j",
            # Playback controls
            "play_pause": "space",
            "next_track": "n",
            "previous_track": "p",
            "volume_up": "+",
            "volume_down": "-",
        }
        save_config("binds.yaml", default_binds)

    keybindings = read_config("binds.yaml")
    return keybindings if keybindings else get_default_keybindings()
