from django.db import models


class Game(models.Model):
    """A single Stone Paper Scissors match between two named players."""

    class Status(models.TextChoices):
        IN_PROGRESS = 'IN_PROGRESS', 'In progress'
        COMPLETED = 'COMPLETED', 'Completed'

    class Winner(models.TextChoices):
        PLAYER1 = 'PLAYER1', 'Player 1'
        PLAYER2 = 'PLAYER2', 'Player 2'
        TIE = 'TIE', 'Tie'

    player1_name = models.CharField(max_length=100)
    player2_name = models.CharField(max_length=100)

    player1_score = models.PositiveSmallIntegerField(default=0)
    player2_score = models.PositiveSmallIntegerField(default=0)
    ties = models.PositiveSmallIntegerField(default=0)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IN_PROGRESS,
    )
    # Null until the game reaches its final round; can be PLAYER1, PLAYER2, or TIE.
    winner = models.CharField(
        max_length=10,
        choices=Winner.choices,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.player1_name} vs {self.player2_name} ({self.status})'


class Round(models.Model):
    """A single round of stone/paper/scissors within a Game."""

    class Choice(models.TextChoices):
        STONE = 'STONE', 'Stone'
        PAPER = 'PAPER', 'Paper'
        SCISSORS = 'SCISSORS', 'Scissors'

    class RoundWinner(models.TextChoices):
        PLAYER1 = 'PLAYER1', 'Player 1'
        PLAYER2 = 'PLAYER2', 'Player 2'
        TIE = 'TIE', 'Tie'

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='rounds')
    round_number = models.PositiveSmallIntegerField()

    player1_choice = models.CharField(max_length=10, choices=Choice.choices)
    player2_choice = models.CharField(max_length=10, choices=Choice.choices)
    winner = models.CharField(max_length=10, choices=RoundWinner.choices)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['round_number']
        constraints = [
            models.UniqueConstraint(
                fields=['game', 'round_number'],
                name='unique_round_number_per_game',
            ),
            models.CheckConstraint(
                condition=models.Q(round_number__gt=0),
                name='round_number_positive',
            ),
        ]

    def __str__(self):
        return f'Game #{self.game_id} - Round {self.round_number}'
