import requests
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

def fetch_chess_com_games(username, limit=100):
    """
    Fetch the last N games from Chess.com API for a given username
    """
    try:
        # Get player's game archives (monthly archives)
        archives_url = f"https://api.chess.com/pub/player/{username}/games/archives"
        archives_response = requests.get(archives_url)
        archives_response.raise_for_status()
        
        archives_data = archives_response.json()
        archives = archives_data.get('archives', [])
        
        if not archives:
            return {'error': 'No game archives found for this player'}
        
        # Get games from the most recent archives until we have enough games
        all_games = []
        for archive_url in reversed(archives):  # Start with most recent
            if len(all_games) >= limit:
                break
                
            games_response = requests.get(archive_url)
            games_response.raise_for_status()
            
            games_data = games_response.json()
            games = games_data.get('games', [])
            
            for game in games:
                if len(all_games) >= limit:
                    break
                all_games.append(game)
        
        return {'games': all_games[:limit]}
        
    except requests.exceptions.RequestException as e:
        return {'error': f'Failed to fetch games: {str(e)}'}
    except json.JSONDecodeError as e:
        return {'error': f'Invalid JSON response: {str(e)}'}
    except Exception as e:
        return {'error': f'Unexpected error: {str(e)}'}

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
            
            # Fetch games from Chess.com
            result = fetch_chess_com_games(username, limit=100)
            
            if 'error' in result:
                return JsonResponse(result, status=400)
            
            return JsonResponse(result)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'POST method required'}, status=405)

def games_list(request):
    """Display list of fetched games"""
    return render(request, 'core/games_list.html')
