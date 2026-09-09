from bridge_game.cards.card import Card, Rank, Suit
from bridge_game.cards.deck import Deck


def test_card_has_expected_identity():
    card = Card(Suit.HEARTS, Rank.ACE)

    assert card.suit == Suit.HEARTS
    assert card.rank == Rank.ACE
    assert str(card) == "A♥"


def test_deck_contains_52_unique_cards():
    deck = Deck()

    assert len(deck) == 52
    assert len(set(deck.cards)) == 52
    assert deck.cards[0] == Card(Suit.CLUBS, Rank.TWO)
    assert deck.cards[-1] == Card(Suit.SPADES, Rank.ACE)


def test_deck_draw_returns_expected_cards_and_updates_size():
    deck = Deck()

    card = deck.draw()

    assert card == Card(Suit.SPADES, Rank.ACE)
    assert len(deck) == 51


def test_deck_deal_handles_multiple_cards():
    deck = Deck()

    dealt = deck.deal(5)

    assert [card.rank for card in dealt] == [Rank.ACE, Rank.KING, Rank.QUEEN, Rank.JACK, Rank.TEN]
    assert len(deck) == 47

def test_deck_shuffle_changes_card_order():
    deck = Deck()
    original_order = deck.cards.copy()

    deck.shuffle()

    assert deck.cards != original_order
    assert len(deck) == 52
    assert set(deck.cards) == set(original_order)