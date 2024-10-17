from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widget import Widget
from textual.containers import Container, Center, Middle, Horizontal, Vertical
from textual.widgets import Footer, Placeholder, ProgressBar
from textual.reactive import reactive

class Current_Time_In_Track(Widget):
    current_time = reactive("track_time")
    def render(self) -> str:
        return "0:00"

class Track_Duration(Widget):
    track_duration = reactive("track_time")
    def render(self) -> str:
        return "3:00"
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
        yield Container(Placeholder("CONTROLS", id="controls"), id="Bottom")
        yield Horizontal(id="bar_container",
            Current_Time_In_Track(),
            ProgressBar(
                    total=100, id="bar", show_percentage=False, show_eta=False
                ),
            Track_Duration())


class MainApp(App):
    def on_mount(self) -> None:
        self.install_screen(Main_Screen(), "main")
        self.push_screen("main")


if __name__ == "__main__":
    app = MainApp()
    app.run()
