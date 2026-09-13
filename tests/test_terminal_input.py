from bridge_game.cards.card import Card, Rank, Suit
from bridge_game.cli.terminal_input import TerminalInput
from bridge_game.game.bid import Bid, Strain
from bridge_game.game.bidding import Bidding
from bridge_game.game.round import Round
from bridge_game.players.player import Player


def make_round_waiting_for_east():
    players = [
        Player("N", "North", "North"),
        Player("E", "East", "East"),
        Player("S", "South", "South"),
        Player("W", "West", "West"),
    ]
    round_ = Round(players)
    north_card = Card(Suit.CLUBS, Rank.TWO)
    players[0].receive_card(north_card)
    round_.play_card(players[0], north_card)
    players[1].receive_card(Card(Suit.HEARTS, Rank.ACE))
    players[1].receive_card(Card(Suit.CLUBS, Rank.THREE))
    return round_, players


def terminal_input(values, messages):
    values = iter(values)
    return TerminalInput(lambda _prompt: next(values), messages.append)


def test_non_numeric_and_out_of_range_card_inputs_do_not_change_state():
    round_, players = make_round_waiting_for_east()
    east = players[1]
    original_cards = list(east.hand.cards)
    messages = []

    terminal_input(["abc", "20", "1"], messages).choose_and_play_card(
        round_, east
    )

    assert "Invalid input. Please enter a number." in messages
    assert "Invalid card number." in messages
    assert east.hand.cards == original_cards[:1]
    assert round_.current_player is players[2]
    assert len(round_.current_trick) == 2


def test_follow_suit_failure_keeps_card_and_same_player_turn():
    round_, players = make_round_waiting_for_east()
    east = players[1]
    heart = east.hand.cards[0]
    messages = []

    terminal_input(["2", "1"], messages).choose_and_play_card(round_, east)

    assert "Invalid card." in messages
    assert "You must follow Clubs." in messages
    assert heart in east.hand
    assert round_.current_player is players[2]
    assert len(round_.current_trick) == 2


def test_player_without_lead_suit_can_play_another_suit():
    round_, players = make_round_waiting_for_east()
    east = players[1]
    east.hand.remove(east.hand.cards[1])

    terminal_input(["1"], []).choose_and_play_card(round_, east)

    assert len(east.hand) == 0
    assert round_.current_player is players[2]


def test_terminal_bidding_uses_core_bidding_and_produces_contract():
    players = ["N", "E", "S", "W"]
    bidding = Bidding(players)
    controls = terminal_input(
        ["bid", "9", "no trump", "pass", "pass", "pass"], []
    )

    while not bidding.finished:
        player_id = bidding.current_player
        player = Player(player_id, player_id, player_id)
        controls.take_bidding_turn(bidding, player)

    assert bidding.result.bidder_id == "N"
    assert bidding.result.bidder_target == 9
    assert bidding.result.bid.strain.name == "NO_TRUMP"


def test_bidding_accepts_case_insensitive_strain_initial():
    bidding = Bidding(["N", "E", "S", "W"])

    terminal_input(["bid", "7", "s"], []).take_bidding_turn(
        bidding, Player("N", "North", "North")
    )

    assert bidding.highest_bid == Bid(1, Strain.SPADES)


def test_bidding_keeps_original_numeric_strain_order():
    bidding = Bidding(["N", "E", "S", "W"])

    terminal_input(["bid", "7", "3"], []).take_bidding_turn(
        bidding, Player("N", "North", "North")
    )

    assert bidding.highest_bid == Bid(1, Strain.HEARTS)


def test_invalid_trump_reprompts_without_crashing():
    messages = []
    controls = terminal_input(["X", "ABC", "6", "n"], messages)

    assert controls._read_strain() == Strain.NO_TRUMP
    assert messages.count("Invalid trump.") == 3
    assert messages.count("Please enter C, D, H, S, or N.") == 3


def test_card_number_selects_from_sorted_hand_view():
    round_, players = make_round_waiting_for_east()
    east = players[1]
    club = east.hand.cards[1]

    terminal_input(["1"], []).choose_and_play_card(round_, east)

    assert club not in east.hand
    assert east.hand.cards == [Card(Suit.HEARTS, Rank.ACE)]
