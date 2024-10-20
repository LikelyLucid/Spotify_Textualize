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

        # Device Information
        if playback_data is None:
            print("No playback data available.")
            self.device_id = None
            return
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
        self.external_url = playback_data["context"]["external_urls"]["spotify"]
        self.context_href = playback_data["context"]["href"]
        self.context_type = playback_data["context"]["type"]
        self.context_uri = playback_data["context"]["uri"]

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

    def _print_playback_data(self):
        """
        Print the playback data

        Returns:
        - None"""
        # Device Information
        print("=== Device Information ===")
        print(f"Device ID: {self.device_id}")
        print(f"Device Name: {self.device_name}")
        print(f"Is Active: {self.device_is_active}")
        print(f"Is Private Session: {self.device_is_private_session}")
        print(f"Is Restricted: {self.device_is_restricted}")
        print(f"Device Type: {self.device_type}")
        print(f"Supports Volume: {self.device_supports_volume}")
        print(f"Volume Percent: {self.device_volume_percent}")
        print()

        # Playback Information
        print("=== Playback Information ===")
        print(f"Shuffle: {self.shuffle}")
        print(f"Smart Shuffle: {self.smart_shuffle}")
        print(f"Repeat State: {self.repeat}")
        print(f"Timestamp: {self.timestamp}")
        print(f"Progress (ms): {self.progress_ms}")
        print(f"Currently Playing Type: {self.currently_playing_type}")
        print(f"Is Playing: {self.is_playing}")
        print()

        # Context Information
        print("=== Context Information ===")
        print(f"External URL: {self.external_url}")
        print(f"Context Href: {self.context_href}")
        print(f"Context Type: {self.context_type}")
        print(f"Context URI: {self.context_uri}")
        print()

        # Track Information
        print("=== Track Information ===")
        print(f"Track Name: {self.track}")
        print(f"Track ID: {self.track_id}")
        print(f"Track URI: {self.track_uri}")
        print(f"Explicit: {self.track_explicit}")
        print(f"Popularity: {self.track_popularity}")
        print(f"Preview URL: {self.track_preview_url}")
        print(f"Track Number: {self.track_number}")
        print(f"Track Duration (ms): {self.track_duration}")
        print()

        # Album Information
        print("=== Album Information ===")
        print(f"Album Name: {self.album_name}")
        print(f"Album ID: {self.album_id}")
        print(f"Album Release Date: {self.album_release_date}")
        print(f"Total Tracks: {self.album_total_tracks}")
        print()

        # Artist Information
        print("=== Artist Information ===")
        print(f"Artists: {', '.join(self.artists)}")
        print(f"Available Markets: {', '.join(self.available_markets)}")
        print()