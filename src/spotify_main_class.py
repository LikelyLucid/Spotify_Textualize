from spotify_functions import authenticate_user

class Spotify_Playback_Data:
    def __init__(self):
        """
        Initialize the Spotify Playback Data object

        Returns:
        - None
        """
        sp = authenticate_user()
        attempts = 0
        while sp is None:
            sp = authenticate_user()
            attempts += 1
            if attempts > 3:
                print("Failed to authenticate after 3 attempts.")
                Exception("Failed to authenticate after 3 attempts  - exiting.")
        self.sp = sp
        self.update()

    def update(self):
        """
        Update the playback data

        Returns:
        - None
        """
        playback_data = self.sp.current_playback()
        print(playback_data)

        # If playback_data is None, set all fields to empty strings or defaults
        if playback_data is None:
            print("No playback data available.")
            self.device_id = None
            self.device_name = None
            self.device_is_active = None
            self.device_is_private_session = None
            self.device_is_restricted = None
            self.device_type = None
            self.device_supports_volume = None
            self.device_volume_percent = None
            self.shuffle = None
            self.smart_shuffle = None
            self.repeat = None
            self.timestamp = None
            self.progress_ms = None
            self.currently_playing_type = None
            self.is_playing = None
            self.external_url = None
            self.context_href = None
            self.context_type = None
            self.context_uri = None
            self.track = None
            self.track_id = None
            self.track_uri = None
            self.track_explicit = None
            self.track_popularity = None
            self.track_preview_url = None
            self.track_number = None
            self.track_duration = None
            self.album_name = None
            self.album_id = None
            self.album_release_date = None
            self.album_total_tracks = None
            self.artists = None
            self.available_markets = None
            return

        # Device Information
        self.device_id = playback_data["device"]["id"]
        self.device_name = playback_data["device"]["name"]
        self.device_is_active = playback_data["device"]["is_active"]
        self.device_is_private_session = playback_data["device"]["is_private_session"]
        self.device_is_restricted = playback_data["device"]["is_restricted"]
        self.device_type = playback_data["device"]["type"]
        self.device_supports_volume = playback_data["device"]["supports_volume"]
        self.device_volume_percent = playback_data["device"]["volume_percent"]

        # Playback Information
        self.shuffle = playback_data["shuffle_state"]
        self.smart_shuffle = playback_data["smart_shuffle"]
        self.repeat = playback_data["repeat_state"]
        self.timestamp = playback_data["timestamp"]
        self.progress_ms = playback_data["progress_ms"]
        self.currently_playing_type = playback_data["currently_playing_type"]
        self.is_playing = playback_data["is_playing"]

        # Context Information
        try:
            self.external_url = playback_data["context"]["external_urls"]["spotify"]
            self.context_href = playback_data["context"]["href"]
            self.context_type = playback_data["context"]["type"]
            self.context_uri = playback_data["context"]["uri"]
        except:
            pass

        # Track Information
        self.track = playback_data["item"]["name"]
        self.track_id = playback_data["item"]["id"]
        self.track_uri = playback_data["item"]["uri"]
        self.track_explicit = playback_data["item"]["explicit"]
        self.track_popularity = playback_data["item"]["popularity"]
        self.track_preview_url = playback_data["item"]["preview_url"]
        self.track_number = playback_data["item"]["track_number"]
        self.track_duration = playback_data["item"]["duration_ms"]

        # Album Information
        self.album_name = playback_data["item"]["album"]["name"]
        self.album_id = playback_data["item"]["album"]["id"]
        self.album_release_date = playback_data["item"]["album"]["release_date"]
        self.album_total_tracks = playback_data["item"]["album"]["total_tracks"]

        # Artist Information
        self.artists = [artist["name"] for artist in playback_data["item"]["artists"]]
        self.available_markets = playback_data["item"]["available_markets"]

    def playing_settings(self):
        """ Creates the text above the progress bar"""
        if self.device_name is not None:
            information = {}
            result = "("

            information["Device"] = self.device_name
            if self.smart_shuffle:
                information["Shuffle"] = "Smart"
            elif self.shuffle:
                information["Shuffle"] = "On"
            else:
                information["Shuffle"] = "Off"

            if self.repeat == "context":
                information["Repeat"] = "All"
            elif self.repeat == "track":
                information["Repeat"] = "Track"
            else:
                information["Repeat"] = "Off"

            information["Volume"] = str(self.device_volume_percent) + "%"

            for key, value in information.items():
                result += f"{key}: {value} | "
            result += ")"

            return result
        else:
            return None
    def get_playlists(self, type="user"):
        """ Get the user's playlists """
        playlists = self.sp.current_user_playlists()
        return [playlist["name"] for playlist in playlists["items"]]



if __name__ == "__main__":
    sp = Spotify_Playback_Data()
    for key, value in sp.__dict__.items():
        print(f"{key}: {value}")