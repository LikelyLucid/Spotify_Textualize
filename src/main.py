from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widget import Widget
from textual.message import Message
from textual.containers import Container, Center, Vertical, ScrollableContainer
from textual.lazy import Lazy
from textual.widgets import (
    Placeholder,
    ProgressBar,
    Static,
    ListView,
    ListItem,
    Label,
    DataTable,
    LoadingIndicator,
    Button,
)
from textual.reactive import reactive
from spotify_main_class import Spotify_Playback_Data
import time
from textual import work
import asyncio
from config_helper import setup_keybindings, setup_settings
import json

playback = Spotify_Playback_Data()
settings = setup_settings()
keybindings = setup_keybindings()
volume_step = settings.get("volume_step", 5)


def cut_string_if_long(string: str, max_length: int) -> str:
    return string[:max_length].strip() + "..." if len(string) > max_length else string


def ms_to_time(ms: int) -> str:
    seconds, ms = divmod(ms, 1000)
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes}:{seconds:02d}"


def get_current_time_with_offset() -> int:
    if playback.progress_ms is None:
        return 0
    if not playback.is_playing:
        return playback.progress_ms
    offset = int(time.time() * 1000) - playback.timestamp
    return playback.progress_ms + offset


class Current_Time_In_Track(Widget):
    current_time = reactive(get_current_time_with_offset())

    def render(self) -> str:
        return ms_to_time(self.current_time) if playback.progress_ms is not None else ""


class Track_Duration(Widget):
    track_duration = reactive(playback.track_duration)

    def render(self) -> str:
        return (
            ms_to_time(self.track_duration) if self.track_duration is not None else ""
        )


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


class Top_Bar(Widget):
    def compose(self) -> ComposeResult:
        with Container(id="top_bar_container"):
            yield Button("\u23ee", id="previous_button")
            yield Button("\u23ef", id="play_pause_button")
            yield Button("\u23ed", id="next_button")
            yield Static(self.get_now_playing(), id="now_playing")

    def get_now_playing(self) -> str:
        if playback.track:
            return f"{playback.track} - {', '.join(playback.artists)}"
        return ""

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "previous_button":
            await self.app.action_previous_track()
        elif button_id == "next_button":
            await self.app.action_next_track()
        elif button_id == "play_pause_button":
            await self.app.action_play_pause()
        self.update_controls()

    def update_controls(self) -> None:
        play_pause = self.query_one("#play_pause_button", Button)
        play_pause.label = "\u23f8" if playback.is_playing else "\u25ba"
        self.query_one("#now_playing", Static).update(self.get_now_playing())

    def on_mount(self) -> None:
        self.update_controls()


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
                Center(ProgressBar(id="bar", show_percentage=False, show_eta=False)),
                Track_Duration(),
                id="bar_with_times",
            ),
            id="bottom_bar_collection",
        )

    @work
    async def update_progress(self, progress=None):
        current_time_widget = self.query_one(Current_Time_In_Track)
        progress_bar = self.query_one(ProgressBar)

        if playback.is_playing and progress is None:
            current_time_widget.current_time += 1000
        else:
            current_time_widget.current_time = progress if progress is not None else 0

        total = playback.track_duration if playback.track_duration is not None else 1

        if current_time_widget.current_time != progress_bar.progress:
            progress_bar.update(
                progress=current_time_widget.current_time,
                total=total,
            )

    @work
    async def song_change(self):
        track_duration_widget = self.query_one(Track_Duration)
        current_time_widget = self.query_one(Current_Time_In_Track)
        artist_info_widget = self.query_one("#artist_info")

        track_duration_widget.track_duration = playback.track_duration
        current_time_widget.current_time = get_current_time_with_offset()
        self.update_progress()
        artist_info_widget.update(self.get_artist_info())

    @work
    async def update_playback_settings(self):
        self.border_title = playback.playing_settings()
        if playback.is_playing:
            self.update_progress(playback.progress_ms)

    def on_mount(self):
        self.styles.border = ("hkey", "blue")
        self.update_playback_settings()
        self.set_interval(1, self.update_progress)


class Side_Bar(Widget):
    def compose(self):
        with ScrollableContainer(id="sidebar_container"):
            yield Library_List(
                library_data=playback.get_featured_playlists(limit=5),
                id="featured_playlists_list",
            )
            yield Library_List(
                library_data=playback.get_user_library(),
                id="user_library_list",
            )


class Library_List(Widget):

    def __init__(self, library_data, id=None):
        self.library_data = library_data
        super().__init__(id=id)

    class PlaylistSelected(Message):
        """Sent when a playlist is selected."""

        def __init__(self, playlist_id: str) -> None:
            self.playlist_id = playlist_id
            super().__init__()

    @work
    async def on_list_view_selected(self, selected_item):
        playlist_id = next(
            (
                item["id"]
                for item in self.library_data
                if item["name"] == selected_item.item.name
            ),
            None,
        )

        if playlist_id is None:
            self.notify("Error: Playlist ID not found")
            return

        self.post_message(self.PlaylistSelected(str(playlist_id)))

    def compose(self):
        items = [
            ListItem(
                Label(f"{item['name']} ({item['type'].capitalize()})"),
                name=item["name"],
            )
            for item in self.library_data
        ]
        yield ListView(*items)


class Main_Page(Widget):
    def compose(self):
        with Container(id="main_page_container"):
            yield Playlist_Track_View(playlist_id="liked_songs", id="playlist_tracks")


class Playlist_Track_View(Widget):
    can_focus = True

    track_weight, artist_weight, album_weight = 2, 1, 1
    old_size = (0, 0)
    adjusting_size = False

    def __init__(self, playlist_id, max_title_length=40, id=None):
        self.playlist_id = playlist_id
        self.max_title_length = max_title_length
        self.tracks = []
        super().__init__(id=id)

    @work
    async def change_playlist(self, playlist_id):
        self.playlist_id = playlist_id
        self.set_tracks()

    def on_data_table_row_selected(self, row):
        selected_track = self.tracks[row.cursor_row]["id"]
        playback.play_track(selected_track, self.playlist_id)

    def adjust_columns(self):
        current_size = self.query_one(DataTable).size[0]
        if self.old_size == current_size or self.adjusting_size:
            return
        self.old_size = current_size
        self.post_display_hook()

    def compose(self) -> ComposeResult:
        yield DataTable()

    @work
    async def set_tracks(self):
        table = self.query_one(DataTable)
        table.loading = True
        table.clear(columns=True)

        if self.playlist_id == "saved_episodes":
            columns = table.add_columns("#", "Title", "Show", "Duration", "Description")
            self.tracks = playback.get_saved_episodes()

            for i, episode in enumerate(self.tracks):
                description = episode.get("description", "")
                description = description[:50] + "..." if description else ""

                table.add_row(
                    str(i + 1),
                    episode["name"],
                    episode["show"],
                    ms_to_time(episode.get("duration_ms", 0)),
                    description,
                )
        else:
            columns = table.add_columns(
                "#", "Title", "Artist", "Album", "Duration", "Liked"
            )
            self.tracks = playback.get_playlist_tracks(self.playlist_id)

            add_row = table.add_row
            for i, track in enumerate(self.tracks):
                track_name = str(track["name"])
                artist_string = ", ".join(track.get("artists", []))
                album_name = track.get("album", "")

                add_row(
                    str(i + 1),
                    track_name,
                    artist_string,
                    album_name,
                    ms_to_time(track.get("duration_ms", 0)),
                    "♥" if track.get("is_liked", False) else "",
                )
        table.loading = False

        self.post_display_hook()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.styles.scrollbar_size_horizontal = 0

        self.set_tracks()

    @work
    async def post_display_hook(self) -> None:
        self.adjusting_size = True
        table = self.query_one(DataTable)
        size = table.container_size

        if not all(size):
            self.call_later(self.post_display_hook)
            return

        taken_chars = -1
        for c in table.columns.values():
            c.auto_width = False
            if str(c.label) == "#":
                c.width = len(str(table.row_count))
            elif str(c.label) in ["Duration", "Liked"]:
                c.auto_width = True
            taken_chars += c.width

        for c in table.columns.values():
            if str(c.label) in ["Title", "Artist", "Album"]:
                c.width = int((size[0] - taken_chars) / (len(table.columns) - 3)) + 1
        table.refresh()
        self.adjusting_size = False


class Main_Screen(Screen):
    CSS_PATH = "main_page.tcss"

    def on_library_list_playlist_selected(
        self, message: Library_List.PlaylistSelected
    ) -> None:
        playlist_view = self.query_one("#playlist_tracks", Playlist_Track_View)
        playlist_view.change_playlist(message.playlist_id)

    def compose(self) -> ComposeResult:
        yield Top_Bar(id="top_bar")
        yield Side_Bar(id="sidebar")
        yield Main_Page(id="main_page")
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
        self.query_one(Top_Bar).update_controls()

    async def on_mount(self) -> None:
        self.set_interval(2, self.update_stats)


class MainApp(App):
    BINDINGS = [
        ("space", "play_pause", "Play/Pause"),
        (">", "next_track", "Next Track"),
        ("<", "previous_track", "Previous Track"),
        (keybindings.get("volume_up", "+"), "volume_up", "Volume Up"),
        (keybindings.get("volume_down", "-"), "volume_down", "Volume Down"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.playback = playback
        self.volume_step = volume_step

    async def action_play_pause(self):
        if playback.is_playing:
            playback.is_playing = False
            self.query_one(Bottom_Bar).update_progress(
                progress=playback.progress_ms
            )
            await playback.pause_playback()
        else:
            playback.is_playing = True
            await playback.start_playback()
        self.query_one(Top_Bar).update_controls()

    async def action_next_track(self):
        await playback.next_track()
        playback.update()
        self.query_one(Bottom_Bar).update_playback_settings()
        self.query_one(Bottom_Bar).song_change()
        self.query_one(Top_Bar).update_controls()

    async def action_previous_track(self):
        await playback.previous_track()
        playback.update()
        self.query_one(Bottom_Bar).update_playback_settings()
        self.query_one(Bottom_Bar).song_change()
        self.query_one(Top_Bar).update_controls()

    async def action_volume_up(self):
        current_volume = playback.device_volume_percent or 0
        new_volume = min(current_volume + self.volume_step, 100)
        await playback.set_volume(new_volume)

    async def action_volume_down(self):
        current_volume = playback.device_volume_percent or 0
        new_volume = max(current_volume - self.volume_step, 0)
        await playback.set_volume(new_volume)

    async def on_mount(self) -> None:
        self.install_screen(Main_Screen(), "main")
        await self.push_screen("main")


if __name__ == "__main__":
    app = MainApp(ansi_color=True)
    app.run()
