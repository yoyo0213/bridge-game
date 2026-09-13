from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from bridge_game.game.contract_assignment import ContractAssignment
from bridge_game.game.round import Round
from bridge_game.players.team import Team


@dataclass(frozen=True)
class RoundResult:
    round_number: int
    contract_assignment: ContractAssignment
    trump: object | None
    player_trick_counts: Mapping[object, int]
    player_round_scores: Mapping[object, int]
    contract_met: bool
    contract_bonus_awarded: bool

    def __post_init__(self):
        if not isinstance(self.contract_assignment, ContractAssignment):
            raise TypeError("contract_assignment must be a ContractAssignment")
        if not isinstance(self.round_number, int):
            raise TypeError("Round number must be an integer")
        if not 1 <= self.round_number <= 4:
            raise ValueError("Round number must be between 1 and 4")
        if sum(self.player_trick_counts.values()) != Round.TRICKS_PER_ROUND:
            raise ValueError("Player trick counts must sum to 13")
        if any(count < 0 for count in self.player_trick_counts.values()):
            raise ValueError("Player trick counts cannot be negative")
        if any(score < 0 for score in self.player_round_scores.values()):
            raise ValueError("Player round scores cannot be negative")
        if set(self.player_trick_counts) != set(self.player_round_scores):
            raise ValueError("Trick counts and scores must contain the same players")
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

    @property
    def contract(self) -> int:
        return self.contract_assignment.bidding_team_target

    @property
    def bidder(self):
        return self.contract_assignment.bidder

    @property
    def bidding_team(self) -> Team:
        return self.contract_assignment.bidding_team

    @property
    def opposing_team(self) -> Team:
        return self.contract_assignment.opposing_team

    @property
    def bidding_team_target(self) -> int:
        return self.contract

    @property
    def opposing_team_target(self) -> int:
        return self.contract_assignment.opposing_team_target

    @property
    def bidding_team_trick_count(self) -> int:
        return sum(
            self.player_trick_counts[player.player_id]
            for player in (self.bidding_team.player1, self.bidding_team.player2)
        )

    @property
    def opposing_team_trick_count(self) -> int:
        return sum(
            self.player_trick_counts[player.player_id]
            for player in (self.opposing_team.player1, self.opposing_team.player2)
        )

    @property
    def bidding_team_met_target(self) -> bool:
        return self.contract_met

    @property
    def opposing_team_met_target(self) -> bool:
        return self.opposing_team_trick_count >= self.opposing_team_target


def create_round_result(
    round_: Round,
    round_number: int,
    contract_assignment: ContractAssignment,
) -> RoundResult:
    if len(round_.completed_tricks) != Round.TRICKS_PER_ROUND:
        raise ValueError("Round must contain exactly 13 completed tricks")
    if not round_.is_complete:
        raise ValueError("Cannot create a result for an incomplete round")

    # Local import keeps scoring independent while avoiding a module cycle.
    from bridge_game.game.scoring import BaseScoringPolicy, ScoringContext

    scoring = BaseScoringPolicy().calculate(
        ScoringContext(round_, contract_assignment)
    )
    return RoundResult(
        round_number=round_number,
        contract_assignment=contract_assignment,
        trump=round_.trump,
        player_trick_counts=scoring.player_trick_counts,
        player_round_scores=scoring.player_round_scores,
        contract_met=scoring.contract_met,
        contract_bonus_awarded=scoring.contract_bonus_awarded,
    )
