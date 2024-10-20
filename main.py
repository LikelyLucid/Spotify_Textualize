from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widget import Widget
from textual.containers import Container, Center, Middle, Horizontal, Vertical
from textual.widgets import Footer, Placeholder, ProgressBar, Button
from textual.reactive import reactive
from spotify_main_class import Spotify_Playback_Data

playback = Spotify_Playback_Data() # This is the object that will be used to get the playback data

def ms_to_time(ms: int) -> str:
    """
    Convert milliseconds to a time string

    Args:
    - ms: The milliseconds to convert

    Returns:
    - A string in the format "MM:SS"
    """
    seconds = ms // 1000
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes}:{seconds:02d}"

class Current_Time_In_Track(Widget):
    current_time = reactive(playback.progress_ms)


    def render(self) -> str:
        return ms_to_time(playback.progress_ms)

    # def watch_current_time(self, current_time: int):
    #     self.query_one(ProgressBar).update(progress=current_time)

class Track_Duration(Widget):
    track_duration = reactive(playback.track_duration)

    def render(self) -> str:
        return ms_to_time(playback.track_duration)


class Current_Track(Widget):
    current_track = reactive(playback.track)

    def render(self) -> str:
        return self.current_track


class Current_Volume(Widget):
    current_volume = reactive(playback.device_volume_percent)

    def render(self) -> str:
        return f"{self.current_volume}%"


class Current_Device(Widget):
    current_device = reactive(playback.device_name)

    def render(self) -> str:
        return self.current_device


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
    def on_mount(self) -> None:
        def update_progress(current_time: int):
            self.query_one(ProgressBar).update(progress=current_time)
            self.query_one(ProgressBar).update(total=playback.track_duration)

        # Song change
        def update_song(song: str):
            self.query_one(Current_Track).update(current_track=song)
            self.query(Track_Duration).update()

        self.watch(self.query_one(Current_Time_In_Track), "current_time", update_progress)


class MainApp(App):
    def on_mount(self) -> None:
        self.install_screen(Main_Screen(), "main")
        self.push_screen("main")


if __name__ == "__main__":
    app = MainApp()
    app.run()
