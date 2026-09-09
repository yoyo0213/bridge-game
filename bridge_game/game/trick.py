from bridge_game.game.rules import can_play_card

#============================
# trump=None means No Trump
#============================

class Trick:
    def __init__(self, leader, trump=None):
        self.leader = leader
        self.trump = trump
        self.plays = []

    def __len__(self):
        return len(self.plays)

    @property
    def lead_suit(self):
        if not self.plays:
            return None

        return self.plays[0][1].suit

    @property
    def is_complete(self):
        return len(self.plays) == 4

    def play_card(self, player, card):
        if self.is_complete:
            raise ValueError("Trick is already complete")

        if not can_play_card(player.hand, card, self.lead_suit):
            raise ValueError("Illegal card")

        player.play_card(card)
        self.plays.append((player, card))

    def winner(self):
        if not self.is_complete:
            raise ValueError("Trick is not complete")

        winning_player, winning_card = self.plays[0]

        for player, card in self.plays[1:]:
            if self._beats(card, winning_card):
                winning_player = player
                winning_card = card

        return winning_player

    def _beats(self, challenger, current):
        # Trump exists
        if self.trump is not None:
            challenger_is_trump = challenger.suit == self.trump
            current_is_trump = current.suit == self.trump

            if challenger_is_trump and not current_is_trump:
                return True

            if current_is_trump and not challenger_is_trump:
                return False


        # Neither has trump advantage:
        # only lead suit can win
        challenger_is_lead = challenger.suit == self.lead_suit
        current_is_lead = current.suit == self.lead_suit

        if challenger_is_lead and not current_is_lead:
            return True

        if current_is_lead and not challenger_is_lead:
            return False

        # Same relevant suit → compare rank
        if challenger.suit == current.suit:
            return challenger.rank.value > current.rank.value

        return False