from backend.simulator import calculate_probabilities


def test_simulator_returns_metrics_for_valid_hand():
    result = calculate_probabilities(
        {
            "heroHand": ["12-O", "11-C", "7-E", "1-B"],
            "playerIndex": 0,
            "manoIndex": 0,
            "samples": 1200,
            "seed": 7,
            "variant": {"eightKingsAndAces": True},
            "declarations": {
                "pairs": ["unknown", "unknown", "unknown", "unknown"],
                "game": ["unknown", "unknown", "unknown", "unknown"],
            },
            "discardCounts": ["unknown", "unknown", "unknown", "unknown"],
        }
    )

    assert result["meta"]["acceptedSamples"] == 1200
    assert 0 <= result["metrics"]["grande"]["teamWin"] <= 1
    assert result["heroHand"]["game"]["total"] == 28


def test_declarations_filter_unknown_rival_hands_during_simulation():
    result = calculate_probabilities(
        {
            "heroHand": ["12-O", "11-C", "7-E", "1-B"],
            "playerIndex": 0,
            "manoIndex": 0,
            "samples": 1000,
            "seed": 11,
            "variant": {"eightKingsAndAces": True},
            "declarations": {
                "pairs": ["unknown", "yes", "unknown", "unknown"],
                "game": ["unknown", "unknown", "unknown", "unknown"],
            },
            "discardCounts": ["unknown", "unknown", "unknown", "unknown"],
        }
    )

    assert result["meta"]["acceptedSamples"] == 1000
    assert result["metrics"]["pares"]["active"] == 1


def test_total_dealt_cards_feeds_behavioral_model_metadata():
    result = calculate_probabilities(
        {
            "heroHand": ["12-O", "11-C", "7-E", "1-B"],
            "playerIndex": 0,
            "manoIndex": 0,
            "samples": 1000,
            "seed": 19,
            "variant": {"eightKingsAndAces": True},
            "discardModel": "heuristic",
            "totalDealtCards": 36,
            "declarations": {
                "pairs": ["unknown", "unknown", "unknown", "unknown"],
                "game": ["unknown", "unknown", "unknown", "unknown"],
            },
            "discardCounts": ["unknown", "unknown", "unknown", "unknown"],
        }
    )

    assert result["meta"]["algorithm"] == "montecarlo-behavioral"
    assert result["meta"]["totalDealtCards"] == 36
    assert result["meta"]["deadCardsModeled"] == 20
    assert result["meta"]["effectiveSamples"] > 0
