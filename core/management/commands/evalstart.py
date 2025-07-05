import chess
import chess.engine
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Evaluate the starting position using Stockfish engine'

    def add_arguments(self, parser):
        parser.add_argument(
            '--depth',
            type=int,
            default=10,
            help='Search depth for Stockfish (default: 10)'
        )

    def handle(self, *args, **options):
        depth = options['depth']
        
        # Check if Stockfish path is configured
        stockfish_path = getattr(settings, 'STOCKFISH_PATH', None)
        if not stockfish_path:
            self.stdout.write(
                self.style.ERROR('STOCKFISH_PATH not configured in settings')
            )
            return
        
        # Check if Stockfish executable exists
        if not os.path.exists(stockfish_path):
            self.stdout.write(
                self.style.ERROR(f'Stockfish not found at: {stockfish_path}')
            )
            return
        
        try:
            # Create board and engine
            board = chess.Board()
            
            self.stdout.write(f'Evaluating starting position with depth {depth}...')
            
            with chess.engine.SimpleEngine.popen_uci(stockfish_path) as engine:
                info = engine.analyse(board, chess.engine.Limit(depth=depth))
                score = info["score"]
                
                # Format the score
                if score.is_mate():
                    if score.mate() > 0:
                        result = f"Mate in {score.mate()}"
                    else:
                        result = f"Mate in {abs(score.mate())}"
                else:
                    cp_score = score.score() / 100.0  # Convert centipawns to pawns
                    result = f"{cp_score:+.2f} pawns"
                
                self.stdout.write(
                    self.style.SUCCESS(f'Initial position evaluation: {result}')
                )
                
                # Show additional info
                if 'pv' in info:
                    pv_moves = [board.san(move) for move in info['pv'][:5]]
                    self.stdout.write(f'Best moves: {" ".join(pv_moves)}')
                
        except Exception as e:
            raise CommandError(f'Engine evaluation failed: {str(e)}') 