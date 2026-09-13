from bridge_game.cards.hand import Hand


class Player:
    def __init__(self, player_id, name, position):
        self.player_id = player_id
        self.name = name
        self.position = position
        self.hand = Hand()
        self._score = 0

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        if not isinstance(value, int):
            raise TypeError("Score must be an integer")
        if value < 0:
            raise ValueError("Score cannot be negative")
        self._score = value

    def add_score(self, points):
        if not isinstance(points, int):
            raise TypeError("Score points must be an integer")
        if points < 0:
            raise ValueError("Score points cannot be negative")
        self._score += points

    def receive_card(self, card):
        self.hand.add(card)

    def play_card(self, card):
        self.hand.remove(card)
        return card
