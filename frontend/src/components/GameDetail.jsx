const WINNER_LABELS = { PLAYER1: 'Player 1', PLAYER2: 'Player 2', TIE: 'Tie' }
const CHOICE_EMOJI = { STONE: '🪨', PAPER: '📄', SCISSORS: '✂️' }

function roundWinnerLabel(round, game) {
  if (round.winner === 'PLAYER1') return game.player1_name
  if (round.winner === 'PLAYER2') return game.player2_name
  return 'Tie'
}

function statusLabel(status) {
  return status === 'COMPLETED' ? 'Completed' : 'In progress'
}

function GameDetail({ game, loading, error, onRetry, onBack }) {
  return (
    <div className="card card-wide">
      <div className="screen-header">
        <h2>Game Detail</h2>
        <button type="button" className="btn btn-secondary" onClick={onBack}>
          Back to History
        </button>
      </div>

      {loading && <p className="status-text">Loading game…</p>}

      {error && (
        <div className="error-banner" role="alert">
          <p>{error}</p>
          <button type="button" className="btn btn-secondary" onClick={onRetry}>
            Retry
          </button>
        </div>
      )}

      {!loading && !error && game && (
        <>
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
          </div>

          <p className="status-text">
            Status: {statusLabel(game.status)}
            {game.winner ? ` · Winner: ${WINNER_LABELS[game.winner] || game.winner}` : ''}
          </p>

          <table className="rounds-table">
            <thead>
              <tr>
                <th>Round</th>
                <th>{game.player1_name}</th>
                <th>{game.player2_name}</th>
                <th>Winner</th>
              </tr>
            </thead>
            <tbody>
              {game.rounds.map((round) => (
                <tr key={round.round_number}>
                  <td>{round.round_number}</td>
                  <td>
                    {CHOICE_EMOJI[round.player1_choice]} {round.player1_choice}
                  </td>
                  <td>
                    {CHOICE_EMOJI[round.player2_choice]} {round.player2_choice}
                  </td>
                  <td>{roundWinnerLabel(round, game)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  )
}

export default GameDetail
