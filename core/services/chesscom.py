import requests
import logging
from chessdotcom import get_player_game_archives, get_player_games_by_month, Client
from datetime import datetime
from typing import List, Dict, Optional

# Configure chessdotcom client with proper User-Agent
Client.request_config['headers']['User-Agent'] = 'Chess Analysis Tool (github.com/chiedu18/chess-analysis; contact: chiedu@example.com)'

# User-Agent for direct API calls
USER_AGENT = "chess-analysis-app/0.3 (github.com/chiedu18)"

logger = logging.getLogger(__name__)

def player_profile(username: str) -> Dict:
    """
    Fetch player profile and stats from Chess.com API
    
    Args:
        username: Chess.com username
        
    Returns:
        Dict with username, title, and blitz_rating
    """
    try:
        headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
        base = f"https://api.chess.com/pub/player/{username.lower()}"
        
        # Get profile info
        prof_response = requests.get(base, headers=headers, timeout=10)
        prof_response.raise_for_status()
        prof = prof_response.json()
        
        # Get stats
        stats_response = requests.get(base + "/stats", headers=headers, timeout=10)
        stats_response.raise_for_status()
        stats = stats_response.json()
        
        blitz_rating = stats.get("chess_blitz", {}).get("last", {}).get("rating")
        
        return {
            "username": prof["username"],
            "title": prof.get("title"),
            "blitz_rating": blitz_rating
        }
    except Exception as e:
        logger.error(f"Error fetching profile for {username}: {e}")
        # Return basic info if profile fetch fails
        return {
            "username": username,
            "title": None,
            "blitz_rating": None
        }

def player_games(username: str, *, limit: int = 100) -> List[Dict]:
    """
    Fetch the last N games from Chess.com API for a given username
    
    Args:
        username: Chess.com username
        limit: Maximum number of games to fetch
        
    Returns:
        List of raw game dictionaries from Chess.com API
    """
    # Normalize username to lowercase
    username = username.strip().lower()
    
    try:
        # Get player's game archives using chessdotcom library
        archives_response = get_player_game_archives(username)
        archives = archives_response.json['archives']
        
        if not archives:
            return []
        
        # Get games from the most recent archives until we have enough games
        all_games = []
        for archive_url in reversed(archives):  # Start with most recent
            if len(all_games) >= limit:
                break
                
            # Extract year and month from archive URL
            # URL format: https://api.chess.com/pub/player/username/games/YYYY/MM
            parts = archive_url.split('/')
            year = int(parts[-2])
            month = int(parts[-1])
            
            # Get games for this month
            month_response = get_player_games_by_month(username, year, month)
            games = month_response.json['games']
            
            for game in games:
                if len(all_games) >= limit:
                    break
                all_games.append(game)
        
        # Sort by newest first before returning
        all_games.sort(key=lambda g: g["end_time"], reverse=True)
        
        return all_games[:limit]
        
    except Exception as e:
        logger.error(f"Error fetching games for {username}: {e}")
        error_msg = str(e)
        if '404' in error_msg or 'not found' in error_msg.lower():
            raise ValueError(f'Username "{username}" not found on Chess.com')
        elif '403' in error_msg or 'forbidden' in error_msg.lower():
            raise ValueError(f'Username "{username}" not found or account is private. Please check the username and ensure the account is public.')
        elif '429' in error_msg or 'rate limit' in error_msg.lower():
            raise ValueError('Rate limit exceeded. Please try again in a few minutes.')
        else:
            raise ValueError(f'Error fetching games: {error_msg}') 