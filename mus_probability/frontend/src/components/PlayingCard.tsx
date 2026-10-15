import type { CardSpec } from "../types";
import { RANK_NAMES } from "../types";
import { SuitIcon } from "./SuitIcon";

interface Props {
  card: CardSpec;
  selected?: boolean;
  disabled?: boolean;
  onClick?: () => void;
  size?: "sm" | "md" | "lg";
}

const RANK_LABEL: Record<number, string> = {
  1: "1",
  2: "2",
  3: "3",
  4: "4",
  5: "5",
  6: "6",
  7: "7",
  10: "S",  // Sota
  11: "C",  // Caballo
  12: "R",  // Rey
};

export function PlayingCard({ card, selected, disabled, onClick, size = "md" }: Props) {
  const iconSize = size === "sm" ? 18 : size === "lg" ? 40 : 28;
  const cls = [
    "playing-card",
    `playing-card--${size}`,
    selected && "playing-card--selected",
    disabled && "playing-card--disabled",
    onClick && "playing-card--clickable",
  ]
    .filter(Boolean)
    .join(" ");

  const title = `${RANK_NAMES[card.rank]} de ${card.suit}`;

  return (
    <button
      type="button"
      className={cls}
      onClick={disabled ? undefined : onClick}
      disabled={disabled && !selected}
      title={title}
      aria-pressed={selected}
    >
      <span className="playing-card__rank">{RANK_LABEL[card.rank]}</span>
      <span className="playing-card__suit">
        <SuitIcon suit={card.suit} size={iconSize} />
      </span>
    </button>
  );
}
