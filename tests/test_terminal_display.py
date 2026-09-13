from bridge_game.cards.card import Card, Rank, Suit
from bridge_game.cli.hand_view import sorted_hand_view
from bridge_game.cli.terminal_display import TerminalDisplay
from bridge_game.game.round import Round
from bridge_game.players.player import Player


def make_players():
    return [
        Player("N", "North", "North"),
        Player("E", "East", "East"),
        Player("S", "South", "South"),
        Player("W", "West", "West"),
    ]


def test_sorted_hand_view_uses_presentation_order_without_mutating_hand():
    player = make_players()[0]
    cards = [
        Card(Suit.SPADES, Rank.ACE),
        Card(Suit.CLUBS, Rank.THREE),
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.SPADES, Rank.TWO),
        Card(Suit.DIAMONDS, Rank.TEN),
        Card(Suit.CLUBS, Rank.SEVEN),
        Card(Suit.HEARTS, Rank.QUEEN),
        Card(Suit.DIAMONDS, Rank.FOUR),
    ]
    for card in cards:
        player.receive_card(card)

    view = sorted_hand_view(player.hand)

    assert [str(card) for card in view] == [
        "3♣", "7♣", "4♦", "10♦", "2♠", "A♠", "Q♥", "K♥"
    ]
    assert player.hand.cards == cards


def test_turn_state_marks_only_core_legal_cards_in_sorted_view():
    players = make_players()
    round_ = Round(players)
    lead = Card(Suit.CLUBS, Rank.TEN)
    players[0].receive_card(lead)
    round_.play_card(players[0], lead)
    east = players[1]
    for card in (
        Card(Suit.HEARTS, Rank.KING),
        Card(Suit.CLUBS, Rank.ACE),
        Card(Suit.SPADES, Rank.SEVEN),
        Card(Suit.CLUBS, Rank.TWO),
    ):
        east.receive_card(card)

    messages = []
    display = TerminalDisplay(messages.append)

    class Team:
        player1 = players[0]
        player2 = players[2]

        def __contains__(self, player):
            return player in (self.player1, self.player2)

    class Assignment:
        bidding_team = Team()
        bidder = players[0]
        bidding_team_target = 7

    class Scoring:
        player_trick_counts = {player.player_id: 0 for player in players}

    display.turn_state(east, 1, round_, Assignment(), Scoring())

    hand_lines = [line for line in messages if "[" in line]
    assert hand_lines == [
        "* [1] 2♣",
        "* [2] A♣",
        "  [3] 7♠",
        "  [4] K♥",
    ]
