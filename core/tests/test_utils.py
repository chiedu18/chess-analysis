from django.test import TestCase
from datetime import datetime
from core.utils.outcomes import calculate_outcome, get_outcome_class, calculate_outcome_with_class
from core.utils.transform import massage_game, massage_games

class OutcomesTestCase(TestCase):
    
    def test_calculate_outcome_user_wins_as_white(self):
        """Test user wins as white"""
        game = {
            "white": {"username": "testuser", "result": "win"},
            "black": {"username": "opponent", "result": "resigned"}
        }
        self.assertEqual(calculate_outcome(game, "testuser"), "Win")
    
    def test_calculate_outcome_user_loses_as_white(self):
        """Test user loses as white"""
        game = {
            "white": {"username": "testuser", "result": "resigned"},
            "black": {"username": "opponent", "result": "win"}
        }
        self.assertEqual(calculate_outcome(game, "testuser"), "Loss")
    
    def test_calculate_outcome_user_wins_as_black(self):
        """Test user wins as black"""
        game = {
            "white": {"username": "opponent", "result": "resigned"},
            "black": {"username": "testuser", "result": "win"}
        }
        self.assertEqual(calculate_outcome(game, "testuser"), "Win")
    
    def test_calculate_outcome_user_loses_as_black(self):
        """Test user loses as black"""
        game = {
            "white": {"username": "opponent", "result": "win"},
            "black": {"username": "testuser", "result": "resigned"}
        }
        self.assertEqual(calculate_outcome(game, "testuser"), "Loss")
    
    def test_calculate_outcome_draw(self):
        """Test draw outcome"""
        game = {
            "white": {"username": "testuser", "result": "draw"},
            "black": {"username": "opponent", "result": "draw"}
        }
        self.assertEqual(calculate_outcome(game, "testuser"), "Draw")
    
    def test_get_outcome_class_win(self):
        """Test CSS class for win"""
        self.assertEqual(get_outcome_class("Win"), "bg-success")
    
    def test_get_outcome_class_loss(self):
        """Test CSS class for loss"""
        self.assertEqual(get_outcome_class("Loss"), "bg-danger")
    
    def test_get_outcome_class_draw(self):
        """Test CSS class for draw"""
        self.assertEqual(get_outcome_class("Draw"), "bg-secondary")
    
    def test_calculate_outcome_with_class(self):
        """Test combined outcome and class calculation"""
        game = {
            "white": {"username": "testuser", "result": "win"},
            "black": {"username": "opponent", "result": "resigned"}
        }
        outcome, css_class = calculate_outcome_with_class(game, "testuser")
        self.assertEqual(outcome, "Win")
        self.assertEqual(css_class, "bg-success")

class TransformTestCase(TestCase):
    
    def test_massage_game(self):
        """Test game data transformation"""
        raw_game = {
            "end_time": 1704067200,  # Jan 1, 2024
            "white": {"username": "testuser", "rating": 1500, "result": "win"},
            "black": {"username": "opponent", "rating": 1400, "result": "resigned"},
            "time_class": "blitz",
            "pgn": "1. e4 e5 2. Nf3",
            "url": "https://chess.com/game/1"
        }
        
        result = massage_game(raw_game, "testuser")
        
        self.assertEqual(result["white"], "testuser")
        self.assertEqual(result["black"], "opponent")
        self.assertEqual(result["white_rating"], 1500)
        self.assertEqual(result["black_rating"], 1400)
        self.assertEqual(result["time_class"], "blitz")
        self.assertEqual(result["pgn"], "1. e4 e5 2. Nf3")
        self.assertEqual(result["url"], "https://chess.com/game/1")
        self.assertEqual(result["outcome"], "Win")
        self.assertEqual(result["outcome_class"], "bg-success")
        self.assertIsInstance(result["end"], datetime)
    
    def test_massage_games(self):
        """Test massaging multiple games"""
        raw_games = [
            {
                "end_time": 1704067200,
                "white": {"username": "testuser", "rating": 1500, "result": "win"},
                "black": {"username": "opponent", "rating": 1400, "result": "resigned"},
                "time_class": "blitz",
                "pgn": "1. e4 e5 2. Nf3",
                "url": "https://chess.com/game/1"
            },
            {
                "end_time": 1706745600,
                "white": {"username": "opponent", "rating": 1400, "result": "resigned"},
                "black": {"username": "testuser", "rating": 1500, "result": "win"},
                "time_class": "blitz",
                "pgn": "1. d4 d5 2. c4",
                "url": "https://chess.com/game/2"
            }
        ]
        
        result = massage_games(raw_games, "testuser")
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["outcome"], "Win")
        self.assertEqual(result[1]["outcome"], "Win")
        self.assertEqual(result[0]["outcome_class"], "bg-success")
        self.assertEqual(result[1]["outcome_class"], "bg-success") 