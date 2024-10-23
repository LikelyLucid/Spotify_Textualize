from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widget import Widget
from textual.containers import Container, Center, Vertical, ScrollableContainer
from textual.widgets import Placeholder, ProgressBar, Static, ListView, ListItem, Label
from textual.reactive import reactive
from spotify_main_class import Spotify_Playback_Data
import time

playback = Spotify_Playback_Data()

def ms_to_time(ms: int) -> str:
    if ms is None:
        return "0:00"
    seconds, ms = divmod(ms, 1000)
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes}:{seconds:02d}"

def get_current_time_with_offset() -> int:
    if playback.progress_ms is None:
        return 0
    offset = int(time.time() * 1000) - playback.timestamp
    return playback.progress_ms + offset

class Current_Time_In_Track(Widget):
    current_time = reactive(get_current_time_with_offset())

    def render(self) -> str:
        return ms_to_time(self.current_time) if playback.progress_ms is not None else ""

class Track_Duration(Widget):
    track_duration = reactive(playback.track_duration)

    def render(self) -> str:
        return ms_to_time(self.track_duration) if self.track_duration is not None else ""

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
        if playback.track is not None:
            artist_information = f"[b][italic]{playback.track}[/italic][/b] | "
            artist_information += ", ".join(playback.artists)
            return artist_information
        return ""

    def compose(self):
        yield Vertical(
            Static(self.get_artist_info(), id="artist_info"),
            Container(
                Current_Time_In_Track(),
                Center(ProgressBar(total=100, id="bar", show_percentage=False, show_eta=False)),
                Track_Duration(),
                id="bar_with_times",
            ),
            id="bottom_bar_collection",
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
        self.query_one(Current_Time_In_Track).current_time = get_current_time_with_offset()
        self.query_one("#artist_info").update(self.get_artist_info())

    def update_playback_settings(self):
        self.border_title = playback.playing_settings()
        self.update_progress(playback.progress_ms)

    def on_mount(self):
        self.styles.border = ("hkey", "blue")
        self.update_playback_settings()
        self.set_interval(1, self.update_progress)

class Side_Bar(Widget):
    def compose(self):
        with ScrollableContainer(id="sidebar_container"):
            yield Library_List(library_data=playback.get_featured_playlists(limit=5), id="featured_playlists_list")
            yield Library_List(library_data=playback.get_user_library(), id="user_library_list")

class Library_List(Widget):
    def __init__(self, library_data, id=None):
        self.library_data = library_data
        super().__init__(id=id)

    def compose(self):
        items = [ListItem(Label(f"{item['name']} ({item['type'].capitalize()})")) for item in self.library_data]
        yield ListView(*items)

class Main_Page(Widget):
    def compose(self):
        with Container(id="main_page_container"):
            yield Static("Main Page", id="main_page_header")

class Playlist_Track_View(Widget):
    def __init__(self, playlist_id, id=None):
        self.playlist_id = playlist_id
        super().__init__(id=id)

    def get_playlist_tracks(self):
        return playback.get_playlist_tracks(self.playlist_id)

    def compose(self):
        # TODO: Implement the composition of playlist tracks
        pass

class Main_Screen(Screen):
    CSS_PATH = "main_page.tcss"

    def compose(self) -> ComposeResult:
        yield Placeholder("top_bar", id="top_bar")
        yield Side_Bar(id="sidebar")
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
        elif old_song != playback.track and playback.is_playing:
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
