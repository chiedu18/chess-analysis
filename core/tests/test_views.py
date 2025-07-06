from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch, MagicMock
from datetime import datetime

class ViewsTestCase(TestCase):
    
    def test_home_view(self):
        """Test home view returns form"""
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Chess Analysis Tool')
        self.assertContains(response, 'id_username')
    
    @patch('core.views.player_games')
    @patch('core.views.player_profile')
    def test_games_list_view_success(self, mock_profile, mock_games):
        """Test games list view with successful data fetch"""
        # Mock profile
        mock_profile.return_value = {
            "username": "testuser",
            "title": "GM",
            "blitz_rating": 2500
        }
        
        # Mock games
        mock_games.return_value = [
            {
                "end_time": 1704067200,
                "white": {"username": "testuser", "rating": 1500, "result": "win"},
                "black": {"username": "opponent", "rating": 1400, "result": "resigned"},
                "time_class": "blitz",
                "pgn": "1. e4 e5 2. Nf3",
                "url": "https://chess.com/game/1"
            }
        ]
        
        response = self.client.get(reverse('core:games_list'), {'username': 'testuser'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
        self.assertContains(response, 'GM')
        self.assertContains(response, '2500')
        self.assertContains(response, 'Win')
    
    @patch('core.views.player_games')
    @patch('core.views.player_profile')
    def test_games_list_view_error(self, mock_profile, mock_games):
        """Test games list view with error"""
        # Mock profile
        mock_profile.return_value = {
            "username": "testuser",
            "title": None,
            "blitz_rating": None
        }
        
        # Mock games error
        mock_games.side_effect = ValueError("User not found")
        
        response = self.client.get(reverse('core:games_list'), {'username': 'testuser'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'User not found')
    
    def test_games_list_view_no_username(self):
        """Test games list view without username"""
        response = self.client.get(reverse('core:games_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No games found')
    
    @patch('core.views.player_games')
    def test_fetch_games_api_success(self, mock_games):
        """Test fetch games API endpoint success"""
        mock_games.return_value = [
            {
                "end_time": 1704067200,
                "white": {"username": "testuser", "rating": 1500, "result": "win"},
                "black": {"username": "opponent", "rating": 1400, "result": "resigned"},
                "time_class": "blitz",
                "pgn": "1. e4 e5 2. Nf3",
                "url": "https://chess.com/game/1"
            }
        ]
        
        response = self.client.post(
            reverse('core:fetch_games'),
            data='{"username": "testuser"}',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('games', data)
        self.assertEqual(len(data['games']), 1)
        self.assertEqual(data['games'][0]['outcome'], 'Win')
    
    @patch('core.views.player_games')
    def test_fetch_games_api_error(self, mock_games):
        """Test fetch games API endpoint with error"""
        mock_games.side_effect = ValueError("User not found")
        
        response = self.client.post(
            reverse('core:fetch_games'),
            data='{"username": "testuser"}',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'User not found')
    
    def test_fetch_games_api_no_username(self):
        """Test fetch games API endpoint without username"""
        response = self.client.post(
            reverse('core:fetch_games'),
            data='{}',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Username is required')
    
    @patch('core.views.player_games')
    def test_test_api_view_success(self, mock_games):
        """Test API test endpoint success"""
        mock_games.return_value = [
            {
                "end_time": 1704067200,
                "white": {"username": "Hikaru", "rating": 1500, "result": "win"},
                "black": {"username": "opponent", "rating": 1400, "result": "resigned"},
                "time_class": "blitz",
                "pgn": "1. e4 e5 2. Nf3",
                "url": "https://chess.com/game/1"
            }
        ]
        
        response = self.client.get(reverse('core:test_api'))
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('API working', data['message'])
    
    @patch('core.views.player_games')
    def test_test_api_view_error(self, mock_games):
        """Test API test endpoint with error"""
        mock_games.side_effect = Exception("API error")
        
        response = self.client.get(reverse('core:test_api'))
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertIn('API error', data['message']) 