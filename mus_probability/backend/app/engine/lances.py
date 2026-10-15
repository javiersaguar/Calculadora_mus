"""Lance evaluators for Mus.

Each evaluator returns a *comparable key* where higher = better. The team
comparator then picks the higher key (with mano tiebreak on equality).

Lances:
- grande:  highest cards (effective rank, 8 reyes mapping applied)
- chica:   lowest cards
- pares:   no-pair / pareja / medias / duples
- juego:   sum >= 31, ranked 31 > 32 > 40 > 37 > 36 > 35 > 34 > 33
- punto:   only relevant when nobody has juego; closest-to-30 wins
"""

from collections import Counter

from ..models.hand import Hand

# Ranking of valid juego sums, best first.
JUEGO_ORDER: tuple[int, ...] = (31, 32, 40, 37, 36, 35, 34, 33)
JUEGO_RANK = {s: len(JUEGO_ORDER) - i for i, s in enumerate(JUEGO_ORDER)}


def grande_key(hand: Hand) -> tuple[int, ...]:
    """Effective ranks sorted descending. Compare lexicographically, higher wins."""
    return tuple(sorted((c.effective for c in hand), reverse=True))


def chica_key(hand: Hand) -> tuple[int, ...]:
    """Effective ranks negated and sorted descending so that higher == lower-card hand."""
    return tuple(sorted((-c.effective for c in hand), reverse=True))


# Categories for pares, higher = stronger
PARES_NONE = 0
PARES_PAREJA = 1
PARES_MEDIAS = 2
PARES_DUPLES = 3


def pares_key(hand: Hand) -> tuple[int, ...]:
    """Return (category, tie_breaker...) where higher = better.

    Duples (4-of-a-kind or two pairs): key = (3, high_pair, low_pair).
    Medias (three-of-a-kind):          key = (2, trio_rank).
    Pareja (one pair):                 key = (1, pair_rank).
    None:                              key = (0,).
    """
    counts = Counter(c.effective for c in hand)
    # ranks with count >= 2, paired with their count
    grouped = [(rank, cnt) for rank, cnt in counts.items() if cnt >= 2]

    # 4 of a kind -> treat as duples with (rank, rank)
    quads = [r for r, c in grouped if c == 4]
    if quads:
        r = quads[0]
        return (PARES_DUPLES, r, r)

    pairs = sorted([r for r, c in grouped if c == 2], reverse=True)
    trios = [r for r, c in grouped if c == 3]

    if len(pairs) == 2:
        return (PARES_DUPLES, pairs[0], pairs[1])
    if trios:
        return (PARES_MEDIAS, trios[0])
    if len(pairs) == 1:
        return (PARES_PAREJA, pairs[0])
    return (PARES_NONE,)


def has_pares(hand: Hand) -> bool:
    return pares_key(hand)[0] >= PARES_PAREJA


def juego_sum(hand: Hand) -> int:
    return sum(c.points for c in hand)


def has_juego(hand: Hand) -> bool:
    return juego_sum(hand) >= 31


def juego_key(hand: Hand) -> tuple[int, int]:
    """(has_juego, ranking) so higher = better.

    For non-juego hands we still return (0, sum) so the same key can be used
    in 'punto' fallback comparisons.
    """
    s = juego_sum(hand)
    if s >= 31:
        return (1, JUEGO_RANK[s])
    return (0, s)


def punto_key(hand: Hand) -> tuple[int, int]:
    """Higher sum wins among non-juego hands (closer to 30 is best)."""
    return (0, juego_sum(hand))
