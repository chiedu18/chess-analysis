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
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            return {'error': f'Username "{username}" not found or account is private. Please check the username and ensure the account is public.'}
        elif e.response.status_code == 404:
            return {'error': f'Username "{username}" not found on Chess.com'}
        elif e.response.status_code == 429:
            return {'error': 'Rate limit exceeded. Please try again in a few minutes.'}
        else:
            return {'error': f'HTTP Error {e.response.status_code}: {str(e)}'}
    except requests.exceptions.RequestException as e:
        return {'error': f'Network error: {str(e)}'}
    except json.JSONDecodeError as e:
        return {'error': f'Invalid response from Chess.com: {str(e)}'}
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
    return render(request, 'core/games_list.html')

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
