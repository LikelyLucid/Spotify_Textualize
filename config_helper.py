import os
from pathlib import Path

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


def save_config(config_filename: str, config_data: str):
    """
    Save configuration data to a file in the application's .config directory.

    Parameters:
    - APP_NAME: The name of the application, used to create a subdirectory within .config
    - config_filename: The name of the configuration file to save
    - config_data: The configuration data to write into the file
    """
    config_dir = get_config_directory()
    config_file_path = config_dir / config_filename

    # Save the configuration data
    with config_file_path.open("w") as config_file:
        if isinstance(config_data, dict):
            for key, value in config_data.items():
                config_file.write(f"{key}: {value}\n")
        else:
            config_file.write(config_data)

    print(f"Configuration saved to: {config_file_path}")


def read_config(config_filename: str):
    """
    Read configuration data from a file in the application's .config directory.

    Parameters:
    - APP_NAME: The name of the application, used to locate a subdirectory within .config
    - config_filename: The name of the configuration file to read

    Returns:
    - A string containing the contents of the configuration file, or None if the file does not exist
    """
    config_dir = get_config_directory()
    config_file_path = config_dir / config_filename

    config_data = {}

    if config_file_path.exists():
        with config_file_path.open("r") as config_file:
            config_data = config_file.read()
            for line in config_data.split():
                key, value = line.split(":")
                config_data[key] = value
        return config_data
    else:
        print(f"Configuration file not found: {config_file_path}")
        return None
