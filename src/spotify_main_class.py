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
            self.device_id = ""
            self.device_name = ""
            self.device_is_active = False
            self.device_is_private_session = False
            self.device_is_restricted = False
            self.device_type = ""
            self.device_supports_volume = False
            self.device_volume_percent = 0
            self.shuffle = False
            self.smart_shuffle = False
            self.repeat = ""
            self.timestamp = 0
            self.progress_ms = 0
            self.currently_playing_type = ""
            self.is_playing = False
            self.external_url = ""
            self.context_href = ""
            self.context_type = ""
            self.context_uri = ""
            self.track = ""
            self.track_id = ""
            self.track_uri = ""
            self.track_explicit = False
            self.track_popularity = 0
            self.track_preview_url = ""
            self.track_number = 0
            self.track_duration = 0
            self.album_name = ""
            self.album_id = ""
            self.album_release_date = ""
            self.album_total_tracks = 0
            self.artists = []
            self.available_markets = []
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

        information = {}
        result = "("
        if self.device_name is not None:
            information["Device"] = self.device_name
        if self.shuffle is not None:
            if self.smart_shuffle:
                information["Shuffle"] = "Smart"
            elif self.shuffle:
                information["Shuffle"] = "On"
            else:
                information["Shuffle"] = "Off"
        if self.repeat is not None:
            information["Repeat"] = self.repeat
        if self.is_playing is not None:
            information["Volume"] = self.device_volume_percent + "%"

        for key, value in information.items():
            result += f"{key}: {value} | "
        result += ")"

        return result