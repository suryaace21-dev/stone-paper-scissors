import { useCallback, useReducer, useState } from 'react'
import GameBoard from './components/GameBoard'
import GameDetail from './components/GameDetail'
import GameHistory from './components/GameHistory'
import StartGame from './components/StartGame'
import { gameReducer, initialGameState } from './gameReducer'
import { createGame, getGame, getGames, playRound } from './services/api'
import './App.css'

function App() {
  const [view, setView] = useState('start')

  const [gameState, dispatch] = useReducer(gameReducer, initialGameState)
  const { game, creatingGame, startError, playingRound, roundError, lastRound } = gameState

  const [historyGames, setHistoryGames] = useState([])
  const [historyLoading, setHistoryLoading] = useState(false)
  const [historyError, setHistoryError] = useState('')

  const [detailGame, setDetailGame] = useState(null)
  const [detailGameId, setDetailGameId] = useState(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [detailError, setDetailError] = useState('')

  async function handleStartGame(player1Name, player2Name) {
    dispatch({ type: 'START_GAME' })
    try {
      const newGame = await createGame(player1Name, player2Name)
      dispatch({ type: 'START_GAME_SUCCESS', game: newGame })
      setView('game')
    } catch (error) {
      dispatch({ type: 'START_GAME_ERROR', error: error.message })
    }
  }

  async function handlePlayRound(player1Choice, player2Choice) {
    if (!game || playingRound) {
      return
    }

    dispatch({ type: 'CHOICE_SUBMITTED' })
    try {
      const roundNumber = game.rounds.length + 1
      const result = await playRound(game.id, roundNumber, player1Choice, player2Choice)
      dispatch({ type: 'ROUND_COMPLETED', game: result.game, round: result.round })
    } catch (error) {
      dispatch({ type: 'ROUND_ERROR', error: error.message })
    }
  }

  function handleDismissLastRound() {
    dispatch({ type: 'ROUND_RESULT_DISMISSED' })
  }

  const loadHistory = useCallback(async () => {
    setHistoryLoading(true)
    setHistoryError('')
    try {
      const games = await getGames()
      setHistoryGames(games)
    } catch (error) {
      setHistoryError(error.message)
    } finally {
      setHistoryLoading(false)
    }
  }, [])

  function handleViewHistory() {
    setView('history')
    loadHistory()
  }

  const loadGameDetail = useCallback(async (gameId) => {
    setDetailLoading(true)
    setDetailError('')
    try {
      const detail = await getGame(gameId)
      setDetailGame(detail)
    } catch (error) {
      setDetailError(error.message)
    } finally {
      setDetailLoading(false)
    }
  }, [])

  function handleSelectHistoryGame(gameId) {
    setDetailGameId(gameId)
    setDetailGame(null)
    setDetailError('')
    setView('detail')
    loadGameDetail(gameId)
  }

  function handlePlayAgain() {
    dispatch({ type: 'RESET_GAME' })
    setView('start')
  }

  function handleBackToStart() {
    setView('start')
  }

  function handleBackToHistory() {
    setView('history')
    loadHistory()
  }

  return (
    <div className="app-shell">
      {view === 'start' && (
        <StartGame
          onStart={handleStartGame}
          submitting={creatingGame}
          submitError={startError}
          onViewHistory={handleViewHistory}
        />
      )}

      {view === 'game' && game && (
        <GameBoard
          game={game}
          onPlayRound={handlePlayRound}
          playingRound={playingRound}
          roundError={roundError}
          lastRound={lastRound}
          onDismissLastRound={handleDismissLastRound}
          onPlayAgain={handlePlayAgain}
          onViewHistory={handleViewHistory}
        />
      )}

      {view === 'history' && (
        <GameHistory
          games={historyGames}
          loading={historyLoading}
          error={historyError}
          onRetry={loadHistory}
          onSelectGame={handleSelectHistoryGame}
          onBack={handleBackToStart}
        />
      )}

      {view === 'detail' && (
        <GameDetail
          game={detailGame}
          loading={detailLoading}
          error={detailError}
          onRetry={() => loadGameDetail(detailGameId)}
          onBack={handleBackToHistory}
        />
      )}
    </div>
  )
}

export default App
