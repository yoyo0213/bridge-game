from bridge_game.game.bid import Bid
from bridge_game.game.bidding_result import BiddingResult

class Bidding:
    def __init__(self, player_ids):
        if len(player_ids) != 4:
            raise ValueError("Bidding requires exactly 4 players")

        if any(
            player_id in player_ids[:index]
            for index, player_id in enumerate(player_ids)
        ):
            raise ValueError("Bidding requires 4 unique player IDs")

        self.player_ids = list(player_ids)
        self.current_index = 0

        self.highest_bid = None
        self.highest_bidder = None

        self.history = []
        self.consecutive_passes = 0
        self.finished = False

    @property
    def current_player(self):
        return self.player_ids[self.current_index]

    def make_bid(self, player_id, bid: Bid):
        self._validate_not_finished()
        self._validate_turn(player_id)

        if self.highest_bid is not None and not self.highest_bid < bid:
            raise ValueError(
                "New bid must be higher than the current highest bid"
            )

        self.highest_bid = bid
        self.highest_bidder = player_id
        self.consecutive_passes = 0

        self.history.append((player_id, bid))

        self._advance_turn()

    def pass_turn(self, player_id):
        self._validate_not_finished()
        self._validate_turn(player_id)

        self.history.append((player_id, None))
        self.consecutive_passes += 1

        if self.highest_bid is None:
            if self.consecutive_passes == 4:
                self.finished = True
                return
        elif self.consecutive_passes == 3:
            self.finished = True
            return

        self._advance_turn()

    def _advance_turn(self):
        self.current_index = (
            self.current_index + 1
        ) % len(self.player_ids)

    def _validate_turn(self, player_id):
        if player_id != self.current_player:
            raise ValueError("It is not this player's turn")

    def _validate_not_finished(self):
        if self.finished:
            raise ValueError("Bidding has already finished")

    @property
    def result(self) -> BiddingResult:
        if not self.finished:
            raise ValueError(
                "Cannot get bidding result before bidding is finished"
            )

        return BiddingResult(
            bid=self.highest_bid,
            bidder_id=self.highest_bidder,
        )
