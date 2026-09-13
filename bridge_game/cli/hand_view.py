from bridge_game.cards.card import Suit


HAND_SUIT_ORDER = {
    Suit.CLUBS: 0,
    Suit.DIAMONDS: 1,
    Suit.SPADES: 2,
    Suit.HEARTS: 3,
}


def sorted_hand_view(hand):
    """Return a presentation-only copy of a hand in terminal display order."""
    return sorted(
        hand.cards,
        key=lambda card: (HAND_SUIT_ORDER[card.suit], card.rank.value),
    )
