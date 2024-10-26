from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widget import Widget
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
    # Lazy,
    LoadingIndicator
)
from textual.reactive import reactive
from spotify_main_class import Spotify_Playback_Data
import time
from textual import work

playback = Spotify_Playback_Data()

def cut_string_if_long(string: str, max_length: int) -> str:
    return string[:abs(max_length)].strip() + "..." if len(string) > abs(max_length) else string

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
                Center(
                    ProgressBar(
                        total=100, id="bar", show_percentage=False, show_eta=False
                    )
                ),
                Track_Duration(),
                id="bar_with_times",
            ),
            id="bottom_bar_collection",
        )

    def update_progress(self, progress=None):
        current_time_widget = self.query_one(Current_Time_In_Track)

        try:
            self.query_one(ProgressBar).update(
                progress=current_time_widget.current_time,
                total=playback.track_duration,
            )
        except:
            return
        if playback.is_playing and progress is None:
            current_time_widget.current_time += 1000
        else:
            current_time_widget.current_time = progress


    def song_change(self):
        self.query_one(Track_Duration).track_duration = playback.track_duration
        # self.query_one(Current_Time_In_Track).current_time = (
        #     get_current_time_with_offset()
        # )
        self.update_progress()
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
            yield Library_List(
                library_data=playback.get_featured_playlists(limit=5),
                id="featured_playlists_list",
            )
            yield Library_List(
                library_data=playback.get_user_library(), id="user_library_list"
            )


class Library_List(Widget):

    # selected_playlist_id = reactive(None)

    def __init__(self, library_data, id=None):
        self.library_data = library_data
        super().__init__(id=id)

    def on_list_view_selected(self, selected_item):
        self.notify(f"item selected: {selected_item.item.name}")
        # playlist_id = self.library_data[selected_item.item.name]["id"]
        for item in self.library_data:
            if item["name"] == selected_item.item.name:
                playlist_id = item["id"]
                self.notify(f"playlist_id: {playlist_id}")
                break

        # table = self.query_one("#playlist_tracks")
        # table.change_playlist(playlist_id)

        # self.selected_playlist_id = playlist_id
        self.post_message(playlist_id)

    def compose(self):
        items = [
            ListItem(Label(f"{item['name']} ({item['type'].capitalize()})"), name=item['name'])
            for item in self.library_data
        ]
        yield ListView(*items)


class Main_Page(Widget):
    def compose(self):
        with Container(id="main_page_container"):
            # yield Static("Main Page", id="main_page_header")
            yield Playlist_Track_View(
                playlist_id="liked_songs", id="playlist_tracks"
            )


class Playlist_Track_View(Widget):

    # weighting
    track_weight, artist_weight, album_weight = 2, 1, 1
    old_size = (0, 0)
    adjusting_size = False

    def __init__(self, playlist_id, max_title_length=40, id=None):
        self.playlist_id = playlist_id
        self.max_title_length = max_title_length
        self.tracks = []
        super().__init__(id=id)

    def change_playlist(self, playlist_id):
        self.playlist_id = playlist_id
        self.set_tracks()

    def on_data_table_row_selected(self, row):
        self.notify(f"Row selected: {row}")
        selected_track = self.tracks[row.cursor_row]['id']
        self.notify(f"Selected track: {selected_track}")
        playback.play_track(selected_track)

    def adjust_columns(self):
        current_size = self.query_one(DataTable).size[0]
        if self.old_size == current_size:
            return
        elif self.adjusting_size:
            return
        self.old_size = current_size
        self.post_display_hook()

    def compose(self) -> ComposeResult:
        yield DataTable()

    @work
    async def set_tracks(self, lengths=[100, 100, 100]):
        table = self.query_one(DataTable)
        table.loading = True
        # table.styles.width = "100%"
        table.clear()

        columns = table.add_columns("#", "Title", "Artist", "Album", "Duration", "Liked")

        self.tracks = playback.get_playlist_tracks(self.playlist_id)

        # if lengths is None:
        #     h, width = table.size()
        #     max_length = width

        #     # calculate max lengths according to the weights
        #     max_track_length = (
        #         max_length
        #         * self.track_weight
        #         // (self.track_weight + self.artist_weight + self.album_weight)
        #     )
        #     max_artist_length = (
        #         max_length
        #         * self.artist_weight
        #         // (self.track_weight + self.artist_weight + self.album_weight)
        #     )
        #     max_album_length = (
        #         max_length
        #         * self.album_weight
        #         // (self.track_weight + self.artist_weight + self.album_weight)
        #     )
        # else:
        #     max_track_length, max_artist_length, max_album_length = lengths

        for i, track in enumerate(self.tracks):
            track_name = str(track["name"])
            artist_string = str(", ".join(track.get("artists", [])))
            album_name = str(track.get("album", ""))

            # track_name = cut_string_if_long(track_name, max_track_length)
            # artist_string = cut_string_if_long(artist_string, max_artist_length)
            # album_name = cut_string_if_long(album_name, max_album_length)

            table.add_row(
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

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        # table.zebra_stripes = True
        # table.styles.scrollbar_size_vertical = 0
        table.styles.scrollbar_size_horizontal = 0
        # table.styles.border = ("heavy", "blue")

        height, width = table.size
        max_length = width - 5

        # calculate max lengths according to the weights
        max_track_length = (
            max_length
            * self.track_weight
            // (self.track_weight + self.artist_weight + self.album_weight)
        )
        max_artist_length = (
            max_length
            * self.artist_weight
            // (self.track_weight + self.artist_weight + self.album_weight)
        )

        max_album_length = (
            max_length
            * self.album_weight
            // (self.track_weight + self.artist_weight + self.album_weight)
        )

        lengths = (max_track_length, max_artist_length, max_album_length)

        # Call the async method to set tracks
        self.set_tracks()
        # self.set_interval(5, self.adjust_columns)

    @work
    async def post_display_hook(self) -> None:
        adjusting_size = True
        # This method adjusts the column widths based on the table size
        table = self.query_one(DataTable)
        size = table.container_size

        # If the size is not valid, try again later
        if not all([c for c in size]):
            self.call_later(self.post_display_hook)
            return

        self.notify(f"size: {str(size)}, {self.is_mounted}")  # Debugging output
        taken_chars = -1
        for c in table.columns.values():
            # self.notify(f"Column: {c}")
            # exit()
            c.auto_width = False
            # if c.label in ["Title", "Artist", "Album"]:
            #     c.percentage_width = 100 / 3
            # elif c.label in ["Duration"]:
            #     c.width = 4
            #     continue
            if not hasattr(c, "percentage_width") or (c.percentage_width is None):
                c.percentage_width = c.width

            # '#' should be 4 characters wide
            # 'Duration' should be 5 characters wide
            # 'Liked' should be 4 characters wide

            # if str(c.label) == "#":
            #     c.percentage_width = None
            #     c.auto_width = True
            # elif str(c.label) == "Duration":
            #     c.percentage_width = None
            #     c.width = 8
            # elif str(c.label) == "Liked":
            #     c.percentage_width = None
            #     c.width = 4

            # --- try auto width
            if str(c.label) == "#":
                c.width = len(str(table.row_count))
            elif str(c.label) == "Duration":
                c.auto_width = True

            elif str(c.label) == "Liked":
                c.auto_width = True
            else:
                pass
            taken_chars += c.width
            # else:
            #     c.percentage_width = None
            #     c.width = int((size[0]-5) / (len(table.columns)-3))
            # self.notify(f"Hit Column: {c.label}, width: {c.width}")

            # c.width = int(size[0] / len(table.columns))
            # self.notify(f"Column: {c.label}, width: {c.width}")
        # Refresh the table display
        for c in table.columns.values():
            if str(c.label) in ["Title", "Artist", "Album"]:
                c.width = int((size[0] - taken_chars) / (len(table.columns) - 3))+1
        table.refresh()
        self.notify(str(self))
        adjusting_size = False


class Main_Screen(Screen):
    CSS_PATH = "main_page.tcss"

    def on_list_view_selected(self, playlist_id):
        self.query_one(Playlist_Track_View).change_playlist(playlist_id)
    #     self.notify(f"item selected: {item.list_view.id}")
    #     # playlist_id = self.library_data[selected_item.item.name]["id"]
    #     # for item in list_view.library_data:
    #     #     if item["name"] == selected_item.item.name:
    #     #         playlist_id = item["id"]
    #     #         self.notify(f"playlist_id: {playlist_id}")
    #     #         break

    #     # table = self.query_one("#playlist_tracks")
    #     # table.change_playlist(playlist_id)

    def compose(self) -> ComposeResult:
        yield Placeholder("top_bar", id="top_bar")
        yield Side_Bar(id="sidebar")
        yield Main_Page(id="main_page")
        # yield Placeholder("Main Page", id="main_page")
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
