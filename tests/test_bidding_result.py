from bridge_game.game.bid import Bid, Strain
from bridge_game.game.bidding_result import BiddingResult


def test_bidding_result_has_contract():
    result = BiddingResult(
        Bid(4, Strain.HEARTS),
        "P3",
    )

    assert result.has_contract is True


def test_bidder_target_is_level_plus_six():
    result = BiddingResult(
        Bid(4, Strain.HEARTS),
        "P3",
    )

    assert result.bidder_target == 10


def test_opponent_target_is_seven_minus_level():
    result = BiddingResult(
        Bid(4, Strain.HEARTS),
        "P3",
    )

    assert result.opponent_target == 3


def test_level_one_targets():
    result = BiddingResult(
        Bid(1, Strain.CLUBS),
        "P1",
    )

    assert result.bidder_target == 7
    assert result.opponent_target == 6


def test_level_seven_targets():
    result = BiddingResult(
        Bid(7, Strain.NO_TRUMP),
        "P2",
    )

    assert result.bidder_target == 13
    assert result.opponent_target == 0


def test_no_trump_has_no_trump_strain():
    result = BiddingResult(
        Bid(3, Strain.NO_TRUMP),
        "P1",
    )

    assert result.trump_strain is None


def test_suit_contract_returns_trump_strain():
    result = BiddingResult(
        Bid(3, Strain.SPADES),
        "P1",
    )

    assert result.trump_strain == Strain.SPADES


def test_all_pass_has_no_contract():
    result = BiddingResult(
        bid=None,
        bidder_id=None,
    )

    assert result.has_contract is False
    assert result.bidder_target is None
    assert result.opponent_target is None
    assert result.trump_strain is None