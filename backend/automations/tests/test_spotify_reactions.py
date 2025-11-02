"""
Tests for Spotify reaction execution.
Tests Spotify reactions through _execute_reaction_logic.
"""

from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from automations.models import Action, Area, Reaction, Service
from automations.tasks import _execute_reaction_logic

User = get_user_model()


class SpotifyReactionTests(TestCase):
    """Test Spotify reaction execution."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Create Spotify service
        self.spotify_service = Service.objects.create(
            name="spotify", description="Spotify Service"
        )

        # Create Action and Reaction (required by Area model)
        self.action = Action.objects.create(
            service=self.spotify_service,
            name="test_action",
            description="Test action",
        )

        self.reaction = Reaction.objects.create(
            service=self.spotify_service,
            name="test_reaction",
            description="Test reaction",
        )

        # Create a test automation area
        self.area = Area.objects.create(
            name="Test Spotify Area",
            owner=self.user,
            action=self.action,
            reaction=self.reaction,
            status=Area.Status.ACTIVE,
        )

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.helpers.spotify_helper.play_track")
    def test_spotify_play_track_success(self, mock_play_track, mock_get_token):
        """Test successful Spotify track playback."""
        mock_get_token.return_value = "test_spotify_token"
        mock_play_track.return_value = {"success": True}

        result = _execute_reaction_logic(
            reaction_name="spotify_play_track",
            reaction_config={
                "track_uri": "spotify:track:3n3Ppam7vgaVa1iaRUc9Lp",
                "position_ms": 0,
            },
            trigger_data={},
            area=self.area,
        )

        # Check result
        self.assertEqual(result["success"], True)

        # Verify API was called correctly
        mock_get_token.assert_called_once_with(self.user, "spotify")
        mock_play_track.assert_called_once_with(
            "test_spotify_token", "spotify:track:3n3Ppam7vgaVa1iaRUc9Lp", 0
        )

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.helpers.spotify_helper.play_track")
    def test_spotify_play_track_from_url(self, mock_play_track, mock_get_token):
        """Test Spotify track playback from URL (converts to URI)."""
        mock_get_token.return_value = "test_token"
        mock_play_track.return_value = {"success": True}

        result = _execute_reaction_logic(
            reaction_name="spotify_play_track",
            reaction_config={
                "track_uri": "https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp",
            },
            trigger_data={},
            area=self.area,
        )

        self.assertEqual(result["success"], True)

        # Verify URI conversion
        call_args = mock_play_track.call_args[0]
        self.assertEqual(call_args[1], "spotify:track:3n3Ppam7vgaVa1iaRUc9Lp")

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    def test_spotify_play_track_missing_uri(self, mock_get_token):
        """Test spotify_play_track with missing track URI."""
        mock_get_token.return_value = "test_token"

        with self.assertRaisesMessage(
            ValueError, "Track URI/URL is required for spotify_play_track"
        ):
            _execute_reaction_logic(
                reaction_name="spotify_play_track",
                reaction_config={},
                trigger_data={},
                area=self.area,
            )

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    def test_spotify_play_track_no_token(self, mock_get_token):
        """Test spotify_play_track when user has no Spotify token."""
        mock_get_token.return_value = None

        with self.assertRaisesMessage(ValueError, "No valid Spotify token"):
            _execute_reaction_logic(
                reaction_name="spotify_play_track",
                reaction_config={"track_uri": "spotify:track:123"},
                trigger_data={},
                area=self.area,
            )

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.helpers.spotify_helper.play_track")
    def test_spotify_play_track_api_error(self, mock_play_track, mock_get_token):
        """Test spotify_play_track when API fails."""
        mock_get_token.return_value = "test_token"
        mock_play_track.side_effect = Exception("Track not found")

        with self.assertRaisesMessage(ValueError, "Spotify play_track failed"):
            _execute_reaction_logic(
                reaction_name="spotify_play_track",
                reaction_config={"track_uri": "spotify:track:invalid"},
                trigger_data={},
                area=self.area,
            )

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.helpers.spotify_helper.pause_playback")
    def test_spotify_pause_playback_success(self, mock_pause, mock_get_token):
        """Test successful Spotify pause."""
        mock_get_token.return_value = "test_token"
        mock_pause.return_value = {"success": True}

        result = _execute_reaction_logic(
            reaction_name="spotify_pause_playback",
            reaction_config={},
            trigger_data={},
            area=self.area,
        )

        self.assertEqual(result["success"], True)
        mock_pause.assert_called_once_with("test_token")

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.helpers.spotify_helper.resume_playback")
    def test_spotify_resume_playback_success(self, mock_resume, mock_get_token):
        """Test successful Spotify resume."""
        mock_get_token.return_value = "test_token"
        mock_resume.return_value = {"success": True}

        result = _execute_reaction_logic(
            reaction_name="spotify_resume_playback",
            reaction_config={},
            trigger_data={},
            area=self.area,
        )

        self.assertEqual(result["success"], True)
        mock_resume.assert_called_once_with("test_token")

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.helpers.spotify_helper.skip_to_next")
    def test_spotify_skip_next_success(self, mock_skip_next, mock_get_token):
        """Test successful Spotify skip to next."""
        mock_get_token.return_value = "test_token"
        mock_skip_next.return_value = {"success": True}

        result = _execute_reaction_logic(
            reaction_name="spotify_skip_next",
            reaction_config={},
            trigger_data={},
            area=self.area,
        )

        self.assertEqual(result["success"], True)
        mock_skip_next.assert_called_once_with("test_token")

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.helpers.spotify_helper.skip_to_previous")
    def test_spotify_skip_previous_success(self, mock_skip_prev, mock_get_token):
        """Test successful Spotify skip to previous."""
        mock_get_token.return_value = "test_token"
        mock_skip_prev.return_value = {"success": True}

        result = _execute_reaction_logic(
            reaction_name="spotify_skip_previous",
            reaction_config={},
            trigger_data={},
            area=self.area,
        )

        self.assertEqual(result["success"], True)
        mock_skip_prev.assert_called_once_with("test_token")

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.helpers.spotify_helper.set_volume")
    def test_spotify_set_volume_success(self, mock_set_volume, mock_get_token):
        """Test successful Spotify volume change."""
        mock_get_token.return_value = "test_token"
        mock_set_volume.return_value = {"success": True}

        result = _execute_reaction_logic(
            reaction_name="spotify_set_volume",
            reaction_config={"volume_percent": 75},
            trigger_data={},
            area=self.area,
        )

        self.assertEqual(result["success"], True)
        mock_set_volume.assert_called_once_with("test_token", 75)

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.helpers.spotify_helper.set_volume")
    def test_spotify_set_volume_default(self, mock_set_volume, mock_get_token):
        """Test Spotify volume with default value."""
        mock_get_token.return_value = "test_token"
        mock_set_volume.return_value = {"success": True}

        result = _execute_reaction_logic(
            reaction_name="spotify_set_volume",
            reaction_config={},  # No volume specified
            trigger_data={},
            area=self.area,
        )

        self.assertEqual(result["success"], True)
        # Should use default of 50%
        mock_set_volume.assert_called_once_with("test_token", 50)

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.helpers.spotify_helper.create_playlist")
    def test_spotify_create_playlist_success(self, mock_create, mock_get_token):
        """Test successful Spotify playlist creation."""
        mock_get_token.return_value = "test_token"
        mock_create.return_value = {
            "success": True,
            "playlist_id": "playlist_123",
            "name": "My New Playlist",
        }

        result = _execute_reaction_logic(
            reaction_name="spotify_create_playlist",
            reaction_config={
                "name": "My New Playlist",
                "description": "Created by AREA",
                "public": True,
            },
            trigger_data={},
            area=self.area,
        )

        self.assertEqual(result["success"], True)
        self.assertEqual(result["name"], "My New Playlist")

        mock_create.assert_called_once_with(
            "test_token", "My New Playlist", "Created by AREA", True
        )

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    def test_spotify_create_playlist_missing_name(self, mock_get_token):
        """Test spotify_create_playlist with missing name."""
        mock_get_token.return_value = "test_token"

        with self.assertRaisesMessage(
            ValueError, "Playlist name is required for spotify_create_playlist"
        ):
            _execute_reaction_logic(
                reaction_name="spotify_create_playlist",
                reaction_config={},
                trigger_data={},
                area=self.area,
            )

    @patch("users.oauth.manager.OAuthManager.get_valid_token")
    @patch("automations.helpers.spotify_helper.create_playlist")
    def test_spotify_create_playlist_default_values(self, mock_create, mock_get_token):
        """Test spotify_create_playlist uses default values."""
        mock_get_token.return_value = "test_token"
        mock_create.return_value = {"success": True}

        result = _execute_reaction_logic(
            reaction_name="spotify_create_playlist",
            reaction_config={"name": "Test Playlist"},
            trigger_data={},
            area=self.area,
        )

        # Verify default values
        call_args = mock_create.call_args[0]
        self.assertEqual(call_args[2], "")  # default description
        self.assertEqual(call_args[3], False)  # default public=False
