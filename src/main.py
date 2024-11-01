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
)
from textual.reactive import reactive
from spotify_main_class import Spotify_Playback_Data
import time
from textual import work
import asyncio  # Ensure asyncio is imported

# Initialize Spotify playback data
playback = Spotify_Playback_Data()

# Function to cut a string if it exceeds the specified max length
def cut_string_if_long(string: str, max_length: int) -> str:
    return string[:max_length].strip() + "..." if len(string) > max_length else string


# Function to convert milliseconds to time in minutes:seconds format
def ms_to_time(ms: int) -> str:
    seconds, ms = divmod(ms, 1000)
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes}:{seconds:02d}"


# Function to get the current time in the track with an offset
def get_current_time_with_offset() -> int:
    if playback.progress_ms is None:
        return 0
    # If playback is not playing, return progress_ms without offset
    if not playback.is_playing:
        return playback.progress_ms
    # Calculate the offset based on the current system time and the playback timestamp
    offset = int(time.time() * 1000) - playback.timestamp
    return playback.progress_ms + offset


# Widget to display the current time in the track
class Current_Time_In_Track(Widget):
    current_time = reactive(get_current_time_with_offset())

    def render(self) -> str:
        return ms_to_time(self.current_time) if playback.progress_ms is not None else ""


# Widget to display the track duration
class Track_Duration(Widget):
    track_duration = reactive(playback.track_duration)

    def render(self) -> str:
        return (
            ms_to_time(self.track_duration) if self.track_duration is not None else ""
        )


# Widget to display the current track name
class Current_Track(Widget):
    current_track = reactive(playback.track)

    def render(self) -> str:
        return self.current_track


# Widget to display the current volume level
class Current_Volume(Widget):
    current_volume = reactive(playback.device_volume_percent)

    def render(self) -> str:
        return f"{self.current_volume}%"


# Widget to display the current device name
class Current_Device(Widget):
    current_device = reactive(playback.device_name)

    def render(self) -> str:
        return self.current_device


# Widget to display the bottom bar with track and artist information
class Bottom_Bar(Widget):
    # Get the artist and track information
    def get_artist_info(self):
        if playback.track is not None:
            artist_information = f"[b][italic]{playback.track}[/italic][/b] | "
            artist_information += ", ".join(playback.artists)
            return artist_information
        return ""

    # Compose the bottom bar with track information, progress bar, and times
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

    # Update the progress bar based on the current playback progress
    @work
    async def update_progress(self, progress=None):
        current_time_widget = self.query_one(Current_Time_In_Track)
        progress_bar = self.query_one(ProgressBar)

        if playback.is_playing and progress is None:
            current_time_widget.current_time += 1000
        else:
            current_time_widget.current_time = progress if progress is not None else 0

        # Ensure track_duration is not None
        total = playback.track_duration if playback.track_duration is not None else 1

        # Update progress bar only if necessary to reduce rendering overhead
        if current_time_widget.current_time != progress_bar.progress:
            progress_bar.update(
                progress=current_time_widget.current_time,
                total=total,
            )

    # Handle changes in the current song
    @work
    async def song_change(self):
        track_duration_widget = self.query_one(Track_Duration)
        current_time_widget = self.query_one(Current_Time_In_Track)
        artist_info_widget = self.query_one("#artist_info")

        track_duration_widget.track_duration = playback.track_duration
        current_time_widget.current_time = get_current_time_with_offset()
        self.update_progress()
        artist_info_widget.update(self.get_artist_info())

    # Update playback settings like the border title
    @work
    async def update_playback_settings(self):
        self.border_title = playback.playing_settings()
        if playback.is_playing:
            self.update_progress(playback.progress_ms)

    # Mount the widget and set up the update interval
    def on_mount(self):
        self.styles.border = ("hkey", "blue")
        self.update_playback_settings()
        self.set_interval(1, self.update_progress)


# Widget to display the side bar with featured playlists and user library
class Side_Bar(Widget):
    def compose(self):
        with ScrollableContainer(id="sidebar_container"):
            yield Library_List(
                library_data=playback.get_featured_playlists(limit=5),
                id="featured_playlists_list",

            )
            yield Library_List(
                library_data=playback.get_user_library(), id="user_library_list",

            )


# Widget to display a list of playlists in the library
class Library_List(Widget):

    def __init__(self, library_data, id=None):
        self.library_data = library_data
        super().__init__(id=id)

    # Message to notify when a playlist is selected
    class PlaylistSelected(Message):
        """Sent when a playlist is selected."""

        def __init__(self, playlist_id: str) -> None:
            self.playlist_id = playlist_id
            super().__init__()

    # Handle the selection of a playlist in the list view
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

        # Post a message to the app about the playlist selection
        self.post_message(self.PlaylistSelected(str(playlist_id)))

    # Compose the list of playlists
    def compose(self):
        items = [
            ListItem(
                Label(f"{item['name']} ({item['type'].capitalize()})"),
                name=item["name"],
            )
            for item in self.library_data
        ]
        yield ListView(*items)


# Widget to display the main page with playlist track view
class Main_Page(Widget):
    def compose(self):
        with Container(id="main_page_container"):
            yield Playlist_Track_View(playlist_id="liked_songs", id="playlist_tracks")


# Widget to display the tracks of a selected playlist
class Playlist_Track_View(Widget):
    can_focus = True

    # Weighting for track, artist, and album columns
    track_weight, artist_weight, album_weight = 2, 1, 1
    old_size = (0, 0)
    adjusting_size = False

    def __init__(self, playlist_id, max_title_length=40, id=None):
        self.playlist_id = playlist_id
        self.max_title_length = max_title_length
        self.tracks = []
        super().__init__(id=id)

    # Change the playlist being displayed
    @work
    async def change_playlist(self, playlist_id):
        self.playlist_id = playlist_id
        self.set_tracks()

    # Handle row selection in the data table
    def on_data_table_row_selected(self, row):
        selected_track = self.tracks[row.cursor_row]["id"]
        playback.play_track(selected_track, self.playlist_id)

    # Adjust the column sizes based on the current table size
    def adjust_columns(self):
        current_size = self.query_one(DataTable).size[0]
        if self.old_size == current_size or self.adjusting_size:
            return
        self.old_size = current_size
        self.post_display_hook()

    # Compose the data table for displaying tracks
    def compose(self) -> ComposeResult:
        yield DataTable()

    # Set the tracks for the current playlist
    @work
    async def set_tracks(self):
        table = self.query_one(DataTable)
        table.loading = True
        table.clear(columns=True)

        # Set columns based on playlist type (saved episodes or general playlist)
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

            # Add rows to the data table for each track
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

        # After setting the tracks, apply the auto-resizing hook
        self.post_display_hook()

    # Mount the widget and set up the data table
    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.styles.scrollbar_size_horizontal = 0

        # Call the async method to set tracks
        self.set_tracks()

    # Adjust column widths after display
    @work
    async def post_display_hook(self) -> None:
        adjusting_size = True
        # Adjust the column widths based on the table size
        table = self.query_one(DataTable)
        size = table.container_size

        # If the size is not valid, try again later
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

        # Set width for Title, Artist, Album columns
        for c in table.columns.values():
            if str(c.label) in ["Title", "Artist", "Album"]:
                c.width = int((size[0] - taken_chars) / (len(table.columns) - 3)) + 1
        table.refresh()
        adjusting_size = False


# Main screen to display different widgets
class Main_Screen(Screen):
    CSS_PATH = "main_page.tcss"

    # Handle playlist selection messages
    def on_library_list_playlist_selected(
        self, message: Library_List.PlaylistSelected
    ) -> None:
        playlist_view = self.query_one("#playlist_tracks", Playlist_Track_View)
        playlist_view.change_playlist(message.playlist_id)

    # Compose the main screen with different widgets
    def compose(self) -> ComposeResult:
        yield Placeholder("top_bar", id="top_bar")
        yield Side_Bar(id="sidebar")
        yield Main_Page(id="main_page")
        yield Bottom_Bar(id="bottom_bar")

    # Update playback statistics periodically
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

    # Set up periodic updates for playback statistics
    async def on_mount(self) -> None:
        self.set_interval(2, self.update_stats)


# Main app class
class MainApp(App):
    """Main application class."""

    BINDINGS = [
        ("space", "play_pause", "Play/Pause"),
        (">", "next_track", "Next Track"),
        ("<", "previous_track", "Previous Track"),
        ("+", "volume_up", "Volume Up"),
        ("-", "volume_down", "Volume Down"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.playback = playback

    def action_play_pause(self) -> None:
        """Toggle play/pause state."""
        async def toggle():
            if self.playback.is_playing:
                await self.playback.pause_playback()
            else:
                await self.playback.start_playback()

            self.playback.update()
            bottom_bar = self.query_one(Bottom_Bar)
            await bottom_bar.update_playback_settings()
            await bottom_bar.song_change()

        asyncio.create_task(toggle())

    def action_next_track(self) -> None:
        """Skip to next track."""
        async def next_track():
            await self.playback.next_track()
            self.playback.update()
            bottom_bar = self.query_one(Bottom_Bar)
            await bottom_bar.update_playback_settings()
            await bottom_bar.song_change()

        asyncio.create_task(next_track())

    def action_previous_track(self) -> None:
        """Go back to previous track."""
        async def previous_track():
            await self.playback.previous_track()
            self.playback.update()
            bottom_bar = self.query_one(Bottom_Bar)
            await bottom_bar.update_playback_settings()
            await bottom_bar.song_change()

        asyncio.create_task(previous_track())

    def action_volume_up(self) -> None:
        """Increase volume by 5%."""
        async def volume_up():
            if self.playback.device_volume_percent is not None:
                new_volume = min(100, self.playback.device_volume_percent + 5)
                await self.playback.set_volume(new_volume)
                self.playback.update()
                bottom_bar = self.query_one(Bottom_Bar)
                await bottom_bar.update_playback_settings()

        asyncio.create_task(volume_up())

    def action_volume_down(self) -> None:
        """Decrease volume by 5%."""
        async def volume_down():
            if self.playback.device_volume_percent is not None:
                new_volume = max(0, self.playback.device_volume_percent - 5)
                await self.playback.set_volume(new_volume)
                self.playback.update()
                bottom_bar = self.query_one(Bottom_Bar)
                await bottom_bar.update_playback_settings()

        asyncio.create_task(volume_down())

    # Mount the main screen
    async def on_mount(self) -> None:
        self.install_screen(Main_Screen(), "main")  # Removed await
        await self.push_screen("main")  # Keep await


# Run the app if the script is executed directly
if __name__ == "__main__":
    app = MainApp(ansi_color=True)
    app.run()