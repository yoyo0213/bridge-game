from dataclasses import dataclass

from bridge_game.game.contract_assignment import ContractAssignment
from bridge_game.game.round import Round
from bridge_game.players.team import Team


@dataclass(frozen=True)
class RoundResult:
    round_number: int
    contract_assignment: ContractAssignment
    bidding_team_trick_count: int
    opposing_team_trick_count: int

    def __post_init__(self):
        if not isinstance(self.contract_assignment, ContractAssignment):
            raise TypeError("contract_assignment must be a ContractAssignment")

        if not isinstance(self.round_number, int):
            raise TypeError("Round number must be an integer")

        if not 1 <= self.round_number <= 4:
            raise ValueError("Round number must be between 1 and 4")

        if not isinstance(self.bidding_team_trick_count, int):
            raise TypeError("Bidding team trick count must be an integer")

        if not isinstance(self.opposing_team_trick_count, int):
            raise TypeError("Opposing team trick count must be an integer")

        if self.bidding_team_trick_count < 0:
            raise ValueError("Bidding team trick count cannot be negative")

        if self.opposing_team_trick_count < 0:
            raise ValueError("Opposing team trick count cannot be negative")

        if (
            self.bidding_team_trick_count
            + self.opposing_team_trick_count
            != Round.TRICKS_PER_ROUND
        ):
            raise ValueError("Team trick counts must sum to 13")

    @property
    def bidding_team(self) -> Team:
        return self.contract_assignment.bidding_team

    @property
    def opposing_team(self) -> Team:
        return self.contract_assignment.opposing_team

    @property
    def bidding_team_target(self) -> int:
        return self.contract_assignment.bidding_team_target

    @property
    def opposing_team_target(self) -> int:
        return self.contract_assignment.opposing_team_target

    @property
    def bidding_team_met_target(self) -> bool:
        return self.bidding_team_trick_count >= self.bidding_team_target

    @property
    def opposing_team_met_target(self) -> bool:
        return self.opposing_team_trick_count >= self.opposing_team_target


def create_round_result(
    round_: Round,
    round_number: int,
    contract_assignment: ContractAssignment,
) -> RoundResult:
    completed_trick_count = len(round_.completed_tricks)
    if completed_trick_count != Round.TRICKS_PER_ROUND:
        raise ValueError("Round must contain exactly 13 completed tricks")

    if not round_.is_complete:
        raise ValueError("Cannot create a result for an incomplete round")

    bidding_count = 0
    opposing_count = 0

    for trick in round_.completed_tricks:
        winner = trick.winner()
        winner_teams = [
            team
            for team in (
                contract_assignment.bidding_team,
                contract_assignment.opposing_team,
            )
            if team.player1 is winner or team.player2 is winner
        ]

        if len(winner_teams) != 1:
            raise ValueError("Each trick winner must belong to exactly one team")

        if winner_teams[0] is contract_assignment.bidding_team:
            bidding_count += 1
        else:
            opposing_count += 1

    return RoundResult(
        round_number=round_number,
        contract_assignment=contract_assignment,
        bidding_team_trick_count=bidding_count,
        opposing_team_trick_count=opposing_count,
    )
