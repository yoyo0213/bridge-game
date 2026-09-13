from dataclasses import FrozenInstanceError

import pytest

from bridge_game.cards.card import Card, Rank, Suit
from bridge_game.game.bid import Bid, Strain
from bridge_game.game.bidding_result import BiddingResult
from bridge_game.game.contract_assignment import assign_contract_to_teams
from bridge_game.game.game_state import GameState
from bridge_game.game.round import Round
from bridge_game.game.round_result import create_round_result
from bridge_game.game.scoring import (
    CONTRACT_BONUSES,
    BaseScoringPolicy,
    ScoringContext,
    ScoringResult,
)
from bridge_game.players.player import Player
from bridge_game.players.team import Team


def create_players_and_teams():
    players = [
        Player(1, "North", "North"),
        Player(2, "East", "East"),
        Player(3, "South", "South"),
        Player(4, "West", "West"),
    ]
    teams = [
        Team("North/South", players[0], players[2]),
        Team("East/West", players[1], players[3]),
    ]
    return players, teams


def create_completed_round(players, winners):
    round_ = Round(players)
    for desired_winner in winners:
        for _ in range(4):
            player = round_.current_player
            rank = Rank.ACE if player is desired_winner else Rank.TWO
            card = Card(Suit.CLUBS, rank)
            player.receive_card(card)
            round_.play_card(player, card)
    return round_


def create_scoring_context(bidding_tricks, contract=7, round_number=1):
    players, teams = create_players_and_teams()
    bidding_result = BiddingResult(
        Bid(contract - 6, Strain.CLUBS), players[0].player_id
    )
    assignment = assign_contract_to_teams(bidding_result, players, teams)
    winners = [teams[0].player1] * bidding_tricks + [
        teams[1].player1
    ] * (13 - bidding_tricks)
    round_ = create_completed_round(players, winners)
    result = create_round_result(round_, round_number, assignment)
    return ScoringContext(round_, result), players, teams


def score(context):
    return BaseScoringPolicy().calculate(context)


@pytest.mark.parametrize(
    ("contract", "bidding_tricks", "expected"),
    [
        (7, 6, 60),
        (7, 7, 110),
        (7, 8, 125),
        (9, 9, 155),
        (9, 10, 170),
        (13, 13, 365),
    ],
)
def test_contract_team_scoring(contract, bidding_tricks, expected):
    context, _, _ = create_scoring_context(bidding_tricks, contract)
    assert score(context).bidding_team_score_delta == expected


@pytest.mark.parametrize(
    ("defending_tricks", "expected"), [(0, 0), (4, 60), (6, 90)]
)
def test_defending_team_scores_fifteen_per_trick(defending_tricks, expected):
    context, _, _ = create_scoring_context(13 - defending_tricks)
    assert score(context).opposing_team_score_delta == expected


def test_contract_bonus_table_is_defined_once():
    assert CONTRACT_BONUSES == {
        7: 40,
        8: 50,
        9: 65,
        10: 90,
        11: 125,
        12: 170,
        13: 235,
    }


def test_round_number_does_not_change_scoring():
    first, _, _ = create_scoring_context(8, round_number=1)
    fourth, _, _ = create_scoring_context(8, round_number=4)
    assert score(first) == score(fourth) == ScoringResult(125, 75)


def test_scoring_rejects_round_result_that_does_not_match_round():
    context, _, _ = create_scoring_context(7)
    mismatched_result = type(context.round_result)(
        round_number=context.round_result.round_number,
        contract_assignment=context.round_result.contract_assignment,
        bidding_team_trick_count=8,
        opposing_team_trick_count=5,
    )
    with pytest.raises(ValueError, match="do not match"):
        score(ScoringContext(context.round_state, mismatched_result))


def test_scoring_does_not_mutate_domain_inputs_or_game_state():
    context, players, teams = create_scoring_context(7)
    game_state = GameState(players, teams)
    completed_tricks = list(context.round_state.completed_tricks)
    player_state = [player.__dict__.copy() for player in players]
    team_state = [team.__dict__.copy() for team in teams]
    result = score(context)
    assert context.round_state.completed_tricks == completed_tricks
    assert [player.__dict__ for player in players] == player_state
    assert [team.__dict__ for team in teams] == team_state
    assert game_state.team_scores == {teams[0]: 0, teams[1]: 0}
    assert result == ScoringResult(110, 90)


def test_scoring_context_and_result_are_immutable():
    context, _, _ = create_scoring_context(7)
    result = score(context)
    with pytest.raises(FrozenInstanceError):
        context.round_result = None
    with pytest.raises(FrozenInstanceError):
        result.bidding_team_score_delta = 0
