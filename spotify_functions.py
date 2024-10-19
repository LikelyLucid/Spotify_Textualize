import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config_helper import read_config, save_config

scope = "user-library-read"

credentials = read_conf


# sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
