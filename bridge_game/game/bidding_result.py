from dataclasses import dataclass

from bridge_game.game.bid import Bid, Strain


@dataclass(frozen=True)
class BiddingResult:
    bid: Bid | None
    bidder_id: object | None

    def __post_init__(self):
        if (self.bid is None) != (self.bidder_id is None):
            raise ValueError(
                "Bid and bidder_id must either both be set or both be None"
            )

    @property
    def has_contract(self) -> bool:
        return self.bid is not None

    @property
    def bidder_target(self) -> int | None:
        if self.bid is None:
            return None

        return self.bid.level + 6

    @property
    def opponent_target(self) -> int | None:
        if self.bid is None:
            return None

        return 7 - self.bid.level

    @property
    def trump_strain(self) -> Strain | None:
        if self.bid is None:
            return None

        if self.bid.strain == Strain.NO_TRUMP:
            return None

        return self.bid.strain
