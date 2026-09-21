const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

if (!API_BASE_URL) {
  throw new Error(
    'VITE_API_BASE_URL is not set. Copy frontend/.env.example to .env and configure it.',
  )
}

export class ApiError extends Error {
  constructor(message, { status = null } = {}) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

function extractErrorMessage(data) {
  if (!data) {
    return null
  }
  if (typeof data.detail === 'string') {
    return data.detail
  }

  const fieldMessages = Object.entries(data)
    .filter(([, value]) => Array.isArray(value) || typeof value === 'string')
    .map(([field, value]) => `${field}: ${Array.isArray(value) ? value.join(' ') : value}`)

  return fieldMessages.length > 0 ? fieldMessages.join(' ') : null
}

async function request(path, options = {}) {
  let response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    })
  } catch {
    throw new ApiError(
      'Unable to reach the server. Check that the backend is running and try again.',
    )
  }

  const text = await response.text()
  let data = null
  if (text) {
    try {
      data = JSON.parse(text)
    } catch {
      data = null
    }
  }

  if (!response.ok) {
    const message = extractErrorMessage(data) || `Request failed (${response.status}). Please try again.`
    throw new ApiError(message, { status: response.status })
  }

  return data
}

export function createGame(player1Name, player2Name) {
  return request('/games/', {
    method: 'POST',
    body: JSON.stringify({ player1_name: player1Name, player2_name: player2Name }),
  })
}

export function getGames() {
  return request('/games/')
}

export function getGame(gameId) {
  return request(`/games/${gameId}/`)
}

export function playRound(gameId, roundNumber, player1Choice, player2Choice) {
  return request(`/games/${gameId}/rounds/`, {
    method: 'POST',
    body: JSON.stringify({
      round_number: roundNumber,
      player1_choice: player1Choice,
      player2_choice: player2Choice,
    }),
  })
}
