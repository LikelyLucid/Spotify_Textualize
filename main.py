from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widget import Widget
from textual.containers import Container, Center, Middle, Horizontal, Vertical
from textual.widgets import Footer, Placeholder, ProgressBar, Button
from textual.reactive import reactive
from spotify_functions import authenticate_user

class Spotify_Playback_Data:
    def __init__(
        self
    ):
        sp = authenticate_user()
        self.sp = sp
        self.update()

    def __str__(self):
        if self.device is not None:
            return f"Playing({self.device} | Shuffle: {self.shuffle} | Repeat: {self.repeat} | Volume: {self.volume}"

    def update(self):
        playback_data = self.sp.current_playback()
        playback_data = self.sp.current_playback()

        # Device Information
        self.device_id = playback_data["device"]["id"]
        self.device_name = playback_data["device"]["name"]
        self.device_is_active = playback_data["device"]["is_active"]
        self.device_is_private_session = playback_data["device"]["is_private_session"]
        self.device_is_restricted = playback_data["device"]["is_restricted"]
        self.device_type = playback_data["device"]["type"]
        self.device_supports_volume = playback_data["device"]["supports_volume"]

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

        # Actions
        self.actions_disallows_resuming = playback_data["actions"]["disallows"]["resuming"]


class Current_Time_In_Track(Widget):
    current_time = reactive("track_time")

    def render(self) -> str:
        return "0:00"


class Track_Duration(Widget):
    track_duration = Spotify_Playback_Data().track_time

    def render(self) -> str:
        return "3:00"


class Current_Track(Widget):
    current_track = reactive("track")

    def render(self) -> str:
        return "TRACK PLACEHOLDER"


class Current_Volume(Widget):
    current_volume = reactive("volume")

    def render(self) -> str:
        return "VOLUME PLACEHOLDER"


class Current_Device(Widget):
    current_device = reactive("device")

    def render(self) -> str:
        return "DEVICE PLACEHOLDER"


class Playing_Information(Widget):
    def render(self):
        # Return a string with playback info for the bottom bar
        return (
            "(Device: DEVICE PLACEHOLDER | Shuffle: OFF | Repeat: OFF | Volume: 100%)"
        )


class Main_Screen(Screen):
    """The main page that contains:
    Main side bar
    Changelog
    Footer
    Playing bar"""

    CSS_PATH = "main_page.tcss"

    def compose(self) -> ComposeResult:
        yield Placeholder("top_bar", id="top_bar")
        yield Placeholder("Spotify Stuff | Playlists", id="sidebar")
        yield Placeholder("Main Page", id="main_page")
        # yield Playing_Information(),
        yield Container(
            Current_Time_In_Track(),
            Center(
                ProgressBar(total=100, id="bar", show_percentage=False, show_eta=False)
            ),
            Track_Duration(),
            id="bar_container",
        )


class MainApp(App):
    def on_mount(self) -> None:
        self.install_screen(Main_Screen(), "main")
        self.push_screen("main")


if __name__ == "__main__":
    app = MainApp()
    app.run()
