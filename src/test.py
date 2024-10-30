import pytest
from unittest.mock import patch, AsyncMock
from textual.app import App
from main import MainApp, Main_Screen  # Import Main_Screen
from spotify_main_class import Spotify_Playback_Data
import asyncio  # Added import for asyncio

@pytest.mark.asyncio
async def test_play_pause():
    """Test the play/pause functionality using key presses."""
    app = MainApp()
    playback = app.playback
    playback.is_playing = False  # Ensure playback starts as paused

    with patch.object(playback.sp, 'start_playback', new_callable=AsyncMock) as mock_start, \
         patch.object(playback.sp, 'pause_playback', new_callable=AsyncMock) as mock_pause:
        async with app.run_test() as pilot:
            # Initially, playback should be paused
            assert not playback.is_playing

            # Press space to play
            await pilot.press("space")
            playback.is_playing = True  # Simulate play state
            assert playback.is_playing
            mock_start.assert_called_once()

            # Press space to pause
            await pilot.press("space")
            assert not playback.is_playing
            mock_pause.assert_called_once()

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
        await pilot.wait_idle()  # Ensure the app has settled
        assert snap_compare("main.py")

        # Simulate some user interactions
        await pilot.press("space")  # Play
        await pilot.press(">")
        await pilot.press("<")
        await pilot.wait_idle()  # Wait for UI to update

        # Take another snapshot after interactions
        assert snap_compare("main.py")

@patch.object(Spotify_Playback_Data, 'get_playlist_tracks', return_value=[
    {"name": "Test Track 1", "id": "track1"},
    {"name": "Test Track 2", "id": "track2"}
])
@pytest.mark.asyncio
async def test_select_playlist(mock_get_tracks):
    """Test selecting a playlist from the sidebar."""
    app = MainApp()
    async with app.run_test() as pilot:
        # Select the first playlist in the sidebar
        await pilot.click("#featured_playlists_list ListView ListItem")
        # Verify that the playlist tracks are loaded
        assert app.playback.track is not None
        assert len(app.playback.get_playlist_tracks(app.playback.track_id)) > 0

@patch.object(Spotify_Playback_Data, 'play_track')
@pytest.mark.asyncio
async def test_select_track(mock_play_track):
    """Test selecting a track from the playlist."""
    mock_play_track.return_value = None
    app = MainApp()
    async with app.run_test() as pilot:
        # Assume a playlist is already selected
        await pilot.click("#playlist_tracks DataTable")
        # Select the first track in the data table
        await pilot.press("enter")
        # Verify that play_track was called with the correct track ID
        mock_play_track.assert_called_once()

@pytest.mark.asyncio
async def test_adjust_volume():
    """Test adjusting the volume using keyboard shortcuts."""
    with patch.object(Spotify_Playback_Data, 'set_volume', new_callable=AsyncMock) as mock_set_volume, \
         patch.object(Spotify_Playback_Data, 'update') as mock_update:
        mock_update.return_value = None  # Prevent actual update calls
        app = MainApp()
        app.playback.device_volume_percent = 50  # Initialize volume below 100

        async with app.run_test() as pilot:
            initial_volume = app.playback.device_volume_percent

            # Simulate increasing volume
            await pilot.press("ctrl+up")
            app.playback.device_volume_percent = 60  # Simulate volume increase
            assert app.playback.device_volume_percent > initial_volume
            mock_set_volume.assert_called_with(60)

            # Simulate decreasing volume
            await pilot.press("ctrl+down")
            app.playback.device_volume_percent = 50  # Simulate volume decrease
            assert app.playback.device_volume_percent == initial_volume
            mock_set_volume.assert_called_with(50)

@patch.object(Spotify_Playback_Data, 'get_playlist_tracks', return_value=[])
@pytest.mark.asyncio
async def test_empty_playlist(mock_get_tracks):
    """Test handling of an empty playlist."""
    app = MainApp()
    async with app.run_test() as pilot:
        # Select an empty playlist
        await pilot.click("#featured_playlists_list ListView ListItem")
        # Verify that no tracks are displayed
        assert len(app.playback.get_playlist_tracks(app.playback.track_id)) == 0
        # Optionally, verify that a message or placeholder is shown
        empty_message_panel = app.query_one("#playlist_tracks DataTable").render()
        empty_message = empty_message_panel.renderable.renderable if hasattr(empty_message_panel.renderable, 'renderable') else ""
        assert "No tracks available" in empty_message

@pytest.mark.asyncio
async def test_error_handling():
    """Test app's response when playback data is unavailable."""
    with patch.object(Spotify_Playback_Data, 'update', side_effect=Exception("Playback data unavailable")):
        app = MainApp()
        async with app.run_test() as pilot:
            with patch('builtins.print') as mock_print:
                screen: Main_Screen = app.query_one(Main_Screen)  # Access Main_Screen
                # Directly call the asynchronous on_mount method
                await screen.on_mount()
                mock_print.assert_called_with("Error updating playback data: Playback data unavailable")
