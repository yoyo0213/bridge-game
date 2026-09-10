from bridge_game.cards.card import Suit
from bridge_game.game.bid import Strain
from bridge_game.game.bidding_result import BiddingResult


def strain_to_suit(strain: Strain | None) -> Suit | None:
    if strain is None:
        return None

    mapping = {
        Strain.CLUBS: Suit.CLUBS,
        Strain.DIAMONDS: Suit.DIAMONDS,
        Strain.HEARTS: Suit.HEARTS,
        Strain.SPADES: Suit.SPADES,
        Strain.NO_TRUMP: None,
    }

    return mapping[strain]


def bidding_result_to_trump(
    result: BiddingResult,
) -> Suit | None:
    if not result.has_contract:
        return None

    return strain_to_suit(result.bid.strain)