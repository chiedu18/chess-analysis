from django.urls import path
from .views import HomeView, FetchGamesAPIView, GamesListView, TestAPIView

app_name = "core"
urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("api/fetch-games/", FetchGamesAPIView.as_view(), name="fetch_games"),
    path("games/", GamesListView.as_view(), name="games_list"),
    path("api/test/", TestAPIView.as_view(), name="test_api"),
] 