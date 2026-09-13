from bridge_game.cli.hand_view import sorted_hand_view
from bridge_game.game.rules import can_play_card


class TerminalDisplay:
    def __init__(self, output_fn=print):
        self.output = output_fn

    def bidding_state(self, bidding, players_by_id):
        highest = self.format_bid(bidding.highest_bid)
        current = players_by_id[bidding.current_player].name
        self.output(f"Current highest bid: {highest}")
        self.output(f"Current player: {current}")
        player = players_by_id[bidding.current_player]
        self.output(f"Your total score: {player.score}")
        self.output("Your hand:")
        for index, card in enumerate(sorted_hand_view(player.hand), start=1):
            self.output(f"  [{index}] {card}")
        self.output("Bidding actions:")
        for player_id, bid in bidding.history:
            name = players_by_id[player_id].name
            self.output(f"  {name}: {self.format_bid(bid)}")

    def turn_state(
        self,
        player,
        round_number,
        round_,
        assignment,
        scoring,
    ):
        player_id = player.player_id
        total = player.score
        contract_tricks = sum(
            scoring.player_trick_counts[p.player_id]
            for p in (
                assignment.bidding_team.player1,
                assignment.bidding_team.player2,
            )
        )
        defending_tricks = len(round_.completed_tricks) - contract_tricks
        self.output(f"Round: {round_number}")
        self.output(f"Trick: {len(round_.completed_tricks) + 1} / 13")
        self.output(f"Current player: {player.name}")
        self.output(f"Your total score: {total}")
        self.output(f"Contract: {assignment.bidding_team_target}")
        self.output(f"Bidder: {assignment.bidder.name}")
        self.output(f"Trump: {self.format_trump(round_.trump)}")
        if player in assignment.bidding_team:
            self.output(
                f"Your team's round tricks: {contract_tricks} / "
                f"{assignment.bidding_team_target}"
            )
        else:
            self.output(f"Your team tricks: {defending_tricks}")
            self.output(
                f"Contract team tricks: {contract_tricks} / "
                f"{assignment.bidding_team_target}"
            )
        lead = round_.current_trick.lead_suit
        self.output(f"Lead suit: {lead.value if lead else 'None'}")
        plays = ", ".join(
            f"{played.name}: {card}"
            for played, card in round_.current_trick.plays
        )
        self.output(f"Cards played: {plays or 'None'}")
        self.output("Your hand:")
        for index, card in enumerate(sorted_hand_view(player.hand), start=1):
            marker = (
                "*"
                if can_play_card(player.hand, card, round_.current_trick.lead_suit)
                else " "
            )
            self.output(f"{marker} [{index}] {card}")
        self.output("* = legal card")

    def trick_result(
        self,
        trick,
        winner,
        winner_points,
        winner_total,
        assignment,
        scoring,
    ):
        cards = ", ".join(f"{p.name}: {c}" for p, c in trick.plays)
        contract_tricks = sum(
            scoring.player_trick_counts[p.player_id]
            for p in (
                assignment.bidding_team.player1,
                assignment.bidding_team.player2,
            )
        )
        defending_tricks = sum(
            scoring.player_trick_counts[p.player_id]
            for p in (
                assignment.opposing_team.player1,
                assignment.opposing_team.player2,
            )
        )
        self.output(f"Trick cards: {cards}")
        self.output(f"Trick winner: {winner.name}")
        self.output(f"Winner trick points: {winner_points}")
        self.output(f"Winner total score: {winner_total}")
        self.output(f"Contract team tricks: {contract_tricks}")
        self.output(f"Defending team tricks: {defending_tricks}")
        self.output(f"Contract target: {assignment.bidding_team_target}")
        self.output(f"Contract made: {scoring.contract_met}")
        self.output(f"Contract bonus awarded: {scoring.contract_bonus_awarded}")

    def round_result(self, result, players):
        self.output(f"Round {result.round_number} Result")
        self.output(f"Bidder: {result.bidder.name}")
        self.output(f"Contract: {result.contract}")
        self.output(f"Trump: {self.format_trump(result.trump)}")
        self.output(f"Contract made: {result.contract_met}")
        self.output(f"Contract bonus awarded: {result.contract_bonus_awarded}")
        for player in players:
            player_id = player.player_id
            self.output(
                f"{player.name}: {result.player_trick_counts[player_id]} "
                f"tricks, {result.player_round_scores[player_id]} round "
                f"points, {player.score} total points"
            )

    def final_result(self, result, players, teams):
        self.output("Final Individual Scores")
        ranking = sorted(
            players,
            key=lambda player: result.individual_scores[player.player_id],
            reverse=True,
        )
        for rank, player in enumerate(ranking, start=1):
            self.output(
                f"{rank}. {player.name}: "
                f"{result.individual_scores[player.player_id]}"
            )
        self.output("Final Team Scores")
        for team in teams:
            self.output(f"{team.name}: {result.team_scores[team]}")
        winner = result.winning_team.name if result.winning_team else "Tie"
        self.output(f"Winning team: {winner}")
        self.output("Game Over")

    @staticmethod
    def format_bid(bid):
        if bid is None:
            return "Pass / None"
        return f"{bid.level + 6} {bid.strain.name.replace('_', ' ').title()}"

    @staticmethod
    def format_trump(trump):
        return trump.value if trump is not None else "No Trump"
