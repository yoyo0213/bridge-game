from bridge_game.cards.card import Card, Rank, Suit
from bridge_game.cards.hand import Hand
from bridge_game.game.rules import can_play_card


def test_first_player_can_play_any_card():
    hand = Hand()

    spade_ace = Card(Suit.SPADES, Rank.ACE)
    heart_two = Card(Suit.HEARTS, Rank.TWO)

    hand.add(spade_ace)
    hand.add(heart_two)

    assert can_play_card(hand, spade_ace, None)
    assert can_play_card(hand, heart_two, None)


def test_player_must_follow_lead_suit():
    hand = Hand()

    heart_ace = Card(Suit.HEARTS, Rank.ACE)
    spade_king = Card(Suit.SPADES, Rank.KING)

    hand.add(heart_ace)
    hand.add(spade_king)

    assert can_play_card(hand, heart_ace, Suit.HEARTS)
    assert not can_play_card(hand, spade_king, Suit.HEARTS)


def test_player_can_play_other_suit_if_void_in_lead_suit():
    hand = Hand()

    spade_king = Card(Suit.SPADES, Rank.KING)
    club_two = Card(Suit.CLUBS, Rank.TWO)

    hand.add(spade_king)
    hand.add(club_two)

    assert can_play_card(hand, spade_king, Suit.HEARTS)
    assert can_play_card(hand, club_two, Suit.HEARTS)


def test_player_cannot_play_card_not_in_hand():
    hand = Hand()

    heart_ace = Card(Suit.HEARTS, Rank.ACE)
    spade_ace = Card(Suit.SPADES, Rank.ACE)

    hand.add(heart_ace)

    assert not can_play_card(hand, spade_ace, None)