import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config_helper import read_config, save_config

CONFIG_FILE = "spotify_creds.conf"


scope = "user-library-read"


credentials = read_config(CONFIG_FILE)
if credentials == None:
    print("User not authenticated.")
    client_id = input("Enter your client ID: ")
    client_secret = input("Enter your client secret: ")
    redirect_uri = input("Enter your redirect URI: ")

    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope=scope,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
        )
    )

    


print(credentials)

# sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
print(sp.me())