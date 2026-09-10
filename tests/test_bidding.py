import pytest

from bridge_game.game.bid import Bid, Strain
from bridge_game.game.bidding import Bidding


PLAYERS = ["P1", "P2", "P3", "P4"]


def test_bidding_starts_with_first_player():
    bidding = Bidding(PLAYERS)

    assert bidding.current_player == "P1"
    assert bidding.highest_bid is None
    assert bidding.finished is False


def test_turn_advances_after_bid():
    bidding = Bidding(PLAYERS)

    bidding.make_bid("P1", Bid(1, Strain.HEARTS))

    assert bidding.current_player == "P2"
    assert bidding.highest_bid == Bid(1, Strain.HEARTS)


def test_turn_advances_after_pass():
    bidding = Bidding(PLAYERS)

    bidding.pass_turn("P1")

    assert bidding.current_player == "P2"


def test_player_cannot_act_out_of_turn():
    bidding = Bidding(PLAYERS)

    with pytest.raises(ValueError):
        bidding.make_bid("P2", Bid(1, Strain.HEARTS))


def test_new_bid_must_be_higher():
    bidding = Bidding(PLAYERS)

    bidding.make_bid("P1", Bid(1, Strain.SPADES))

    with pytest.raises(ValueError):
        bidding.make_bid("P2", Bid(1, Strain.HEARTS))


def test_three_passes_after_bid_end_bidding():
    bidding = Bidding(PLAYERS)

    bidding.make_bid("P1", Bid(1, Strain.HEARTS))
    bidding.pass_turn("P2")
    bidding.pass_turn("P3")
    bidding.pass_turn("P4")

    assert bidding.finished is True
    assert bidding.highest_bid == Bid(1, Strain.HEARTS)
    assert bidding.highest_bidder == "P1"


def test_new_bid_resets_consecutive_passes():
    bidding = Bidding(PLAYERS)

    bidding.make_bid("P1", Bid(1, Strain.HEARTS))
    bidding.pass_turn("P2")
    bidding.pass_turn("P3")

    bidding.make_bid("P4", Bid(1, Strain.SPADES))

    assert bidding.consecutive_passes == 0
    assert bidding.finished is False


def test_four_initial_passes_end_bidding_without_bid():
    bidding = Bidding(PLAYERS)

    bidding.pass_turn("P1")
    bidding.pass_turn("P2")
    bidding.pass_turn("P3")
    bidding.pass_turn("P4")

    assert bidding.finished is True
    assert bidding.highest_bid is None
    assert bidding.highest_bidder is None


def test_cannot_act_after_bidding_finished():
    bidding = Bidding(PLAYERS)

    bidding.make_bid("P1", Bid(1, Strain.HEARTS))
    bidding.pass_turn("P2")
    bidding.pass_turn("P3")
    bidding.pass_turn("P4")

    with pytest.raises(ValueError):
        bidding.make_bid("P1", Bid(1, Strain.SPADES))

def test_finished_bidding_returns_result():
    bidding = Bidding(PLAYERS)

    bidding.make_bid(
        "P1",
        Bid(4, Strain.HEARTS),
    )

    bidding.pass_turn("P2")
    bidding.pass_turn("P3")
    bidding.pass_turn("P4")

    result = bidding.result

    assert result.bid == Bid(4, Strain.HEARTS)
    assert result.bidder_id == "P1"
    assert result.bidder_target == 10
    assert result.opponent_target == 3


def test_result_cannot_be_requested_before_bidding_finishes():
    bidding = Bidding(PLAYERS)

    with pytest.raises(ValueError):
        _ = bidding.result