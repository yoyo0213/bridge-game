def can_play_card(hand, card, lead_suit):
    if card not in hand:
        return False

    if lead_suit is None:
        return True

    has_lead_suit = any(
        hand_card.suit == lead_suit
        for hand_card in hand.cards
    )

    if has_lead_suit:
        return card.suit == lead_suit

    return True