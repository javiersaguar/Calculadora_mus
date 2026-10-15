from __future__ import annotations

import random
from math import exp
from dataclasses import dataclass
from typing import Any

from .mus_rules import (
    Card,
    MusRulesError,
    MusVariant,
    describe_hand,
    effective_rank,
    evaluate_table,
    game_total,
    has_game,
    has_pairs,
    make_deck,
    parse_cards,
    pairs_key,
    team_for_player,
)


class SimulationError(ValueError):
    """Raised when a probability request cannot be simulated."""


LANCES = ("grande", "chica", "pares", "juego", "punto")


@dataclass
class LanceAccumulator:
    total_weight: float = 0.0
    active_weight: float = 0.0
    bettable_weight: float = 0.0
    team_win_weight: float = 0.0
    hero_win_weight: float = 0.0
    partner_win_weight: float = 0.0
    opponents_win_weight: float = 0.0

    def record(
        self,
        weight: float,
        result: dict,
        user_team: int,
        player_index: int,
        partner_index: int,
    ) -> None:
        self.total_weight += weight
        if result.get("active"):
            self.active_weight += weight
        if result.get("bettable"):
            self.bettable_weight += weight

        winner = result.get("winner")
        if winner is None:
            return

        if winner == player_index:
            self.hero_win_weight += weight
        elif winner == partner_index:
            self.partner_win_weight += weight

        if team_for_player(winner) == user_team:
            self.team_win_weight += weight
        else:
            self.opponents_win_weight += weight

    def to_dict(self) -> dict:
        return {
            "teamWin": probability(self.team_win_weight, self.total_weight),
            "teamWinWhenActive": probability(self.team_win_weight, self.active_weight),
            "heroWin": probability(self.hero_win_weight, self.total_weight),
            "partnerWin": probability(self.partner_win_weight, self.total_weight),
            "opponentsWin": probability(self.opponents_win_weight, self.total_weight),
            "active": probability(self.active_weight, self.total_weight),
            "bettable": probability(self.bettable_weight, self.total_weight),
        }


def probability(value: float, total: float) -> float:
    if total <= 0:
        return 0.0
    return max(0.0, min(1.0, value / total))


def clamp_int(value: Any, default: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    return max(minimum, min(maximum, parsed))


def normalize_player_index(value: Any, field_name: str) -> int:
    index = clamp_int(value, 0, 0, 3)
    if index not in (0, 1, 2, 3):
        raise SimulationError(f"{field_name} debe estar entre 0 y 3.")
    return index


def normalize_declaration(value: Any) -> str:
    if value in ("yes", "no", "unknown"):
        return value
    return "unknown"


def normalize_declarations(payload: dict, name: str) -> list[str]:
    declarations = payload.get("declarations") or {}
    raw_values = declarations.get(name) or []
    values = [normalize_declaration(value) for value in raw_values[:4]]
    while len(values) < 4:
        values.append("unknown")
    return values


def normalize_discard_counts(payload: dict) -> list[int | None]:
    raw_values = payload.get("discardCounts") or []
    values: list[int | None] = []
    for value in raw_values[:4]:
        if value in (None, "", "unknown"):
            values.append(None)
            continue
        values.append(clamp_int(value, 0, 0, 4))
    while len(values) < 4:
        values.append(None)
    return values


def variant_from_payload(payload: dict) -> MusVariant:
    raw = payload.get("variant") or {}
    if "eightKingsAndAces" in raw:
        enabled = bool(raw.get("eightKingsAndAces"))
        return MusVariant(eight_kings=enabled, eight_aces=enabled)
    return MusVariant(
        eight_kings=bool(raw.get("eightKings", True)),
        eight_aces=bool(raw.get("eightAces", True)),
    )


def known_hands_from_payload(payload: dict, player_index: int) -> list[list[Card]]:
    known_hands: list[list[Card]] = [[] for _ in range(4)]
    raw_known = payload.get("knownHands") or []
    for index, raw_hand in enumerate(raw_known[:4]):
        if raw_hand:
            known_hands[index] = parse_cards(raw_hand)

    hero_hand = payload.get("heroHand") or payload.get("playerCards") or []
    if hero_hand:
        parsed_hero = parse_cards(hero_hand)
        if len(parsed_hero) != 4:
            raise SimulationError("Tu mano debe tener exactamente 4 cartas.")
        if known_hands[player_index] and {card.code for card in known_hands[player_index]} != {
            card.code for card in parsed_hero
        }:
            raise SimulationError("Las cartas propias no coinciden con las cartas conocidas del jugador.")
        known_hands[player_index] = parsed_hero

    if len(known_hands[player_index]) != 4:
        raise SimulationError("Selecciona tus 4 cartas antes de calcular.")

    all_known = [card for hand in known_hands for card in hand]
    try:
        from .mus_rules import ensure_unique_cards

        ensure_unique_cards(all_known)
    except MusRulesError as exc:
        raise SimulationError(str(exc)) from exc

    for index, hand in enumerate(known_hands):
        if len(hand) > 4:
            raise SimulationError(f"El jugador {index + 1} tiene mas de 4 cartas conocidas.")

    return known_hands


def declarations_match(
    hands: list[list[Card]],
    variant: MusVariant,
    pair_declarations: list[str],
    game_declarations: list[str],
) -> bool:
    for index, hand in enumerate(hands):
        if len(hand) != 4:
            continue

        pair_declaration = pair_declarations[index]
        game_declaration = game_declarations[index]

        if pair_declaration == "yes" and not has_pairs(hand, variant):
            return False
        if pair_declaration == "no" and has_pairs(hand, variant):
            return False
        if game_declaration == "yes" and not has_game(hand, variant):
            return False
        if game_declaration == "no" and has_game(hand, variant):
            return False
    return True


def normalize_total_dealt_cards(payload: dict) -> int | None:
    raw_value = payload.get("totalDealtCards", payload.get("cardsDealtTotal", "unknown"))
    if raw_value in (None, "", "unknown"):
        return None
    return clamp_int(raw_value, 16, 16, 80)


def selection_opportunity(total_dealt_cards: int | None) -> float:
    if total_dealt_cards is None:
        return 0.55
    extra_cards = max(0, total_dealt_cards - 16)
    return min(1.35, 0.22 + (extra_cards / 24) * 0.95)


def cards_dealt_but_not_held(total_dealt_cards: int | None, available_after_current: int) -> int:
    if total_dealt_cards is None:
        return 0
    return min(max(0, total_dealt_cards - 16), max(0, available_after_current))


def clamp_float(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def card_keep_score(card: Card, variant: MusVariant) -> float:
    rank = effective_rank(card, variant)
    if rank == 12:
        return 2.35
    if rank == 11:
        return 1.25
    if rank == 10:
        return 0.68
    if rank == 7:
        return 0.28
    if rank == 1:
        return 0.16
    return -0.18


def hand_behavior_score(hand: list[Card], variant: MusVariant) -> float:
    ranks = [effective_rank(card, variant) for card in hand]
    pair_category = pairs_key(hand, variant)[0]
    total = game_total(hand, variant)

    card_score = sum(card_keep_score(card, variant) for card in hand)
    pair_bonus = {0: 0.0, 1: 0.62, 2: 1.55, 3: 2.2}[pair_category]
    game_bonus = 0.0
    if total == 31:
        game_bonus = 1.65
    elif total == 32:
        game_bonus = 1.35
    elif total >= 33:
        game_bonus = 0.62
    elif total == 30:
        game_bonus = 0.28

    king_count = ranks.count(12)
    horse_count = ranks.count(11)
    structure_bonus = 0.45 if king_count >= 2 else 0.0
    structure_bonus += 0.2 if king_count and horse_count else 0.0

    weak_hand_penalty = 0.0
    if king_count == 0 and horse_count == 0 and pair_category == 0 and total < 29:
        weak_hand_penalty = 0.85

    return card_score + pair_bonus + game_bonus + structure_bonus - weak_hand_penalty - 2.35


def retained_fraction(discard_count: int | None, opportunity: float) -> float:
    if discard_count is None:
        return 0.48 + opportunity * 0.22
    return {
        0: 1.16,
        1: 0.94,
        2: 0.68,
        3: 0.4,
        4: 0.12,
    }[discard_count]


def behavioral_hand_likelihood(
    hand: list[Card],
    discard_count: int | None,
    variant: MusVariant,
    opportunity: float,
) -> float:
    score = hand_behavior_score(hand, variant)
    retained = retained_fraction(discard_count, opportunity)
    base = exp(0.36 * opportunity * retained * score)
    return clamp_float(base * last_discard_likelihood(hand, discard_count, variant), 0.12, 9.5)


def last_discard_likelihood(hand: list[Card], discard_count: int | None, variant: MusVariant) -> float:
    if discard_count is None:
        return 1.0

    pair_category = pairs_key(hand, variant)[0]
    total = game_total(hand, variant)
    has_made_game = total >= 31
    has_strong_game = total in (31, 32)
    has_strong_pairs = pair_category >= 2

    if discard_count == 0:
        if has_strong_game or has_strong_pairs:
            return 3.2
        if pair_category == 1 or has_made_game:
            return 2.1
        return 0.55

    if discard_count == 1:
        if has_strong_pairs or has_strong_game:
            return 2.0
        if pair_category == 1 or has_made_game:
            return 1.45
        return 0.85

    if discard_count == 2:
        if pair_category or has_made_game:
            return 1.15
        return 1.0

    if discard_count == 3:
        if pair_category >= 2:
            return 0.9
        return 1.05

    return 1.0


def card_discardability(card: Card, variant: MusVariant) -> float:
    rank = effective_rank(card, variant)
    if rank == 12:
        return -2.25
    if rank == 11:
        return -1.05
    if rank == 10:
        return -0.25
    if rank == 7:
        return 0.18
    if rank in (5, 6):
        return 0.52
    if rank == 4:
        return 0.7
    if rank == 1:
        return 0.2
    return 0.45


def dead_cards_likelihood(dead_cards: list[Card], variant: MusVariant, opportunity: float) -> float:
    if not dead_cards:
        return 1.0
    discardability = sum(card_discardability(card, variant) for card in dead_cards)
    scaled = discardability / max(4, len(dead_cards))
    size_factor = min(2.0, len(dead_cards) / 8)
    return clamp_float(exp(0.42 * opportunity * size_factor * scaled), 0.16, 5.0)


def scenario_weight(
    hands: list[list[Card]],
    variant: MusVariant,
    discard_counts: list[int | None],
    discard_model: str,
    player_index: int,
    total_dealt_cards: int | None,
    dead_cards: list[Card],
) -> float:
    if discard_model != "heuristic":
        return 1.0

    opportunity = selection_opportunity(total_dealt_cards)
    weight = 1.0
    for index, hand in enumerate(hands):
        if index == player_index:
            continue
        weight *= behavioral_hand_likelihood(hand, discard_counts[index], variant, opportunity)
    weight *= dead_cards_likelihood(dead_cards, variant, opportunity)
    return weight


def empty_stats() -> dict[str, LanceAccumulator]:
    return {lance: LanceAccumulator() for lance in LANCES}


def calculate_probabilities(payload: dict) -> dict:
    variant = variant_from_payload(payload)
    player_index = normalize_player_index(payload.get("playerIndex", 0), "playerIndex")
    mano_index = normalize_player_index(payload.get("manoIndex", 0), "manoIndex")
    partner_index = (player_index + 2) % 4
    user_team = team_for_player(player_index)
    samples = clamp_int(payload.get("samples"), 20000, 1000, 200000)
    seed = payload.get("seed")
    rng = random.Random(seed)

    known_hands = known_hands_from_payload(payload, player_index)
    pair_declarations = normalize_declarations(payload, "pairs")
    game_declarations = normalize_declarations(payload, "game")
    discard_counts = normalize_discard_counts(payload)
    total_dealt_cards = normalize_total_dealt_cards(payload)
    discard_model = payload.get("discardModel") if payload.get("discardModel") in ("heuristic", "neutral") else "heuristic"

    if not declarations_match(known_hands, variant, pair_declarations, game_declarations):
        raise SimulationError("Las declaraciones no son compatibles con las cartas conocidas.")

    full_deck = make_deck()
    known_codes = {card.code for hand in known_hands for card in hand}
    deck = [card for card in full_deck if card.code not in known_codes]
    slots = [4 - len(hand) for hand in known_hands]
    unknown_total = sum(slots)
    max_dead_cards = max(0, len(deck) - unknown_total)
    dead_cards_to_model = cards_dealt_but_not_held(total_dealt_cards, max_dead_cards)
    reshuffle_pressure = bool(total_dealt_cards and total_dealt_cards > 40)
    opportunity = selection_opportunity(total_dealt_cards)

    accumulators = empty_stats()
    accepted = 0
    attempts = 0
    max_attempts = max(samples * 80, 5000)
    total_weight = 0.0
    total_weight_sq = 0.0
    game_reaches_point_weight = 0.0

    while accepted < samples and attempts < max_attempts:
        attempts += 1
        draw = rng.sample(deck, unknown_total) if unknown_total else []
        draw_codes = {card.code for card in draw}
        leftover = [card for card in deck if card.code not in draw_codes]
        dead_cards = rng.sample(leftover, dead_cards_to_model) if dead_cards_to_model else []
        offset = 0
        hands = [list(hand) for hand in known_hands]
        for index, slot_count in enumerate(slots):
            if slot_count:
                hands[index].extend(draw[offset : offset + slot_count])
                offset += slot_count

        if not declarations_match(hands, variant, pair_declarations, game_declarations):
            continue

        weight = scenario_weight(
            hands,
            variant,
            discard_counts,
            discard_model,
            player_index,
            total_dealt_cards,
            dead_cards,
        )
        table = evaluate_table(hands, mano_index, variant)
        for lance in LANCES:
            accumulators[lance].record(
                weight,
                table[lance],
                user_team=user_team,
                player_index=player_index,
                partner_index=partner_index,
            )

        if table["punto"]["reaches_point"]:
            game_reaches_point_weight += weight

        total_weight += weight
        total_weight_sq += weight * weight
        accepted += 1

    if accepted == 0 or total_weight <= 0:
        raise SimulationError(
            "No se han encontrado manos posibles con esos filtros. Revisa cartas conocidas y declaraciones."
        )

    effective_samples = int((total_weight * total_weight) / total_weight_sq) if total_weight_sq else 0

    if accepted < max(1000, samples * 0.15) or effective_samples < max(400, samples * 0.08):
        quality = "baja"
    elif accepted < samples or effective_samples < samples * 0.35:
        quality = "media"
    else:
        quality = "alta"

    metrics = {lance: accumulator.to_dict() for lance, accumulator in accumulators.items()}
    metrics["punto"]["reachesPoint"] = probability(game_reaches_point_weight, total_weight)

    hero_description = describe_hand(known_hands[player_index], variant)
    notes = build_notes(
        metrics,
        accepted,
        attempts,
        discard_model,
        total_dealt_cards,
        dead_cards_to_model,
        opportunity,
        reshuffle_pressure,
    )

    return {
        "metrics": metrics,
        "heroHand": hero_description,
        "meta": {
            "acceptedSamples": accepted,
            "attempts": attempts,
            "requestedSamples": samples,
            "effectiveSamples": effective_samples,
            "quality": quality,
            "algorithm": "montecarlo-behavioral" if discard_model == "heuristic" else "montecarlo-neutral",
            "discardModel": discard_model,
            "totalDealtCards": total_dealt_cards,
            "deadCardsModeled": dead_cards_to_model,
            "selectionOpportunity": opportunity,
            "reshufflePressure": reshuffle_pressure,
            "playerIndex": player_index,
            "manoIndex": mano_index,
            "partnerIndex": partner_index,
            "userTeam": user_team,
        },
        "notes": notes,
    }


def build_notes(
    metrics: dict,
    accepted: int,
    attempts: int,
    discard_model: str,
    total_dealt_cards: int | None,
    dead_cards_modeled: int,
    opportunity: float,
    reshuffle_pressure: bool,
) -> list[str]:
    notes: list[str] = []
    strongest = max(("grande", "chica", "pares", "juego"), key=lambda lance: metrics[lance]["teamWin"])
    weakest = min(("grande", "chica", "pares", "juego"), key=lambda lance: metrics[lance]["teamWin"])
    notes.append(
        f"Mejor lance estimado: {label_lance(strongest)} con {metrics[strongest]['teamWin'] * 100:.1f}% para tu pareja."
    )
    notes.append(
        f"Lance mas delicado: {label_lance(weakest)} con {metrics[weakest]['teamWin'] * 100:.1f}% para tu pareja."
    )
    if metrics["punto"].get("reachesPoint", 0) > 0.4:
        notes.append("Hay una probabilidad relevante de que la mano se resuelva a punto.")
    if discard_model == "heuristic":
        notes.append(
            "Modelo realista activo: favorece reyes, caballos, pares y juego fuerte, pero deja margen a manos raras."
        )
        if total_dealt_cards is None:
            notes.append("Cartas repartidas totales desconocidas: se usa una presion media de seleccion.")
        else:
            notes.append(
                f"Se modelan {total_dealt_cards} cartas repartidas en la mano y {dead_cards_modeled} cartas ya descartadas."
            )
        if reshuffle_pressure:
            notes.append("Como se superan 40 cartas, el posible reciclaje del descarte se trata como presion estrategica.")
        elif opportunity >= 0.9:
            notes.append("Muchas cartas repartidas elevan la probabilidad de que los rivales hayan filtrado cartas flojas.")
    if attempts > accepted * 4:
        notes.append("Los filtros de declaraciones descartan muchas combinaciones; conviene subir simulaciones si quieres mas precision.")
    return notes


def label_lance(lance: str) -> str:
    return {
        "grande": "grande",
        "chica": "chica",
        "pares": "pares",
        "juego": "juego",
        "punto": "punto",
    }[lance]
