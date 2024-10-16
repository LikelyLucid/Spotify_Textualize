from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer


class Spotify_app(App):
    async def on_mount(self) -> None:
        await super().on_mount()
        self.bindings = [
            Binding("q", "quit", "Quit"),
            Binding("c", "compose", "Compose"),
        ]

    async def compose(self) -> ComposeResult:
        return ComposeResult(
            content="Hello, world!",
            footer=Footer("Press 'q' to quit"),
        )

if __name__ == "__main__":
    app = Spotify_app()
    app.run()