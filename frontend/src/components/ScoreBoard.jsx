function ScoreBoard({ game }) {
  const currentRound = Math.min(game.rounds.length + 1, 6)
  const isComplete = game.status === 'COMPLETED'

  return (
    <div className="scoreboard">
      <div className="score">
        <span className="score-name">{game.player1_name}</span>
        <span className="score-value">{game.player1_score}</span>
      </div>
      <div className="score score-ties">
        <span className="score-name">Ties</span>
        <span className="score-value">{game.ties}</span>
      </div>
      <div className="score">
        <span className="score-name">{game.player2_name}</span>
        <span className="score-value">{game.player2_score}</span>
      </div>
      <div className="round-indicator">
        {isComplete ? 'Game Complete' : `Round ${currentRound} of 6`}
      </div>
    </div>
  )
}

export default ScoreBoard
