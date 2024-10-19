import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import MemoryCacheHandler
from config_helper import read_config, save_config

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
    else:
        client_id = credentials["client_id"]
        client_secret = credentials["client_secret"]
        redirect_uri = credentials["redirect_uri"]
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope=scope,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            cache_handler=MemoryCacheHandler(),
        )
    )
    if sp.me() is not None:
        save_config(CONFIG_FILE, f"client_id: {client_id}\nclient_secret: {client_secret}\nredirect_url: {redirect_uri}")
        return sp

    
