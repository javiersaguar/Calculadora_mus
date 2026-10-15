"""Card model for the Spanish deck used in Mus (8 reyes variant).

In the 8 reyes variant:
- The four 3s count as kings (rank 12 effective)
- The four 2s count as aces (rank 1 effective)

We keep both the printed rank (what the player sees) and the effective rank
(what the rules use for comparisons) so the UI can show the real card while
the engine reasons about the game-theoretic value.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Iterator


class Suit(str, Enum):
    OROS = "oros"
    COPAS = "copas"
    ESPADAS = "espadas"
    BASTOS = "bastos"


# Printed ranks present in the Spanish 40-card deck.
# We omit 8 and 9 (not present in the Spanish deck).
PRINTED_RANKS: tuple[int, ...] = (1, 2, 3, 4, 5, 6, 7, 10, 11, 12)


def effective_rank(printed: int) -> int:
    """Map printed rank to effective rank under the 8 reyes variant."""
    if printed == 2:
        return 1   # 2 counts as as
    if printed == 3:
        return 12  # 3 counts as rey
    return printed


def juego_value(printed: int) -> int:
    """Value of a card when counting points for 'juego' / 'punto'.

    Figures (sota 10, caballo 11, rey 12) are worth 10.
    The 3 (rey) is worth 10. The 2 (as) is worth 1.
    Everything else is worth its printed rank.
    """
    if printed == 3:
        return 10  # rey
    if printed == 2:
        return 1   # as
    if printed in (10, 11, 12):
        return 10  # sota, caballo, rey
    return printed


@dataclass(frozen=True, slots=True)
class Card:
    rank: int   # printed rank: 1,2,3,4,5,6,7,10,11,12
    suit: Suit

    def __post_init__(self) -> None:
        if self.rank not in PRINTED_RANKS:
            raise ValueError(f"Invalid printed rank: {self.rank}")

    @property
    def effective(self) -> int:
        return effective_rank(self.rank)

    @property
    def points(self) -> int:
        return juego_value(self.rank)

    def __repr__(self) -> str:
        return f"{self.rank}{self.suit.value[0].upper()}"


def full_deck() -> list[Card]:
    """Return a fresh ordered 40-card Spanish deck."""
    return [Card(r, s) for s in Suit for r in PRINTED_RANKS]


def iter_deck() -> Iterator[Card]:
    yield from full_deck()
