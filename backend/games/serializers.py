from rest_framework import serializers

from .models import Game, Round


class RoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Round
        fields = ['round_number', 'player1_choice', 'player2_choice', 'winner', 'created_at']


class GameSerializer(serializers.ModelSerializer):
    """Full game representation, including rounds. Used to create and retrieve games."""

    rounds = RoundSerializer(many=True, read_only=True)

    class Meta:
        model = Game
        fields = [
            'id',
            'player1_name',
            'player2_name',
            'player1_score',
            'player2_score',
            'ties',
            'status',
            'winner',
            'created_at',
            'completed_at',
            'rounds',
        ]
        read_only_fields = [
            'id',
            'player1_score',
            'player2_score',
            'ties',
            'status',
            'winner',
            'created_at',
            'completed_at',
        ]

    def validate_player1_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('This field may not be blank.')
        return value

    def validate_player2_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('This field may not be blank.')
        return value


class GameListSerializer(serializers.ModelSerializer):
    """Lightweight game summary used for the games list / history endpoint."""

    class Meta:
        model = Game
        fields = [
            'id',
            'player1_name',
            'player2_name',
            'player1_score',
            'player2_score',
            'ties',
            'status',
            'winner',
            'created_at',
            'completed_at',
        ]


class PlayRoundSerializer(serializers.Serializer):
    """Validates the shape of a play-round request.

    Game rules (valid choices, round sequencing, winner calculation) are
    enforced by games.services.play_round, not here.
    """

    round_number = serializers.IntegerField(min_value=1)
    player1_choice = serializers.CharField(max_length=10)
    player2_choice = serializers.CharField(max_length=10)
