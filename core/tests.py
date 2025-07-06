from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch, MagicMock
from datetime import datetime
import json

# Create your tests here.

class GamesListTestCase(TestCase):
    
    @patch('core.views.get_player_game_archives')
    @patch('core.views.get_player_games_by_month')
    @patch('core.views.requests.get')
    def test_games_sorted_by_newest_first(self, mock_requests_get, mock_get_games, mock_get_archives):
        """Test that games are sorted by newest first"""
        
        # Mock the profile API calls
        mock_profile_response = MagicMock()
        mock_profile_response.json.return_value = {
            "username": "testuser",
            "title": None
        }
        mock_profile_response.raise_for_status.return_value = None
        
        mock_stats_response = MagicMock()
        mock_stats_response.json.return_value = {
            "chess_blitz": {
                "last": {
                    "rating": 1500
                }
            }
        }
        mock_stats_response.raise_for_status.return_value = None
        
        mock_requests_get.side_effect = [mock_profile_response, mock_stats_response]
        
        # Mock the archives
        mock_archives_response = MagicMock()
        mock_archives_response.json = {'archives': ['https://api.chess.com/pub/player/testuser/games/2024/01']}
        mock_get_archives.return_value = mock_archives_response
        
        # Mock the games with different timestamps
        mock_games_response = MagicMock()
        mock_games_response.json = {
            'games': [
                {
                    "end_time": 1704067200,  # Jan 1, 2024
                    "white": {"username": "testuser", "rating": 1500, "result": "win"},
                    "black": {"username": "opponent", "rating": 1400, "result": "resigned"},
                    "time_class": "blitz",
                    "pgn": "1. e4 e5 2. Nf3",
                    "url": "https://chess.com/game/1"
                },
                {
                    "end_time": 1706745600,  # Jan 30, 2024 (newer)
                    "white": {"username": "opponent", "rating": 1400, "result": "resigned"},
                    "black": {"username": "testuser", "rating": 1500, "result": "win"},
                    "time_class": "blitz",
                    "pgn": "1. d4 d5 2. c4",
                    "url": "https://chess.com/game/2"
                }
            ]
        }
        mock_get_games.return_value = mock_games_response
        
        # Make the request
        response = self.client.get(reverse('core:games_list'), {'username': 'testuser'})
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that the games are in the context and sorted by newest first
        self.assertIn('games', response.context)
        games = response.context['games']
        
        # The second game should be first (newer timestamp)
        self.assertEqual(games[0]['end'], datetime.utcfromtimestamp(1706745600))
        self.assertEqual(games[1]['end'], datetime.utcfromtimestamp(1704067200))
        
        # Check that the profile is in the context
        self.assertIn('profile', response.context)
        profile = response.context['profile']
        self.assertEqual(profile['username'], 'testuser')
        self.assertEqual(profile['blitz_rating'], 1500)
    
    def test_outcome_calculation(self):
        """Test that game outcomes are calculated correctly from user's perspective"""
        from core.views import _outcome
        
        # Test user wins as white
        game = {
            "white": {"username": "testuser", "result": "win"},
            "black": {"username": "opponent", "result": "resigned"}
        }
        self.assertEqual(_outcome(game, "testuser"), "Win")
        
        # Test user loses as white
        game = {
            "white": {"username": "testuser", "result": "resigned"},
            "black": {"username": "opponent", "result": "win"}
        }
        self.assertEqual(_outcome(game, "testuser"), "Loss")
        
        # Test user wins as black
        game = {
            "white": {"username": "opponent", "result": "resigned"},
            "black": {"username": "testuser", "result": "win"}
        }
        self.assertEqual(_outcome(game, "testuser"), "Win")
        
        # Test draw
        game = {
            "white": {"username": "testuser", "result": "draw"},
            "black": {"username": "opponent", "result": "draw"}
        }
        self.assertEqual(_outcome(game, "testuser"), "Draw")
