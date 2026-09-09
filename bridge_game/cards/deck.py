from bridge_game.cards.card import Card, Rank, Suit
import random

class Deck:
    def __init__(self):
        self.cards = [
            Card(suit, rank)
            for suit in Suit
            for rank in Rank
        ]

    def __len__(self):
        return len(self.cards)

    def draw(self):
        return self.cards.pop()

    def deal(self, count):
        return [self.draw() for _ in range(count)]

    def shuffle(self):
        random.shuffle(self.cards)