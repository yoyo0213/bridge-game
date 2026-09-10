import pytest

from bridge_game.game.bid import Bid, Strain


def test_bid_level_must_be_between_1_and_7():
    with pytest.raises(ValueError):
        Bid(0, Strain.CLUBS)

    with pytest.raises(ValueError):
        Bid(8, Strain.CLUBS)


def test_bid_accepts_valid_levels():
    for level in range(1, 8):
        bid = Bid(level, Strain.CLUBS)

        assert bid.level == level


def test_strain_order_within_same_level():
    assert Bid(1, Strain.CLUBS) < Bid(1, Strain.DIAMONDS)
    assert Bid(1, Strain.DIAMONDS) < Bid(1, Strain.HEARTS)
    assert Bid(1, Strain.HEARTS) < Bid(1, Strain.SPADES)
    assert Bid(1, Strain.SPADES) < Bid(1, Strain.NO_TRUMP)


def test_higher_level_beats_lower_level():
    assert Bid(1, Strain.NO_TRUMP) < Bid(2, Strain.CLUBS)


def test_bid_equality():
    assert Bid(2, Strain.HEARTS) == Bid(2, Strain.HEARTS)


def test_different_bids_are_not_equal():
    assert Bid(2, Strain.HEARTS) != Bid(2, Strain.SPADES)