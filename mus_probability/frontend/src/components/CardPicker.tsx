import type { CardSpec, Suit } from "../types";
import { RANKS, SUITS, SUIT_NAMES, cardKey } from "../types";
import { PlayingCard } from "./PlayingCard";

interface Props {
  selected: CardSpec[];
  onChange: (next: CardSpec[]) => void;
  max?: number;
}

export function CardPicker({ selected, onChange, max = 4 }: Props) {
  const selectedSet = new Set(selected.map(cardKey));

  const toggle = (c: CardSpec) => {
    const k = cardKey(c);
    if (selectedSet.has(k)) {
      onChange(selected.filter((x) => cardKey(x) !== k));
    } else if (selected.length < max) {
      onChange([...selected, c]);
    }
  };

  return (
    <div className="card-picker">
      {SUITS.map((suit: Suit) => (
        <div key={suit} className="card-picker__row">
          <div className="card-picker__row-label">{SUIT_NAMES[suit]}</div>
          <div className="card-picker__row-cards">
            {RANKS.map((rank) => {
              const c = { rank, suit };
              const isSelected = selectedSet.has(cardKey(c));
              const isFull = selected.length >= max && !isSelected;
              return (
                <PlayingCard
                  key={cardKey(c)}
                  card={c}
                  selected={isSelected}
                  disabled={isFull}
                  onClick={() => toggle(c)}
                  size="sm"
                />
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
