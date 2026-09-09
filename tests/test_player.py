from bridge_game.cards.card import Card, Rank, Suit
from bridge_game.players.player import Player


def test_player_creation():
    player = Player(1, "Alice", "North")

    assert player.player_id == 1
    assert player.name == "Alice"
    assert player.position == "North"
    assert len(player.hand) == 0


def test_player_can_receive_card():
    player = Player(1, "Alice", "North")
    card = Card(Suit.SPADES, Rank.ACE)

    player.receive_card(card)

    assert len(player.hand) == 1
    assert card in player.hand


def test_player_can_play_card():
    player = Player(1, "Alice", "North")
    card = Card(Suit.HEARTS, Rank.KING)

    player.receive_card(card)
    played_card = player.play_card(card)

    assert played_card == card
    assert card not in player.hand
    assert len(player.hand) == 0