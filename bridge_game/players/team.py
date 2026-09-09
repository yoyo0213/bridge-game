class Team:
    def __init__(self, name, player1, player2):
        self.name = name
        self.player1 = player1
        self.player2 = player2

    def __contains__(self, player):
        return player == self.player1 or player == self.player2