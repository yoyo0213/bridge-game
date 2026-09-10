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


def create_scoring_context(
    winner_team_indexes,
    round_number=1,
    level=1,
    strain=Strain.CLUBS,
):
    players, teams = create_players_and_teams()
    bidding_result = BiddingResult(Bid(level, strain), players[0].player_id)
    assignment = assign_contract_to_teams(bidding_result, players, teams)
    winners = [teams[index].player1 for index in winner_team_indexes]
    round_ = create_completed_round(players, winners)
    round_result = create_round_result(round_, round_number, assignment)
    return ScoringContext(round_, round_result), players, teams


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


def score(context):
    return BaseScoringPolicy().calculate(context)


def test_decision_on_last_trick_keeps_every_trick_worth_two():
    context, _, _ = create_scoring_context([0, 1] * 6 + [0])

    result = score(context)

    assert result.bidding_team_score_delta == 14
    assert result.opposing_team_score_delta == 12
    assert result.total_score_delta == 26


def test_bidding_team_deciding_trick_is_two_and_later_tricks_are_three():
    context, _, _ = create_scoring_context([0] * 7 + [1, 0, 1, 0, 1, 0])

    result = score(context)

    assert result.bidding_team_score_delta == 23
    assert result.opposing_team_score_delta == 9
    assert result.total_score_delta == 32


def test_opposing_team_deciding_trick_is_two_and_later_tricks_are_three():
    context, _, _ = create_scoring_context([1] * 6 + [0, 1, 0, 1, 0, 1, 0])

    result = score(context)

    assert result.bidding_team_score_delta == 11
    assert result.opposing_team_score_delta == 20
    assert result.total_score_delta == 31


def test_transition_starts_after_the_exact_deciding_trick():
    context, _, _ = create_scoring_context([0] * 7 + [1] * 6)

    result = score(context)

    assert result.bidding_team_score_delta == 14
    assert result.opposing_team_score_delta == 18


@pytest.mark.parametrize("round_number", [2, 3])
def test_rounds_two_and_three_use_the_same_transition(round_number):
    context, _, _ = create_scoring_context(
        [0] * 7 + [1] * 6,
        round_number=round_number,
    )

    result = score(context)

    assert result.bidding_team_score_delta == 14
    assert result.opposing_team_score_delta == 18
    assert result.total_score_delta == 32


def test_round_four_scores_every_trick_at_four_despite_early_decision():
    context, _, _ = create_scoring_context(
        [0] * 7 + [1] * 6,
        round_number=4,
    )

    result = score(context)

    assert result.bidding_team_score_delta == 28
    assert result.opposing_team_score_delta == 24
    assert result.total_score_delta == 52


def test_round_four_all_thirteen_tricks_to_one_team_scores_fifty_two():
    context, _, _ = create_scoring_context([0] * 13, round_number=4)

    result = score(context)

    assert result.bidding_team_score_delta == 52
    assert result.opposing_team_score_delta == 0
    assert result.total_score_delta == 52


def test_level_four_opposing_target_does_not_decide_contract_failure():
    context, _, _ = create_scoring_context(
        [1] * 3 + [0] * 10,
        level=4,
    )

    result = score(context)

    assert context.round_result.opposing_team_target == 3
    assert result.bidding_team_score_delta == 20
    assert result.opposing_team_score_delta == 6
    assert result.total_score_delta == 26


def test_level_four_fourth_opposing_trick_decides_failure():
    context, _, _ = create_scoring_context(
        [1] * 4 + [0] * 9,
        level=4,
    )

    result = score(context)

    assert result.opposing_team_score_delta == 8
    assert result.bidding_team_score_delta == 27
    assert result.total_score_delta == 35


def test_level_seven_starts_undecided_and_can_succeed_after_thirteen_tricks():
    context, _, _ = create_scoring_context([0] * 13, level=7)

    result = score(context)

    assert context.round_result.opposing_team_target == 0
    assert result.bidding_team_score_delta == 26
    assert result.opposing_team_score_delta == 0


def test_level_seven_remains_alive_through_twelve_bidding_team_tricks():
    context, _, _ = create_scoring_context([0] * 12 + [1], level=7)

    result = score(context)

    assert result.bidding_team_score_delta == 24
    assert result.opposing_team_score_delta == 2
    assert result.total_score_delta == 26


def test_level_seven_first_opposing_trick_decides_failure_at_two_points():
    context, _, _ = create_scoring_context([1] + [0] * 12, level=7)

    result = score(context)

    assert result.opposing_team_score_delta == 2
    assert result.bidding_team_score_delta == 36
    assert result.total_score_delta == 38


def test_round_four_ignores_level_seven_failure_transition():
    context, _, _ = create_scoring_context(
        [1] + [0] * 12,
        round_number=4,
        level=7,
    )

    result = score(context)

    assert result.opposing_team_score_delta == 4
    assert result.bidding_team_score_delta == 48
    assert result.total_score_delta == 52


def test_no_trump_does_not_change_base_scoring():
    suit_context, _, _ = create_scoring_context([0] * 7 + [1] * 6)
    no_trump_context, _, _ = create_scoring_context(
        [0] * 7 + [1] * 6,
        strain=Strain.NO_TRUMP,
    )

    assert score(no_trump_context) == score(suit_context)


def test_scoring_rejects_round_result_that_does_not_match_round():
    context, _, _ = create_scoring_context([0] * 7 + [1] * 6)
    round_result_type = type(context.round_result)
    mismatched_result = round_result_type(
        round_number=context.round_result.round_number,
        contract_assignment=context.round_result.contract_assignment,
        bidding_team_trick_count=8,
        opposing_team_trick_count=5,
    )
    mismatched = ScoringContext(
        context.round_state,
        mismatched_result,
    )

    with pytest.raises(ValueError, match="do not match"):
        score(mismatched)


def test_invalid_round_number_is_rejected_before_scoring():
    context, _, _ = create_scoring_context([0] * 7 + [1] * 6)

    with pytest.raises(ValueError):
        type(context.round_result)(
            round_number=5,
            contract_assignment=context.round_result.contract_assignment,
            bidding_team_trick_count=7,
            opposing_team_trick_count=6,
        )


def test_scoring_does_not_mutate_domain_inputs_or_game_state():
    context, players, teams = create_scoring_context([0] * 7 + [1] * 6)
    game_state = GameState(players, teams)
    completed_tricks = list(context.round_state.completed_tricks)
    player_state = [player.__dict__.copy() for player in players]
    team_state = [team.__dict__.copy() for team in teams]
    game_state_snapshot = {
        "round_number": game_state.current_round_number,
        "round": game_state.current_round,
        "scores": game_state.team_scores.copy(),
        "finished": game_state.is_finished,
    }

    result = score(context)

    assert context.round_state.completed_tricks == completed_tricks
    assert [player.__dict__ for player in players] == player_state
    assert [team.__dict__ for team in teams] == team_state
    assert game_state.current_round_number == game_state_snapshot["round_number"]
    assert game_state.current_round is game_state_snapshot["round"]
    assert game_state.team_scores == game_state_snapshot["scores"]
    assert game_state.is_finished is game_state_snapshot["finished"]
    assert result == ScoringResult(14, 18)


def test_scoring_context_and_result_are_immutable():
    context, _, _ = create_scoring_context([0] * 7 + [1] * 6)
    result = score(context)

    with pytest.raises(FrozenInstanceError):
        context.round_result = None

    with pytest.raises(FrozenInstanceError):
        result.bidding_team_score_delta = 0
