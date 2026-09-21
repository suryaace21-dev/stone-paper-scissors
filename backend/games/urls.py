from django.urls import path

from . import views

urlpatterns = [
    path('games/', views.GameListCreateView.as_view(), name='game-list-create'),
    path('games/<int:pk>/', views.GameDetailView.as_view(), name='game-detail'),
    path('games/<int:pk>/rounds/', views.PlayRoundView.as_view(), name='game-play-round'),
]
