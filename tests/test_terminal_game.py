from bridge_game.cards.card import Card, Rank, Suit
from bridge_game.cli.terminal_game import TerminalGame
from bridge_game.game.bid import Bid, Strain
from bridge_game.game.bidding_result import BiddingResult
from bridge_game.game.round import Round


class SilentInput:
    def input(self, _prompt):
        return ""


class RecordingDisplay:
    def __init__(self):
        self.rounds = []
        self.final = None

    def round_result(self, result, _players):
        self.rounds.append(result)

    def final_result(self, result, _players, _teams):
        self.final = result


class CompletedRoundTerminalGame(TerminalGame):
    def _prepare_round(self):
        round_ = Round(self.players)
        round_.set_bidding_result(
            BiddingResult(Bid(1, Strain.CLUBS), self.players[0].player_id)
        )
        for _ in range(13):
            desired_winner = self.players[0]
            for _ in range(4):
                player = round_.current_player
                rank = Rank.ACE if player is desired_winner else Rank.TWO
                card = Card(Suit.CLUBS, rank)
                player.receive_card(card)
                round_.play_card(player, card)
        return round_

    def _play_round(self, _round, _assignment):
        pass


def test_deal_gives_each_player_thirteen_cards():
    game = TerminalGame(clear_fn=lambda: None)

    game._deal_cards()

    assert [len(player.hand) for player in game.players] == [13, 13, 13, 13]
    assert len({card for player in game.players for card in player.hand.cards}) == 52


def test_terminal_game_completes_four_rounds_and_builds_final_result():
    display = RecordingDisplay()
    game = CompletedRoundTerminalGame(
        terminal_input=SilentInput(),
        display=display,
        clear_fn=lambda: None,
    )

    result = game.run()

    assert game.game_state.is_finished is True
    assert len(game.game_state.round_results) == 4
    assert len(display.rounds) == 4
    assert display.final is result
    assert game.players[0].score == 800
    assert result.individual_scores[game.players[0].player_id] == 800
    assert result.team_scores[game.teams[0]] == 800
    assert result.winning_team is game.teams[0]
