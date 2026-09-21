function winnerText(game) {
  if (game.winner === 'PLAYER1') return `${game.player1_name} wins the game!`
  if (game.winner === 'PLAYER2') return `${game.player2_name} wins the game!`
  return "It's a tie game!"
}

function FinalResult({ game, onPlayAgain, onViewHistory }) {
  return (
    <div className="final-result">
      <h2>Game Over</h2>
      <p className="final-result-winner">{winnerText(game)}</p>

      <div className="final-result-actions">
        <button type="button" className="btn btn-primary" onClick={onPlayAgain}>
          Play Again
        </button>
        <button type="button" className="btn btn-secondary" onClick={onViewHistory}>
          Game History
        </button>
      </div>
    </div>
  )
}

export default FinalResult
