"""Integration tests for the FastAPI endpoints."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _request_body(rank_suits, pos=0, n_sims=1000):
    return {
        "my_cards": [{"rank": r, "suit": s} for r, s in rank_suits],
        "my_position": pos,
        "n_sims": n_sims,
        "seed": 1,
    }


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_calculate_returns_all_lances():
    body = _request_body([(12, "oros"), (11, "copas"), (10, "espadas"), (1, "bastos")])
    r = client.post("/calculate", json=body)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["n_sims"] == 1000
    assert set(data["lances"].keys()) == {"grande", "chica", "pares", "juego", "punto"}


def test_calculate_rejects_duplicate_cards():
    body = _request_body([(12, "oros"), (12, "oros"), (10, "espadas"), (1, "bastos")])
    r = client.post("/calculate", json=body)
    assert r.status_code == 422


def test_calculate_rejects_invalid_rank():
    body = _request_body([(8, "oros"), (11, "copas"), (10, "espadas"), (1, "bastos")])
    r = client.post("/calculate", json=body)
    assert r.status_code == 422


def test_calculate_rejects_invalid_position():
    body = _request_body(
        [(12, "oros"), (11, "copas"), (10, "espadas"), (1, "bastos")], pos=4
    )
    r = client.post("/calculate", json=body)
    assert r.status_code == 422


def test_calculate_accepts_discard_history():
    body = _request_body([(12, "oros"), (11, "copas"), (10, "espadas"), (1, "bastos")])
    body["discards"] = [
        {
            "player_position": 1,
            "rounds": [
                {"discarded": 3, "kept_after": 1},
                {"discarded": 2, "kept_after": None},
            ],
        }
    ]
    r = client.post("/calculate", json=body)
    assert r.status_code == 200
