from bridge_game.game.trick import Trick
from bridge_game.game.bidding_result import BiddingResult
from bridge_game.game.contract import bidding_result_to_trump


class Round:
    def __init__(self, players, leader_index=0, trump=None):
        if len(players) != 4:
            raise ValueError("Round requires exactly 4 players")

        self.bidding_result = None

        self.bidder_id = None
        self.bidder_target = None
        self.opponent_target = None

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

    def set_bidding_result(self, result: BiddingResult):
        if not result.has_contract:
            raise ValueError(
                "Cannot start round without a bidding contract"
            )

        self.bidding_result = result

        self.bidder_id = result.bidder_id
        self.bidder_target = result.bidder_target
        self.opponent_target = result.opponent_target

        self.trump = bidding_result_to_trump(result)

        # 重新建立第一墩，讓它使用 bidding 決定的 trump
        self.current_trick = Trick(
            self.players[self.current_leader_index],
            trump=self.trump,
        )

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