import json
from django.views.generic import TemplateView, View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import render

from .services.chesscom import player_profile, player_games
from .utils.transform import massage_games
from .forms import UsernameForm

class HomeView(TemplateView):
    """Home page with form to enter username"""
    template_name = "core/home.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = UsernameForm()
        return context

@method_decorator(csrf_exempt, name='dispatch')
class FetchGamesAPIView(View):
    """API endpoint to fetch games for a given username"""
    
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            
            if not username:
                return JsonResponse({'error': 'Username is required'}, status=400)
            
            # Normalize username to lowercase
            username = username.strip().lower()
            
            print(f"Fetching games for username: {username}")  # Debug print
            
            # Fetch games from Chess.com
            raw_games = player_games(username, limit=100)
            processed_games = massage_games(raw_games, username)
            
            print(f"Successfully fetched {len(processed_games)} games")  # Debug print
            return JsonResponse({'games': processed_games})
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")  # Debug print
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except ValueError as e:
            print(f"Value error: {e}")  # Debug print
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            print(f"Unexpected error: {e}")  # Debug print
            return JsonResponse({'error': str(e)}, status=500)

class GamesListView(TemplateView):
    """Display list of fetched games"""
    template_name = "core/games_list.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.request.GET.get('username')
        
        if username:
            try:
                # Fetch profile information
                profile = player_profile(username)
                
                # Fetch games
                raw_games = player_games(username, limit=100)
                processed_games = massage_games(raw_games, username)
                
                context.update({
                    'games': processed_games,
                    'profile': profile
                })
            except ValueError as e:
                context.update({
                    'error': str(e),
                    'profile': profile if 'profile' in locals() else None
                })
        else:
            context.update({
                'games': [],
                'profile': None
            })
        
        return context

class TestAPIView(View):
    """Test endpoint to verify Chess.com API is working"""
    
    def get(self, request, *args, **kwargs):
        try:
            # Test with a known public account
            raw_games = player_games('Hikaru', limit=5)
            processed_games = massage_games(raw_games, 'Hikaru')
            
            return JsonResponse({
                'status': 'success', 
                'message': f'API working! Found {len(processed_games)} games for Hikaru',
                'sample_game': processed_games[0] if processed_games else None
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
