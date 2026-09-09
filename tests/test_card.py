from bridge_game.cards.card import Card

def test_card_creation():
    card = Card("Spades", "A")

    assert card.suit == "Spades"
    assert card.rank == "A"

def test_card_equality():
    card1 = Card("Spades", "A")
    card2 = Card("Spades", "A")
    card3 = Card("Hearts", "A")

    assert card1 == card2
    assert card1 != card3