from backend.mus_rules import (
    MusVariant,
    evaluate_table,
    game_total,
    has_pairs,
    parse_cards,
    pairs_name,
)


def test_eight_kings_and_aces_affect_pairs_and_game_total():
    variant = MusVariant(eight_kings=True, eight_aces=True)
    hand = parse_cards(["12-O", "3-C", "2-E", "1-B"])

    assert has_pairs(hand, variant)
    assert pairs_name(hand, variant) == "duples"
    assert game_total(hand, variant) == 22


def test_grande_tie_is_resolved_by_mano():
    variant = MusVariant()
    hands = [
        parse_cards(["12-O", "7-O", "6-O", "5-O"]),
        parse_cards(["12-C", "7-C", "6-C", "5-C"]),
        parse_cards(["11-E", "7-E", "6-E", "5-E"]),
        parse_cards(["10-B", "7-B", "6-B", "5-B"]),
    ]

    table = evaluate_table(hands, mano_index=1, variant=variant)

    assert table["grande"]["winner"] == 1


def test_pairs_hierarchy_prioritizes_duples_over_medias():
    variant = MusVariant()
    hands = [
        parse_cards(["12-O", "12-C", "1-O", "1-C"]),
        parse_cards(["11-O", "11-C", "11-E", "5-C"]),
        parse_cards(["7-O", "7-C", "4-O", "5-O"]),
        parse_cards(["6-O", "5-C", "4-E", "1-B"]),
    ]

    table = evaluate_table(hands, mano_index=0, variant=variant)

    assert table["pares"]["winner"] == 0


def test_game_order_places_31_above_32_and_40():
    variant = MusVariant()
    hands = [
        parse_cards(["12-O", "11-C", "7-E", "4-B"]),
        parse_cards(["12-C", "11-E", "10-B", "2-O"]),
        parse_cards(["12-E", "11-B", "10-O", "10-C"]),
        parse_cards(["7-O", "6-C", "5-E", "4-B"]),
    ]

    table = evaluate_table(hands, mano_index=2, variant=variant)

    assert table["juego"]["winner"] == 0


def test_point_only_exists_when_nobody_has_game():
    variant = MusVariant(eight_kings=False, eight_aces=False)
    hands = [
        parse_cards(["7-O", "6-O", "5-O", "4-O"]),
        parse_cards(["7-C", "6-C", "5-C", "3-C"]),
        parse_cards(["7-E", "6-E", "5-E", "2-E"]),
        parse_cards(["7-B", "6-B", "4-B", "2-B"]),
    ]

    table = evaluate_table(hands, mano_index=0, variant=variant)

    assert table["juego"]["winner"] is None
    assert table["punto"]["winner"] == 0
