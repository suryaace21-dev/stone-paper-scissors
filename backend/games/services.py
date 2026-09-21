"""Game engine: the backend's single source of truth for Stone Paper Scissors rules."""
from django.db import transaction
from django.utils import timezone

from .models import Game, Round

TOTAL_ROUNDS = 6

# Maps each choice to the choice it beats.
BEATS = {
    Round.Choice.STONE: Round.Choice.SCISSORS,
    Round.Choice.SCISSORS: Round.Choice.PAPER,
    Round.Choice.PAPER: Round.Choice.STONE,
}


class InvalidRoundError(Exception):
    """Raised when a round cannot be played in the game's current state."""


def determine_round_winner(player1_choice, player2_choice):
    """Return the RoundWinner for two valid choices."""
    if player1_choice == player2_choice:
        return Round.RoundWinner.TIE
    if BEATS[player1_choice] == player2_choice:
        return Round.RoundWinner.PLAYER1
    return Round.RoundWinner.PLAYER2


def _determine_final_winner(game):
    """Return the Game.Winner implied by a game's current scores."""
    if game.player1_score > game.player2_score:
        return Game.Winner.PLAYER1
    if game.player2_score > game.player1_score:
        return Game.Winner.PLAYER2
    return Game.Winner.TIE


def _complete_game(game):
    """Mark a game finished and record its final winner."""
    game.status = Game.Status.COMPLETED
    game.completed_at = timezone.now()
    game.winner = _determine_final_winner(game)


@transaction.atomic
def play_round(game, round_number, player1_choice, player2_choice):
    """Record one round for a game, updating its score and, on round 6, completing it.

    Raises InvalidRoundError if the round cannot legally be played (game already
    completed, wrong round number, or an invalid choice), leaving the game and its
    rounds unchanged.
    """
    game = Game.objects.select_for_update().get(pk=game.pk)

    if game.status == Game.Status.COMPLETED:
        raise InvalidRoundError('Cannot add a round to a completed game.')

    if player1_choice not in Round.Choice.values or player2_choice not in Round.Choice.values:
        raise InvalidRoundError('Choices must be one of STONE, PAPER, SCISSORS.')

    expected_round_number = game.rounds.count() + 1
    if round_number != expected_round_number:
        raise InvalidRoundError(
            f'Expected round number {expected_round_number}, got {round_number}.'
        )

    winner = determine_round_winner(player1_choice, player2_choice)

    round_ = Round.objects.create(
        game=game,
        round_number=round_number,
        player1_choice=player1_choice,
        player2_choice=player2_choice,
        winner=winner,
    )

    if winner == Round.RoundWinner.PLAYER1:
        game.player1_score += 1
    elif winner == Round.RoundWinner.PLAYER2:
        game.player2_score += 1
    else:
        game.ties += 1

    if round_number == TOTAL_ROUNDS:
        _complete_game(game)

    game.save()
    return round_
