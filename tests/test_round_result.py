from dataclasses import FrozenInstanceError

import pytest

from bridge_game.cards.card import Card, Rank, Suit
from bridge_game.game.bid import Bid, Strain
from bridge_game.game.bidding_result import BiddingResult
from bridge_game.game.contract_assignment import assign_contract_to_teams
from bridge_game.game.round import Round
from bridge_game.game.round_result import RoundResult, create_round_result
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


def create_assignment(players, teams, level=1, strain=Strain.CLUBS):
    result = BiddingResult(Bid(level, strain), bidder_id=players[0].player_id)
    return assign_contract_to_teams(result, players, teams)


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


def test_create_valid_round_result_and_preserve_team_identity():
    players, teams = create_players_and_teams()
    assignment = create_assignment(players, teams, level=3)
    round_ = create_completed_round(players, [players[0]] * 9 + [players[1]] * 4)

    result = create_round_result(round_, 2, assignment)

    assert result.round_number == 2
    assert result.contract_assignment is assignment
    assert result.bidding_team is teams[0]
    assert result.opposing_team is teams[1]
    assert result.bidding_team_target == 9
    assert result.opposing_team_target == 4
    assert result.bidding_team_trick_count == 9
    assert result.opposing_team_trick_count == 4
    assert result.bidding_team_met_target is True
    assert result.opposing_team_met_target is True


@pytest.mark.parametrize("round_number", [1, 2, 3, 4])
def test_valid_round_numbers(round_number):
    players, teams = create_players_and_teams()
    assignment = create_assignment(players, teams)
    round_ = create_completed_round(players, [players[0]] * 7 + [players[1]] * 6)

    result = create_round_result(round_, round_number, assignment)

    assert result.round_number == round_number


@pytest.mark.parametrize("round_number", [0, 5])
def test_invalid_round_numbers_are_rejected(round_number):
    players, teams = create_players_and_teams()
    assignment = create_assignment(players, teams)
    round_ = create_completed_round(players, [players[0]] * 13)

    with pytest.raises(ValueError):
        create_round_result(round_, round_number, assignment)


def test_non_integer_round_number_is_rejected():
    players, teams = create_players_and_teams()
    assignment = create_assignment(players, teams)
    round_ = create_completed_round(players, [players[0]] * 13)

    with pytest.raises(TypeError):
        create_round_result(round_, "1", assignment)


@pytest.mark.parametrize(
    (
        "level",
        "bidding_tricks",
        "bidding_met",
        "opposing_met",
    ),
    [
        (1, 7, True, True),
        (1, 6, False, True),
        (7, 13, True, True),
        (7, 12, False, True),
    ],
)
def test_target_boundaries(
    level,
    bidding_tricks,
    bidding_met,
    opposing_met,
):
    players, teams = create_players_and_teams()
    assignment = create_assignment(players, teams, level=level)
    winners = (
        [players[0]] * bidding_tricks
        + [players[1]] * (13 - bidding_tricks)
    )
    round_ = create_completed_round(players, winners)

    result = create_round_result(round_, 1, assignment)

    assert result.bidding_team_trick_count == bidding_tricks
    assert result.opposing_team_trick_count == 13 - bidding_tricks
    assert result.bidding_team_met_target is bidding_met
    assert result.opposing_team_met_target is opposing_met
    assert (
        result.bidding_team_trick_count
        + result.opposing_team_trick_count
        == 13
    )


def test_all_thirteen_tricks_can_be_won_by_opposing_team():
    players, teams = create_players_and_teams()
    assignment = create_assignment(players, teams, level=1)
    round_ = create_completed_round(players, [players[1]] * 13)

    result = create_round_result(round_, 1, assignment)

    assert result.bidding_team_trick_count == 0
    assert result.opposing_team_trick_count == 13
    assert result.bidding_team_met_target is False
    assert result.opposing_team_met_target is True


def test_opposing_team_can_miss_target():
    players, teams = create_players_and_teams()
    assignment = create_assignment(players, teams, level=1)
    round_ = create_completed_round(players, [players[0]] * 8 + [players[1]] * 5)

    result = create_round_result(round_, 1, assignment)

    assert result.bidding_team_met_target is True
    assert result.opposing_team_met_target is False


def test_incomplete_round_is_rejected():
    players, teams = create_players_and_teams()
    assignment = create_assignment(players, teams)

    with pytest.raises(ValueError, match="exactly 13"):
        create_round_result(Round(players), 1, assignment)


@pytest.mark.parametrize("trick_count", [12, 14])
def test_wrong_number_of_completed_tricks_is_rejected(trick_count):
    players, teams = create_players_and_teams()
    assignment = create_assignment(players, teams)
    round_ = create_completed_round(players, [players[0]] * 13)

    if trick_count == 12:
        round_.completed_tricks.pop()
    else:
        round_.completed_tricks.append(round_.completed_tricks[-1])

    with pytest.raises(ValueError, match="exactly 13"):
        create_round_result(round_, 1, assignment)


def test_winner_not_belonging_to_either_team_is_rejected():
    players, teams = create_players_and_teams()
    assignment = create_assignment(players, teams)
    round_ = create_completed_round(players, [players[0]] * 13)
    outsider = Player(5, "Outsider", "Outside")
    winning_card = round_.completed_tricks[0].plays[0][1]
    round_.completed_tricks[0].plays[0] = (outsider, winning_card)

    with pytest.raises(ValueError, match="exactly one team"):
        create_round_result(round_, 1, assignment)


def test_winner_belonging_to_both_teams_is_rejected():
    players, teams = create_players_and_teams()
    assignment = create_assignment(players, teams)
    assignment.opposing_team.player1 = players[0]
    round_ = create_completed_round(players, [players[0]] * 13)

    with pytest.raises(ValueError, match="exactly one team"):
        create_round_result(round_, 1, assignment)


def test_round_result_is_immutable():
    players, teams = create_players_and_teams()
    assignment = create_assignment(players, teams)
    round_ = create_completed_round(players, [players[0]] * 7 + [players[1]] * 6)
    result = create_round_result(round_, 1, assignment)

    with pytest.raises(FrozenInstanceError):
        result.bidding_team_trick_count = 0


def test_creating_round_result_does_not_mutate_inputs():
    players, teams = create_players_and_teams()
    assignment = create_assignment(players, teams)
    round_ = create_completed_round(players, [players[0]] * 7 + [players[1]] * 6)
    completed_tricks = list(round_.completed_tricks)
    team_state = [team.__dict__.copy() for team in teams]

    result = create_round_result(round_, 1, assignment)

    assert result.contract_assignment is assignment
    assert round_.completed_tricks == completed_tricks
    assert [team.__dict__ for team in teams] == team_state


def test_no_trump_does_not_change_result_semantics():
    players, teams = create_players_and_teams()
    assignment = create_assignment(
        players,
        teams,
        level=2,
        strain=Strain.NO_TRUMP,
    )
    round_ = create_completed_round(players, [players[0]] * 8 + [players[1]] * 5)

    result = create_round_result(round_, 3, assignment)

    assert result.bidding_team_target == 8
    assert result.opposing_team_target == 5
    assert result.bidding_team_trick_count == 8
    assert result.opposing_team_trick_count == 5
    assert result.bidding_team_met_target is True
    assert result.opposing_team_met_target is True
