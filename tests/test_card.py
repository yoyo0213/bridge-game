from bridge_game.cards.card import Card, Rank, Suit


def test_card_creation():
    card = Card(Suit.SPADES, Rank.ACE)

    assert card.suit == Suit.SPADES
    assert card.rank == Rank.ACE


def test_card_equality():
    card1 = Card(Suit.SPADES, Rank.ACE)
    card2 = Card(Suit.SPADES, Rank.ACE)
    card3 = Card(Suit.HEARTS, Rank.ACE)

    assert card1 == card2
    assert card1 != card3


def test_card_not_equal_to_other_type():
    card = Card(Suit.SPADES, Rank.ACE)

    assert card != "Spades A"
    assert card != 5
    assert card is not None