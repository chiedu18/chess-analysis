import io
import chess.pgn
import itertools
import json
import logging
from stockfish import Stockfish
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# Initialize Stockfish engine with optimized parameters
try:
    ENGINE = Stockfish(
        depth=18,  # tune depth vs. speed
        parameters={
            "Threads": 2,
            "MultiPV": 3  # ask for three lines
        }
    )
    logger.info("Stockfish engine initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Stockfish engine: {e}")
    ENGINE = None

def _analyse_fen(fen: str) -> dict:
    """
    Analyze a single FEN position
    
    Args:
        fen: FEN string representing the position
        
    Returns:
        Dict with evaluation and top moves
    """
    if not ENGINE:
        return {"eval": {"type": "cp", "value": 0}, "lines": []}
    
    try:
        ENGINE.set_fen_position(fen)
        info = ENGINE.get_top_moves(3)  # [{'Move': 'e4', 'Centipawn': 34, …}]
        score = ENGINE.get_evaluation()  # {'type': 'cp', 'value': 34}
        return {"eval": score, "lines": info}
    except Exception as e:
        logger.error(f"Error analyzing FEN {fen}: {e}")
        return {"eval": {"type": "cp", "value": 0}, "lines": []}

def analyse_pgn(pgn_text: str) -> List[Dict]:
    """
    Analyze a complete PGN game
    
    Args:
        pgn_text: PGN string of the game
        
    Returns:
        List of analysis results for each position
    """
    try:
        game = chess.pgn.read_game(io.StringIO(pgn_text))
        if not game:
            logger.error("Failed to parse PGN")
            return []
            
        board = game.board()
        analysis = []
        
        # Analyze initial position
        analysis.append(_analyse_fen(board.fen()))
        
        # Analyze after each move
        try:
            for move in game.mainline_moves():
                board.push(move)
                analysis.append(_analyse_fen(board.fen()))
        except Exception as move_error:
            logger.error(f"Error processing moves: {move_error}")
            # Return what we have so far
            pass
            
        logger.info(f"Analyzed {len(analysis)} positions")
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing PGN: {e}")
        return []

def get_engine_info() -> Dict:
    """
    Get engine information and status
    
    Returns:
        Dict with engine status and info
    """
    if not ENGINE:
        return {"status": "error", "message": "Engine not available"}
    
    try:
        return {
            "status": "ok",
            "name": "Stockfish",
            "depth": ENGINE.depth,
            "parameters": ENGINE.parameters
        }
    except Exception as e:
        return {"status": "error", "message": str(e)} 