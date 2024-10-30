import pytest
from textual.app import App
from main import MainApp
from spotify_main_class import Spotify_Playback_Data

@pytest.mark.asyncio
async def test_play_pause():
    """Test the play/pause functionality using key presses."""
    app = MainApp()
    async with app.run_test() as pilot:
        # Initially, playback should be paused
        assert not app.playback.is_playing

        # Press space to play
        await pilot.press("space")
        assert app.playback.is_playing

        # Press space to pause
        await pilot.press("space")
        assert not app.playback.is_playing

@pytest.mark.asyncio
async def test_next_track():
    """Test skipping to the next track using key presses."""
    app = MainApp()
    initial_track = app.playback.track
    async with app.run_test() as pilot:
        await pilot.press(">")
        assert app.playback.track != initial_track

@pytest.mark.asyncio
async def test_previous_track():
    """Test going back to the previous track using key presses."""
    app = MainApp()
    initial_track = app.playback.track
    async with app.run_test() as pilot:
        await pilot.press("<")
        assert app.playback.track != initial_track

@pytest.mark.asyncio
async def test_ui_snapshot(snap_compare):
    """Snapshot test to verify the UI renders correctly."""
    app = MainApp()
    async with app.run_test() as pilot:
        # Perform initial UI snapshot
        assert snap_compare("main.py")

        # Simulate some user interactions
        await pilot.press("space")  # Play
        await pilot.press(">")
        await pilot.press("<")

        # Take another snapshot after interactions
        assert snap_compare("main.py")
