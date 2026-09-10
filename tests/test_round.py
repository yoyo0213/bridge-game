import pytest

from bridge_game.cards.card import Card, Rank, Suit
from bridge_game.game.round import Round
from bridge_game.players.player import Player
from bridge_game.game.bid import Bid, Strain
from bridge_game.game.bidding_result import BiddingResult


def create_players():
    return [
        Player(1, "North", "North"),
        Player(2, "East", "East"),
        Player(3, "South", "South"),
        Player(4, "West", "West"),
    ]


def test_round_requires_four_players():
    players = create_players()

    with pytest.raises(ValueError):
        Round(players[:3])


def test_round_requires_unique_players_and_player_ids():
    players = create_players()

    with pytest.raises(ValueError):
        Round([players[0], players[1], players[2], players[0]])

    players[3].player_id = players[0].player_id

    with pytest.raises(ValueError):
        Round(players)


@pytest.mark.parametrize("leader_index", [-1, 4])
def test_round_rejects_invalid_leader_index(leader_index):
    with pytest.raises(ValueError):
        Round(create_players(), leader_index=leader_index)


def test_round_starts_with_selected_leader():
    players = create_players()

    round_ = Round(players, leader_index=2)

    assert round_.current_player == players[2]
    assert round_.current_trick.leader == players[2]


def test_players_take_turns_in_order():
    players = create_players()

    cards = [
        Card(Suit.CLUBS, Rank.TWO),
        Card(Suit.CLUBS, Rank.THREE),
    ]

    players[0].receive_card(cards[0])
    players[1].receive_card(cards[1])

    round_ = Round(players)

    round_.play_card(players[0], cards[0])

    assert round_.current_player == players[1]


def test_player_cannot_play_out_of_turn():
    players = create_players()

    card = Card(Suit.CLUBS, Rank.ACE)
    players[1].receive_card(card)

    round_ = Round(players)

    with pytest.raises(ValueError):
        round_.play_card(players[1], card)


def test_trick_winner_leads_next_trick():
    players = create_players()

    cards = [
        Card(Suit.HEARTS, Rank.TWO),
        Card(Suit.HEARTS, Rank.ACE),
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.HEARTS, Rank.QUEEN),
    ]

    for player, card in zip(players, cards):
        player.receive_card(card)

    round_ = Round(players)

    winner = None

    for player, card in zip(players, cards):
        winner = round_.play_card(player, card)

    assert winner == players[1]
    assert len(round_.completed_tricks) == 1
    assert round_.current_player == players[1]
    assert round_.current_trick.leader == players[1]


def test_round_accepts_bidding_result():
    players = create_players()
    round_ = Round(players)

    result = BiddingResult(
        Bid(4, Strain.HEARTS),
        3,
    )

    round_.set_bidding_result(result)

    assert round_.bidding_result == result
    assert round_.bidder_id == 3
    assert round_.bidder_target == 10
    assert round_.opponent_target == 3
    assert round_.trump == Suit.HEARTS
    assert round_.current_trick.trump == Suit.HEARTS


def test_round_supports_no_trump():
    players = create_players()
    round_ = Round(players)

    result = BiddingResult(
        Bid(3, Strain.NO_TRUMP),
        1,
    )

    round_.set_bidding_result(result)

    assert round_.trump is None
    assert round_.current_trick.trump is None
    assert round_.bidder_target == 9
    assert round_.opponent_target == 4


def test_round_rejects_all_pass_result():
    players = create_players()
    round_ = Round(players)

    result = BiddingResult(
        bid=None,
        bidder_id=None,
    )

    with pytest.raises(ValueError):
        round_.set_bidding_result(result)


def test_round_rejects_bidding_result_for_unknown_bidder():
    round_ = Round(create_players())
    result = BiddingResult(Bid(2, Strain.CLUBS), "unknown")

    with pytest.raises(ValueError):
        round_.set_bidding_result(result)

    assert round_.bidding_result is None
    assert round_.trump is None


def test_bidding_result_cannot_be_changed_after_it_is_set():
    round_ = Round(create_players())
    first_result = BiddingResult(Bid(2, Strain.CLUBS), 1)
    second_result = BiddingResult(Bid(3, Strain.SPADES), 2)
    round_.set_bidding_result(first_result)

    with pytest.raises(ValueError):
        round_.set_bidding_result(second_result)

    assert round_.bidding_result == first_result
    assert round_.trump == Suit.CLUBS


def test_bidding_result_cannot_be_set_after_play_starts():
    players = create_players()
    card = Card(Suit.CLUBS, Rank.TWO)
    players[0].receive_card(card)
    round_ = Round(players)
    original_trick = round_.current_trick
    round_.play_card(players[0], card)

    with pytest.raises(ValueError):
        round_.set_bidding_result(BiddingResult(Bid(2, Strain.HEARTS), 1))

    assert round_.bidding_result is None
    assert round_.current_trick is original_trick
    assert len(round_.current_trick) == 1


def test_bidding_trump_is_used_by_later_tricks():
    players = create_players()
    cards = [
        Card(Suit.HEARTS, Rank.ACE),
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.SPADES, Rank.TWO),
        Card(Suit.HEARTS, Rank.QUEEN),
    ]
    for player, card in zip(players, cards):
        player.receive_card(card)

    round_ = Round(players)
    round_.set_bidding_result(BiddingResult(Bid(2, Strain.SPADES), 1))

    for player, card in zip(players, cards):
        round_.play_card(player, card)

    assert round_.current_trick.leader == players[2]
    assert round_.current_trick.trump == Suit.SPADES


def test_round_finishes_after_exactly_thirteen_tricks():
    players = create_players()
    ranks = [Rank.JACK, Rank.QUEEN, Rank.KING, Rank.ACE]
    for player, rank in zip(players, ranks):
        for _ in range(13):
            player.receive_card(Card(Suit.CLUBS, rank))

    round_ = Round(players)

    for _ in range(52):
        player = round_.current_player
        round_.play_card(player, player.hand.cards[0])

    assert round_.is_complete
    assert len(round_.completed_tricks) == 13
    assert round_.current_player is None
    assert round_.current_trick is round_.completed_tricks[-1]

    extra_card = Card(Suit.CLUBS, Rank.TWO)
    players[3].receive_card(extra_card)
    with pytest.raises(ValueError):
        round_.play_card(players[3], extra_card)

    assert extra_card in players[3].hand
