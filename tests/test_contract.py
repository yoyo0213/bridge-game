from bridge_game.cards.card import Suit
from bridge_game.game.bid import Bid, Strain
from bridge_game.game.bidding_result import BiddingResult
from bridge_game.game.contract import (
    strain_to_suit,
    bidding_result_to_trump,
)


def test_clubs_strain_to_suit():
    assert strain_to_suit(Strain.CLUBS) == Suit.CLUBS


def test_diamonds_strain_to_suit():
    assert strain_to_suit(Strain.DIAMONDS) == Suit.DIAMONDS


def test_hearts_strain_to_suit():
    assert strain_to_suit(Strain.HEARTS) == Suit.HEARTS


def test_spades_strain_to_suit():
    assert strain_to_suit(Strain.SPADES) == Suit.SPADES


def test_no_trump_returns_none():
    assert strain_to_suit(Strain.NO_TRUMP) is None


def test_bidding_result_returns_correct_trump():
    result = BiddingResult(
        Bid(4, Strain.HEARTS),
        "P3",
    )

    assert bidding_result_to_trump(result) == Suit.HEARTS


def test_no_trump_result_returns_none():
    result = BiddingResult(
        Bid(3, Strain.NO_TRUMP),
        "P1",
    )

    assert bidding_result_to_trump(result) is None


def test_all_pass_returns_none():
    result = BiddingResult(
        bid=None,
        bidder_id=None,
    )

    assert bidding_result_to_trump(result) is None