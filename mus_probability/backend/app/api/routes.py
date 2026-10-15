"""FastAPI routes."""

from fastapi import APIRouter, HTTPException

from ..models.card import Card
from ..models.hand import Hand
from ..probability.simulator import simulate
from .schemas import CalculateRequest, CalculateResponse, LanceProb

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/calculate", response_model=CalculateResponse)
def calculate(req: CalculateRequest) -> CalculateResponse:
    try:
        cards = tuple(Card(c.rank, c.suit) for c in req.my_cards)
        hand = Hand(cards)  # type: ignore[arg-type]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    out = simulate(
        my_hand=hand,
        my_pos=req.my_position,
        n_sims=req.n_sims,
        seed=req.seed,
    )
    return CalculateResponse(
        n_sims=out.n_sims,
        lances={k: LanceProb(**v.as_dict()) for k, v in out.lances.items()},
    )
