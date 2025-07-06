import unittest
from unittest.mock import Mock, patch
from ..services.engine import _analyse_fen, analyse_pgn, get_engine_info

class TestEngineService(unittest.TestCase):
    
    def setUp(self):
        self.sample_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        self.sample_pgn = """[Event "Test Game"]
[Site "Test Site"]
[Date "2024.01.01"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. d3 d6 5. Nc3 Nf6 6. Bg5 h6 7. Bh4 g5 8. Bg3 Nh5 9. Nxe5 Nxe5 10. d4 Bxd4 11. Qxd4 Nc6 12. Qh4 Nf6 13. Bxf7+ Rxf7 14. Qxf6 Qe7 15. Qxe7+ Nxe7 16. Nxd6 cxd6 17. Rfe1 Be6 18. Rxe6 Nc6 19. Rae1 Rf8 20. Rxc6 bxc6 21. Rxe7 1-0"""
    
    @patch('core.services.engine.ENGINE')
    def test_analyse_fen_success(self, mock_engine):
        """Test successful FEN analysis"""
        mock_engine.set_fen_position.return_value = None
        mock_engine.get_top_moves.return_value = [
            {'Move': 'e4', 'Centipawn': 34},
            {'Move': 'd4', 'Centipawn': 12}
        ]
        mock_engine.get_evaluation.return_value = {'type': 'cp', 'value': 34}
        
        result = _analyse_fen(self.sample_fen)
        
        self.assertEqual(result['eval']['type'], 'cp')
        self.assertEqual(result['eval']['value'], 34)
        self.assertEqual(len(result['lines']), 2)
        self.assertEqual(result['lines'][0]['Move'], 'e4')
    
    @patch('core.services.engine.ENGINE')
    def test_analyse_fen_engine_error(self, mock_engine):
        """Test FEN analysis when engine fails"""
        mock_engine.set_fen_position.side_effect = Exception("Engine error")
        
        result = _analyse_fen(self.sample_fen)
        
        self.assertEqual(result['eval']['type'], 'cp')
        self.assertEqual(result['eval']['value'], 0)
        self.assertEqual(result['lines'], [])
    
    @patch('core.services.engine.ENGINE')
    def test_analyse_pgn_success(self, mock_engine):
        """Test successful PGN analysis"""
        mock_engine.set_fen_position.return_value = None
        mock_engine.get_top_moves.return_value = [
            {'Move': 'e4', 'Centipawn': 34}
        ]
        mock_engine.get_evaluation.return_value = {'type': 'cp', 'value': 34}
        
        result = analyse_pgn(self.sample_pgn)
        
        # Should have analysis for each position (initial + moves)
        self.assertGreater(len(result), 0)
        self.assertEqual(result[0]['eval']['type'], 'cp')
        self.assertEqual(result[0]['eval']['value'], 34)
    
    def test_analyse_pgn_invalid_pgn(self):
        """Test PGN analysis with invalid PGN"""
        result = analyse_pgn("invalid pgn")
        self.assertEqual(result, [])
    
    @patch('core.services.engine.ENGINE')
    def test_get_engine_info_success(self, mock_engine):
        """Test getting engine info when engine is available"""
        mock_engine.depth = 18
        mock_engine.parameters = {'Threads': 2}
        
        result = get_engine_info()
        
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['name'], 'Stockfish')
        self.assertEqual(result['depth'], 18)
    
    @patch('core.services.engine.ENGINE', None)
    def test_get_engine_info_no_engine(self):
        """Test getting engine info when engine is not available"""
        result = get_engine_info()
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('Engine not available', result['message'])

if __name__ == '__main__':
    unittest.main() 