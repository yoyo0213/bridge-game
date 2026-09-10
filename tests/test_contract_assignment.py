from dataclasses import FrozenInstanceError

import pytest

from bridge_game.game.bid import Bid, Strain
from bridge_game.game.bidding_result import BiddingResult
from bridge_game.game.contract_assignment import (
    ContractAssignment,
    assign_contract_to_teams,
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


def test_team_a_bidder_assigns_original_team_objects():
    players, teams = create_players_and_teams()
    result = BiddingResult(Bid(3, Strain.HEARTS), bidder_id=3)

    assignment = assign_contract_to_teams(result, players, teams)

    assert assignment.bidding_team is teams[0]
    assert assignment.opposing_team is teams[1]


def test_team_b_bidder_assigns_original_team_objects():
    players, teams = create_players_and_teams()
    result = BiddingResult(Bid(3, Strain.SPADES), bidder_id=4)

    assignment = assign_contract_to_teams(result, players, teams)

    assert assignment.bidding_team is teams[1]
    assert assignment.opposing_team is teams[0]


@pytest.mark.parametrize(
    ("bid", "bidding_target", "opposing_target"),
    [
        (Bid(1, Strain.CLUBS), 7, 6),
        (Bid(7, Strain.SPADES), 13, 0),
        (Bid(4, Strain.NO_TRUMP), 10, 3),
    ],
)
def test_contract_targets_come_from_bidding_result(
    bid,
    bidding_target,
    opposing_target,
):
    players, teams = create_players_and_teams()
    result = BiddingResult(bid, bidder_id=1)

    assignment = assign_contract_to_teams(result, players, teams)

    assert assignment.bidding_team_target == result.bidder_target
    assert assignment.opposing_team_target == result.opponent_target
    assert assignment.bidding_team_target == bidding_target
    assert assignment.opposing_team_target == opposing_target


def test_unknown_bidder_id_is_rejected():
    players, teams = create_players_and_teams()
    result = BiddingResult(Bid(2, Strain.DIAMONDS), bidder_id="unknown")

    with pytest.raises(ValueError):
        assign_contract_to_teams(result, players, teams)


def test_bidder_not_assigned_to_a_game_team_is_rejected():
    players, _ = create_players_and_teams()
    replacement = Player(5, "Replacement", "North")
    inconsistent_teams = [
        Team("North/South", replacement, players[2]),
        Team("East/West", players[1], players[3]),
    ]
    result = BiddingResult(Bid(2, Strain.DIAMONDS), bidder_id=1)

    with pytest.raises(ValueError):
        assign_contract_to_teams(result, players, inconsistent_teams)


def test_bidder_assigned_to_both_teams_is_rejected():
    players, _ = create_players_and_teams()
    inconsistent_teams = [
        Team("One", players[0], players[2]),
        Team("Two", players[0], players[3]),
    ]
    result = BiddingResult(Bid(2, Strain.DIAMONDS), bidder_id=1)

    with pytest.raises(ValueError):
        assign_contract_to_teams(result, players, inconsistent_teams)


def test_all_pass_result_is_rejected_explicitly():
    players, teams = create_players_and_teams()
    result = BiddingResult(bid=None, bidder_id=None)

    with pytest.raises(ValueError, match="without a bidding contract"):
        assign_contract_to_teams(result, players, teams)


def test_contract_assignment_is_immutable_and_does_not_mutate_inputs():
    players, teams = create_players_and_teams()
    result = BiddingResult(Bid(5, Strain.NO_TRUMP), bidder_id=2)
    player_state = [player.__dict__.copy() for player in players]
    team_state = [team.__dict__.copy() for team in teams]

    assignment = assign_contract_to_teams(result, players, teams)

    assert isinstance(assignment, ContractAssignment)
    assert result == BiddingResult(Bid(5, Strain.NO_TRUMP), bidder_id=2)
    assert [player.__dict__ for player in players] == player_state
    assert [team.__dict__ for team in teams] == team_state

    with pytest.raises(FrozenInstanceError):
        assignment.bidding_team_target = 0
