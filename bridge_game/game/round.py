from bridge_game.game.trick import Trick
from bridge_game.game.bidding_result import BiddingResult
from bridge_game.game.contract import bidding_result_to_trump


class Round:
    TRICKS_PER_ROUND = 13

    def __init__(self, players, leader_index=0, trump=None):
        if len(players) != 4:
            raise ValueError("Round requires exactly 4 players")

        if len({id(player) for player in players}) != 4:
            raise ValueError("Round requires 4 unique players")

        player_ids = [player.player_id for player in players]
        if any(
            player_id in player_ids[:index]
            for index, player_id in enumerate(player_ids)
        ):
            raise ValueError("Round requires 4 unique player IDs")

        if not 0 <= leader_index < len(players):
            raise ValueError("leader_index must identify one of the players")

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
        if self.is_complete:
            return None

        return self.players[self.current_player_index]

    @property
    def is_complete(self):
        return len(self.completed_tricks) == self.TRICKS_PER_ROUND

    def set_bidding_result(self, result: BiddingResult):
        if self.bidding_result is not None:
            raise ValueError("Bidding result has already been set")

        if self.current_trick.plays or self.completed_tricks:
            raise ValueError("Cannot set bidding result after play has started")

        if not result.has_contract:
            raise ValueError(
                "Cannot start round without a bidding contract"
            )

        if not any(
            player.player_id == result.bidder_id
            for player in self.players
        ):
            raise ValueError("Bidder must be one of the round players")

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
        if self.is_complete:
            raise ValueError("Round is already complete")

        if player != self.current_player:
            raise ValueError("It is not this player's turn")

        self.current_trick.play_card(player, card)

        if self.current_trick.is_complete:
            winner = self.current_trick.winner()

            self.completed_tricks.append(self.current_trick)

            winner_index = self.players.index(winner)

            self.current_leader_index = winner_index
            self.current_player_index = winner_index

            if not self.is_complete:
                self.current_trick = Trick(
                    winner,
                    trump=self.trump,
                )

            return winner

        self.current_player_index = (
            self.current_player_index + 1
        ) % len(self.players)

        return None
