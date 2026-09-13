from bridge_game.cards.deck import Deck
from bridge_game.game.bidding import Bidding
from bridge_game.game.contract_assignment import assign_contract_to_teams
from bridge_game.game.game_state import GameState
from bridge_game.game.round import Round
from bridge_game.game.scoring import BaseScoringPolicy
from bridge_game.players.player import Player
from bridge_game.players.team import Team

from bridge_game.cli.terminal_display import TerminalDisplay
from bridge_game.cli.terminal_input import TerminalInput


class TerminalGame:
    def __init__(self, terminal_input=None, display=None, clear_fn=None):
        self.input = terminal_input or TerminalInput()
        self.display = display or TerminalDisplay()
        self.clear = clear_fn or self._clear_screen
        self.players = [
            Player("N", "North", "North"),
            Player("E", "East", "East"),
            Player("S", "South", "South"),
            Player("W", "West", "West"),
        ]
        self.teams = [
            Team("North / South", self.players[0], self.players[2]),
            Team("East / West", self.players[1], self.players[3]),
        ]
        self.game_state = GameState(self.players, self.teams)
        self.scoring_policy = BaseScoringPolicy()

    def run(self):
        while not self.game_state.is_finished:
            round_ = self._prepare_round()
            self.game_state.start_round(round_)
            assignment = assign_contract_to_teams(
                round_.bidding_result,
                self.players,
                self.teams,
            )
            self._play_round(round_, assignment)
            result = self.game_state.complete_current_round()
            self.display.round_result(result, self.players)
            if not self.game_state.is_finished:
                self.input.input("Press Enter to start the next round...")
                self.clear()

        final_result = self.game_state.final_result
        self.display.final_result(final_result, self.players, self.teams)
        return final_result

    def _prepare_round(self):
        self._deal_cards()
        bidding_result = self._run_bidding()
        round_ = Round(
            self.players,
            leader_index=self.game_state.current_round_number - 1,
        )
        round_.set_bidding_result(bidding_result)
        return round_

    def _deal_cards(self):
        deck = Deck()
        deck.shuffle()
        for _ in range(13):
            for player in self.players:
                player.receive_card(deck.draw())

    def _run_bidding(self):
        players_by_id = {player.player_id: player for player in self.players}
        while True:
            bidding = Bidding([player.player_id for player in self.players])
            while not bidding.finished:
                player = players_by_id[bidding.current_player]
                self.clear()
                self.input.wait_until_ready(player)
                self.display.bidding_state(bidding, players_by_id)
                self.input.take_bidding_turn(bidding, player)
                self.clear()
            if bidding.result.has_contract:
                return bidding.result
            self.display.output("All players passed. Bidding restarts.")

    def _play_round(self, round_, assignment):
        previous_scores = {
            player.player_id: 0 for player in self.players
        }
        while not round_.is_complete:
            player = round_.current_player
            self.clear()
            self.input.wait_until_ready(player)
            scoring = self.scoring_policy.calculate_progress(round_, assignment)
            self.display.turn_state(
                player,
                self.game_state.current_round_number,
                round_,
                assignment,
                scoring,
            )
            winner = self.input.choose_and_play_card(round_, player)
            self.clear()
            if winner is None:
                continue

            scoring = self.game_state.score_current_round_progress()
            winner_points = (
                scoring.player_round_scores[winner.player_id]
                - previous_scores[winner.player_id]
            )
            winner_total = winner.score
            self.display.trick_result(
                round_.completed_tricks[-1],
                winner,
                winner_points,
                winner_total,
                assignment,
                scoring,
            )
            previous_scores = dict(scoring.player_round_scores)
            self.input.input("Press Enter to continue...")
            self.clear()

    @staticmethod
    def _clear_screen():
        print("\033[2J\033[H", end="", flush=True)
