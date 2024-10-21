from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widget import Widget
from textual.containers import Container, Center, Middle, Horizontal, Vertical
from textual.widgets import Footer, Placeholder, ProgressBar, Button, Static
from textual.reactive import reactive
from spotify_main_class import Spotify_Playback_Data
from textual import work
import time

playback = (
    Spotify_Playback_Data()
)  # This is the object that will be used to get the playback data


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


def get_current_time_with_offset() -> int:
    """
    Get the current playback time considering the offset.

    Returns:
    - The current time in milliseconds.
    """
    offset = int(time.time() * 1000) - playback.timestamp
    print(f"Offset: {offset}")
    return playback.progress_ms + offset


class Current_Time_In_Track(Widget):
    current_time = reactive(get_current_time_with_offset())

    def render(self) -> str:
        if playback.progress_ms is not None:
            return f"{ms_to_time(self.current_time)}"
        else:
            return ""


class Track_Duration(Widget):
    track_duration = reactive(playback.track_duration)

    def render(self) -> str:
        if playback.track_duration is not None:
            return ms_to_time(playback.track_duration)
        else:
            return ""


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


class Bottom_Bar(Widget):
    def get_artist_info(self):
        print("HIT")
        if playback.track is not None:
            artist_information = f"[b][style size="30px"]{playback.track}[/b] | "
            for artist in playback.artists:
                artist_information += artist + ", "
            artist_information = artist_information[:-2]
            print(str(artist_information))
            return str(artist_information)
        else:
            return ""

    def compose(self):
        info = self.get_artist_info()
        print("WHAT THE FUCK")
        yield Vertical(
            Static(f"{info}", id="artist_info"),
            Container(
                Current_Time_In_Track(),
                Center(
                    ProgressBar(
                        total=100, id="bar", show_percentage=False, show_eta=False
                    )
                ),
                Track_Duration(),
                id="bar_with_times",
            ),
            id = "bottom_bar_collection"
        )

    def update_progress(self, progress=None):
        current_time_widget = self.query_one(Current_Time_In_Track)
        if playback.is_playing and progress is None:
            current_time_widget.current_time += 1000
        else:
            current_time_widget.current_time = progress
        self.query_one(ProgressBar).update(
            progress=current_time_widget.current_time,
            total=playback.track_duration,
        )

    def song_change(self):
        self.query_one(Track_Duration).track_duration = playback.track_duration
        self.query_one(Current_Time_In_Track).current_time = (
            get_current_time_with_offset()
        )
        self.query_one("#artist_info").update(f"{self.get_artist_info()}")

    def update_playback_settings(self):
        self.border_title = playback.playing_settings()
        self.update_progress(playback.progress_ms)

    def on_mount(self):
        self.styles.border = ("hkey", "blue")
        self.update_playback_settings()
        self.set_interval(1, self.update_progress)


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
        yield Bottom_Bar(id="bottom_bar")

    async def update_stats(self):
        old_song = playback.track
        try:
            playback.update()
        except Exception as e:
            print(f"Error updating playback data: {e}")
            return
        if playback.track is None:
            return
        elif old_song != playback.track:
            if playback.is_playing:
                self.query_one(Bottom_Bar).song_change()

        self.query_one(Bottom_Bar).update_playback_settings()

    def on_mount(self) -> None:
        self.set_interval(2, self.update_stats)


class MainApp(App):
    def on_mount(self) -> None:
        self.install_screen(Main_Screen(), "main")
        self.push_screen("main")


if __name__ == "__main__":
    app = MainApp(ansi_color=True)
    app.run()
