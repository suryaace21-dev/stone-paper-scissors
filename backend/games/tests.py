from unittest import mock

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Game, Round
from .services import InvalidRoundError, determine_round_winner, play_round


class GameModelTests(TestCase):
    def test_game_can_be_created(self):
        game = Game.objects.create(player1_name='Alice', player2_name='Bob')

        self.assertEqual(game.status, Game.Status.IN_PROGRESS)
        self.assertIsNone(game.winner)
        self.assertEqual(game.player1_score, 0)
        self.assertEqual(game.player2_score, 0)
        self.assertEqual(game.ties, 0)


class RoundModelTests(TestCase):
    def setUp(self):
        self.game = Game.objects.create(player1_name='Alice', player2_name='Bob')

    def test_round_can_be_created_for_a_game(self):
        round_ = Round.objects.create(
            game=self.game,
            round_number=1,
            player1_choice=Round.Choice.STONE,
            player2_choice=Round.Choice.SCISSORS,
            winner=Round.RoundWinner.PLAYER1,
        )

        self.assertEqual(round_.game, self.game)

    def test_game_rounds_relationship(self):
        Round.objects.create(
            game=self.game,
            round_number=1,
            player1_choice=Round.Choice.STONE,
            player2_choice=Round.Choice.SCISSORS,
            winner=Round.RoundWinner.PLAYER1,
        )
        Round.objects.create(
            game=self.game,
            round_number=2,
            player1_choice=Round.Choice.PAPER,
            player2_choice=Round.Choice.PAPER,
            winner=Round.RoundWinner.TIE,
        )

        self.assertEqual(self.game.rounds.count(), 2)

    def test_duplicate_round_number_for_same_game_is_rejected(self):
        Round.objects.create(
            game=self.game,
            round_number=1,
            player1_choice=Round.Choice.STONE,
            player2_choice=Round.Choice.SCISSORS,
            winner=Round.RoundWinner.PLAYER1,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Round.objects.create(
                    game=self.game,
                    round_number=1,
                    player1_choice=Round.Choice.PAPER,
                    player2_choice=Round.Choice.PAPER,
                    winner=Round.RoundWinner.TIE,
                )

    def test_different_games_can_both_have_round_number_one(self):
        other_game = Game.objects.create(player1_name='Carol', player2_name='Dave')

        Round.objects.create(
            game=self.game,
            round_number=1,
            player1_choice=Round.Choice.STONE,
            player2_choice=Round.Choice.SCISSORS,
            winner=Round.RoundWinner.PLAYER1,
        )
        Round.objects.create(
            game=other_game,
            round_number=1,
            player1_choice=Round.Choice.PAPER,
            player2_choice=Round.Choice.STONE,
            winner=Round.RoundWinner.PLAYER1,
        )

        self.assertEqual(Round.objects.filter(round_number=1).count(), 2)

    def test_invalid_choice_value_is_rejected_by_model_validation(self):
        round_ = Round(
            game=self.game,
            round_number=1,
            player1_choice='LIZARD',
            player2_choice=Round.Choice.SCISSORS,
            winner=Round.RoundWinner.PLAYER1,
        )

        with self.assertRaises(Exception):
            round_.full_clean()

    def test_round_number_must_be_positive(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Round.objects.create(
                    game=self.game,
                    round_number=0,
                    player1_choice=Round.Choice.STONE,
                    player2_choice=Round.Choice.SCISSORS,
                    winner=Round.RoundWinner.PLAYER1,
                )


class DetermineRoundWinnerTests(TestCase):
    """Pure win/lose/tie logic, independent of the database."""

    def test_stone_vs_scissors_player1_wins(self):
        winner = determine_round_winner(Round.Choice.STONE, Round.Choice.SCISSORS)
        self.assertEqual(winner, Round.RoundWinner.PLAYER1)

    def test_scissors_vs_stone_player2_wins(self):
        winner = determine_round_winner(Round.Choice.SCISSORS, Round.Choice.STONE)
        self.assertEqual(winner, Round.RoundWinner.PLAYER2)

    def test_paper_vs_stone_player1_wins(self):
        winner = determine_round_winner(Round.Choice.PAPER, Round.Choice.STONE)
        self.assertEqual(winner, Round.RoundWinner.PLAYER1)

    def test_stone_vs_paper_player2_wins(self):
        winner = determine_round_winner(Round.Choice.STONE, Round.Choice.PAPER)
        self.assertEqual(winner, Round.RoundWinner.PLAYER2)

    def test_scissors_vs_paper_player1_wins(self):
        winner = determine_round_winner(Round.Choice.SCISSORS, Round.Choice.PAPER)
        self.assertEqual(winner, Round.RoundWinner.PLAYER1)

    def test_paper_vs_scissors_player2_wins(self):
        winner = determine_round_winner(Round.Choice.PAPER, Round.Choice.SCISSORS)
        self.assertEqual(winner, Round.RoundWinner.PLAYER2)

    def test_same_choice_is_a_tie(self):
        for choice in Round.Choice.values:
            self.assertEqual(determine_round_winner(choice, choice), Round.RoundWinner.TIE)


class PlayRoundServiceTests(TestCase):
    """Behaviour of the play_round service function, which owns all game state changes."""

    def setUp(self):
        self.game = Game.objects.create(player1_name='Alice', player2_name='Bob')

    def _play_rounds(self, game, choice_pairs, start=1):
        """Play a sequence of (player1_choice, player2_choice) rounds in order."""
        for offset, (p1_choice, p2_choice) in enumerate(choice_pairs):
            play_round(game, start + offset, p1_choice, p2_choice)

    def test_scores_update_correctly_after_each_round(self):
        play_round(self.game, 1, Round.Choice.STONE, Round.Choice.SCISSORS)
        self.game.refresh_from_db()
        self.assertEqual(self.game.player1_score, 1)
        self.assertEqual(self.game.player2_score, 0)

        play_round(self.game, 2, Round.Choice.SCISSORS, Round.Choice.STONE)
        self.game.refresh_from_db()
        self.assertEqual(self.game.player1_score, 1)
        self.assertEqual(self.game.player2_score, 1)

    def test_tie_count_updates_correctly(self):
        play_round(self.game, 1, Round.Choice.STONE, Round.Choice.STONE)
        self.game.refresh_from_db()
        self.assertEqual(self.game.ties, 1)

        play_round(self.game, 2, Round.Choice.PAPER, Round.Choice.PAPER)
        self.game.refresh_from_db()
        self.assertEqual(self.game.ties, 2)

    def test_round_numbers_proceed_from_1_to_6(self):
        self._play_rounds(
            self.game,
            [(Round.Choice.STONE, Round.Choice.SCISSORS)] * 6,
        )
        round_numbers = list(
            self.game.rounds.order_by('round_number').values_list('round_number', flat=True)
        )
        self.assertEqual(round_numbers, [1, 2, 3, 4, 5, 6])

    def test_game_remains_in_progress_before_round_6(self):
        self._play_rounds(
            self.game,
            [(Round.Choice.STONE, Round.Choice.SCISSORS)] * 5,
        )
        self.game.refresh_from_db()
        self.assertEqual(self.game.status, Game.Status.IN_PROGRESS)
        self.assertIsNone(self.game.winner)

    def test_game_becomes_completed_after_round_6(self):
        self._play_rounds(
            self.game,
            [(Round.Choice.STONE, Round.Choice.SCISSORS)] * 6,
        )
        self.game.refresh_from_db()
        self.assertEqual(self.game.status, Game.Status.COMPLETED)

    def test_final_winner_is_player1_when_player1_has_higher_score(self):
        self._play_rounds(
            self.game,
            [(Round.Choice.STONE, Round.Choice.SCISSORS)] * 6,
        )
        self.game.refresh_from_db()
        self.assertEqual(self.game.winner, Game.Winner.PLAYER1)

    def test_final_winner_is_player2_when_player2_has_higher_score(self):
        self._play_rounds(
            self.game,
            [(Round.Choice.SCISSORS, Round.Choice.STONE)] * 6,
        )
        self.game.refresh_from_db()
        self.assertEqual(self.game.winner, Game.Winner.PLAYER2)

    def test_final_winner_is_tie_when_scores_are_equal(self):
        self._play_rounds(
            self.game,
            [
                (Round.Choice.STONE, Round.Choice.SCISSORS),   # player 1 wins
                (Round.Choice.SCISSORS, Round.Choice.STONE),   # player 2 wins
                (Round.Choice.STONE, Round.Choice.SCISSORS),   # player 1 wins
                (Round.Choice.SCISSORS, Round.Choice.STONE),   # player 2 wins
                (Round.Choice.STONE, Round.Choice.SCISSORS),   # player 1 wins
                (Round.Choice.SCISSORS, Round.Choice.STONE),   # player 2 wins
            ],
        )
        self.game.refresh_from_db()
        self.assertEqual(self.game.player1_score, self.game.player2_score)
        self.assertEqual(self.game.winner, Game.Winner.TIE)

    def test_completed_at_set_after_round_6(self):
        self._play_rounds(
            self.game,
            [(Round.Choice.STONE, Round.Choice.SCISSORS)] * 6,
        )
        self.game.refresh_from_db()
        self.assertIsNotNone(self.game.completed_at)

    def test_completed_at_remains_null_before_round_6(self):
        self._play_rounds(
            self.game,
            [(Round.Choice.STONE, Round.Choice.SCISSORS)] * 5,
        )
        self.game.refresh_from_db()
        self.assertIsNone(self.game.completed_at)

    def test_seventh_round_is_rejected(self):
        self._play_rounds(
            self.game,
            [(Round.Choice.STONE, Round.Choice.SCISSORS)] * 6,
        )

        with self.assertRaises(InvalidRoundError):
            play_round(self.game, 7, Round.Choice.STONE, Round.Choice.SCISSORS)

    def test_adding_round_to_completed_game_is_rejected(self):
        self._play_rounds(
            self.game,
            [(Round.Choice.STONE, Round.Choice.SCISSORS)] * 6,
        )

        with self.assertRaises(InvalidRoundError):
            play_round(self.game, 1, Round.Choice.PAPER, Round.Choice.STONE)

    def test_invalid_choice_is_rejected_by_service(self):
        with self.assertRaises(InvalidRoundError):
            play_round(self.game, 1, 'LIZARD', Round.Choice.SCISSORS)

    def test_state_remains_consistent_if_round_creation_fails(self):
        with self.assertRaises(InvalidRoundError):
            play_round(self.game, 1, 'LIZARD', Round.Choice.SCISSORS)

        self.game.refresh_from_db()
        self.assertEqual(self.game.rounds.count(), 0)
        self.assertEqual(self.game.player1_score, 0)
        self.assertEqual(self.game.player2_score, 0)
        self.assertEqual(self.game.ties, 0)
        self.assertEqual(self.game.status, Game.Status.IN_PROGRESS)


class GameAPITests(APITestCase):
    """End-to-end tests for the REST API, exercised through Django's test client."""

    def _play_round(self, game_id, round_number, player1_choice, player2_choice):
        return self.client.post(
            reverse('game-play-round', args=[game_id]),
            {
                'round_number': round_number,
                'player1_choice': player1_choice,
                'player2_choice': player2_choice,
            },
            format='json',
        )

    def test_create_game_successfully(self):
        response = self.client.post(
            reverse('game-list-create'),
            {'player1_name': 'Alice', 'player2_name': 'Bob'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['player1_name'], 'Alice')
        self.assertEqual(response.data['player2_name'], 'Bob')
        self.assertEqual(response.data['player1_score'], 0)
        self.assertEqual(response.data['player2_score'], 0)
        self.assertEqual(response.data['ties'], 0)
        self.assertEqual(response.data['status'], Game.Status.IN_PROGRESS)
        self.assertIsNone(response.data['winner'])
        self.assertIsNone(response.data['completed_at'])
        self.assertEqual(response.data['rounds'], [])

    def test_create_game_missing_player1_name_is_rejected(self):
        response = self.client.post(
            reverse('game-list-create'), {'player2_name': 'Bob'}, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('player1_name', response.data)

    def test_create_game_missing_player2_name_is_rejected(self):
        response = self.client.post(
            reverse('game-list-create'), {'player1_name': 'Alice'}, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('player2_name', response.data)

    def test_create_game_blank_player_names_are_rejected(self):
        response = self.client.post(
            reverse('game-list-create'),
            {'player1_name': '   ', 'player2_name': ''},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('player1_name', response.data)
        self.assertIn('player2_name', response.data)

    def test_list_games_returns_newest_first(self):
        Game.objects.create(player1_name='Alice', player2_name='Bob')
        Game.objects.create(player1_name='Carol', player2_name='Dave')

        response = self.client.get(reverse('game-list-create'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['player1_name'], 'Carol')
        self.assertEqual(response.data[1]['player1_name'], 'Alice')

    def test_retrieve_existing_game(self):
        game = Game.objects.create(player1_name='Alice', player2_name='Bob')

        response = self.client.get(reverse('game-detail', args=[game.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], game.id)
        self.assertEqual(response.data['rounds'], [])

    def test_retrieve_nonexistent_game_returns_404(self):
        response = self.client.get(reverse('game-detail', args=[999999]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_play_round_successfully(self):
        game = Game.objects.create(player1_name='Alice', player2_name='Bob')

        response = self._play_round(game.id, 1, 'STONE', 'SCISSORS')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['round']['round_number'], 1)
        self.assertEqual(response.data['round']['winner'], Round.RoundWinner.PLAYER1)

    def test_round_is_saved(self):
        game = Game.objects.create(player1_name='Alice', player2_name='Bob')

        self._play_round(game.id, 1, 'STONE', 'SCISSORS')

        self.assertEqual(game.rounds.count(), 1)

    def test_play_round_updates_score(self):
        game = Game.objects.create(player1_name='Alice', player2_name='Bob')

        response = self._play_round(game.id, 1, 'SCISSORS', 'STONE')

        self.assertEqual(response.data['game']['player1_score'], 0)
        self.assertEqual(response.data['game']['player2_score'], 1)

    def test_play_round_updates_tie_count(self):
        game = Game.objects.create(player1_name='Alice', player2_name='Bob')

        response = self._play_round(game.id, 1, 'PAPER', 'PAPER')

        self.assertEqual(response.data['game']['ties'], 1)

    def test_round_winner_is_returned_in_response(self):
        game = Game.objects.create(player1_name='Alice', player2_name='Bob')

        response = self._play_round(game.id, 1, 'PAPER', 'STONE')

        self.assertEqual(response.data['round']['winner'], Round.RoundWinner.PLAYER1)

    def test_playing_all_six_rounds_completes_the_game(self):
        game = Game.objects.create(player1_name='Alice', player2_name='Bob')

        response = None
        for round_number in range(1, 7):
            response = self._play_round(game.id, round_number, 'STONE', 'SCISSORS')

        self.assertEqual(response.data['game']['status'], Game.Status.COMPLETED)

    def test_final_winner_is_returned_after_round_six(self):
        game = Game.objects.create(player1_name='Alice', player2_name='Bob')

        response = None
        for round_number in range(1, 7):
            response = self._play_round(game.id, round_number, 'STONE', 'SCISSORS')

        self.assertEqual(response.data['game']['winner'], Game.Winner.PLAYER1)

    def test_seventh_round_is_rejected(self):
        game = Game.objects.create(player1_name='Alice', player2_name='Bob')
        for round_number in range(1, 7):
            self._play_round(game.id, round_number, 'STONE', 'SCISSORS')

        response = self._play_round(game.id, 7, 'STONE', 'SCISSORS')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)

    def test_round_out_of_sequence_is_rejected(self):
        game = Game.objects.create(player1_name='Alice', player2_name='Bob')

        response = self._play_round(game.id, 2, 'STONE', 'SCISSORS')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)

    def test_round_on_completed_game_is_rejected(self):
        game = Game.objects.create(player1_name='Alice', player2_name='Bob')
        for round_number in range(1, 7):
            self._play_round(game.id, round_number, 'STONE', 'SCISSORS')

        response = self._play_round(game.id, 1, 'STONE', 'SCISSORS')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)

    def test_invalid_choice_is_rejected(self):
        game = Game.objects.create(player1_name='Alice', player2_name='Bob')

        response = self._play_round(game.id, 1, 'LIZARD', 'SCISSORS')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_view_delegates_to_service_layer(self):
        """The view must call games.services.play_round rather than
        recomputing Stone/Paper/Scissors rules itself."""
        game = Game.objects.create(player1_name='Alice', player2_name='Bob')

        with mock.patch('games.views.play_round', wraps=play_round) as mocked_play_round:
            self._play_round(game.id, 1, 'STONE', 'SCISSORS')

        mocked_play_round.assert_called_once_with(
            game, round_number=1, player1_choice='STONE', player2_choice='SCISSORS'
        )
