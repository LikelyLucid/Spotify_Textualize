import pytest
from unittest.mock import patch
from textual.app import App
from main import MainApp, Main_Screen  # Import Main_Screen
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

@patch.object(Spotify_Playback_Data, 'update')
@pytest.mark.asyncio
async def test_select_playlist(mock_update):
    """Test selecting a playlist from the sidebar."""
    mock_update.return_value = None
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

@patch.object(Spotify_Playback_Data, 'update')
@pytest.mark.asyncio
async def test_adjust_volume(mock_update):
    """Test adjusting the volume using keyboard shortcuts."""
    mock_update.return_value = None
    app = MainApp()
    async with app.run_test() as pilot:
        initial_volume = app.playback.device_volume_percent
        # Simulate increasing volume
        await pilot.press("ctrl+up")
        assert app.playback.device_volume_percent > initial_volume
        # Simulate decreasing volume
        await pilot.press("ctrl+down")
        assert app.playback.device_volume_percent == initial_volume

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
        empty_message = app.query_one("#playlist_tracks DataTable").render()
        assert "No tracks available" in empty_message

@patch.object(Spotify_Playback_Data, 'update', side_effect=Exception("Playback data unavailable"))
@pytest.mark.asyncio
async def test_error_handling(mock_update):
    """Test app's response when playback data is unavailable."""
    app = MainApp()
    async with app.run_test() as pilot:
        with patch('builtins.print') as mock_print:
            screen: Main_Screen = app.query_one(Main_Screen)  # Access Main_Screen
            await screen.on_mount()
            mock_print.assert_called_with("Error updating playback data: Playback data unavailable")
