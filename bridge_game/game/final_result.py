from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from bridge_game.players.team import Team


@dataclass(frozen=True)
class FinalResult:
    individual_scores: Mapping[object, int]
    team_scores: Mapping[Team, int]
    winning_team: Team | None

    def __post_init__(self):
        object.__setattr__(
            self,
            "individual_scores",
            MappingProxyType(dict(self.individual_scores)),
        )
        object.__setattr__(
            self,
            "team_scores",
            MappingProxyType(dict(self.team_scores)),
        )


def create_final_result(players, teams) -> FinalResult:
    individual_scores = {player.player_id: player.score for player in players}
    team_scores = {
        team: team.player1.score + team.player2.score for team in teams
    }
    highest_score = max(team_scores.values())
    winners = [
        team for team, score in team_scores.items() if score == highest_score
    ]
    return FinalResult(
        individual_scores=individual_scores,
        team_scores=team_scores,
        winning_team=winners[0] if len(winners) == 1 else None,
    )
