class Hand:
    def __init__(self):
        self.cards = []

    def __len__(self):
        return len(self.cards)

    def __contains__(self, card):
        return card in self.cards

    def add(self, card):
        self.cards.append(card)

    def remove(self, card):
        self.cards.remove(card)