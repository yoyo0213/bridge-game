from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from bridge_game.game.contract_assignment import ContractAssignment
from bridge_game.game.round import Round


CONTRACT_BONUSES = {
    7: 40,
    8: 50,
    9: 65,
    10: 90,
    11: 125,
    12: 170,
    13: 235,
}
CONTRACT_TRICK_POINTS = 10
OVERTRICK_POINTS = 15
DEFENDING_TRICK_POINTS = 15


@dataclass(frozen=True)
class ScoringContext:
    round_state: Round
    contract_assignment: ContractAssignment

    def __post_init__(self):
        if not isinstance(self.round_state, Round):
            raise TypeError("round_state must be a Round")
        if not isinstance(self.contract_assignment, ContractAssignment):
            raise TypeError("contract_assignment must be a ContractAssignment")
        if not self.round_state.is_complete:
            raise ValueError("Scoring requires a completed round")
        if len(self.round_state.completed_tricks) != Round.TRICKS_PER_ROUND:
            raise ValueError("Scoring requires exactly 13 completed tricks")


@dataclass(frozen=True)
class ScoringResult:
    player_trick_counts: Mapping[object, int]
    player_round_scores: Mapping[object, int]
    contract_met: bool
    contract_bonus_awarded: bool

    def __post_init__(self):
        object.__setattr__(
            self,
            "player_trick_counts",
            MappingProxyType(dict(self.player_trick_counts)),
        )
        object.__setattr__(
            self,
            "player_round_scores",
            MappingProxyType(dict(self.player_round_scores)),
        )


class BaseScoringPolicy:
    """Assign round points to the player who earned each trick."""

    def calculate(self, context: ScoringContext) -> ScoringResult:
        round_ = context.round_state
        assignment = context.contract_assignment
        contract = assignment.bidding_team_target
        if contract not in CONTRACT_BONUSES:
            raise ValueError("Contract must be between 7 and 13")

        player_tricks = {player.player_id: 0 for player in round_.players}
        player_scores = {player.player_id: 0 for player in round_.players}
        contract_team_tricks = 0
        bonus_awarded = False

        for trick in round_.completed_tricks:
            winner = trick.winner()
            winner_team = self._team_for_player(winner, assignment)
            player_tricks[winner.player_id] += 1

            if winner_team is assignment.bidding_team:
                contract_team_tricks += 1
                points = (
                    CONTRACT_TRICK_POINTS
                    if contract_team_tricks <= contract
                    else OVERTRICK_POINTS
                )
                player_scores[winner.player_id] += points
                if contract_team_tricks == contract:
                    player_scores[assignment.bidder.player_id] += (
                        CONTRACT_BONUSES[contract]
                    )
                    bonus_awarded = True
            else:
                player_scores[winner.player_id] += DEFENDING_TRICK_POINTS

        return ScoringResult(
            player_trick_counts=player_tricks,
            player_round_scores=player_scores,
            contract_met=contract_team_tricks >= contract,
            contract_bonus_awarded=bonus_awarded,
        )

    @staticmethod
    def _team_for_player(player, assignment):
        teams = [
            team
            for team in (assignment.bidding_team, assignment.opposing_team)
            if player in team
        ]
        if len(teams) != 1:
            raise ValueError("Each trick winner must belong to exactly one team")
        return teams[0]
