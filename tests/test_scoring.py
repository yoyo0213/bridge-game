import pytest

from bridge_game.cards.card import Card, Rank, Suit
from bridge_game.game.bid import Bid, Strain
from bridge_game.game.bidding_result import BiddingResult
from bridge_game.game.contract_assignment import assign_contract_to_teams
from bridge_game.game.round import Round
from bridge_game.game.round_result import create_round_result
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


def result_for(winner_indexes, contract=7):
    players, teams = create_players_and_teams()
    assignment = assign_contract_to_teams(
        BiddingResult(Bid(contract - 6, Strain.CLUBS), players[0].player_id),
        players,
        teams,
    )
    winners = [players[index] for index in winner_indexes]
    round_ = create_completed_round(players, winners)
    return create_round_result(round_, 1, assignment), players, teams


def test_contract_trick_points_belong_to_individual_winner():
    result, players, _ = result_for([0] + [1] * 12)
    assert result.player_round_scores[players[0].player_id] == 10
    assert result.player_round_scores[players[2].player_id] == 0


def test_contract_partners_keep_independent_scores():
    result, players, _ = result_for([0] * 4 + [2] * 2 + [1] * 7)
    assert result.player_round_scores[players[0].player_id] == 40
    assert result.player_round_scores[players[2].player_id] == 20


def test_contract_bonus_goes_to_bidder_not_seventh_trick_winner():
    result, players, _ = result_for([0] * 6 + [2] + [1] * 6)
    assert result.player_round_scores[players[0].player_id] == 100
    assert result.player_round_scores[players[2].player_id] == 10
    assert result.contract_bonus_awarded is True


def test_overtrick_gives_fifteen_to_its_winner():
    result, players, _ = result_for([0] * 7 + [2] + [1] * 5)
    assert result.player_round_scores[players[2].player_id] == 15


def test_contract_nine_combines_partner_tricks_but_keeps_scores_separate():
    result, players, _ = result_for([0] * 5 + [2] * 4 + [1] * 4, contract=9)
    assert result.player_round_scores[players[0].player_id] == 115
    assert result.player_round_scores[players[2].player_id] == 40
    assert result.bidding_team_trick_count == 9
    assert result.contract_met is True


def test_unmade_contract_keeps_trick_points_without_bonus():
    result, players, _ = result_for([0] * 5 + [2] * 3 + [1] * 5, contract=9)
    assert result.player_round_scores[players[0].player_id] == 50
    assert result.player_round_scores[players[2].player_id] == 30
    assert result.contract_bonus_awarded is False


def test_defenders_score_individually():
    result, players, _ = result_for([0] * 9 + [1] * 3 + [3], contract=9)
    assert result.player_round_scores[players[1].player_id] == 45
    assert result.player_round_scores[players[3].player_id] == 15


def test_contract_bonus_is_awarded_only_once_with_overtricks():
    result, players, _ = result_for([0] * 7 + [2] * 3 + [1] * 3)
    assert result.player_round_scores[players[0].player_id] == 110
    assert result.player_round_scores[players[2].player_id] == 45
    assert sum(result.player_round_scores.values()) == 200


def test_creating_round_result_does_not_mutate_player_totals():
    result, players, _ = result_for([0] * 7 + [1] * 6)
    assert result.player_round_scores[players[0].player_id] == 110
    assert all(player.score == 0 for player in players)


def test_round_score_mappings_are_immutable():
    result, players, _ = result_for([0] * 7 + [1] * 6)
    with pytest.raises(TypeError):
        result.player_round_scores[players[0].player_id] = 0
