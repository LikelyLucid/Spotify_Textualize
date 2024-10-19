import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import MemoryCacheHandler
from config_helper import read_config, save_config, get_config_directory

CONFIG_FILE = "spotify_creds.conf"


scope = "user-library-read"


def authenticate_user():
    """
    Authenticate the user with Spotify using the SpotifyOAuth flow and config

    Returns:
    - A Spotify object with the user's credentials
    """
    credentials = read_config(CONFIG_FILE)
    if credentials is None:
        print("User not authenticated.")

        default_redirect_uri = "http://localhost:8888/callback"

        client_id = input("Enter your client ID: ")
        client_secret = input("Enter your client secret: ")
        redirect_uri = input(
            f"Enter your redirect URI (leave blank for {default_redirect_uri}): "
        )

        if redirect_uri == "":
            redirect_uri = default_redirect_uri

    else:  # Use the saved credentials
        client_id = credentials["client_id"]
        client_secret = credentials["client_secret"]
        redirect_uri = credentials["redirect_uri"]

    try:
        sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                scope=scope,
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                cache_path=f"{get_config_directory()}/.cache-{client_id}",
            )
        )
        if sp.me() is not None:  # Check if the user is authenticated
            if (
                credentials is None
            ):  # Save the credentials if they are not already saved
                save_config(
                    CONFIG_FILE,
                    f"client_id: {client_id}\nclient_secret: {client_secret}\nredirect_uri: {redirect_uri}",
                )
            return sp
        else:
            print("Authentication failed.")
    except Exception as e:
        print(f"Error: {e}")
        return None
    return None # Return None if the user is not authenticated

sp = authenticate_user()
sp.current_playback()