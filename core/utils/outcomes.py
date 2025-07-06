from typing import Dict, Tuple

def calculate_outcome(game: Dict, username: str) -> str:
    """
    Determine game outcome from the searched user's perspective
    
    Args:
        game: Raw game dictionary from Chess.com API
        username: The username we're analyzing for
        
    Returns:
        "Win", "Loss", or "Draw"
    """
    w = game["white"]["username"].lower()
    wr = game["white"]["result"]
    br = game["black"]["result"]
    
    if wr == br:  # both "draw"
        return "Draw"
    
    won = wr == "win"
    user_is_white = username.lower() == w
    return "Win" if won == user_is_white else "Loss"

def get_outcome_class(outcome: str) -> str:
    """
    Get the CSS class for an outcome badge
    
    Args:
        outcome: "Win", "Loss", or "Draw"
        
    Returns:
        Bootstrap badge class
    """
    if outcome == "Win":
        return "bg-success"
    elif outcome == "Loss":
        return "bg-danger"
    else:
        return "bg-secondary"

def calculate_outcome_with_class(game: Dict, username: str) -> Tuple[str, str]:
    """
    Calculate both outcome and CSS class in one call
    
    Args:
        game: Raw game dictionary from Chess.com API
        username: The username we're analyzing for
        
    Returns:
        Tuple of (outcome, css_class)
    """
    outcome = calculate_outcome(game, username)
    css_class = get_outcome_class(outcome)
    return outcome, css_class 