from bridge_game.game.round import Round


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
        self.team_scores = {team: 0 for team in self.teams}
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

        self.current_round = None

        if self.current_round_number == self.ROUND_COUNT:
            self.is_finished = True
        else:
            self.current_round_number += 1

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
