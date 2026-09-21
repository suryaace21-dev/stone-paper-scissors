from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import services
from .models import Game
from .serializers import GameListSerializer, GameSerializer, PlayRoundSerializer, RoundSerializer


@api_view(['GET', 'POST'])
def game_list_create(request):
    """GET /api/games/ - list game summaries, newest first.
    POST /api/games/ - create a new game from two player names.
    """
    if request.method == 'POST':
        serializer = GameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    games = Game.objects.all().order_by('-created_at')
    serializer = GameListSerializer(games, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def game_detail(request, game_id):
    """GET /api/games/<id>/ - full game detail, including all rounds."""
    game = get_object_or_404(Game.objects.prefetch_related('rounds'), pk=game_id)
    serializer = GameSerializer(game)
    return Response(serializer.data)


@api_view(['POST'])
def play_round(request, game_id):
    """POST /api/games/<id>/rounds/ - play the next round via the game engine."""
    game = get_object_or_404(Game, pk=game_id)

    request_serializer = PlayRoundSerializer(data=request.data)
    request_serializer.is_valid(raise_exception=True)

    try:
        round_ = services.play_round(game, **request_serializer.validated_data)
    except services.InvalidRoundError as exc:
        return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    game.refresh_from_db()
    return Response(
        {
            'round': RoundSerializer(round_).data,
            'game': GameSerializer(game).data,
        },
        status=status.HTTP_201_CREATED,
    )
