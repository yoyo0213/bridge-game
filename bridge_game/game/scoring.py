from dataclasses import dataclass

from bridge_game.game.round import Round
from bridge_game.game.round_result import RoundResult


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
    STANDARD_TRICK_POINTS = 2
    POST_DECISION_TRICK_POINTS = 3
    FOURTH_ROUND_TRICK_POINTS = 4

    def calculate(self, context: ScoringContext) -> ScoringResult:
        round_result = context.round_result
        assignment = round_result.contract_assignment

        bidding_tricks = 0
        opposing_tricks = 0
        bidding_score = 0
        opposing_score = 0

        decided = self._is_decided(
            bidding_tricks,
            opposing_tricks,
            round_result,
        )

        for trick in context.round_state.completed_tricks:
            winner = trick.winner()
            winner_is_bidding_team = self._winner_is_bidding_team(
                winner,
                assignment,
            )

            if round_result.round_number == 4:
                trick_points = self.FOURTH_ROUND_TRICK_POINTS
            elif decided:
                trick_points = self.POST_DECISION_TRICK_POINTS
            else:
                trick_points = self.STANDARD_TRICK_POINTS

            if winner_is_bidding_team:
                bidding_tricks += 1
                bidding_score += trick_points
            else:
                opposing_tricks += 1
                opposing_score += trick_points

            decided = self._is_decided(
                bidding_tricks,
                opposing_tricks,
                round_result,
            )

        if (
            bidding_tricks != round_result.bidding_team_trick_count
            or opposing_tricks != round_result.opposing_team_trick_count
        ):
            raise ValueError("RoundResult trick counts do not match the round")

        return ScoringResult(
            bidding_team_score_delta=bidding_score,
            opposing_team_score_delta=opposing_score,
        )

    @staticmethod
    def _is_decided(bidding_tricks, opposing_tricks, round_result):
        tricks_played = bidding_tricks + opposing_tricks
        remaining_tricks = Round.TRICKS_PER_ROUND - tricks_played

        bidding_success_decided = (
            bidding_tricks >= round_result.bidding_team_target
        )
        bidding_failure_decided = (
            bidding_tricks + remaining_tricks
            < round_result.bidding_team_target
        )

        return bidding_success_decided or bidding_failure_decided

    @staticmethod
    def _winner_is_bidding_team(winner, assignment):
        winner_teams = [
            team
            for team in (assignment.bidding_team, assignment.opposing_team)
            if team.player1 is winner or team.player2 is winner
        ]

        if len(winner_teams) != 1:
            raise ValueError("Each trick winner must belong to exactly one team")

        return winner_teams[0] is assignment.bidding_team
