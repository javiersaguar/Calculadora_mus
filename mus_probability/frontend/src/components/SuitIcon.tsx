import type { Suit } from "../types";

interface Props {
  suit: Suit;
  size?: number;
}

const COLOR: Record<Suit, string> = {
  oros: "#d4a017",     // gold
  copas: "#b22222",    // copper red
  espadas: "#1e3a5f",  // steel blue
  bastos: "#5a3a1e",   // wood brown
};

export function SuitIcon({ suit, size = 24 }: Props) {
  const color = COLOR[suit];
  const s = size;
  switch (suit) {
    case "oros":
      return (
        <svg width={s} height={s} viewBox="0 0 24 24" aria-label="oros">
          <circle cx="12" cy="12" r="10" fill={color} stroke="#8a6e0f" strokeWidth="1.2" />
          <circle cx="12" cy="12" r="6" fill="none" stroke="#8a6e0f" strokeWidth="1" />
          <circle cx="12" cy="12" r="2" fill="#8a6e0f" />
        </svg>
      );
    case "copas":
      return (
        <svg width={s} height={s} viewBox="0 0 24 24" aria-label="copas">
          <path
            d="M5 4 H19 V8 Q19 14 12 15 Q5 14 5 8 Z"
            fill={color}
            stroke="#7a1414"
            strokeWidth="1"
          />
          <rect x="11" y="15" width="2" height="4" fill={color} />
          <rect x="8" y="19" width="8" height="2" rx="0.5" fill={color} />
        </svg>
      );
    case "espadas":
      return (
        <svg width={s} height={s} viewBox="0 0 24 24" aria-label="espadas">
          <path
            d="M12 2 L13.5 4 V16 H10.5 V4 Z"
            fill={color}
            stroke="#0e1e30"
            strokeWidth="0.8"
          />
          <rect x="8" y="16" width="8" height="1.5" fill="#666" />
          <rect x="11" y="17.5" width="2" height="4" fill={color} />
        </svg>
      );
    case "bastos":
      return (
        <svg width={s} height={s} viewBox="0 0 24 24" aria-label="bastos">
          <path
            d="M11 3 L13 3 L14 9 L17 13 L12 21 L7 13 L10 9 Z"
            fill={color}
            stroke="#3a230f"
            strokeWidth="0.8"
          />
          <line x1="9" y1="7" x2="15" y2="7" stroke="#3a230f" strokeWidth="0.6" />
          <line x1="9" y1="10" x2="15" y2="10" stroke="#3a230f" strokeWidth="0.6" />
        </svg>
      );
  }
}
