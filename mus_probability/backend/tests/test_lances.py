"""Unit tests for lance evaluators using canonical mus examples."""

import pytest

from app.engine.lances import (
    PARES_DUPLES,
    PARES_MEDIAS,
    PARES_NONE,
    PARES_PAREJA,
    chica_key,
    grande_key,
    has_juego,
    has_pares,
    juego_key,
    juego_sum,
    pares_key,
)
from app.models.card import Card, Suit
from app.models.hand import Hand


def H(*specs: tuple[int, Suit]) -> Hand:
    return Hand(tuple(Card(r, s) for r, s in specs)[:4])  # type: ignore[arg-type]


# Shorthand suits
O, C, E, B = Suit.OROS, Suit.COPAS, Suit.ESPADAS, Suit.BASTOS


class TestEffectiveRanks:
    def test_two_counts_as_as(self):
        assert Card(2, O).effective == 1

    def test_three_counts_as_rey(self):
        assert Card(3, O).effective == 12

    def test_normal_ranks_unchanged(self):
        for r in (1, 4, 5, 6, 7, 10, 11, 12):
            assert Card(r, O).effective == r


class TestGrande:
    def test_higher_rey_beats_caballo(self):
        a = H((12, O), (11, C), (10, E), (1, B))  # Rey, Cab, Sota, As
        b = H((11, O), (11, C), (10, E), (10, B))  # Cab, Cab, Sota, Sota
        assert grande_key(a) > grande_key(b)

    def test_two_as_three_replaces_rey(self):
        # Two 3s should act as two reyes for grande
        a = H((3, O), (3, C), (1, E), (1, B))   # 2 reyes + 2 ases
        b = H((12, O), (11, C), (11, E), (10, B))  # rey + 2 cab + sota
        assert grande_key(a) > grande_key(b)

    def test_tie_when_identical_ranks(self):
        a = H((12, O), (11, C), (5, E), (4, B))
        b = H((12, B), (11, E), (5, C), (4, O))
        assert grande_key(a) == grande_key(b)


class TestChica:
    def test_lower_as_beats_cuatro(self):
        a = H((1, O), (1, C), (4, E), (5, B))
        b = H((4, O), (4, C), (5, E), (6, B))
        assert chica_key(a) > chica_key(b)

    def test_two_counts_as_as_for_chica(self):
        a = H((2, O), (2, C), (4, E), (5, B))  # 2 ases + 4 + 5
        b = H((1, O), (4, C), (4, E), (5, B))  # 1 as + 4 + 4 + 5
        assert chica_key(a) > chica_key(b)


class TestPares:
    def test_no_pair(self):
        h = H((12, O), (10, C), (5, E), (1, B))
        assert pares_key(h) == (PARES_NONE,)
        assert not has_pares(h)

    def test_simple_pair(self):
        h = H((7, O), (7, C), (5, E), (1, B))
        key = pares_key(h)
        assert key[0] == PARES_PAREJA
        assert key[1] == 7
        assert has_pares(h)

    def test_medias(self):
        h = H((10, O), (10, C), (10, E), (1, B))
        key = pares_key(h)
        assert key[0] == PARES_MEDIAS
        assert key[1] == 10

    def test_duples_two_pairs(self):
        h = H((12, O), (12, C), (1, E), (1, B))  # rey, rey, as, as
        key = pares_key(h)
        assert key == (PARES_DUPLES, 12, 1)

    def test_duples_quads(self):
        h = H((11, O), (11, C), (11, E), (11, B))  # 4 caballos
        key = pares_key(h)
        assert key == (PARES_DUPLES, 11, 11)

    def test_duples_reyes_ases_beat_quad_sotas(self):
        a = H((12, O), (12, C), (1, E), (1, B))     # duples R-A
        b = H((10, O), (10, C), (10, E), (10, B))   # 4 sotas
        assert pares_key(a) > pares_key(b)

    def test_two_pairs_caballo_seis_beat_quad_sotas(self):
        # From the spec: 2 caballos + 2 seises beats 4 sotas
        a = H((11, O), (11, C), (6, E), (6, B))
        b = H((10, O), (10, C), (10, E), (10, B))
        assert pares_key(a) > pares_key(b)

    def test_three_replaces_rey_for_pares(self):
        # Two 3s + two reyes should be duples of (12, 12) effectively == quads
        h = H((3, O), (3, C), (12, E), (12, B))
        key = pares_key(h)
        assert key == (PARES_DUPLES, 12, 12)


class TestJuego:
    def test_31_is_best(self):
        h = H((12, O), (11, C), (10, E), (1, B))  # 10+10+10+1 = 31
        assert juego_sum(h) == 31
        assert has_juego(h)

    def test_31_beats_40(self):
        a = H((12, O), (11, C), (10, E), (1, B))   # 31
        b = H((12, O), (12, C), (10, E), (3, B))   # 10+10+10+10 = 40
        assert juego_sum(b) == 40
        assert juego_key(a) > juego_key(b)

    def test_juego_order_full(self):
        order = [31, 32, 40, 37, 36, 35, 34, 33]
        prev = None
        for s in order:
            # Construct a hand summing to s
            hand = _hand_with_sum(s)
            assert juego_sum(hand) == s
            if prev is not None:
                assert juego_key(prev) > juego_key(hand)
            prev = hand

    def test_below_31_is_no_juego(self):
        h = H((10, O), (10, C), (7, E), (1, B))  # 10+10+7+1 = 28
        assert not has_juego(h)


def _hand_with_sum(target: int) -> Hand:
    """Build a 4-card hand with given juego sum. Used in tests only."""
    examples = {
        31: H((12, O), (11, C), (10, E), (1, B)),    # 10+10+10+1
        32: H((12, O), (11, C), (7, E), (5, B)),     # 10+10+7+5
        33: H((12, O), (11, C), (7, E), (6, B)),     # 10+10+7+6
        34: H((12, O), (11, C), (10, E), (4, B)),    # 10+10+10+4
        35: H((12, O), (11, C), (10, E), (5, B)),    # 10+10+10+5
        36: H((12, O), (11, C), (10, E), (6, B)),    # 10+10+10+6
        37: H((12, O), (11, C), (10, E), (7, B)),    # 10+10+10+7
        40: H((12, O), (12, C), (12, E), (12, B)),   # 10+10+10+10
    }
    return examples[target]
