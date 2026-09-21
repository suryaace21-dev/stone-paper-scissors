const CHOICE_INFO = {
  STONE: { emoji: '🪨', label: 'Stone' },
  PAPER: { emoji: '📄', label: 'Paper' },
  SCISSORS: { emoji: '✂️', label: 'Scissors' },
}

function ChoiceButton({ choice, selected, disabled, onSelect }) {
  const { emoji, label } = CHOICE_INFO[choice]

  return (
    <button
      type="button"
      className={`choice-button${selected ? ' selected' : ''}`}
      aria-pressed={selected}
      disabled={disabled}
      onClick={() => onSelect(choice)}
    >
      <span className="choice-emoji" aria-hidden="true">
        {emoji}
      </span>
      <span className="choice-label">{label}</span>
    </button>
  )
}

export default ChoiceButton
