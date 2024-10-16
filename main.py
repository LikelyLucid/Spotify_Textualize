from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer


class Main_Screen(Screen):
    """The main page that contains:
    Main side bar
    Changelog
    Footer
    Playing bar"""
    def compose(self) -> ComposeResult:
        yield Footer(text="Footer")

class MainApp(App):
    def on_mount(self) -> None:
        self.install_screen(Main_Screen(), "main")

if __name__ == "__main__":
    app = MainApp()
    app.run()