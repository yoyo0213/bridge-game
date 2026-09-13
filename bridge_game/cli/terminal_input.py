from bridge_game.game.bid import Bid, Strain
from bridge_game.cli.hand_view import sorted_hand_view


class TerminalInput:
    STRAINS = {
        "c": Strain.CLUBS,
        "clubs": Strain.CLUBS,
        "1": Strain.CLUBS,
        "d": Strain.DIAMONDS,
        "diamonds": Strain.DIAMONDS,
        "2": Strain.DIAMONDS,
        "h": Strain.HEARTS,
        "hearts": Strain.HEARTS,
        "3": Strain.HEARTS,
        "s": Strain.SPADES,
        "spades": Strain.SPADES,
        "4": Strain.SPADES,
        "n": Strain.NO_TRUMP,
        "no trump": Strain.NO_TRUMP,
        "nt": Strain.NO_TRUMP,
        "5": Strain.NO_TRUMP,
    }

    def __init__(self, input_fn=input, output_fn=print):
        self.input = input_fn
        self.output = output_fn

    def wait_until_ready(self, player):
        self.input(
            f"{player.name}'s turn. Other players please look away. "
            "Press Enter when ready..."
        )

    def take_bidding_turn(self, bidding, player):
        while True:
            action = self.input("Bid or Pass? ").strip().lower()
            if action in {"pass", "p"}:
                bidding.pass_turn(player.player_id)
                return
            if action not in {"bid", "b"}:
                self.output("Invalid input. Enter Bid or Pass.")
                continue
            contract = self._read_contract()
            strain = self._read_strain()
            try:
                bidding.make_bid(
                    player.player_id,
                    Bid(contract - 6, strain),
                )
                return
            except ValueError as error:
                self.output(f"Invalid bid: {error}")

    def choose_and_play_card(self, round_, player):
        hand_view = sorted_hand_view(player.hand)
        while True:
            raw_value = self.input("Choose card: ").strip()
            try:
                card_number = int(raw_value)
            except ValueError:
                self.output("Invalid input. Please enter a number.")
                continue
            if not 1 <= card_number <= len(hand_view):
                self.output("Invalid card number.")
                continue

            card = hand_view[card_number - 1]
            try:
                return round_.play_card(player, card)
            except ValueError:
                self.output("Invalid card.")
                if round_.current_trick.lead_suit is not None:
                    self.output(
                        f"You must follow "
                        f"{round_.current_trick.lead_suit.value}."
                    )

    def _read_contract(self):
        while True:
            raw_value = self.input("Bidding number (1-7): ").strip()
            try:
                contract = int(raw_value) + 6
            except ValueError:
                self.output("Invalid input. Please enter a number.")
                continue
            if 7 <= contract <= 13:
                return contract
            self.output("Bidding number must be between 1 and 7.")

    def _read_strain(self):
        while True:
            self.output("Choose trump:")
            self.output("[C] Clubs")
            self.output("[D] Diamonds")
            self.output("[H] Hearts")
            self.output("[S] Spades")
            self.output("[N] No Trump")
            value = self.input("> ").strip().lower()
            if value in self.STRAINS:
                return self.STRAINS[value]
            self.output("Invalid trump.")
            self.output("Please enter C, D, H, S, or N.")
