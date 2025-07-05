from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('api/fetch-games/', views.fetch_games, name='fetch_games'),
    path('games/', views.games_list, name='games_list'),
] 