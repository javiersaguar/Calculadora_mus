"""Pydantic schemas for the /calculate endpoint."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from ..models.card import PRINTED_RANKS, Suit


class CardInput(BaseModel):
    rank: int = Field(..., description="Printed rank: 1,2,3,4,5,6,7,10,11,12")
    suit: Suit

    @field_validator("rank")
    @classmethod
    def _valid_rank(cls, v: int) -> int:
        if v not in PRINTED_RANKS:
            raise ValueError(f"rank must be one of {PRINTED_RANKS}")
        return v


class DiscardRound(BaseModel):
    """Per-player discard info for a single round of mus.

    `discarded` is required (0..4). `kept_after` is optional — the user can
    say "no lo sé".  These fields are recorded but, in the MVP, do not yet
    affect the prior over opponents' hands.
    """
    discarded: int = Field(..., ge=0, le=4)
    kept_after: int | None = Field(None, ge=0, le=4)


class PlayerDiscards(BaseModel):
    """Discard history for a single opponent."""
    player_position: int = Field(..., ge=0, le=3)
    rounds: list[DiscardRound] = Field(default_factory=list)


class CalculateRequest(BaseModel):
    my_cards: list[CardInput] = Field(..., min_length=4, max_length=4)
    my_position: int = Field(..., ge=0, le=3, description="0=mano, 3=postre")
    n_sims: int = Field(50_000, ge=100, le=1_000_000)
    discards: list[PlayerDiscards] = Field(
        default_factory=list,
        description=(
            "Optional discard history. Reserved for future heuristic priors; "
            "not used in the MVP uniform model."
        ),
    )
    seed: int | None = None

    @field_validator("my_cards")
    @classmethod
    def _unique(cls, cards: list[CardInput]) -> list[CardInput]:
        ids = {(c.rank, c.suit) for c in cards}
        if len(ids) != len(cards):
            raise ValueError("my_cards must be 4 distinct cards")
        return cards


class LanceProb(BaseModel):
    win_prob: float
    play_prob: float
    expected_win: float
    ci95: float
    n_relevant: int


class CalculateResponse(BaseModel):
    n_sims: int
    lances: dict[Literal["grande", "chica", "pares", "juego", "punto"], LanceProb]
