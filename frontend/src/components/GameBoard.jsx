import { useState } from 'react'
import ChoiceButton from './ChoiceButton'
import FinalResult from './FinalResult'
import RoundResult from './RoundResult'
import ScoreBoard from './ScoreBoard'

const CHOICES = ['STONE', 'PAPER', 'SCISSORS']

function GameBoard({
  game,
  onPlayRound,
  playingRound,
  roundError,
  lastRound,
  onDismissLastRound,
  onPlayAgain,
  onViewHistory,
}) {
  const [player1Choice, setPlayer1Choice] = useState(null)
  const [player2Choice, setPlayer2Choice] = useState(null)

  const isComplete = game.status === 'COMPLETED'
  const showingRoundResult = Boolean(lastRound) && !isComplete

  function handlePlayRound() {
    if (!player1Choice || !player2Choice || playingRound) {
      return
    }
    onPlayRound(player1Choice, player2Choice)
  }

  function handleNextRound() {
    setPlayer1Choice(null)
    setPlayer2Choice(null)
    onDismissLastRound()
  }

  if (isComplete) {
    return (
      <div className="card">
        <ScoreBoard game={game} />
        <FinalResult game={game} onPlayAgain={onPlayAgain} onViewHistory={onViewHistory} />
      </div>
    )
  }

  return (
    <div className="card">
      <ScoreBoard game={game} />

      {showingRoundResult ? (
        <RoundResult round={lastRound} game={game} onNextRound={handleNextRound} />
      ) : (
        <>
          <div className="players-choices">
            <div className="player-choice-panel">
              <h3>{game.player1_name}</h3>
              <div className="choice-grid">
                {CHOICES.map((choice) => (
                  <ChoiceButton
                    key={choice}
                    choice={choice}
                    selected={player1Choice === choice}
                    disabled={playingRound}
                    onSelect={setPlayer1Choice}
                  />
                ))}
              </div>
            </div>

            <div className="player-choice-panel">
              <h3>{game.player2_name}</h3>
              <div className="choice-grid">
                {CHOICES.map((choice) => (
                  <ChoiceButton
                    key={choice}
                    choice={choice}
                    selected={player2Choice === choice}
                    disabled={playingRound}
                    onSelect={setPlayer2Choice}
                  />
                ))}
              </div>
            </div>
          </div>

          {roundError && (
            <p className="field-error" role="alert">
              {roundError}
            </p>
          )}

          <button
            type="button"
            className="btn btn-primary"
            disabled={!player1Choice || !player2Choice || playingRound}
            onClick={handlePlayRound}
          >
            {playingRound ? 'Playing…' : 'Play Round'}
          </button>
        </>
      )}
    </div>
  )
}

export default GameBoard
