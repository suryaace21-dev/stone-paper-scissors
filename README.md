# Stone Paper Scissors

A full-stack, 2-player Stone Paper Scissors game built as a technical assessment.

Two players enter their names and play exactly six rounds. The backend is the single source of truth for game rules, scoring, round results, and the final winner. Completed and in-progress games are stored in PostgreSQL hosted on Amazon RDS.

## Overview

- Two players enter their names and play a 6-round match on one shared screen.
- Each round allows both players to choose stone, paper, or scissors.
- The backend determines the round winner, updates scores, tracks ties, and determines the final winner.
- The frontend does not calculate game results; it displays the data returned by the backend API.
- Game data is persisted in PostgreSQL on Amazon RDS.
- A game history page displays previous games.
- A game detail page displays the complete round-by-round results.

## Features

- Two-player Stone Paper Scissors game
- Exactly 6 rounds per game
- Backend-authoritative game rules and scoring
- Automatic final winner calculation
- Tie tracking
- Player name validation
- Duplicate round-submission protection
- Game history
- Detailed round-by-round game view
- REST API using Django REST Framework
- React state management using `useReducer`
- Friendly frontend error handling
- Responsive UI for desktop and mobile
- Production deployment on AWS EC2
- PostgreSQL hosted on Amazon RDS

## Game Rules

The game follows the standard Stone Paper Scissors rules:

- Stone beats Scissors
- Scissors beats Paper
- Paper beats Stone
- Same choice results in a tie

Each game consists of exactly six rounds.

After every round, the backend returns:

- Round winner
- Updated player scores
- Tie count
- Current round number
- Game status

After round six, the backend calculates and stores the final winner.

## Tech Stack

### Frontend

- React
- Vite
- JavaScript
- React `useReducer`
- Native `fetch`
- CSS

### Backend

- Python
- Django
- Django REST Framework
- Gunicorn

### Database

- PostgreSQL
- Amazon RDS for PostgreSQL

### AWS / Production

- Amazon EC2
- Amazon RDS
- Nginx
- Gunicorn
- Ubuntu Linux

## Architecture

```text
                         Internet
                            |
                            v
                    +---------------+
                    |   AWS EC2     |
                    | Ubuntu Linux  |
                    +---------------+
                            |
                            v
                    +---------------+
                    |     Nginx     |
                    +---------------+
                       |           |
                       |           |
                 React static     /api/
                    files           |
                       |            v
                       |     +-------------+
                       |     |  Gunicorn   |
                       |     +-------------+
                       |            |
                       |            v
                       |     +-------------+
                       |     |   Django    |
                       |     |     + DRF   |
                       |     +-------------+
                       |            |
                       |            v
                       |     +-------------+
                       +---->| Amazon RDS  |
                             | PostgreSQL  |
                             +-------------+