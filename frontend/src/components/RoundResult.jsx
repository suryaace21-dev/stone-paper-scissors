const CHOICE_EMOJI = { STONE: '🪨', PAPER: '📄', SCISSORS: '✂️' }

function winnerText(round, game) {
  if (round.winner === 'PLAYER1') return `${game.player1_name} wins the round!`
  if (round.winner === 'PLAYER2') return `${game.player2_name} wins the round!`
  return "It's a tie!"
}

function RoundResult({ round, game, onNextRound }) {
  return (
    <div className={`round-result result-${round.winner.toLowerCase()}`}>
      <p className="round-result-heading">Round {round.round_number} Result</p>

      <div className="round-result-choices">
        <span>
          {game.player1_name}: {CHOICE_EMOJI[round.player1_choice]} {round.player1_choice}
        </span>
        <span>
          {game.player2_name}: {CHOICE_EMOJI[round.player2_choice]} {round.player2_choice}
        </span>
      </div>

      <p className="round-result-winner">{winnerText(round, game)}</p>

      <button type="button" className="btn btn-primary" onClick={onNextRound}>
        Next Round
      </button>
    </div>
  )
}

export default RoundResult
