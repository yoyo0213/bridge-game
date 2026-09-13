import pytest

from bridge_game.cards.card import Card, Rank, Suit
from bridge_game.game.bid import Bid, Strain
from bridge_game.game.bidding_result import BiddingResult
from bridge_game.game.game_state import GameState
from bridge_game.game.round import Round
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


def create_completed_round(players, winners=None, contract=7):
    winners = winners or [players[3]] * 13
    round_ = Round(players)
    round_.set_bidding_result(
        BiddingResult(
            Bid(contract - 6, Strain.CLUBS), players[0].player_id
        )
    )
    for desired_winner in winners:
        for _ in range(4):
            player = round_.current_player
            rank = Rank.ACE if player is desired_winner else Rank.TWO
            card = Card(Suit.CLUBS, rank)
            player.receive_card(card)
            round_.play_card(player, card)

    return round_


def test_game_state_initial_state():
    players, teams = create_players_and_teams()

    game_state = GameState(players, teams)

    assert game_state.players == players
    assert game_state.teams == teams
    assert game_state.current_round_number == 1
    assert game_state.current_round is None
    assert game_state.is_finished is False


def test_player_scores_initially_zero_and_team_has_no_score_state():
    players, teams = create_players_and_teams()

    GameState(players, teams)

    assert all(player.score == 0 for player in players)
    assert all(not hasattr(team, "score") for team in teams)


@pytest.mark.parametrize("player_count", [3, 5])
def test_game_state_requires_exactly_four_players(player_count):
    players, teams = create_players_and_teams()
    candidate_players = players + [Player(5, "Extra", "Extra")]

    with pytest.raises(ValueError):
        GameState(candidate_players[:player_count], teams)


def test_game_state_rejects_duplicate_player_ids():
    players, teams = create_players_and_teams()
    players[3].player_id = players[0].player_id

    with pytest.raises(ValueError):
        GameState(players, teams)


@pytest.mark.parametrize("team_count", [1, 3])
def test_game_state_requires_exactly_two_teams(team_count):
    players, teams = create_players_and_teams()
    extra_team = Team("Extra", players[0], players[1])

    with pytest.raises(ValueError):
        GameState(players, (teams + [extra_team])[:team_count])


def test_each_player_must_belong_to_exactly_one_team():
    players, _ = create_players_and_teams()
    invalid_teams = [
        Team("One", players[0], players[1]),
        Team("Two", players[1], players[2]),
    ]

    with pytest.raises(ValueError):
        GameState(players, invalid_teams)


@pytest.mark.parametrize("round_number", [1, 2, 3, 4])
def test_game_state_accepts_valid_round_numbers(round_number):
    players, teams = create_players_and_teams()

    game_state = GameState(players, teams, current_round_number=round_number)

    assert game_state.current_round_number == round_number


@pytest.mark.parametrize("round_number", [0, 5])
def test_game_state_rejects_out_of_range_round_numbers(round_number):
    players, teams = create_players_and_teams()

    with pytest.raises(ValueError):
        GameState(players, teams, current_round_number=round_number)


def test_game_state_rejects_non_integer_round_number():
    players, teams = create_players_and_teams()

    with pytest.raises(TypeError):
        GameState(players, teams, current_round_number="1")


def test_start_round_tracks_current_round():
    players, teams = create_players_and_teams()
    game_state = GameState(players, teams)
    round_ = Round(players)

    game_state.start_round(round_)

    assert game_state.current_round is round_


def test_start_round_rejects_different_players():
    players, teams = create_players_and_teams()
    other_players, _ = create_players_and_teams()
    game_state = GameState(players, teams)

    with pytest.raises(ValueError):
        game_state.start_round(Round(other_players))


def test_incomplete_round_cannot_be_completed():
    players, teams = create_players_and_teams()
    game_state = GameState(players, teams)
    game_state.start_round(Round(players))

    with pytest.raises(ValueError):
        game_state.complete_current_round()

    assert game_state.current_round_number == 1
    assert game_state.is_finished is False


def test_completing_round_applies_individual_scores_and_advances_round():
    players, teams = create_players_and_teams()
    game_state = GameState(players, teams)
    game_state.start_round(create_completed_round(players))

    result = game_state.complete_current_round()

    assert game_state.current_round_number == 2
    assert game_state.current_round is None
    assert players[3].score == 195
    assert all(player.score == 0 for player in players[:3])
    assert game_state.round_results == [result]
    assert game_state.is_finished is False


def test_completing_fourth_round_finishes_game():
    players, teams = create_players_and_teams()
    game_state = GameState(players, teams, current_round_number=4)
    game_state.start_round(create_completed_round(players))

    game_state.complete_current_round()

    assert game_state.current_round_number == 4
    assert game_state.current_round is None
    assert game_state.is_finished is True

    with pytest.raises(ValueError):
        game_state.start_round(Round(players))


def test_scores_accumulate_across_rounds_without_being_reset():
    players, teams = create_players_and_teams()
    game_state = GameState(players, teams)

    round_one_winners = [players[0]] * 6 + [players[2]] + [players[1]] * 6
    game_state.start_round(create_completed_round(players, round_one_winners))
    game_state.complete_current_round()
    assert players[0].score == 100

    round_two_winners = [players[0]] * 5 + [players[1]] * 8
    game_state.start_round(
        create_completed_round(players, round_two_winners, contract=9)
    )
    game_state.complete_current_round()

    assert players[0].score == 150
    assert len(game_state.round_results) == 2


def test_completed_trick_scores_immediately_and_only_once():
    players, teams = create_players_and_teams()
    game_state = GameState(players, teams)
    round_ = Round(players)
    round_.set_bidding_result(
        BiddingResult(Bid(1, Strain.CLUBS), players[0].player_id)
    )
    game_state.start_round(round_)
    for player in players:
        rank = Rank.ACE if player is players[0] else Rank.TWO
        card = Card(Suit.CLUBS, rank)
        player.receive_card(card)
        round_.play_card(player, card)

    game_state.score_current_round_progress()
    game_state.score_current_round_progress()

    assert players[0].score == 10
    assert [player.score for player in players[1:]] == [0, 0, 0]
