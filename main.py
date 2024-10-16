from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widget import Widget
from textual.containers import Container, Center, Middle, Horizontal, Vertical
from textual.widgets import Footer, Placeholder, ProgressBar, Button
from textual.reactive import reactive


class Spotify_Playback_Data():
    def __init__(self, track, track_time, volume, device, current_time, shuffle, repeat):
        self.track = track
        self.track_time = track_time
        self.volume = volume
        self.device = device
        self.current_time = current_time
        self.shuffle = shuffle
        self.repeat = repeat

    def __str__(self):
        if self.device is not None:
            return f"Playing({self.device} | Shuffle: {self.shuffle} | Repeat: {self.repeat} | Volume: {self.volume}"


    def update(self):
        self.track = "TRACK PLACEHOLDER"
        self.track_time = "0:00"
        self.volume = "VOLUME PLACEHOLDER"
        self.device = "DEVICE PLACEHOLDER"


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

    def render_line(self, y:int):
        segments = []

        if current_track is not None:


class Main_Screen(Screen):
    """The main page that contains:
    Main side bar
    Changelog
    Footer
    Playing bar"""

    CSS_PATH = "main_page.tcss"

    def compose(self) -> ComposeResult:
        yield Placeholder("top_bar", id="top_bar")
        yield Placeholder("PLAYLISTS", id="sidebar")
        yield Placeholder("MAIN PAGE", id="main_page")
        yield Playing_Information(),
        yield Container(Current_Time_In_Track(),
                        Center(ProgressBar(total=100, id="bar", show_percentage=False, show_eta=False)), Track_Duration(),id="bar_container")


class MainApp(App):
    def on_mount(self) -> None:
        self.install_screen(Main_Screen(), "main")
        self.push_screen("main")


if __name__ == "__main__":
    app = MainApp()
    app.run()
