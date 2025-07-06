from django.test import TestCase
from unittest.mock import patch, MagicMock
from core.services.chesscom import player_profile, player_games

class ChessComServiceTestCase(TestCase):
    
    @patch('core.services.chesscom.requests.get')
    def test_player_profile_success(self, mock_get):
        """Test successful profile fetch"""
        # Mock profile response
        mock_profile_response = MagicMock()
        mock_profile_response.json.return_value = {
            "username": "testuser",
            "title": "GM"
        }
        mock_profile_response.raise_for_status.return_value = None
        
        # Mock stats response
        mock_stats_response = MagicMock()
        mock_stats_response.json.return_value = {
            "chess_blitz": {
                "last": {
                    "rating": 2500
                }
            }
        }
        mock_stats_response.raise_for_status.return_value = None
        
        mock_get.side_effect = [mock_profile_response, mock_stats_response]
        
        result = player_profile("testuser")
        
        self.assertEqual(result["username"], "testuser")
        self.assertEqual(result["title"], "GM")
        self.assertEqual(result["blitz_rating"], 2500)
    
    @patch('core.services.chesscom.requests.get')
    def test_player_profile_failure(self, mock_get):
        """Test profile fetch failure"""
        mock_get.side_effect = Exception("Network error")
        
        result = player_profile("testuser")
        
        self.assertEqual(result["username"], "testuser")
        self.assertIsNone(result["title"])
        self.assertIsNone(result["blitz_rating"])
    
    @patch('core.services.chesscom.get_player_game_archives')
    @patch('core.services.chesscom.get_player_games_by_month')
    def test_player_games_success(self, mock_get_games, mock_get_archives):
        """Test successful games fetch"""
        # Mock archives
        mock_archives_response = MagicMock()
        mock_archives_response.json = {'archives': ['https://api.chess.com/pub/player/testuser/games/2024/01']}
        mock_get_archives.return_value = mock_archives_response
        
        # Mock games
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
        
        result = player_games("testuser", limit=2)
        
        self.assertEqual(len(result), 2)
        # Should be sorted by newest first
        self.assertEqual(result[0]["end_time"], 1706745600)
        self.assertEqual(result[1]["end_time"], 1704067200)
    
    @patch('core.services.chesscom.get_player_game_archives')
    def test_player_games_no_archives(self, mock_get_archives):
        """Test games fetch when no archives exist"""
        mock_archives_response = MagicMock()
        mock_archives_response.json = {'archives': []}
        mock_get_archives.return_value = mock_archives_response
        
        result = player_games("testuser")
        
        self.assertEqual(result, [])
    
    @patch('core.services.chesscom.get_player_game_archives')
    def test_player_games_404_error(self, mock_get_archives):
        """Test games fetch with 404 error"""
        mock_get_archives.side_effect = Exception("404 not found")
        
        with self.assertRaises(ValueError) as context:
            player_games("testuser")
        
        self.assertIn("not found on Chess.com", str(context.exception)) 