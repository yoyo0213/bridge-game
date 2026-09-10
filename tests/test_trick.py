import pytest

from bridge_game.cards.card import Card, Rank, Suit
from bridge_game.game.trick import Trick
from bridge_game.players.player import Player


def create_players():
    return [
        Player(1, "North", "North"),
        Player(2, "East", "East"),
        Player(3, "South", "South"),
        Player(4, "West", "West"),
    ]


def test_new_trick_is_empty():
    players = create_players()

    trick = Trick(players[0])

    assert len(trick) == 0
    assert trick.lead_suit is None
    assert not trick.is_complete


def test_first_card_sets_lead_suit():
    players = create_players()

    card = Card(Suit.HEARTS, Rank.TEN)
    players[0].receive_card(card)

    trick = Trick(players[0])
    trick.play_card(players[0], card)

    assert trick.lead_suit == Suit.HEARTS
    assert len(trick) == 1


def test_leader_must_play_first():
    players = create_players()
    card = Card(Suit.HEARTS, Rank.TEN)
    players[1].receive_card(card)

    trick = Trick(players[0])

    with pytest.raises(ValueError):
        trick.play_card(players[1], card)

    assert card in players[1].hand
    assert len(trick) == 0


def test_player_cannot_play_twice_in_same_trick():
    players = create_players()
    first_card = Card(Suit.HEARTS, Rank.TEN)
    second_card = Card(Suit.HEARTS, Rank.JACK)
    players[0].receive_card(first_card)
    players[0].receive_card(second_card)

    trick = Trick(players[0])
    trick.play_card(players[0], first_card)

    with pytest.raises(ValueError):
        trick.play_card(players[0], second_card)

    assert second_card in players[0].hand
    assert len(trick) == 1


def test_play_card_removes_card_from_player_hand():
    players = create_players()

    card = Card(Suit.SPADES, Rank.ACE)
    players[0].receive_card(card)

    trick = Trick(players[0])
    trick.play_card(players[0], card)

    assert card not in players[0].hand


def test_illegal_play_raises_error():
    players = create_players()

    heart_ace = Card(Suit.HEARTS, Rank.ACE)
    heart_two = Card(Suit.HEARTS, Rank.TWO)
    spade_king = Card(Suit.SPADES, Rank.KING)

    players[0].receive_card(heart_ace)

    players[1].receive_card(heart_two)
    players[1].receive_card(spade_king)

    trick = Trick(players[0])

    trick.play_card(players[0], heart_ace)

    with pytest.raises(ValueError):
        trick.play_card(players[1], spade_king)


def test_highest_card_of_lead_suit_wins_without_trump():
    players = create_players()

    cards = [
        Card(Suit.HEARTS, Rank.TEN),
        Card(Suit.HEARTS, Rank.ACE),
        Card(Suit.CLUBS, Rank.ACE),
        Card(Suit.HEARTS, Rank.KING),
    ]

    for player, card in zip(players, cards):
        player.receive_card(card)

    trick = Trick(players[0])

    for player, card in zip(players, cards):
        trick.play_card(player, card)

    assert trick.is_complete
    assert trick.winner() == players[1]


def test_trump_card_beats_lead_suit():
    players = create_players()

    cards = [
        Card(Suit.HEARTS, Rank.ACE),
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.SPADES, Rank.TWO),
        Card(Suit.HEARTS, Rank.QUEEN),
    ]

    for player, card in zip(players, cards):
        player.receive_card(card)

    trick = Trick(players[0], trump=Suit.SPADES)

    for player, card in zip(players, cards):
        trick.play_card(player, card)

    assert trick.winner() == players[2]


def test_winner_cannot_be_checked_before_trick_is_complete():
    players = create_players()

    card = Card(Suit.CLUBS, Rank.ACE)
    players[0].receive_card(card)

    trick = Trick(players[0])
    trick.play_card(players[0], card)

    with pytest.raises(ValueError):
        trick.winner()

        
def test_no_trump_uses_lead_suit_only():
    players = create_players()

    cards = [
        Card(Suit.HEARTS, Rank.TEN),
        Card(Suit.HEARTS, Rank.ACE),
        Card(Suit.SPADES, Rank.ACE),
        Card(Suit.CLUBS, Rank.ACE),
    ]

    for player, card in zip(players, cards):
        player.receive_card(card)

    trick = Trick(players[0], trump=None)

    for player, card in zip(players, cards):
        trick.play_card(player, card)

    assert trick.winner() == players[1]
