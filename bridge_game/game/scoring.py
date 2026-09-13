from dataclasses import dataclass

from bridge_game.game.round import Round
from bridge_game.game.round_result import RoundResult


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
    round_result: RoundResult

    def __post_init__(self):
        if not isinstance(self.round_state, Round):
            raise TypeError("round_state must be a Round")
        if not isinstance(self.round_result, RoundResult):
            raise TypeError("round_result must be a RoundResult")
        if not self.round_state.is_complete:
            raise ValueError("Scoring requires a completed round")
        if len(self.round_state.completed_tricks) != Round.TRICKS_PER_ROUND:
            raise ValueError("Scoring requires exactly 13 completed tricks")


@dataclass(frozen=True)
class ScoringResult:
    bidding_team_score_delta: int
    opposing_team_score_delta: int

    @property
    def total_score_delta(self) -> int:
        return self.bidding_team_score_delta + self.opposing_team_score_delta


class BaseScoringPolicy:
    """Calculate both teams' scores for a completed round."""

    def calculate(self, context: ScoringContext) -> ScoringResult:
        round_result = context.round_result
        self._validate_trick_counts(context)
        contract = round_result.bidding_team_target
        if contract not in CONTRACT_BONUSES:
            raise ValueError("Contract must be between 7 and 13")
        bidding_tricks = round_result.bidding_team_trick_count

        if bidding_tricks < contract:
            bidding_score = bidding_tricks * CONTRACT_TRICK_POINTS
        else:
            bidding_score = (
                contract * CONTRACT_TRICK_POINTS
                + CONTRACT_BONUSES[contract]
                + (bidding_tricks - contract) * OVERTRICK_POINTS
            )

        return ScoringResult(
            bidding_team_score_delta=bidding_score,
            opposing_team_score_delta=(
                round_result.opposing_team_trick_count * DEFENDING_TRICK_POINTS
            ),
        )

    @staticmethod
    def _validate_trick_counts(context: ScoringContext) -> None:
        assignment = context.round_result.contract_assignment
        bidding_tricks = 0
        opposing_tricks = 0
        for trick in context.round_state.completed_tricks:
            winner = trick.winner()
            winner_teams = [
                team
                for team in (assignment.bidding_team, assignment.opposing_team)
                if winner in team
            ]
            if len(winner_teams) != 1:
                raise ValueError("Each trick winner must belong to exactly one team")
            if winner_teams[0] is assignment.bidding_team:
                bidding_tricks += 1
            else:
                opposing_tricks += 1

        if (
            bidding_tricks != context.round_result.bidding_team_trick_count
            or opposing_tricks != context.round_result.opposing_team_trick_count
        ):
            raise ValueError("RoundResult trick counts do not match the round")
