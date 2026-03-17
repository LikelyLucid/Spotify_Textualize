import pytest
from unittest.mock import patch, AsyncMock
from textual.app import App
from main import MainApp, Main_Screen
from spotify_main_class import Spotify_Playback_Data
import asyncio

@pytest.mark.asyncio
async def test_play_pause():
    """Test the play/pause functionality using key presses."""
    app = MainApp()
    playback = app.playback
    playback.is_playing = False

    with patch.object(playback.sp, 'start_playback', new_callable=AsyncMock) as mock_start, \
         patch.object(playback.sp, 'pause_playback', new_callable=AsyncMock) as mock_pause:
        async with app.run_test() as pilot:
            assert not playback.is_playing

            await pilot.press("space")
            playback.is_playing = True
            assert playback.is_playing
            mock_start.assert_called_once()

            await pilot.press("space")
            playback.is_playing = False
            assert not playback.is_playing
            mock_pause.assert_called_once()

@pytest.mark.asyncio
async def test_next_track():
    """Test skipping to the next track using key presses."""
    app = MainApp()
    initial_track = app.playback.track
    with patch.object(playback.sp, 'next_track', new_callable=AsyncMock) as mock_next_track:
        async with app.run_test() as pilot:
            await pilot.press(">")
            playback.update()
            assert app.playback.track != initial_track
            mock_next_track.assert_awaited_once()

@pytest.mark.asyncio
async def test_previous_track():
    """Test going back to the previous track using key presses."""
    app = MainApp()
    initial_track = app.playback.track
    with patch.object(playback.sp, 'previous_track', new_callable=AsyncMock) as mock_previous_track:
        async with app.run_test() as pilot:
            await pilot.press("<")
            playback.update()
            assert app.playback.track != initial_track
            mock_previous_track.assert_awaited_once()

@pytest.mark.asyncio
async def test_ui_snapshot(snap_compare):
    """Snapshot test to verify the UI renders correctly."""
    app = MainApp()
    async with app.run_test() as pilot:
        await asyncio.sleep(1)
        assert snap_compare("main.py")

@patch.object(Spotify_Playback_Data, 'get_playlist_tracks', return_value=[
    {"name": "Test Track 1", "id": "track1"},
    {"name": "Test Track 2", "id": "track2"}
])
@pytest.mark.asyncio
async def test_select_playlist(mock_get_tracks):
    """Test selecting a playlist from the sidebar."""
    app = MainApp()
    with patch.object(playback.sp, 'start_playback', new_callable=AsyncMock) as mock_start_playback:
        async with app.run_test() as pilot:
            await pilot.click("#featured_playlists_list ListView ListItem")
            assert app.playback.track is not None
            assert len(app.playback.get_playlist_tracks(app.playback.track_id)) > 0
            mock_start_playback.assert_not_called()

@patch.object(Spotify_Playback_Data, 'play_track', new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_select_track(mock_play_track):
    """Test selecting a track from the playlist."""
    mock_play_track.return_value = None
    app = MainApp()
    async with app.run_test() as pilot:
        await pilot.click("#playlist_tracks DataTable")
        await pilot.press("enter")
        mock_play_track.assert_awaited_once()

@pytest.mark.asyncio
async def test_adjust_volume():
    """Test adjusting the volume using keyboard shortcuts."""
    with patch.object(Spotify_Playback_Data, 'set_volume', new_callable=AsyncMock) as mock_set_volume, \
         patch.object(Spotify_Playback_Data, 'update', new_callable=AsyncMock) as mock_update:
        mock_update.return_value = None
        app = MainApp()
        app.playback.device_volume_percent = 50

        async with app.run_test() as pilot:
            initial_volume = app.playback.device_volume_percent

            await pilot.press("ctrl+up")
            playback.set_volume = AsyncMock()
            app.playback.device_volume_percent = 60
            assert app.playback.device_volume_percent > initial_volume
            mock_set_volume.assert_awaited_with(60)

            await pilot.press("ctrl+down")
            playback.set_volume = AsyncMock()
            app.playback.device_volume_percent = 50
            assert app.playback.device_volume_percent == initial_volume
            mock_set_volume.assert_awaited_with(50)

@patch.object(Spotify_Playback_Data, 'get_playlist_tracks', return_value=[])
@pytest.mark.asyncio
async def test_empty_playlist(mock_get_tracks):
    """Test handling of an empty playlist."""
    app = MainApp()
    async with app.run_test() as pilot:
        await pilot.click("#featured_playlists_list ListView ListItem")
        assert len(app.playback.get_playlist_tracks(app.playback.track_id)) == 0
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
                screen: Main_Screen = app.query_one(Main_Screen)
                await screen.on_mount()
                mock_print.assert_called_with("Error updating playback data: Playback data unavailable")
