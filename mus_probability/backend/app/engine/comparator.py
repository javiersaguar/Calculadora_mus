"""Determine the winner of each lance for a complete 4-player table.

Mano tiebreak: when keys are equal, the player whose position is closer to
mano (lower index) wins.

All `*_outcome` functions return:
    +1 if my team wins
    -1 if opponents win
     0 if the lance has no winner (pares/juego only — neither team qualifies)
"""

from collections.abc import Callable
from typing import Sequence

from ..models.hand import Hand, opponents, teammates
from .lances import (
    chica_key,
    grande_key,
    has_juego,
    has_pares,
    juego_key,
    pares_key,
    punto_key,
)

Key = tuple[int, ...]
KeyFn = Callable[[Hand], Key]


def _best_in_team(
    hands: Sequence[Hand],
    positions: tuple[int, int],
    key_fn: KeyFn,
) -> tuple[Key, int]:
    """Return (best_key, position_of_best_player) for a 2-player team.

    Within the team, ties are broken in favor of the player closer to mano.
    """
    a, b = positions
    ka, kb = key_fn(hands[a]), key_fn(hands[b])
    if ka > kb or (ka == kb and a < b):
        return ka, a
    return kb, b


def _team_outcome(
    hands: Sequence[Hand],
    my_pos: int,
    key_fn: KeyFn,
) -> int:
    """+1 if my team's best beats opponents' best, with mano tiebreak."""
    my_team = teammates(my_pos)
    opp_team = opponents(my_pos)
    my_key, my_best = _best_in_team(hands, my_team, key_fn)
    opp_key, opp_best = _best_in_team(hands, opp_team, key_fn)
    if my_key > opp_key:
        return 1
    if my_key < opp_key:
        return -1
    return 1 if my_best < opp_best else -1


def grande_outcome(hands: Sequence[Hand], my_pos: int) -> int:
    return _team_outcome(hands, my_pos, grande_key)


def chica_outcome(hands: Sequence[Hand], my_pos: int) -> int:
    return _team_outcome(hands, my_pos, chica_key)


def pares_outcome(hands: Sequence[Hand], my_pos: int) -> int:
    """+1 my team wins, -1 they win, 0 if neither team has pares."""
    my_team = teammates(my_pos)
    opp_team = opponents(my_pos)
    my_has = any(has_pares(hands[p]) for p in my_team)
    opp_has = any(has_pares(hands[p]) for p in opp_team)
    if not my_has and not opp_has:
        return 0
    if my_has and not opp_has:
        return 1
    if opp_has and not my_has:
        return -1
    return _team_outcome(hands, my_pos, pares_key)


def juego_outcome(hands: Sequence[Hand], my_pos: int) -> int:
    """+1 my team wins, -1 they win, 0 if neither has juego (then punto applies)."""
    my_team = teammates(my_pos)
    opp_team = opponents(my_pos)
    my_has = any(has_juego(hands[p]) for p in my_team)
    opp_has = any(has_juego(hands[p]) for p in opp_team)
    if not my_has and not opp_has:
        return 0
    if my_has and not opp_has:
        return 1
    if opp_has and not my_has:
        return -1
    return _team_outcome(hands, my_pos, juego_key)


def punto_outcome(hands: Sequence[Hand], my_pos: int) -> int:
    """Only meaningful when no one has juego. +1 my team wins, -1 they win."""
    return _team_outcome(hands, my_pos, punto_key)


def lance_outcomes(hands: Sequence[Hand], my_pos: int) -> dict[str, int]:
    """Compute all five lance outcomes for one full table."""
    juego = juego_outcome(hands, my_pos)
    return {
        "grande": grande_outcome(hands, my_pos),
        "chica": chica_outcome(hands, my_pos),
        "pares": pares_outcome(hands, my_pos),
        "juego": juego,
        # Punto only matters when juego went unresolved (==0)
        "punto": punto_outcome(hands, my_pos) if juego == 0 else 0,
    }
