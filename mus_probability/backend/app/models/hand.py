"""A hand in Mus is exactly four cards. Position determines mano tiebreak.

Player positions, going right around the table:
    0 = mano (first to speak)
    1 = segundo
    2 = tercero (mano's partner)
    3 = postre (dealer)

Teams: {0, 2} vs {1, 3}.
"""

from dataclasses import dataclass

from .card import Card

HAND_SIZE = 4


@dataclass(frozen=True, slots=True)
class Hand:
    cards: tuple[Card, Card, Card, Card]

    def __post_init__(self) -> None:
        if len(self.cards) != HAND_SIZE:
            raise ValueError(f"Hand must have {HAND_SIZE} cards")

    def __iter__(self):
        return iter(self.cards)


def partner_position(pos: int) -> int:
    return (pos + 2) % 4


def teammates(pos: int) -> tuple[int, int]:
    p = partner_position(pos)
    return (pos, p) if pos < p else (p, pos)


def opponents(pos: int) -> tuple[int, int]:
    a, b = (pos + 1) % 4, (pos + 3) % 4
    return (a, b) if a < b else (b, a)
