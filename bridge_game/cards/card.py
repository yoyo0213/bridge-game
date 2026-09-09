class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __eq__(self, other):
        if not isinstance(other, Card):
            return False

        return self.suit == other.suit and self.rank == other.rank