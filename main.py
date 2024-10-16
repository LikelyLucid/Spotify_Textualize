from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.containers import Center, Middle
from textual.widgets import Footer, Placeholder, ProgressBar


class Main_Screen(Screen):
    """The main page that contains:
    Main side bar
    Changelog
    Footer
    Playing bar"""
    def compose(self) -> ComposeResult:
        with Center():
            with Middle():
                yield ProgressBar(total=30)
                yield Footer()

class MainApp(App):
    def on_mount(self) -> None:
        self.install_screen(Main_Screen(), "main")
        self.push_screen("main")

if __name__ == "__main__":
    app = MainApp()
    app.run()
