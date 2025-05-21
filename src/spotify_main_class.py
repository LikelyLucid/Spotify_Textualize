from spotify_functions import authenticate_user
from config_helper import get_config_directory, get_cache_directory
import os
import json
import time
import asyncio
import spotipy.exceptions

class Spotify_Playback_Data:
    def __init__(self):
        """
        Initialize the Spotify Playback Data object

        Returns:
        - None
        """
        self.sp = None
        self.authentication_successful = False # Initialize
        self.reset_playback_data() # Reset data initially

        attempts = 0
        temp_sp = authenticate_user()
        while temp_sp is None and attempts < 3:
            print(f"Authentication attempt {attempts + 1} failed. Retrying...") # Keep console log for now
            # Potentially add a small delay here if desired, e.g., time.sleep(1)
            temp_sp = authenticate_user()
            attempts += 1

        if temp_sp is not None:
            self.sp = temp_sp
            self.authentication_successful = True
            print("Authentication successful. Updating playback data...") # Keep console log
            self.update() # Call update only if authenticated
        else:
            self.authentication_successful = False
            print("Failed to authenticate after multiple attempts. Playback features will be unavailable.")
            # self.reset_playback_data() # Already called at the beginning

    def update(self):
        """
        Update the playback data

        Returns:
        - None
        """
        try:
            playback_data = self.sp.current_playback()
            if playback_data is None:
                # This case might be when Spotify is idle or no active device, not strictly an error.
                # print("No playback data available (e.g. Spotify idle or no active device).") # Optional: more specific message
                self.reset_playback_data()
                return
        except spotipy.exceptions.SpotifyException as e:
            print(f"Error fetching current playback data: {e}")
            self.reset_playback_data()
            return # Important to return after reset if there was an exception
        except Exception as e: # Catch any other unexpected error during fetch
            print(f"Unexpected error fetching current playback data: {e}")
            self.reset_playback_data()
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
        except Exception as e:
            print(e)
            pass

        try:
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
        except Exception as e:
            print(e)
            pass

    def reset_playback_data(self):
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

    def playing_settings(self):
        """Creates the text above the progress bar"""
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

    def get_user_library(self):
        """Get all user-related playlists, albums, and other items"""
        library = []

        # Add Liked Songs
        library.append({"name": "Liked Songs", "id": "liked_songs", "type": "playlist"})

        # Add Saved Episodes
        library.append(
            {"name": "Your Episodes", "id": "saved_episodes", "type": "playlist"}
        )

        # Add user's playlists
        try:
            user_playlists = self.sp.current_user_playlists()
            library.extend(
                [
                    {"name": playlist["name"], "id": playlist["id"], "type": "playlist"}
                    for playlist in user_playlists["items"]
                ]
            )

            # Add Saved Albums
            saved_albums = self.sp.current_user_saved_albums()
            library.extend(
                [
                    {
                        "name": album["album"]["name"],
                        "id": album["album"]["id"],
                        "type": "album",
                    }
                    for album in saved_albums["items"]
                ]
            )
        except spotipy.exceptions.SpotifyException as e:
            print(f"Error fetching user library data: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error fetching user library data: {e}")
            return []
        return library

    def get_featured_playlists(self, limit=5):
        """Get featured playlists"""
        try:
            featured = self.sp.featured_playlists(limit=limit)
            return [
                {"name": playlist["name"], "id": playlist["id"], "type": "playlist"}
                for playlist in featured["playlists"]["items"]
            ]
        except spotipy.exceptions.SpotifyException as e:
            print(f"Error fetching featured playlists: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error fetching featured playlists: {e}")
            return []

    async def play_playlist(self, playlist_id):
        """Play a playlist given its ID"""
        await self.start_playback(context_uri=f"spotify:playlist:{playlist_id}")

    def get_playlist_tracks(self, playlist_id: str) -> list[dict]:
        """Get tracks from a playlist with efficient caching"""
        playlist_items = []
        offset = 0
        limit = 100 if playlist_id != "liked_songs" else 20
        fetch_function = (
            self.sp.playlist_tracks
            if playlist_id != "liked_songs"
            else self.sp.current_user_saved_tracks
        )

        # Use memory cache first
        if hasattr(self, '_playlist_cache') and playlist_id in self._playlist_cache:
            return self._playlist_cache[playlist_id]

        # Initialize memory cache if needed
        if not hasattr(self, '_playlist_cache'):
            self._playlist_cache = {}

        # Check disk cache
        directory = get_cache_directory()
        playlist_cache = os.path.join(directory, f"{playlist_id}.cache")
        cache_valid = False

        try:
            if os.path.exists(playlist_cache):
                cache_time = os.path.getmtime(playlist_cache)
                if time.time() - cache_time < 300:  # 5 minute cache validity
                    with open(playlist_cache, "r") as cache_file:
                        cached_items = json.load(cache_file)
                        self._playlist_cache[playlist_id] = cached_items
                        return cached_items
        except Exception as e:
            print(f"Error reading cache: {e}")

        # Check and update liked songs cache
        liked_songs = self._get_liked_songs()

        while True:
            try:
                if playlist_id == "liked_songs":
                    playlist = fetch_function(limit=limit, offset=offset)
                else:
                    playlist = fetch_function(playlist_id, limit=limit, offset=offset)
                items = playlist["items"]
            except spotipy.exceptions.SpotifyException as e:
                print(f"Error fetching playlist tracks for {playlist_id}: {e}")
                break # or return playlist_items
            except Exception as e:
                print(f"Unexpected error fetching playlist tracks for {playlist_id}: {e}")
                break # or return playlist_items


            for item in items:
                track = item["track"]
                track_id = track["id"]
                # playlist_items.append(
                #     {
                #         "name": track["name"],
                #         "id": track_id,
                #         "type": "track",
                #         "is_liked": track_id in liked_songs
                #     }
                # )
                playlist_items.append(
                    {
                        "name": track["name"],
                        "artists": [artist["name"] for artist in track["artists"]],
                        "album": track["album"]["name"],
                        "duration_ms": track["duration_ms"],
                        "is_liked": track_id in liked_songs,
                        "id": track_id,
                    }
                )

            if len(items) < limit:
                break
            offset += limit

        # Cache the playlist
        with open(playlist_cache, "w") as cache_file:
            json.dump(playlist_items, cache_file)

        return playlist_items

    def _get_liked_songs(self):
        """Get and cache liked songs"""
        config_dir = get_config_directory()
        liked_songs_file = os.path.join(config_dir, "liked_songs.json")

        # Check if liked songs cache exists and is up-to-date
        try:
            if os.path.exists(liked_songs_file):
                with open(liked_songs_file, "r") as f:
                    cached_liked_songs = json.load(f)
                total_liked = self.sp.current_user_saved_tracks(limit=1)["total"]
                if len(cached_liked_songs) == total_liked:
                    return set(cached_liked_songs)

            # Fetch all liked songs
            liked_songs = []
            offset = 0
            limit = 20

            while True:
                results = self.sp.current_user_saved_tracks(limit=limit, offset=offset)
                items = results["items"]
                liked_songs.extend([track["track"]["id"] for track in items])
                if len(items) < limit:
                    break
                offset += limit

            # Cache the liked songs
            with open(liked_songs_file, "w") as f:
                json.dump(liked_songs, f)
            return set(liked_songs)
        except spotipy.exceptions.SpotifyException as e:
            print(f"Error fetching liked songs: {e}")
            return set()
        except Exception as e:
            print(f"Unexpected error fetching liked songs: {e}")
            return set()


    def get_saved_episodes(self):
        """Get user's saved episodes"""
        try:
            episodes = []
            offset = 0
            limit = 20

            while True:
                results = self.sp.current_user_saved_episodes(limit=limit, offset=offset)
                items = results["items"]
                for item in items:
                    episode = item["episode"]
                    episodes.append({
                        "name": episode["name"],
                        "id": episode["id"],
                        "duration_ms": episode["duration_ms"],
                        "show": episode["show"]["name"],
                        "description": episode["description"],
                        "type": "episode"
                    })
                if len(items) < limit:
                    break
                offset += limit
            return episodes
        except spotipy.exceptions.SpotifyException as e:
            print(f"Error fetching saved episodes: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error fetching saved episodes: {e}")
            return []

    async def play_track(self, uri, playlist_id=None):
        """Play a song or episode given its URI, optionally within a playlist context"""
        if playlist_id == "liked_songs":
            # For liked songs, we need to get the user's collection URI
            user_id = self.sp.current_user()["id"]
            await self.start_playback(
                context_uri=f"spotify:user:{user_id}:collection",
                offset={"uri": f"spotify:track:{uri}"}
            )
        elif playlist_id == "saved_episodes":
            # For episodes, we play directly with the episode URI
            await self.start_playback(uris=[f"spotify:episode:{uri}"])
        elif playlist_id:
            # Play the track within the playlist context
            await self.start_playback(
                context_uri=f"spotify:playlist:{playlist_id}",
                offset={"uri": f"spotify:track:{uri}"}
            )
        else:
            # Play just the single track
            await self.start_playback(uris=[f"spotify:track:{uri}"])

    async def start_playback(self, **kwargs):
        """Asynchronously start playback."""
        # Wrap the synchronous start_playback in a coroutine
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.sp.start_playback, **kwargs)

    async def pause_playback(self, **kwargs):
        """Asynchronously pause playback."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.sp.pause_playback, **kwargs)

    async def next_track(self, **kwargs):
        """Asynchronously skip to the next track."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.sp.next_track, **kwargs)

    async def previous_track(self, **kwargs):
        """Asynchronously go back to the previous track."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.sp.previous_track, **kwargs)

    async def set_volume(self, volume_percent: int):
        """Asynchronously set the device volume, ensuring it's between 0 and 100."""
        volume_percent = max(0, min(100, volume_percent))  # Clamp volume
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.sp.volume, volume_percent)

# if __name__ == "__main__":
#     sp = Spotify_Playback_Data()
#     for key, value in sp.__dict__.items():
#         print(f"{key}: {value}")
#     print()
#     # test playlist items with liked songs
#     library = sp.get_user_library()
#     print(library)
#     print(sp.get_playlist_tracks("liked_songs"))
#     print()
#     print(sp.get_playlist_tracks("3yE07D1ZglwRnCDMM3mq1V"))
#     sp.play_track("spotify:track:5GsJIVCBFjhCcUwJaTW2sB")
