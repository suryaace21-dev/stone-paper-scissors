import { useState } from 'react'

function StartGame({ onStart, submitting, submitError, onViewHistory }) {
  const [player1Name, setPlayer1Name] = useState('')
  const [player2Name, setPlayer2Name] = useState('')
  const [validationError, setValidationError] = useState('')

  function handleSubmit(event) {
    event.preventDefault()

    const trimmed1 = player1Name.trim()
    const trimmed2 = player2Name.trim()

    if (!trimmed1 || !trimmed2) {
      setValidationError('Please enter a name for both players.')
      return
    }

    setValidationError('')
    onStart(trimmed1, trimmed2)
  }

  const errorMessage = validationError || submitError

  return (
    <div className="card">
      <h1 className="app-title">Stone Paper Scissors</h1>
      <p className="app-subtitle">Two players, six rounds, one winner.</p>

      <form className="start-form" onSubmit={handleSubmit} noValidate>
        <div className="form-field">
          <label htmlFor="player1Name">Player 1 Name</label>
          <input
            id="player1Name"
            type="text"
            value={player1Name}
            onChange={(event) => setPlayer1Name(event.target.value)}
            disabled={submitting}
            autoComplete="off"
            maxLength={100}
          />
        </div>

        <div className="form-field">
          <label htmlFor="player2Name">Player 2 Name</label>
          <input
            id="player2Name"
            type="text"
            value={player2Name}
            onChange={(event) => setPlayer2Name(event.target.value)}
            disabled={submitting}
            autoComplete="off"
            maxLength={100}
          />
        </div>

        {errorMessage && (
          <p className="field-error" role="alert">
            {errorMessage}
          </p>
        )}

        <button type="submit" className="btn btn-primary" disabled={submitting}>
          {submitting ? 'Starting…' : 'Start Game'}
        </button>
      </form>

      <button type="button" className="btn btn-link" onClick={onViewHistory}>
        Game History
      </button>
    </div>
  )
}

export default StartGame
