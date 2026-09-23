// Manages the state of the currently active game (creating it, playing rounds,
// showing the last round's result). The Django API remains the source of
// truth for game rules/scores/winner - this reducer only tracks what the UI
// needs to render: the current game object, loading flags, and error text.

export const initialGameState = {
  game: null,
  creatingGame: false,
  startError: '',
  playingRound: false,
  roundError: '',
  lastRound: null,
}

export function gameReducer(state, action) {
  switch (action.type) {
    // A new game is being created.
    case 'START_GAME':
      return { ...state, creatingGame: true, startError: '' }

    case 'START_GAME_SUCCESS':
      return { ...initialGameState, game: action.game }

    case 'START_GAME_ERROR':
      return { ...state, creatingGame: false, startError: action.error }

    // Both choices were submitted for the current round.
    case 'CHOICE_SUBMITTED':
      return { ...state, playingRound: true, roundError: '' }

    // The backend accepted the round; this also carries game completion,
    // since a completed game is just game.status === 'COMPLETED' on the
    // same response - no separate "game completed" action is needed.
    case 'ROUND_COMPLETED':
      return { ...state, playingRound: false, game: action.game, lastRound: action.round }

    case 'ROUND_ERROR':
      return { ...state, playingRound: false, roundError: action.error }

    // The player dismissed the round result and moved on to the next round.
    case 'ROUND_RESULT_DISMISSED':
      return { ...state, lastRound: null }

    // Play Again: drop the finished game and go back to a clean slate.
    case 'RESET_GAME':
      return initialGameState

    default:
      return state
  }
}
