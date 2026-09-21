const STATUS_LABELS = { IN_PROGRESS: 'In progress', COMPLETED: 'Completed' }
const WINNER_LABELS = { PLAYER1: 'Player 1', PLAYER2: 'Player 2', TIE: 'Tie' }

function formatDateTime(isoString) {
  return new Date(isoString).toLocaleString()
}

function GameHistory({ games, loading, error, onRetry, onSelectGame, onBack }) {
  return (
    <div className="card card-wide">
      <div className="screen-header">
        <h2>Game History</h2>
        <button type="button" className="btn btn-secondary" onClick={onBack}>
          Back
        </button>
      </div>

      {loading && <p className="status-text">Loading history…</p>}

      {error && (
        <div className="error-banner" role="alert">
          <p>{error}</p>
          <button type="button" className="btn btn-secondary" onClick={onRetry}>
            Retry
          </button>
        </div>
      )}

      {!loading && !error && games.length === 0 && (
        <p className="status-text">No games have been played yet.</p>
      )}

      {!loading && !error && games.length > 0 && (
        <ul className="history-list">
          {games.map((game) => (
            <li key={game.id}>
              <button
                type="button"
                className="history-item"
                onClick={() => onSelectGame(game.id)}
              >
                <span className="history-players">
                  {game.player1_name} <strong>{game.player1_score}</strong> &ndash;{' '}
                  <strong>{game.player2_score}</strong> {game.player2_name}
                </span>
                <span className="history-meta">
                  Ties: {game.ties} &middot; {STATUS_LABELS[game.status] || game.status}
                  {game.winner ? ` · Winner: ${WINNER_LABELS[game.winner] || game.winner}` : ''}
                </span>
                <span className="history-date">{formatDateTime(game.created_at)}</span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

export default GameHistory
