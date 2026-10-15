export type Suit = "oros" | "copas" | "espadas" | "bastos";

export const SUITS: Suit[] = ["oros", "copas", "espadas", "bastos"];
export const RANKS: number[] = [1, 2, 3, 4, 5, 6, 7, 10, 11, 12];

export const RANK_NAMES: Record<number, string> = {
  1: "As",
  2: "Dos",
  3: "Tres",
  4: "Cuatro",
  5: "Cinco",
  6: "Seis",
  7: "Siete",
  10: "Sota",
  11: "Caballo",
  12: "Rey",
};

export const SUIT_NAMES: Record<Suit, string> = {
  oros: "Oros",
  copas: "Copas",
  espadas: "Espadas",
  bastos: "Bastos",
};

export interface CardSpec {
  rank: number;
  suit: Suit;
}

export type Position = 0 | 1 | 2 | 3;

export const POSITION_NAMES: Record<Position, string> = {
  0: "Mano",
  1: "Segundo",
  2: "Tercero",
  3: "Postre",
};

export interface DiscardRound {
  discarded: number;
  kept_after: number | null;
}

export interface PlayerDiscards {
  player_position: Position;
  rounds: DiscardRound[];
}

export interface CalculateRequest {
  my_cards: CardSpec[];
  my_position: Position;
  n_sims: number;
  discards?: PlayerDiscards[];
  seed?: number | null;
}

export interface LanceProb {
  win_prob: number;
  play_prob: number;
  expected_win: number;
  ci95: number;
  n_relevant: number;
}

export interface CalculateResponse {
  n_sims: number;
  lances: {
    grande: LanceProb;
    chica: LanceProb;
    pares: LanceProb;
    juego: LanceProb;
    punto: LanceProb;
  };
}

export function cardKey(c: CardSpec): string {
  return `${c.rank}-${c.suit}`;
}
