import requests
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from chessdotcom import get_player_game_archives, get_player_games_by_month

def fetch_chess_com_games(username, limit=100):
    """
    Fetch the last N games from Chess.com API for a given username
    """
    # Normalize username to lowercase
    username = username.strip().lower()
    
    try:
        # Get player's game archives using chessdotcom library
        archives_response = get_player_game_archives(username)
        archives = archives_response.json['archives']
        
        if not archives:
            return {'error': 'No game archives found for this player'}
        
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
        
        return {'games': all_games[:limit]}
        
    except Exception as e:
        # chessdotcom library handles most errors, but we'll catch any remaining ones
        error_msg = str(e)
        if '404' in error_msg or 'not found' in error_msg.lower():
            return {'error': f'Username "{username}" not found on Chess.com'}
        elif '403' in error_msg or 'forbidden' in error_msg.lower():
            return {'error': f'Username "{username}" not found or account is private. Please check the username and ensure the account is public.'}
        elif '429' in error_msg or 'rate limit' in error_msg.lower():
            return {'error': 'Rate limit exceeded. Please try again in a few minutes.'}
        else:
            return {'error': f'Error fetching games: {error_msg}'}

def home(request):
    """Home page with form to enter username"""
    return render(request, 'core/home.html')

@csrf_exempt
def fetch_games(request):
    """API endpoint to fetch games for a given username"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            
            if not username:
                return JsonResponse({'error': 'Username is required'}, status=400)
            
            # Normalize username to lowercase
            username = username.strip().lower()
            
            print(f"Fetching games for username: {username}")  # Debug print
            
            # Fetch games from Chess.com
            result = fetch_chess_com_games(username, limit=100)
            
            if 'error' in result:
                print(f"Error fetching games: {result['error']}")  # Debug print
                return JsonResponse(result, status=400)
            
            print(f"Successfully fetched {len(result['games'])} games")  # Debug print
            return JsonResponse(result)
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")  # Debug print
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            print(f"Unexpected error: {e}")  # Debug print
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'POST method required'}, status=405)

def games_list(request):
    """Display list of fetched games"""
    username = request.GET.get('username')
    if username:
        result = fetch_chess_com_games(username, limit=100)
        if 'error' in result:
            return render(request, 'core/games_list.html', {'error': result['error']})
        return render(request, 'core/games_list.html', {'games': result['games']})
    return render(request, 'core/games_list.html', {'games': []})

def test_api(request):
    """Test endpoint to verify Chess.com API is working"""
    try:
        # Test with a known public account
        result = fetch_chess_com_games('Hikaru', limit=5)
        if 'error' in result:
            return JsonResponse({'status': 'error', 'message': result['error']})
        else:
            return JsonResponse({
                'status': 'success', 
                'message': f'API working! Found {len(result["games"])} games for Hikaru',
                'sample_game': result['games'][0] if result['games'] else None
            })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
