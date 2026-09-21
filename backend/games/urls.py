from django.urls import path

from . import views

urlpatterns = [
    path('games/', views.game_list_create, name='game-list-create'),
    path('games/<int:game_id>/', views.game_detail, name='game-detail'),
    path('games/<int:game_id>/rounds/', views.play_round, name='game-play-round'),
]
