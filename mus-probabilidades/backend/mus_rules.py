from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Callable, Iterable


RANKS: tuple[int, ...] = (1, 2, 3, 4, 5, 6, 7, 10, 11, 12)
SUITS: tuple[str, ...] = ("O", "C", "E", "B")

RANK_LABELS: dict[int, str] = {
    1: "As",
    2: "2",
    3: "3",
    4: "4",
    5: "5",
    6: "6",
    7: "7",
    10: "Sota",
    11: "Caballo",
    12: "Rey",
}

SUIT_LABELS: dict[str, str] = {
    "O": "Oros",
    "C": "Copas",
    "E": "Espadas",
    "B": "Bastos",
}

HIGH_ORDER: tuple[int, ...] = (12, 11, 10, 7, 6, 5, 4, 3, 2, 1)
HIGH_STRENGTH: dict[int, int] = {
    rank: len(HIGH_ORDER) - index for index, rank in enumerate(HIGH_ORDER)
}

GAME_ORDER: tuple[int, ...] = (31, 32, 40, 37, 36, 35, 34, 33)
GAME_STRENGTH: dict[int, int] = {
    total: len(GAME_ORDER) - index for index, total in enumerate(GAME_ORDER)
}


@dataclass(frozen=True)
class MusVariant:
    eight_kings: bool = True
    eight_aces: bool = True


@dataclass(frozen=True)
class Card:
    rank: int
    suit: str

    @property
    def code(self) -> str:
        return f"{self.rank}-{self.suit}"

    @property
    def label(self) -> str:
        return f"{RANK_LABELS[self.rank]} de {SUIT_LABELS[self.suit]}"


class MusRulesError(ValueError):
    """Raised when a hand, card or rules request is invalid."""


def make_deck() -> list[Card]:
    return [Card(rank, suit) for suit in SUITS for rank in RANKS]


def parse_card(code: str) -> Card:
    try:
        rank_text, suit = code.split("-", 1)
        rank = int(rank_text)
    except (AttributeError, ValueError) as exc:
        raise MusRulesError(f"Carta no valida: {code!r}") from exc

    suit = suit.upper()
    if rank not in RANKS or suit not in SUITS:
        raise MusRulesError(f"Carta no valida: {code!r}")
    return Card(rank, suit)


def parse_cards(codes: Iterable[str]) -> list[Card]:
    cards = [parse_card(code) for code in codes]
    ensure_unique_cards(cards)
    return cards


def ensure_unique_cards(cards: Iterable[Card]) -> None:
    codes = [card.code for card in cards]
    if len(codes) != len(set(codes)):
        raise MusRulesError("Hay cartas repetidas en los datos introducidos.")


def effective_rank(card: Card, variant: MusVariant) -> int:
    if variant.eight_kings and card.rank == 3:
        return 12
    if variant.eight_aces and card.rank == 2:
        return 1
    return card.rank


def high_strength(rank: int) -> int:
    return HIGH_STRENGTH[rank]


def card_strength(card: Card, variant: MusVariant) -> int:
    return high_strength(effective_rank(card, variant))


def game_value(card: Card, variant: MusVariant) -> int:
    rank = effective_rank(card, variant)
    if rank in (10, 11, 12):
        return 10
    return rank


def game_total(hand: list[Card], variant: MusVariant) -> int:
    return sum(game_value(card, variant) for card in hand)


def has_pairs(hand: list[Card], variant: MusVariant) -> bool:
    counts = Counter(effective_rank(card, variant) for card in hand)
    return any(count >= 2 for count in counts.values())


def has_game(hand: list[Card], variant: MusVariant) -> bool:
    return game_total(hand, variant) >= 31


def grande_key(hand: list[Card], variant: MusVariant) -> tuple[int, ...]:
    return tuple(sorted((card_strength(card, variant) for card in hand), reverse=True))


def chica_key(hand: list[Card], variant: MusVariant) -> tuple[int, ...]:
    low_to_high = sorted(card_strength(card, variant) for card in hand)
    return tuple(-value for value in low_to_high)


def pairs_key(hand: list[Card], variant: MusVariant) -> tuple[int, tuple[int, ...]]:
    counts = Counter(effective_rank(card, variant) for card in hand)

    four = [rank for rank, count in counts.items() if count == 4]
    triples = [rank for rank, count in counts.items() if count == 3]
    pairs = [rank for rank, count in counts.items() if count == 2]

    if four:
        strengths = tuple(sorted((high_strength(four[0]), high_strength(four[0])), reverse=True))
        return (3, strengths)

    if len(pairs) == 2:
        strengths = tuple(sorted((high_strength(rank) for rank in pairs), reverse=True))
        return (3, strengths)

    if triples:
        return (2, (high_strength(max(triples, key=high_strength)),))

    if pairs:
        return (1, (high_strength(max(pairs, key=high_strength)),))

    return (0, ())


def pairs_name(hand: list[Card], variant: MusVariant) -> str:
    category = pairs_key(hand, variant)[0]
    if category == 3:
        return "duples"
    if category == 2:
        return "medias"
    if category == 1:
        return "pareja"
    return "sin pares"


def juego_key(hand: list[Card], variant: MusVariant) -> tuple[int, int]:
    total = game_total(hand, variant)
    if total < 31:
        return (0, total)
    return (GAME_STRENGTH.get(total, 0), total)


def punto_key(hand: list[Card], variant: MusVariant) -> tuple[int]:
    total = game_total(hand, variant)
    if total >= 31:
        return (-1,)
    return (total,)


def seat_order(mano_index: int, player_count: int = 4) -> list[int]:
    return [(mano_index + offset) % player_count for offset in range(player_count)]


def team_for_player(player_index: int) -> int:
    return player_index % 2


def winner_index(
    hands: list[list[Card]],
    mano_index: int,
    key_func: Callable[[list[Card]], tuple],
    eligible: Iterable[int] | None = None,
) -> int | None:
    candidates = list(range(len(hands))) if eligible is None else list(eligible)
    if not candidates:
        return None

    order = seat_order(mano_index, len(hands))
    priority = {player_index: index for index, player_index in enumerate(order)}
    best_player: int | None = None
    best_key: tuple | None = None

    for player_index in candidates:
        key = key_func(hands[player_index])
        if best_key is None or key > best_key:
            best_key = key
            best_player = player_index
            continue
        if key == best_key and priority[player_index] < priority[best_player]:
            best_player = player_index

    return best_player


def team_has(
    hands: list[list[Card]],
    variant: MusVariant,
    team: int,
    predicate: Callable[[list[Card], MusVariant], bool],
) -> bool:
    return any(predicate(hand, variant) for index, hand in enumerate(hands) if team_for_player(index) == team)


def evaluate_table(hands: list[list[Card]], mano_index: int, variant: MusVariant) -> dict:
    if len(hands) != 4 or any(len(hand) != 4 for hand in hands):
        raise MusRulesError("La mesa debe tener exactamente 4 jugadores con 4 cartas cada uno.")

    pair_players = [index for index, hand in enumerate(hands) if has_pairs(hand, variant)]
    game_players = [index for index, hand in enumerate(hands) if has_game(hand, variant)]
    nobody_has_game = len(game_players) == 0

    pair_teams = [team_has(hands, variant, team, has_pairs) for team in (0, 1)]
    game_teams = [team_has(hands, variant, team, has_game) for team in (0, 1)]

    pairs_winner = winner_index(
        hands,
        mano_index,
        lambda hand: pairs_key(hand, variant),
        eligible=pair_players,
    )
    game_winner = winner_index(
        hands,
        mano_index,
        lambda hand: juego_key(hand, variant),
        eligible=game_players,
    )
    point_winner = None
    if nobody_has_game:
        point_winner = winner_index(
            hands,
            mano_index,
            lambda hand: punto_key(hand, variant),
        )

    return {
        "grande": {
            "winner": winner_index(hands, mano_index, lambda hand: grande_key(hand, variant)),
            "active": True,
            "bettable": True,
        },
        "chica": {
            "winner": winner_index(hands, mano_index, lambda hand: chica_key(hand, variant)),
            "active": True,
            "bettable": True,
        },
        "pares": {
            "winner": pairs_winner,
            "active": pairs_winner is not None,
            "bettable": all(pair_teams),
            "team_available": pair_teams,
        },
        "juego": {
            "winner": game_winner,
            "active": game_winner is not None,
            "bettable": all(game_teams),
            "team_available": game_teams,
        },
        "punto": {
            "winner": point_winner,
            "active": point_winner is not None,
            "bettable": nobody_has_game,
            "reaches_point": nobody_has_game,
        },
    }


def describe_hand(hand: list[Card], variant: MusVariant) -> dict:
    total = game_total(hand, variant)
    pair_kind = pairs_name(hand, variant)
    juego_strength = juego_key(hand, variant)[0]
    if total >= 31:
        juego_label = f"juego {total}"
    else:
        juego_label = f"punto {total}"

    return {
        "cards": [{"code": card.code, "label": card.label} for card in hand],
        "grande": list(grande_key(hand, variant)),
        "chica": list(chica_key(hand, variant)),
        "pairs": {
            "kind": pair_kind,
            "hasPairs": pair_kind != "sin pares",
            "key": [pairs_key(hand, variant)[0], list(pairs_key(hand, variant)[1])],
        },
        "game": {
            "total": total,
            "hasGame": total >= 31,
            "label": juego_label,
            "strength": juego_strength,
        },
    }

