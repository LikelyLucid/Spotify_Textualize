import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import MemoryCacheHandler
from config_helper import read_config, save_config

CONFIG_FILE = "spotify_creds.conf"


scope = "user-library-read"


credentials = read_config(CONFIG_FILE)
if credentials == None:
    print("User not authenticated.")

    default_redirect_uri = "http://localhost:8888/callback"

    client_id = input("Enter your client ID: ")
    client_secret = input("Enter your client secret: ")
    redirect_uri = input(
        f"Enter your redirect URI (leave blank for {default_redirect_uri}): "
    )

    if redirect_uri == "":
        redirect_uri = default_redirect_uri
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope=scope,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            cache_handler=MemoryCacheHandler(),
        )
    )


print(credentials)

# sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
print(sp.me())
