import chess
import chess.engine
from django.conf import settings

board = chess.Board()
with chess.engine.SimpleEngine.popen_uci(settings.STOCKFISH_PATH) as eng:
    info = eng.analyse(board, chess.engine.Limit(depth=10))
    print("Initial position evaluation:", info["score"])
