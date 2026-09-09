import pytest

from bridge_game.cards.card import Card, Rank, Suit
from bridge_game.game.round import Round
from bridge_game.players.player import Player


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