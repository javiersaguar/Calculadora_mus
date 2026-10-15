"""Monte Carlo simulator for Mus winning probabilities.

Given the user's known 4-card hand and position, sample many possible
distributions of the remaining 36 cards among the 3 opponents and count how
often the user's team wins each lance.

MVP discard model: opponents' final hands are drawn uniformly from the pool
of unknown cards. The discard counts the user provides do not influence the
sample (a future iteration can replace this with a rational-discard prior).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from ..engine.comparator import lance_outcomes
from ..models.card import Card, full_deck
from ..models.hand import Hand

LANCES: tuple[str, ...] = ("grande", "chica", "pares", "juego", "punto")


@dataclass(frozen=True, slots=True)
class LanceResult:
    win_prob: float       # conditional on lance being played
    play_prob: float      # P(lance is contested at all)
    expected_win: float   # win_prob * play_prob
    ci95: float           # +/- half-width of 95% CI for win_prob
    n_relevant: int       # trials counted towards win_prob

    def as_dict(self) -> dict[str, float | int]:
        return {
            "win_prob": self.win_prob,
            "play_prob": self.play_prob,
            "expected_win": self.expected_win,
            "ci95": self.ci95,
            "n_relevant": self.n_relevant,
        }


@dataclass(frozen=True, slots=True)
class SimulationOutput:
    n_sims: int
    lances: dict[str, LanceResult]

    def as_dict(self) -> dict:
        return {
            "n_sims": self.n_sims,
            "lances": {k: v.as_dict() for k, v in self.lances.items()},
        }


def _wilson_halfwidth(p: float, n: int) -> float:
    """Half-width of a 95% normal-approx CI; safe at p=0,1 by clamping."""
    if n <= 0:
        return 1.0
    p = max(0.0, min(1.0, p))
    return 1.96 * math.sqrt(max(p * (1 - p), 1e-12) / n)


def simulate(
    my_hand: Hand,
    my_pos: int,
    n_sims: int = 50_000,
    *,
    known_excluded: tuple[Card, ...] = (),
    seed: int | None = None,
) -> SimulationOutput:
    """Run Monte Carlo simulation.

    Args:
        my_hand: user's known 4 cards.
        my_pos: 0..3 (0=mano, 3=postre).
        n_sims: number of trials.
        known_excluded: cards known to be out of play (rare; usually empty).
        seed: optional RNG seed for reproducibility.
    """
    if my_pos not in (0, 1, 2, 3):
        raise ValueError("my_pos must be in 0..3")
    if n_sims <= 0:
        raise ValueError("n_sims must be positive")

    rng = random.Random(seed)
    my_cards = set(my_hand.cards)
    excluded = my_cards | set(known_excluded)
    unknown = [c for c in full_deck() if c not in excluded]
    if len(unknown) < 12:
        raise ValueError("Not enough unknown cards to deal 3 opponent hands")

    # Counters
    wins = {l: 0 for l in LANCES}
    losses = {l: 0 for l in LANCES}
    plays = {l: 0 for l in LANCES}  # times the lance had a winner

    opp_positions = [p for p in range(4) if p != my_pos]
    pool = unknown[:]  # working copy we shuffle in place

    for _ in range(n_sims):
        rng.shuffle(pool)
        # Place hands on the table
        table: list[Hand] = [my_hand] * 4  # placeholder, overwritten below
        for i, p in enumerate(opp_positions):
            start = i * 4
            table[p] = Hand(tuple(pool[start:start + 4]))
        # Position my_pos already holds my_hand (it was set in the placeholder
        # init, but only by accident — make it explicit):
        table[my_pos] = my_hand

        outcomes = lance_outcomes(table, my_pos)
        for l in LANCES:
            o = outcomes[l]
            if o == 0:
                continue
            plays[l] += 1
            if o > 0:
                wins[l] += 1
            else:
                losses[l] += 1

    results: dict[str, LanceResult] = {}
    for l in LANCES:
        n_play = plays[l]
        win_prob = wins[l] / n_play if n_play else 0.0
        play_prob = n_play / n_sims
        ci95 = _wilson_halfwidth(win_prob, n_play)
        results[l] = LanceResult(
            win_prob=win_prob,
            play_prob=play_prob,
            expected_win=win_prob * play_prob,
            ci95=ci95,
            n_relevant=n_play,
        )
    return SimulationOutput(n_sims=n_sims, lances=results)
