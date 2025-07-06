from datetime import datetime
from typing import Dict, List
import base64
from .outcomes import calculate_outcome_with_class

def massage_game(game: Dict, username: str) -> Dict:
    """
    Flatten the nested JSON and add user-perspective outcome
    
    Args:
        game: Raw game dictionary from Chess.com API
        username: The username we're analyzing for
        
    Returns:
        Flattened game dictionary with presentation-ready fields
    """
    outcome, outcome_class = calculate_outcome_with_class(game, username)
    
    # Create a unique ID for the PGN
    pgn_id = base64.urlsafe_b64encode(game["pgn"].encode()).decode().rstrip('=')
    
    return {
        "end": datetime.utcfromtimestamp(game["end_time"]),
        "white": game["white"]["username"],
        "white_rating": game["white"]["rating"],
        "white_result": game["white"]["result"],
        "black": game["black"]["username"],
        "black_rating": game["black"]["rating"],
        "black_result": game["black"]["result"],
        "time_class": game["time_class"],
        "pgn": game["pgn"],
        "pgn_id": pgn_id,
        "url": game.get("url", ""),
        "outcome": outcome,
        "outcome_class": outcome_class,
    }

def massage_games(games: List[Dict], username: str) -> List[Dict]:
    """
    Massage a list of games
    
    Args:
        games: List of raw game dictionaries from Chess.com API
        username: The username we're analyzing for
        
    Returns:
        List of flattened game dictionaries
    """
    return [massage_game(game, username) for game in games] 