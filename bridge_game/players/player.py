from bridge_game.cards.hand import Hand


class Player:
    def __init__(self, player_id, name, position):
        self.player_id = player_id
        self.name = name
        self.position = position
        self.hand = Hand()

    def receive_card(self, card):
        self.hand.add(card)

    def play_card(self, card):
        self.hand.remove(card)
        return card