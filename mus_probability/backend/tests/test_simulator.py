"""Sanity tests for the Monte Carlo simulator.

These don't verify exact probabilities (that requires combinatorial work);
they verify the structure and basic invariants of the output.
"""

import pytest

from app.models.card import Card, Suit
from app.models.hand import Hand
from app.probability.simulator import LANCES, simulate


O, C, E, B = Suit.OROS, Suit.COPAS, Suit.ESPADAS, Suit.BASTOS


def H(*specs):
    return Hand(tuple(Card(r, s) for r, s in specs)[:4])


class TestSimulatorBasics:
    def test_returns_all_lances(self):
        hand = H((12, O), (11, C), (10, E), (1, B))
        out = simulate(hand, my_pos=0, n_sims=1000, seed=42)
        assert set(out.lances.keys()) == set(LANCES)

    def test_win_probs_are_in_range(self):
        hand = H((12, O), (11, C), (10, E), (1, B))
        out = simulate(hand, my_pos=0, n_sims=1000, seed=42)
        for l, r in out.lances.items():
            assert 0.0 <= r.win_prob <= 1.0
            assert 0.0 <= r.play_prob <= 1.0

    def test_reproducible_with_seed(self):
        hand = H((12, O), (11, C), (10, E), (1, B))
        a = simulate(hand, my_pos=0, n_sims=500, seed=123)
        b = simulate(hand, my_pos=0, n_sims=500, seed=123)
        for l in LANCES:
            assert a.lances[l].win_prob == b.lances[l].win_prob

    def test_strong_grande_hand_wins_often(self):
        # 4 reyes is the best grande hand possible
        hand = H((12, O), (12, C), (3, E), (3, B))   # four "reyes" (12, 12, 3->12, 3->12)
        out = simulate(hand, my_pos=0, n_sims=5000, seed=7)
        assert out.lances["grande"].win_prob > 0.9

    def test_strong_chica_hand_wins_often(self):
        # 4 ases is the best chica hand possible
        hand = H((1, O), (1, C), (2, E), (2, B))   # four "ases"
        out = simulate(hand, my_pos=0, n_sims=5000, seed=7)
        assert out.lances["chica"].win_prob > 0.9

    def test_31_juego_almost_always_wins_when_played(self):
        hand = H((12, O), (11, C), (10, E), (1, B))   # 31
        out = simulate(hand, my_pos=0, n_sims=5000, seed=7)
        assert out.lances["juego"].win_prob > 0.85

    def test_position_affects_tie_break_only(self):
        # mano (pos 0) should win at least as often as postre (pos 3) for ties,
        # so win prob with pos=0 >= win prob with pos=3 (roughly).
        hand = H((12, O), (11, C), (10, E), (1, B))
        a = simulate(hand, my_pos=0, n_sims=5000, seed=99)
        b = simulate(hand, my_pos=3, n_sims=5000, seed=99)
        # Allow noise; check that grande win prob diff is small (positions don't
        # change distribution drastically, only ties)
        assert abs(a.lances["grande"].win_prob - b.lances["grande"].win_prob) < 0.05
