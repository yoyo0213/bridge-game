from bridge_game.game.trick import Trick


class Round:
    def __init__(self, players, leader_index=0, trump=None):
        if len(players) != 4:
            raise ValueError("Round requires exactly 4 players")

        self.players = players
        self.trump = trump
        self.current_leader_index = leader_index
        self.current_player_index = leader_index

        self.completed_tricks = []

        self.current_trick = Trick(
            self.players[self.current_leader_index],
            trump=self.trump,
        )

    @property
    def current_player(self):
        return self.players[self.current_player_index]

    def play_card(self, player, card):
        if player != self.current_player:
            raise ValueError("It is not this player's turn")

        self.current_trick.play_card(player, card)

        if self.current_trick.is_complete:
            winner = self.current_trick.winner()

            self.completed_tricks.append(self.current_trick)

            winner_index = self.players.index(winner)

            self.current_leader_index = winner_index
            self.current_player_index = winner_index

            self.current_trick = Trick(
                winner,
                trump=self.trump,
            )

            return winner

        self.current_player_index = (
            self.current_player_index + 1
        ) % len(self.players)

        return None