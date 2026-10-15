"""Tests for whole-table outcome determination, with mano tiebreak."""

from app.engine.comparator import (
    chica_outcome,
    grande_outcome,
    juego_outcome,
    lance_outcomes,
    pares_outcome,
    punto_outcome,
)
from app.models.card import Card, Suit
from app.models.hand import Hand


O, C, E, B = Suit.OROS, Suit.COPAS, Suit.ESPADAS, Suit.BASTOS


def H(*specs):
    return Hand(tuple(Card(r, s) for r, s in specs)[:4])


def make_table(h0, h1, h2, h3):
    return [h0, h1, h2, h3]


class TestGrande:
    def test_my_team_with_reyes_wins(self):
        # I (pos 0) have 4 reyes, opponents have low cards
        my_hand = H((12, O), (12, C), (12, E), (12, B))
        partner = H((1, O), (1, C), (4, E), (5, B))
        opp1 = H((1, O), (4, C), (5, E), (6, B))
        opp2 = H((1, O), (4, C), (5, E), (6, B))
        table = make_table(my_hand, opp1, partner, opp2)
        assert grande_outcome(table, my_pos=0) == 1

    def test_opponents_with_reyes_win(self):
        my_hand = H((1, O), (1, C), (4, E), (5, B))
        partner = H((1, O), (4, C), (5, E), (6, B))
        opp1 = H((12, O), (12, C), (12, E), (12, B))
        opp2 = H((1, O), (4, C), (5, E), (6, B))
        table = make_table(my_hand, opp1, partner, opp2)
        assert grande_outcome(table, my_pos=0) == -1


class TestChica:
    def test_my_team_with_low_cards_wins(self):
        my_hand = H((1, O), (1, C), (1, E), (1, B))   # 4 ases
        partner = H((12, O), (11, C), (10, E), (7, B))
        opp1 = H((4, O), (4, C), (5, E), (6, B))
        opp2 = H((12, O), (11, C), (10, E), (7, B))
        table = make_table(my_hand, opp1, partner, opp2)
        assert chica_outcome(table, my_pos=0) == 1


class TestPares:
    def test_only_my_team_has_pares(self):
        my_hand = H((12, O), (12, C), (5, E), (1, B))  # pair of reyes
        partner = H((11, O), (10, C), (7, E), (4, B))
        opp1 = H((12, O), (11, C), (10, E), (1, B))    # no pair
        opp2 = H((11, O), (10, C), (7, E), (4, B))
        table = make_table(my_hand, opp1, partner, opp2)
        assert pares_outcome(table, my_pos=0) == 1

    def test_neither_has_pares(self):
        my_hand = H((12, O), (11, C), (10, E), (1, B))
        partner = H((11, O), (10, C), (7, E), (4, B))
        opp1 = H((12, O), (11, C), (10, E), (1, B))
        opp2 = H((11, O), (10, C), (7, E), (4, B))
        table = make_table(my_hand, opp1, partner, opp2)
        assert pares_outcome(table, my_pos=0) == 0

    def test_duples_beat_medias(self):
        my_hand = H((12, O), (12, C), (1, E), (1, B))  # duples
        partner = H((11, O), (10, C), (7, E), (4, B))
        opp1 = H((12, O), (12, C), (12, E), (4, B))    # medias
        opp2 = H((11, O), (10, C), (7, E), (4, B))
        table = make_table(my_hand, opp1, partner, opp2)
        assert pares_outcome(table, my_pos=0) == 1


class TestJuego:
    def test_31_wins(self):
        my_hand = H((12, O), (11, C), (10, E), (1, B))  # 31
        partner = H((4, O), (4, C), (5, E), (6, B))
        opp1 = H((12, O), (12, C), (12, E), (12, B))     # 40
        opp2 = H((4, O), (4, C), (5, E), (6, B))
        table = make_table(my_hand, opp1, partner, opp2)
        assert juego_outcome(table, my_pos=0) == 1

    def test_no_juego_returns_zero(self):
        low = H((4, O), (4, C), (5, E), (6, B))         # 4+4+5+6 = 19
        table = make_table(low, low, low, low)
        assert juego_outcome(table, my_pos=0) == 0


class TestPunto:
    def test_punto_when_no_juego(self):
        # 30 vs 29 — my team has 30
        my_hand = H((12, O), (12, C), (10, E), (1, B))    # 10+10+10 wait 1=1 -> 31
        # need <31. Use 12+12+5+1 = 28 vs 12+12+4+1 = 27
        my_hand = H((12, O), (12, C), (5, E), (1, B))     # 10+10+5+1 = 26
        partner = H((12, O), (10, C), (7, E), (1, B))     # 10+10+7+1 = 28
        opp1 = H((12, O), (10, C), (6, E), (1, B))        # 10+10+6+1 = 27
        opp2 = H((12, O), (10, C), (5, E), (1, B))        # 10+10+5+1 = 26
        table = make_table(my_hand, opp1, partner, opp2)
        # my team best = 28, opps best = 27
        assert punto_outcome(table, my_pos=0) == 1


class TestManoTiebreak:
    def test_identical_grande_keys_mano_wins(self):
        # Pos 0 (mano) and pos 1 have identical hands -> mano wins
        same = H((12, O), (11, C), (10, E), (1, B))
        partner = H((4, O), (4, C), (5, E), (6, B))
        table = make_table(same, same, partner, partner)
        # Best on both teams have same key, mano (pos 0) closer than (pos 1)
        assert grande_outcome(table, my_pos=0) == 1


class TestLanceOutcomesAggregate:
    def test_lance_outcomes_returns_five_keys(self):
        h = H((12, O), (11, C), (10, E), (1, B))
        result = lance_outcomes([h, h, h, h], my_pos=0)
        assert set(result.keys()) == {"grande", "chica", "pares", "juego", "punto"}
