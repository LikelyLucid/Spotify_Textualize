import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from pathlib import Path

scope = "user-library-read"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))


def get_config_directory(app_name: str):
    """
    Get or create the .config directory for the given application name.

    Parameters:
    - app_name: The name of the application, used to create a subdirectory within .config

    Returns:
    - Path object representing the configuration directory
    """
    # Get the user's home directory
    home = Path.home()

    # Construct the .config path regardless of OS
    config_dir = home / ".config" / app_name

    # Create the directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)

    return config_dir


def save_config(app_name: str, config_filename: str, config_data: str):
    """
    Save configuration data to a file in the application's .config directory.

    Parameters:
    - app_name: The name of the application, used to create a subdirectory within .config
    - config_filename: The name of the configuration file to save
    - config_data: The configuration data to write into the file
    """
    config_dir = get_config_directory(app_name)
    config_file_path = config_dir / config_filename

    # Save the configuration data
    with config_file_path.open("w") as config_file:
        config_file.write(config_data)

    print(f"Configuration saved to: {config_file_path}")


def read_config(app_name: str, config_filename: str):
    """
    Read configuration data from a file in the application's .config directory.

    Parameters:
    - app_name: The name of the application, used to locate a subdirectory within .config
    - config_filename: The name of the configuration file to read

    Returns:
    - A string containing the contents of the configuration file, or None if the file does not exist
    """
    config_dir = get_config_directory(app_name)
    config_file_path = config_dir / config_filename

    if config_file_path.exists():
        with config_file_path.open("r") as config_file:
            config_data = config_file.read()
            return config_data
    else:
        print(f"Configuration file not found: {config_file_path}")
        return None


# Example usage
app_name = "myapp"
config_filename = "settings.conf"

# Save some configuration data
config_data = "example_setting = True"
save_config(app_name, config_filename, config_data)

# Read the configuration data back
config_data_read = read_config(app_name, config_filename)
if config_data_read:
    print("Read configuration data:")
    print(config_data_read)
