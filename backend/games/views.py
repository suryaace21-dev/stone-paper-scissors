from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Game
from .serializers import (
    GameListSerializer,
    GameSerializer,
    PlayRoundSerializer,
    RoundSerializer,
)
from .services import InvalidRoundError, play_round


class GameListCreateView(generics.ListCreateAPIView):
    """GET /api/games/  - list game summaries, newest first.
    POST /api/games/ - create a new game (player names only; everything else defaults).
    """

    queryset = Game.objects.all().order_by('-created_at')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return GameSerializer
        return GameListSerializer


class GameDetailView(generics.RetrieveAPIView):
    """GET /api/games/<id>/ - full game detail, including all rounds."""

    queryset = Game.objects.prefetch_related('rounds')
    serializer_class = GameSerializer


class PlayRoundView(APIView):
    """POST /api/games/<id>/rounds/ - play the next round via the game engine."""

    def post(self, request, pk):
        game = get_object_or_404(Game, pk=pk)

        request_serializer = PlayRoundSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        try:
            round_ = play_round(game, **request_serializer.validated_data)
        except InvalidRoundError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        game.refresh_from_db()
        return Response(
            {
                'round': RoundSerializer(round_).data,
                'game': GameSerializer(game).data,
            },
            status=status.HTTP_201_CREATED,
        )
