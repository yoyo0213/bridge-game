from bridge_game.game.bid import Bid, Strain


class TerminalInput:
    STRAINS = {
        "clubs": Strain.CLUBS,
        "diamonds": Strain.DIAMONDS,
        "hearts": Strain.HEARTS,
        "spades": Strain.SPADES,
        "no trump": Strain.NO_TRUMP,
        "nt": Strain.NO_TRUMP,
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
        while True:
            raw_value = self.input("Choose card: ").strip()
            try:
                card_number = int(raw_value)
            except ValueError:
                self.output("Invalid input. Please enter a number.")
                continue
            if not 1 <= card_number <= len(player.hand):
                self.output("Invalid card number.")
                continue

            card = player.hand.cards[card_number - 1]
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
            raw_value = self.input("Contract (7-13): ").strip()
            try:
                contract = int(raw_value)
            except ValueError:
                self.output("Invalid input. Please enter a number.")
                continue
            if 7 <= contract <= 13:
                return contract
            self.output("Contract must be between 7 and 13.")

    def _read_strain(self):
        while True:
            value = self.input(
                "Strain (Clubs/Diamonds/Hearts/Spades/No Trump): "
            ).strip().lower()
            if value in self.STRAINS:
                return self.STRAINS[value]
            self.output("Invalid strain.")
