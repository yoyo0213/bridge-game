from bridge_game.cards.card import Card, Rank, Suit
from bridge_game.cards.hand import Hand


def test_new_hand_is_empty():
    hand = Hand()

    assert len(hand) == 0


def test_hand_can_add_card():
    hand = Hand()
    card = Card(Suit.SPADES, Rank.ACE)

    hand.add(card)

    assert len(hand) == 1
    assert card in hand


def test_hand_can_remove_card():
    hand = Hand()
    card = Card(Suit.HEARTS, Rank.KING)

    hand.add(card)
    hand.remove(card)

    assert len(hand) == 0
    assert card not in hand


def test_hand_contains_multiple_cards():
    hand = Hand()

    card1 = Card(Suit.CLUBS, Rank.TWO)
    card2 = Card(Suit.DIAMONDS, Rank.TEN)
    card3 = Card(Suit.SPADES, Rank.ACE)

    hand.add(card1)
    hand.add(card2)
    hand.add(card3)

    assert len(hand) == 3
    assert card1 in hand
    assert card2 in hand
    assert card3 in hand