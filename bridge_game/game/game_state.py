from bridge_game.game.round import Round
from bridge_game.game.contract_assignment import assign_contract_to_teams
from bridge_game.game.final_result import create_final_result
from bridge_game.game.round_result import create_round_result


class GameState:
    PLAYER_COUNT = 4
    TEAM_COUNT = 2
    ROUND_COUNT = 4

    def __init__(self, players, teams, current_round_number=1):
        self._validate_players(players)
        self._validate_teams(players, teams)
        self._validate_round_number(current_round_number)

        self.players = list(players)
        self.teams = list(teams)
        self.current_round_number = current_round_number
        self.current_round = None
        self.round_results = []
        self.is_finished = False

    def start_round(self, round_: Round):
        if self.is_finished:
            raise ValueError("Cannot start a round after the game is finished")

        if self.current_round is not None:
            raise ValueError("A round is already in progress")

        if not isinstance(round_, Round):
            raise TypeError("current round must be a Round")

        if {id(player) for player in round_.players} != {
            id(player) for player in self.players
        }:
            raise ValueError("Round players must match the game players")

        self.current_round = round_

    def complete_current_round(self):
        if self.current_round is None:
            raise ValueError("There is no current round to complete")

        if not self.current_round.is_complete:
            raise ValueError("Cannot complete a round while it is still in progress")

        if self.current_round.bidding_result is None:
            raise ValueError("Cannot score a round without a bidding contract")

        assignment = assign_contract_to_teams(
            self.current_round.bidding_result,
            self.players,
            self.teams,
        )
        result = create_round_result(
            self.current_round,
            self.current_round_number,
            assignment,
        )
        players_by_id = {player.player_id: player for player in self.players}
        for player_id, points in result.player_round_scores.items():
            players_by_id[player_id].add_score(points)
        self.round_results.append(result)

        self.current_round = None

        if self.current_round_number == self.ROUND_COUNT:
            self.is_finished = True
        else:
            self.current_round_number += 1

        return result

    @property
    def final_result(self):
        if not self.is_finished:
            raise ValueError("Final result is only available after four rounds")
        return create_final_result(self.players, self.teams)

    @classmethod
    def _validate_players(cls, players):
        if len(players) != cls.PLAYER_COUNT:
            raise ValueError("GameState requires exactly 4 players")

        if len({id(player) for player in players}) != cls.PLAYER_COUNT:
            raise ValueError("GameState requires 4 unique players")

        player_ids = [player.player_id for player in players]
        if any(
            player_id in player_ids[:index]
            for index, player_id in enumerate(player_ids)
        ):
            raise ValueError("GameState requires 4 unique player IDs")

    @classmethod
    def _validate_teams(cls, players, teams):
        if len(teams) != cls.TEAM_COUNT:
            raise ValueError("GameState requires exactly 2 teams")

        if len({id(team) for team in teams}) != cls.TEAM_COUNT:
            raise ValueError("GameState requires 2 unique teams")

        team_players = [
            player
            for team in teams
            for player in (team.player1, team.player2)
        ]

        if len({id(player) for player in team_players}) != cls.PLAYER_COUNT:
            raise ValueError("Each game player must belong to exactly one team")

        if {id(player) for player in team_players} != {
            id(player) for player in players
        }:
            raise ValueError("Teams must contain all and only the game players")

    @classmethod
    def _validate_round_number(cls, round_number):
        if not isinstance(round_number, int):
            raise TypeError("Round number must be an integer")

        if not 1 <= round_number <= cls.ROUND_COUNT:
            raise ValueError("Round number must be between 1 and 4")
